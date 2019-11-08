#!/usr/bin/env python

#
# Author: Rui Yan 08/29/14 (yan49@purdue.edu)
# Copyright (c) 2014- Baylor College of Medicine
#
# This software is issued under a joint BSD/GNU license. You may use the
# source code in this file under either license. However, note that the
# complete EMAN2 and SPARX software packages have some GPL dependencies,
# so you are responsible for compliance with the licenses of these packages
# if you opt to use BSD licensing. The warranty disclaimer below holds
# in either instance.
#
# This complete copyright notice must be included in any revised version of the
# source code. Additional authorship citations may be added, but existing
# author citations must be preserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  2111-1307 USA
#
#

from EMAN2 import *
from optparse import OptionParser
from math import *
import os
import sys
import time
import traceback
import math
from EMAN2star import StarFile

def main():
	progname = os.path.basename(sys.argv[0])
	usage = """prog [options] <relion STAR file>

This program will take data from a Relion project and convert it into a basic EMAN2 project and generate a .lst file. Provide 
the name of the Relion STAR file associated with the raw particle data. An eman2 subdirectory will be
created, and the images, and available metadata will be copied into the new project. CTF parameters
will be extracted from the STAR file and will be automatically processed through EMAN1's CTF procedure
(this takes most of the time the script will require).

"""
	parser = EMArgumentParser(usage=usage,version=EMANVERSION)

	parser.add_argument("--lst", type=str, default='', help='.lst file.')
	parser.add_argument('--boxsize', type=int, default=0, help='box size')
	parser.add_argument('--allrelion',type=int, default=0, help='convert all relion parameters to lst file if set to 1')
	parser.add_argument("--verbose", "-v", dest="verbose", action="store", metavar="n", type=int, default=0, help="verbose level [0-9], higner number means higher level of verboseness")
	parser.add_argument("--ny", type=int, help="Particle NY size, so no need to read image to get this value",default=0)
	parser.add_argument("--ppid", type=int, help="Set the PID of the parent process, used for cross platform PPID",default=-1)

	(options, args) = parser.parse_args()

	logid=E2init(sys.argv,options.ppid)

	inputStarFileName = args[0]
	if not os.path.islink(inputStarFileName): 
            inputStarFileName = os.path.abspath(inputStarFileName)
        else:
            #print "%s is a link file"%(inputStarFileName)
            inputStarFileName = os.path.abspath(os.readlink(inputStarFileName))
	
	topdir = os.path.dirname(inputStarFileName)

#	try: os.mkdir("particles")
#	except: pass

	if options.verbose>0:
		print "Parsing STAR file %s" % (inputStarFileName)

	star=StarFile(inputStarFileName)
	#print star

	if (options.lst):
		lstfile = options.lst
	else:
		lstfile = os.path.basename(inputStarFileName)
		lstfile = lstfile[0: lstfile.rfind('.')] + '.lst'

	oldname=""
	olddf=-1.0
	micronum=0		# number of micrograph
	fnum=0			# image number in new file
	params = []
	for i in xrange(len(star["rlnImageName"])):
		name=star["rlnImageName"][i].split("@")[1]
		name=os.path.join(topdir, name)
		imgnum=int(star["rlnImageName"][i].split("@")[0])-1
		
		if (star.has_key("rlnMagnificationCorrection")): #for old version relion star filr
			apix = 1e4*float(star["rlnDetectorPixelSize"][i])/(float(star["rlnMagnification"][i])*float(star["rlnMagnificationCorrection"][i]))
		else:
			apix = 1e4*float(star["rlnDetectorPixelSize"][i])/(float(star["rlnMagnification"][i]))

		if name!=oldname:
	#		hdr=EMData(name,0,True)
	#		nx=hdr["nx"]
	#		ny=hdr["ny"]
			nx = options.ny
			ny = options.ny
			oldname=name

		if i==0 or star["rlnDefocusU"][i-1]!=star["rlnDefocusU"][i]:
                        #this line will not run when i==0 (the 1st loop)
			if micronum>0 and options.verbose>1:
				print "Image {}: {} particles, df={}, size={}x{}".format(micronum,fnum,ctf.defocus, nx, ny)

			micronum+=1
			fnum=0  #when reaching a new micrograph, fnum need to start from 0 for write_image to a new good particle HDF stack
			microname="particles/{}_{:04d}.hdf".format(base_name(name),micronum)

		boxsize = options.boxsize
		if boxsize<=0:
			boxsize=ny

		# Make a "micrograph" CTF entry for each set of different defocuses to use when fitting
		# check ctffind3.f function CTF(CS,WL,WGH1,WGH2,DFMID1,DFMID2,ANGAST,THETATR, IX, IY)
		dfu=star["rlnDefocusU"][i]/1e4
		dfv=star["rlnDefocusV"][i]/1e4
		dfang=star["rlnDefocusAngle"][i]

		defocus = (dfu+dfv)/2.
		dfdiff = math.fabs(dfu-dfv)/2.   # dfu can be larger or smaller than dfv
		if dfu>dfv:
			dfang = math.fmod(dfang+360.+90., 360.) # largest defocus direction to smallest defocus direction
		else:
			pass # already at smallest defocus direction

		ctf=EMAN1Ctf()
		ctf.from_dict({"defocus":defocus, "dfang":dfang, "dfdiff":dfdiff, "voltage":star["rlnVoltage"][i], "cs":star["rlnSphericalAberration"][i], "ampcont":star["rlnAmplitudeContrast"][i]*100.0, "apix":apix, "amplitude":1, "bfactor":1e-5})

		# copy the image
	#	if name[-5:]==".mrcs":
	#		img=EMData(name,imgnum)		# read one slice from the MRC stack
	#	else:
	#		img=EMData(name,0,False,Region(0,0,imgnum,nx,ny,1))		# read one slice from the MRC stack

	#	img["ctf"] = ctf
	#	img['apix_x'] = apix
	#	img['apix_y'] = apix

	#	if options.verbose>2:
	#		print "Particle %d: %s" % (i, img["ctf"].to_dict())

	#	img.write_image(microname,fnum,EMUtil.ImageType.IMAGE_HDF,False) #microname is a .hdf file, False tells it to write both header and image data

		#print star["rlnAngleRot"][i], star["rlnAngleTilt"][i], star["rlnAnglePsi"][i]
		alt, az, phi, x, y = relion2EMAN2(star["rlnAngleRot"][i], star["rlnAngleTilt"][i], star["rlnAnglePsi"][i], star["rlnOriginX"][i], star["rlnOriginY"][i], boxsize)

		#all particles in eman2/particles folder are good particles, so the 1st column in .lst file should be 0,1,2,3,4,... in order
		new_file = os.path.relpath(microname, os.getcwd())
		param = [fnum, new_file, alt, az, phi, x, y, defocus, dfdiff, dfang]

		if (options.allrelion):
			for var in sorted(star.keys()):
				param.append(star[var][i])

		params.append(param)
		fnum+=1

	#generate .lst file corresponding to EMAN2 convention
	fp = open(lstfile,'w')
	fp.write("#LST\n")
	for p in params:
		fp.write("%d\t%s\teuler=%g,%g,%g\tcenter=%g,%g\tdefocus=%s\tdfdiff=%s\tdfang=%s" % (p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7], p[8], p[9]))
		if options.allrelion:
			vars = sorted(star.keys())
			for vi, var in enumerate(vars):
				fp.write("\t%s=%s" % (var.split("rln")[-1], p[10+vi]))
		fp.write("\n")
	fp.close()
        
        
	if options.verbose>0:
		print "%d particles saved to %s" % (len(star["rlnImageName"]), lstfile)

	E2end(logid)

def relion2EMAN2(rot, tilt, psi, OriginX, OriginY, boxsize):
	# http://www2.mrc-lmb.cam.ac.uk/relion/index.php/Conventions_%26_File_formats

	#From Relion Euler angle definitions
	#The first rotation is denoted by phi or rot and is around the Z-axis.
	#The second rotation is called theta or tilt and is around the new Y-axis.
	#The third rotation is denoted by psi and is around the new Z axis

	t = Transform()
	t = Transform({"type":"spider","phi":rot,"theta":tilt,"psi":psi})
	t_eman = t.get_rotation("eman")
	alt, az, phi = t_eman['alt'], t_eman['az'], t_eman['phi']
	#print alt, az, phi

	# "Origin offsets reported for individual images translate the image to its center"
	x = -OriginX + boxsize/2
	y = -OriginY + boxsize/2
	#x = boxsize/2 + OriginY
	#y = (boxsize/2 - 1) - OriginX

	return alt, az, phi, x, y

    

if __name__ == "__main__":
    main()

#!/usr/bin/env python

import math, os, sys
try:
	from optparse import OptionParser
except:
	from optik import OptionParser

def main():
	(lstfile, ny,output) =  parse_command_line()
	g = open(lstfile, "r")
	lst_line = g.readlines()
	r=open(output,"w")
	test=str(lst_line[0].split()[0])
	start=3
	if(test=="#LST"):
		start=1
	warning=0
	for j in range (2,len(lst_line[start].split())):
		tmp=str((lst_line[start].split()[j]).split('=')[0])
		if(tmp=="defocus"):
			defocus_pos=j
			warning+=1
		elif(tmp=="dfdiff"):
			dfdiff_pos=j
			warning+=1
		elif(tmp=="dfang"):
			dfang_pos=j
			warning+=1
		elif(tmp=="euler"):
			euler_pos=j
			warning+=1
		elif(tmp=="center"):
			center_pos=j
			warning+=1
	if(warning<5):
		print("Your list file lacks of critical component such as defocus values. EXIT now.")
		os._exit(0)
	for j in range (2,len(lst_line[start].split())):
		tmp=str((lst_line[start].split()[j]).split('=')[0])
		if(tmp=="AmplitudeContrast"):
			ampcont_pos=j
		if(tmp=="CoordinateX"):
			coordX_pos=j
		if(tmp=="CoordinateY"):
			coordY_pos=j
		if(tmp=="DetectorPixelSize"):
			dps_pos=j
		if(tmp=="ImageName"):
			image_pos=j
		if(tmp=="Magnification"):
			mag_pos=j
		if(tmp=="MicrographName"):
			mgn_pos=j
		if(tmp=="RandomSubset"):
			rs_pos=j
		if(tmp=="SphericalAberration"):
			cs_pos=j
		if(tmp=="Voltage"):
			voltage_pos=j
		if(tmp=="GroupNumber"):
			group_pos=j
		if(tmp=="CtfFigureOfMerit"):
			ctfFOM_pos=j
		if(tmp=="ClassNumber"):
			class_pos=j
		if(tmp=="RandomSubset"):
			rdn_pos=j
			
	for i in range (start,len(lst_line)):
		filename=str(lst_line[i].split()[mgn_pos].split('=')[1])
		AS=str(lst_line[i].split()[image_pos].split('=')[1])
		defocus=float((lst_line[i].split()[defocus_pos]).split('=')[1])*10000
		dfdiff=float((lst_line[i].split()[dfdiff_pos]).split('=')[1])*10000
		dfang=float((lst_line[i].split()[dfang_pos]).split('=')[1])
		dfu=defocus-dfdiff
		dfv=defocus+dfdiff
		euler_tmp=(lst_line[i].split()[euler_pos]).split('=')[1]
		euler1=float(euler_tmp.split(',')[0])
		euler2=float(euler_tmp.split(',')[1])
		euler3=float(euler_tmp.split(',')[2])
		center_tmp=(lst_line[i].split()[center_pos]).split('=')[1]
		center1=float(((lst_line[i].split()[coordX_pos]).split('=')[1]))
		center1_pointer=ny/2-float(center_tmp.split(',')[0])
		center2=float(((lst_line[i].split()[coordY_pos]).split('=')[1]))
		center2_pointer=ny/2-float(center_tmp.split(',')[1])
		voltage=float((lst_line[i].split()[voltage_pos]).split('=')[1])
		cs=float(((lst_line[i].split()[cs_pos]).split('=')[1]))
		ampcont=float(((lst_line[i].split()[ampcont_pos]).split('=')[1]))
		mag=float(((lst_line[i].split()[mag_pos]).split('=')[1]))
		dps=float(((lst_line[i].split()[dps_pos]).split('=')[1]))
		ctffom=float(((lst_line[i].split()[ctfFOM_pos]).split('=')[1]))
		groupnum=int(((lst_line[i].split()[group_pos]).split('=')[1]))
		classnum=int(((lst_line[i].split()[class_pos]).split('=')[1]))
		rdn=int(((lst_line[i].split()[rdn_pos]).split('=')[1]))
		r.write(filename+"\t")
		r.write(str(center1)+"\t"+str(center2)+"\t")
		r.write(AS+"\t")
		r.write(str(dfu)+"\t"+str(dfv)+"\t"+str(dfang)+"\t")
		r.write(str(voltage)+"\t"+str(cs)+"\t"+str(ampcont)+"\t"+str(mag)+"\t"+str(dps)+"\t")
		r.write(str(ctffom)+"\t"+str(groupnum)+"\t")
		r.write(str(math.fmod(euler2-90,360))+"\t"+str(euler1)+"\t"+str(math.fmod(euler3+90,360))+"\t")
		r.write(str(center1_pointer)+"\t"+str(center2_pointer)+"\t")
	#	r.write(str("0.0\t0.0\t"))
	#	use 0.0 0.0 when tranlation is done with e2proc2d.py but the list has not changed.
		r.write(str(classnum)+"\t")
		r.write("0.6\t1.8e+05\t1.000000\t1\t")
		r.write(str(rdn)+"\n")
	
	g.close()
	r.close()
	
def parse_command_line():
	usage="%prog <lstfile> <particle boxsize ny> <output>"
	parser = OptionParser(usage=usage, version="%1")
	
	if len(sys.argv)<4: 
		print "<lstfile> <particle boxsize ny> <output>"
		sys.exit(-1)
	
	(options, args)=parser.parse_args()
	lstfile = args[0]
#	filename=str(args[1])
	ny=float(args[1])
	output=args[2]
	return (lstfile, ny,output)

if __name__== "__main__":
	main()

#	The metadata is in to_add_star_metadata.txt	

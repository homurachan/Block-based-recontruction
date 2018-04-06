#!/usr/bin/env python

import math, os, sys
try:
	from optparse import OptionParser
except:
	from optik import OptionParser

def main():
	(lstfile, filename,ny,apix,output) =  parse_command_line()
	g = open(lstfile, "r")
	lst_line = g.readlines()
	r=open(output,"w")
	for i in range (1,len(lst_line)):
		defocus=float((lst_line[i].split()[4]).split('=')[1])*10000
		dfdiff=float((lst_line[i].split()[2]).split('=')[1])*10000
		dfang=float((lst_line[i].split()[3]).split('=')[1])
		dfu=defocus-dfdiff
		dfv=defocus+dfdiff
		euler_tmp=(lst_line[i].split()[5]).split('=')[1]
		euler1=float(euler_tmp.split(',')[0])
		euler2=float(euler_tmp.split(',')[1])
		euler3=float(euler_tmp.split(',')[2])
		center_tmp=(lst_line[i].split()[6]).split('=')[1]
		center1=math.floor(float(center_tmp.split(',')[0])+0.5)
		center1_pointer=ny/2-float(center_tmp.split(',')[0])
		center2=math.floor(float(center_tmp.split(',')[1])+0.5)
		center2_pointer=ny/2-float(center_tmp.split(',')[1])
		apix_c=apix*0.0001
		apix_c=14/apix_c
		r.write(filename+"\t")
		r.write(str(center1)+"\t"+str(center2)+"\t")
		r.write("%06d" % i)
		r.write("@"+filename+"\t")
		r.write(str(dfu)+"\t"+str(dfv)+"\t"+str(dfang)+"\t300.000000\t2.7000000\t0.100000\t"+str(apix_c)+"\t14.000000\t")
		r.write("0.14000\t1\t")
		r.write(str(math.fmod(euler2-90,360))+"\t"+str(euler1)+"\t"+str(math.fmod(euler3+90,360))+"\t")
	# 	only for EMAN ICOS to relion I3 symmetry
		r.write(str(center1_pointer)+"\t"+str(center2_pointer)+"\t")
	#	r.write(str("0.0\t0.0\t"))
		r.write("1\t0.6\t1.8e+05\t1.000000\t1\n")
	
	g.close()
	r.close()
	
def parse_command_line():
	usage="%prog <lstfile> <spi or mrcs filename> <ny> <apix> <output>"
	parser = OptionParser(usage=usage, version="%1")
	
	if len(sys.argv)<5: 
		print "<lstfile> <spi or mrcs filename> <ny> <apix> <output>"
		sys.exit(-1)
	
	(options, args)=parser.parse_args()
	lstfile = args[0]
	filename=str(args[1])
	ny=float(args[2])
	apix=float(args[3])
	output=args[4]
	return (lstfile, filename,ny,apix,output)

if __name__== "__main__":
	main()

#	The metadata is in to_add_star_metadata.txt	

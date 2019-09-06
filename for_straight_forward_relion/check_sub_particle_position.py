#!/usr/bin/env python

import math, os, sys
try:
	from optparse import OptionParser
except:
	from optik import OptionParser

def main():
	(starfile,mline,nx, ny,output) =  parse_command_line()
	g = open(starfile, "r")
	star_line = g.readlines()
	r=open(output,"w")
	for i in range(0,mline):
		r.write(str(star_line[i]))
	for i in range(4,mline):
		if (star_line[i].split()):
			if str(star_line[i].split()[0])=="_rlnCoordinateX":
				coordX_index=int(star_line[i].split('#')[1])-1
			if str(star_line[i].split()[0])=="_rlnCoordinateY":
				coordY_index=int(star_line[i].split('#')[1])-1
			if str(star_line[i].split()[0])=="_rlnOriginX":
				oriX_index=int(star_line[i].split('#')[1])-1
			if str(star_line[i].split()[0])=="_rlnOriginY":
				oriY_index=int(star_line[i].split('#')[1])-1
	count=0
	for i in range(mline,len(star_line)):
		if(star_line[i].split()):
			coordX=float(star_line[i].split()[coordX_index])
			coordY=float(star_line[i].split()[coordY_index])
			oriX=float(star_line[i].split()[oriX_index])
			oriY=float(star_line[i].split()[oriY_index])
			tmpx=coordX-oriX
			tmpy=coordY-oriY
			if(tmpx>=0.0 and tmpx<=nx and tmpy>=0.0 and tmpy<=ny):
				r.write(str(star_line[i]))
			else:
				count+=1
	print("Total number of "+str(count)+" particles were dropped due to outside of micrograph.")
	g.close()
	r.close()
	
def parse_command_line():
	usage="%prog <starfile> <mline +4> <micrograph nx> <micrograph ny> <output>"
	parser = OptionParser(usage=usage, version="%1")
	
	if len(sys.argv)<6: 
		print "<starfile> <mline +4> <micrograph nx> <micrograph ny> <output>"
		sys.exit(-1)
	
	(options, args)=parser.parse_args()
	starfile = args[0]
	mline=int(args[1])
	nx=float(args[2])
	ny=float(args[3])
	output=args[4]
	return (starfile,mline,nx, ny,output)

if __name__== "__main__":
	main()


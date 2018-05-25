#!/usr/bin/env python

import math, os, sys
try:
	from optparse import OptionParser
except:
	from optik import OptionParser

def main():
	(lstfile, filename,ny,apix,voltage,cs,output) =  parse_command_line()
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
	for i in range (start,len(lst_line)):
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
		center1=math.floor(float(center_tmp.split(',')[0])+0.5)
		center1_pointer=ny/2-float(center_tmp.split(',')[0])
		center2=math.floor(float(center_tmp.split(',')[1])+0.5)
		center2_pointer=ny/2-float(center_tmp.split(',')[1])
		apix_c=apix*0.0001
		apix_c=14/apix_c
		r.write(filename+"\t")
		r.write(str(center1)+"\t"+str(center2)+"\t")
		r.write("%06d" % i-start+1)
		r.write("@"+filename+"\t")
		r.write(str(dfu)+"\t"+str(dfv)+"\t"+str(dfang)+"\t")
		r.write(str(voltage)+"\t"+str(cs)+"\t0.100000\t"+str(apix_c)+"\t14.000000\t")
		r.write("0.14000\t1\t")
		r.write(str(math.fmod(euler2-90,360))+"\t"+str(euler1)+"\t"+str(math.fmod(euler3+90,360))+"\t")
		r.write(str(center1_pointer)+"\t"+str(center2_pointer)+"\t")
	#	r.write(str("0.0\t0.0\t"))
	#	use 0.0 0.0 when tranlation is done with e2proc2d.py but the list has not changed.
		r.write("1\t0.6\t1.8e+05\t1.000000\t1\n")
	
	g.close()
	r.close()
	
def parse_command_line():
	usage="%prog <lstfile> <spi or mrcs filename> <ny> <apix> <voltage> <Cs> <output>"
	parser = OptionParser(usage=usage, version="%1")
	
	if len(sys.argv)<8: 
		print "<lstfile> <spi or mrcs filename> <ny> <apix> <voltage> <Cs> <output>"
		sys.exit(-1)
	
	(options, args)=parser.parse_args()
	lstfile = args[0]
	filename=str(args[1])
	ny=float(args[2])
	apix=float(args[3])
	voltage=float(args[4])
	cs=float(args[5])
	output=args[6]
	return (lstfile, filename,ny,apix,voltage,cs,output)

if __name__== "__main__":
	main()

#	The metadata is in to_add_star_metadata.txt	

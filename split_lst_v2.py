#!/usr/bin/env python

import math, os, sys
try:
	from optparse import OptionParser
except:
	from optik import OptionParser
	
def main():
	(lstfile, patch,newlst,b_boxsize,runort_name,file_type) =  parse_command_line()
	a=open(lstfile,"r")
	newlst_name=newlst+".00.lst"
	b=open(newlst_name,"w")
	line_a=a.readlines()
	j=0
	patch_num=0
	b.write("#LST\n")
	x=open(runort_name,"a")
	tmp=newlst_name.split('.lst')[0]
	x.write("e2proc2d.py "+newlst_name+" "+tmp+"."+file_type+" --process=xform.centerbyxform --clip="+b_boxsize+","+b_boxsize+"\n")
	for i in range (1,len(line_a)):
		b.write(str(line_a[i]))		
		j+=1
		if(j>=patch):
			j=0
			b.close()
			patch_num+=1
			newlst_name=newlst+"."+('%02d' % patch_num)+".lst"
			newlst_name_prefix=newlst+"."+str('%02d' % patch_num)
			x.write("e2proc2d.py "+newlst_name+" "+newlst_name_prefix+"."+file_type+" --process=xform.centerbyxform --clip="+b_boxsize+","+b_boxsize+"\n")
			b=open(newlst_name,"w")
			b.write("#LST\n")

	a.close()
	b.close()
	x.close()
def parse_command_line():
	usage="%prog <lstfile> <split patch per lst> <new lstfile root name> <block boxsize> <runort filename> <file type spi/hdf>"
	parser = OptionParser(usage=usage, version="%1")
	
	if len(sys.argv)<7: 
		print "<lstfile> <split patch per lst> <new lstfile root name> <block boxsize> <runort filename> <file type spi/hdf>"
		sys.exit(-1)
	(options, args)=parser.parse_args()
	lstfile = args[0]
	patch=int(args[1])
	newlst = str(args[2])
	b_boxsize=str(args[3])
	runort_name=str(args[4])
	file_type=str(args[5])
	return (lstfile, patch,newlst,b_boxsize,runort_name,file_type)

if __name__== "__main__":
	main()

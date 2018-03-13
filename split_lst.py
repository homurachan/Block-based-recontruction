#!/usr/bin/env python

import math, os, sys
try:
	from optparse import OptionParser
except:
	from optik import OptionParser
	
def main():
	(lstfile, patch,newlst) =  parse_command_line()
	a=open(lstfile,"r")
	newlst_name=newlst+".0.lst"
	b=open(newlst_name,"w")
	line_a=a.readlines()
	j=0
	patch_num=0
	b.write("#LST\n")
	for i in range (1,len(line_a)):
		b.write(str(line_a[i]))		
		j+=1
		if(j>=patch):
			j=0
			b.close()
			patch_num+=1
			newlst_name=newlst+"."+str(patch_num)+".lst"
			b=open(newlst_name,"w")
			b.write("#LST\n")

	a.close()
	b.close()

def parse_command_line():
	usage="%prog <lstfile> <split patch per lst> <new lstfile root name>"
	parser = OptionParser(usage=usage, version="%1")
	
	if len(sys.argv)<4: 
		print "<lstfile> <split patch per lst> <new lstfile root name>"
		sys.exit(-1)
	(options, args)=parser.parse_args()
	newlst = str(args[2])
	patch=int(args[1])
	lstfile = args[0]
	
	return (lstfile, patch,newlst)

if __name__== "__main__":
	main()

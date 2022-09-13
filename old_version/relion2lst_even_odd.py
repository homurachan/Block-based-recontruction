#!/usr/bin/env python

import math, os, sys
try:
	from optparse import OptionParser
except:
	from optik import OptionParser

def main():
	(starfile,mline, lstfile, new_odd_lstfile, new_even_lstfile) =  parse_command_line()
	f = open(starfile, "r")
	g = open(lstfile, "r")
	h = open(new_odd_lstfile, "w")
	l = open(new_even_lstfile, "w")
	star_line = f.readlines()
	lst_line = g.readlines()
	j=0
	h.write("#LST\n")
	l.write("#LST\n")
	found=0
	for i in range(4,mline):
		metadata_name=str(star_line[i].split()[0])
#		print metadata_name
		if(metadata_name=="_rlnRandomSubset"):
			found=1
			MN=int(star_line[i].split("#")[1])
	if (found==0):
		print ("The star file dose not contains random subset imformation. EXIT.")
		sys.exit(-1)
	for i in range(mline, len(star_line)):
		if(star_line[i].split()):
			DATA_line = int(star_line[i].split()[MN-1])
			if DATA_line == 1:
				h.write(str(lst_line[j+1]))
			else:
				l.write(str(lst_line[j+1]))
			j+=1
			
	h.close()
	f.close()
	g.close()
	l.close()
	
	
def parse_command_line():
	usage="%prog <starfile> <metadata line +4> <lstfile> <new odd lstfile> <new even lstfile>"
	parser = OptionParser(usage=usage, version="%1")
	
	if len(sys.argv)<6: 
		print "<starfile> <metadata line +4> <lstfile> <new odd lstfile> <new even lstfile>"
		sys.exit(-1)
	
	(options, args)=parser.parse_args()


	starfile = args[0]
	mline=int(args[1])
	lstfile = args[2]
	new_odd_lstfile = args[3]
	new_even_lstfile = args[4]
	
	return (starfile,mline, lstfile, new_odd_lstfile, new_even_lstfile)




if __name__== "__main__":
	main()


			

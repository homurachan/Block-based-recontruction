#!/usr/bin/env python

import math, os, sys
try:
	from optparse import OptionParser
except:
	from optik import OptionParser
#	You need a Refine3D data star file.
#	Check the metadata, and find like "rlnRandomSubse #26", Replace "24" below into the 26-1
#	Replace "33" below into x+4 in the final line of "rln****** #x"

def main():
	(starfile, lstfile, new_odd_lstfile, new_even_lstfile) =  parse_command_line()
	f = open(starfile, "r")
	g = open(lstfile, "r")
	h = open(new_odd_lstfile, "w")
	l = open(new_even_lstfile, "w")
	star_line = f.readlines()
	lst_line = g.readlines()
	j=0
	h.write("#LST\n")
	l.write("#LST\n")
	for i in range(33, len(star_line)):
		DATA_line = int(star_line[i].split()[24])
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
	usage="%prog <starfile> <lstfile> <new odd lstfile> <new even lstfile>"
	parser = OptionParser(usage=usage, version="%1")
	
	if len(sys.argv)<4: 
		print "<starfile> <lstfile> <new odd lstfile> <new even lstfile>"
		sys.exit(-1)
	
	(options, args)=parser.parse_args()


	starfile = args[0]
	lstfile = args[1]
	new_odd_lstfile = args[2]
	new_even_lstfile = args[3]
	
	return (starfile, lstfile, new_odd_lstfile, new_even_lstfile)




if __name__== "__main__":
	main()


			

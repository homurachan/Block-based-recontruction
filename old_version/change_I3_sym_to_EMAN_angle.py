#!/usr/bin/env python

import math, os, sys
try:
	from optparse import OptionParser
except:
	from optik import OptionParser

def main():
	(input_lst,output) =  parse_command_line()
	f = open(input_lst, "r")
	l = open(output, "w")
	lst_line = f.readlines()
	l.write("#LST\n")
	for i in range(3, len(lst_line)):
		l.write(str(lst_line[i].split()[0])+"\t"+str(lst_line[i].split()[1])+"\t"+str((lst_line[i].split()[2]).split(',')[0]))

		euler2=math.fmod(float((lst_line[i].split()[2]).split(',')[1])+180,360)
		l.write(","+str(euler2)+","+str((lst_line[i].split()[2]).split(',')[2])+"\t"+str(lst_line[i].split()[3])+"\t"+str(lst_line[i].split()[4])+"\t"+str(lst_line[i].split()[5])+"\t"+str(lst_line[i].split()[6])+"\n")


	f.close()
	l.close()
	
	
def parse_command_line():
	usage="%prog <input lst> <output>"
	parser = OptionParser(usage=usage, version="%1")
	
	if len(sys.argv)<3: 
		print "<input lst> <output>"
		sys.exit(-1)
	
	(options, args)=parser.parse_args()


	input_lst = args[0]
	output = args[1]

	return (input_lst,output)




if __name__== "__main__":
	main()


			

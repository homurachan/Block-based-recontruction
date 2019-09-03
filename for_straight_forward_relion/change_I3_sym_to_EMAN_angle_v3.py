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
	start=1
	if(str(lst_line[0].split()[0])=="#LSX"):
		start=3
	
	l.write("#LST\n")
	
	for i in range(start, len(lst_line)):
		xxxx=len(lst_line[i].split())
	#	print xxxx
		tmp=""
		for j in range(0,xxxx):
			SET=str(lst_line[i].split()[j].split('=')[0])
			if(SET=="euler"):
				euler2=math.fmod(float((lst_line[i].split()[j]).split(',')[1])+180,360)
				tmp+=str((lst_line[i].split()[j]).split(',')[0])
				tmp+=(","+str(euler2)+","+str((lst_line[i].split()[j]).split(',')[2]))
			else:
				tmp+=str(lst_line[i].split()[j])
			if(j==xxxx-1):
				tmp+="\n"
			else:
				tmp+="\t"

		l.write(tmp)
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


			

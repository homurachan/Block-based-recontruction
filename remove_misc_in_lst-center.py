#!/usr/bin/env python

import math, os, sys
try:
	from optparse import OptionParser
except:
	from optik import OptionParser

def main():
	(lstfile, image_name,wr_lst,center,write_LST) =  parse_command_line()
	g = open(lstfile, "r")
	w=open(wr_lst,"w")
	if(write_LST):
		w.write("#LST\n")
	lst_line = g.readlines()
	temp=""

	for i in range(1, len(lst_line)):
#	for i in range(3, 5):
		
		temp=str(i-1)+"\t"+str(image_name)+"\t"
		for k in range(2,8):
			temp=temp+str(lst_line[i].split()[k])+"\t"
	#	temp=temp+str(lst_line[i].split()[9])+"\t"
		temp=temp+"center="+str(center)+","+str(center)+"\t"
		for l in range(9,11):
			temp=temp+str(lst_line[i].split()[l])+"\t"
		temp=temp+str(lst_line[i].split()[11])+"\n"
		w.write(temp)
		temp=""
		
	g.close()
	w.close()
	
	
def parse_command_line():
	usage="%prog <lstfile> <image filename> <changed lst> <center> <1 for write LST>"
	parser = OptionParser(usage=usage, version="%1")
	
	if len(sys.argv)<4: 
		print "<lstfile> <image filename> <changed lst> <center> <1 for write LST>"
		sys.exit(-1)
	
	(options, args)=parser.parse_args()
	
	lstfile = args[0]
	image_name=args[1]
	wr_lst = args[2]
	center=int(args[3])
	write_LST = int(args[4])
	return (lstfile, image_name,wr_lst,center,write_LST)

if __name__== "__main__":
	main()


			

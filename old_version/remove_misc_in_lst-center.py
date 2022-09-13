#!/usr/bin/env python

import math, os, sys
try:
	from optparse import OptionParser
except:
	from optik import OptionParser

def main():
	(lstfile, image_name,wr_lst,center,apix,cs,voltage,write_LST) =  parse_command_line()
	g = open(lstfile, "r")
	w=open(wr_lst,"w")
	if(write_LST):
		w.write("#LST\n")
	lst_line = g.readlines()
	temp=""
	test=str(lst_line[0].split()[0])
	center_pos=-1
	nowrite=0
	start=3
	if(test=="#LST"):
		start=1
	len_len=int(len(lst_line[start].split()))
	for j in range (2,len_len):
		tmp=str((lst_line[start].split()[j]).split('=')[0])
		if(tmp=="center"):
			center_pos=j
		if(tmp=="ampcont"):
			nowrite=1
	for i in range(start, len(lst_line)):
#	for i in range(3, 5):
		temp=str(i-1)+"\t"+str(image_name)+"\t"
		for k in range(2,len(lst_line[i].split())):
			if (k==center_pos):
				temp=temp+"center="+str(center)+","+str(center)
			else:
				temp=temp+str(lst_line[i].split()[k])
			if(k!=len(lst_line[i].split())-1):
				temp=temp+"\t"
			else:
				if(nowrite):
					temp=temp+"\n"
				else:
					temp=temp+"\tapix="+str(apix)+"\tcs="+str(cs)+"\tvoltage="+str(voltage)+"\tampcont=0.1\n"
		w.write(temp)
		temp=""
		
	g.close()
	w.close()
	
	
def parse_command_line():
	usage="%prog <lstfile> <image filename> <changed lst> <center> <apix> <Cs> <voltage> <1 for write LST>"
	parser = OptionParser(usage=usage, version="%1")
	
	if len(sys.argv)<9: 
		print "<lstfile> <image filename> <changed lst> <center> <apix> <Cs> <voltage> <1 for write LST>"
		sys.exit(-1)
	
	(options, args)=parser.parse_args()
	
	lstfile = args[0]
	image_name=args[1]
	wr_lst = args[2]
	center=int(args[3])
	apix=float(args[4])
	cs=float(args[5])
	voltage=float(args[6])
	write_LST = int(args[7])
	return (lstfile, image_name,wr_lst,center,apix,cs,voltage,write_LST)

if __name__== "__main__":
	main()


			

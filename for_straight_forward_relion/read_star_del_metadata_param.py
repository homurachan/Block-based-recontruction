#!/usr/bin/env python

import math,os,sys
try:
	from optparse import OptionParser
except:
	from optik import OptionParser

def main():
	(star,mline,line_name,output) =  parse_command_line()
	aa=open(star,"r")
	instar_line=aa.readlines()
	out=open(output,"w")
	
	for i in range(0,mline):
		if (instar_line[i].split()):
			if (str(instar_line[i].split()[0])==line_name):
				line_index=int(instar_line[i].split('#')[1])-1
				skip=i
	for i in range(0,mline):
		if(i<skip):
			out.write(instar_line[i])
		if(i>skip):
			tmp=str(instar_line[i].split('#')[0])
			tmp_num=int(instar_line[i].split('#')[1])
			tmp_num-=1
			tmp=tmp+"#"+str(tmp_num)
			out.write(tmp+"\n")
	for i in range(mline,len(instar_line)):
		if (instar_line[i].split()):
			tmp=""
			xx=len(instar_line[i].split())
			for j in range(0,xx):
				if(j!=line_index):
					tmp+=str(instar_line[i].split()[j])
							
					if(j!=xx-1):
						tmp+="\t"
					else:
						tmp+="\n"
			out.write(tmp)
		
	out.close()
	aa.close()
	
	
def parse_command_line():
	usage="%prog <input star> <mline +4> <line name> <output>"
	parser = OptionParser(usage=usage, version="%1")
	
	if len(sys.argv)<5: 
		print "<input star> <mline +4> <line name> <output>"
		sys.exit(-1)
	
	(options, args)=parser.parse_args()
	star = str(args[0])
	mline=int(args[1])

	line_name=str(args[2])
	output=str(args[3])
	return (star,mline,line_name,output)
def SQR(x):
	y=float(x)
	return(y*y)
if __name__== "__main__":
	main()

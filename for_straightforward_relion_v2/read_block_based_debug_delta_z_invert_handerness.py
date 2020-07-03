#!/usr/bin/env python

import math,os,sys
try:
	from optparse import OptionParser
except:
	from optik import OptionParser

def main():
	(lst,output) =  parse_command_line()
	aa=open(lst,"r")
	instar_line=aa.readlines()
	mline=judge_mline0(instar_line)

	out=open(output,"w")
	for i in range(0,mline):
		if (instar_line[i].split()):
			if (str(instar_line[i].split()[0])=="_rlnDefocusU"):
				DFU_index=int(instar_line[i].split('#')[1])-1
			if (str(instar_line[i].split()[0])=="_rlnDefocusV"):
				DFV_index=int(instar_line[i].split('#')[1])-1
			if (str(instar_line[i].split()[0])=="_rlnDeltaZ"):
				DZ_index=int(instar_line[i].split('#')[1])-1
	for i in range(0,mline):
		out.write(instar_line[i])

	for l in range(mline,len(instar_line)):
		if (instar_line[l].split()):
			dz=float(instar_line[l].split()[DZ_index])
			dfu=float(instar_line[l].split()[DFU_index])
			dfv=float(instar_line[l].split()[DFV_index])
			new_dfu=dfu-2.0*dz
			new_dfv=dfv-2.0*dz
			new_dz=-1.0*dz
			xx=len(instar_line[l].split())
			tmp=""
			for j in range(0,xx):
				if(j!=DZ_index and j!=DFU_index and j!=DFV_index):
					tmp+=str(instar_line[l].split()[j])
				if(j==DZ_index):
					tmp+=(str(new_dz))
				if(j==DFU_index):
					tmp+=(str(new_dfu))
				if(j==DFV_index):
					tmp+=(str(new_dfv))
				if(j!=xx-1):
					tmp+="\t"
				if(j==xx-1):
					tmp+="\n"
			out.write(tmp)
	out.close()
	aa.close()
	
def parse_command_line():
	usage="%prog <input star> <output star>"
	parser = OptionParser(usage=usage, version="%1")
	
	if len(sys.argv)<3: 
		print "<input list> <output>"
		sys.exit(-1)
	
	(options, args)=parser.parse_args()
	lst=str(args[0])
	output=str(args[1])
	return (lst,output)
def SQR(x):
	y=float(x)
	return(y*y)
def judge_mline0(inline):
	trys=60
	intarget=-1
	for i in range (0,trys):
		if(inline[i].split()):
			if(inline[i].split()[0][0]!="_"):
				if(intarget==1):
					return i
					break
				else:
					continue
			if(inline[i].split()[0][0]=="_"):
				intarget=1
if __name__== "__main__":
	main()

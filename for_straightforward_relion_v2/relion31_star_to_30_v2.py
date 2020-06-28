#!/usr/bin/env python

import math, os, sys, random
try:
	from optparse import OptionParser
except:
	from optik import OptionParser

def main():
	(instar,output) =  parse_command_line()
	g = open(instar, "r")
	instar_line=g.readlines()
	o1=open(output,"w")
	mline0=judge_mline0(instar_line)
	mline1=judge_mline1(mline0,instar_line)
#	print mline0,mline1
#	print instar_line[mline0]
#	print instar_line[mline1]
	mline0-=1
	mline1-=1
	R_mline0=int(instar_line[mline0].split('#')[1])-1
	R_mline1=int(instar_line[mline1].split('#')[1])-1
	First_mline0=mline0-R_mline0
	First_mline1=mline1-R_mline1
#	print First_mline0,mline0+1,First_mline1,mline1+1
#	read relion 3.1 optical group info fesible for relion 3.0, high order aberration info was dropped.
#	BeamTiltX & BeamTiltY is unnecessary, must have the rest.
	BTX_index=-1
	BTY_index=-1
	for i in range(First_mline0,mline0+1):
		if str(instar_line[i].split()[0])=="_rlnAmplitudeContrast":
			AC_index=int(str(instar_line[i].split('#')[1]))-1
		if str(instar_line[i].split()[0])=="_rlnBeamTiltX":
			BTX_index=int(str(instar_line[i].split('#')[1]))-1
		if str(instar_line[i].split()[0])=="_rlnBeamTiltY":
			BTY_index=int(str(instar_line[i].split('#')[1]))-1
		if str(instar_line[i].split()[0])=="_rlnSphericalAberration":
			CS_index=int(str(instar_line[i].split('#')[1]))-1
		if str(instar_line[i].split()[0])=="_rlnVoltage":
			VOLTAGE_index=int(str(instar_line[i].split('#')[1]))-1	
		if str(instar_line[i].split()[0])=="_rlnImagePixelSize":
			IPS_index=int(str(instar_line[i].split('#')[1]))-1
		if str(instar_line[i].split()[0])=="_rlnImageSize":
			IMS_index=int(str(instar_line[i].split('#')[1]))-1
		if str(instar_line[i].split()[0])=="_rlnImageDimensionality":
			ID_index=int(str(instar_line[i].split('#')[1]))-1

	ac=float(str(instar_line[mline0+1].split()[AC_index]))
	if(BTX_index!=-1):
		btx=float(str(instar_line[mline0+1].split()[BTX_index]))
	if(BTY_index!=-1):
		bty=float(str(instar_line[mline0+1].split()[BTY_index]))
	cs=float(str(instar_line[mline0+1].split()[CS_index]))
	voltage=float(str(instar_line[mline0+1].split()[VOLTAGE_index]))
	apix=float(str(instar_line[mline0+1].split()[IPS_index]))
	imagesize=int(str(instar_line[mline0+1].split()[IMS_index]))
	imagediamention=int(str(instar_line[mline0+1].split()[ID_index]))
#	print ac,btx,bty,cs,voltage,apix,imagesize,imagediamention
#	magnification=10000.0, detector pixel size=apix
#	remove rln_opticsgroup rln_originXAngst rln_originYAngst

	modified_metadata_lable=[]
	modified_metadata_lable_num=[]
	c=0
	for i in range(First_mline1,mline1+1):

		modified_metadata_lable.append([])
		modified_metadata_lable_num.append([])
		modified_metadata_lable[c]=str(instar_line[i].split()[0])
		modified_metadata_lable_num[c]=int(str(instar_line[i].split('#')[1]))-1
		c+=1
		if str(instar_line[i].split()[0])=="_rlnOpticsGroup":
			OG_index=int(str(instar_line[i].split('#')[1]))-1
		if str(instar_line[i].split()[0])=="_rlnOriginXAngst":
			OXA_index=int(str(instar_line[i].split('#')[1]))-1
		if str(instar_line[i].split()[0])=="_rlnOriginYAngst":
			OYA_index=int(str(instar_line[i].split('#')[1]))-1
#	print modified_metadata_lable
#	print modified_metadata_lable_num
#	print OG_index,OXA_index,OYA_index
	for i in range(0,len(modified_metadata_lable)):
		if(modified_metadata_lable[i]=="_rlnOpticsGroup"):
			del modified_metadata_lable[i]
			del modified_metadata_lable_num[i]
			break
	for i in range(0,len(modified_metadata_lable)):
		if(modified_metadata_lable[i]=="_rlnOriginXAngst"):
			del modified_metadata_lable[i]
			del modified_metadata_lable_num[i]
			break
	for i in range(0,len(modified_metadata_lable)):
		if(modified_metadata_lable[i]=="_rlnOriginYAngst"):
			del modified_metadata_lable[i]
			del modified_metadata_lable_num[i]
			break
	c=len(modified_metadata_lable)
	CCC=len(modified_metadata_lable)
	for i in range(0,9):
		modified_metadata_lable.append([])
		modified_metadata_lable_num.append([])
		
	modified_metadata_lable[c+0]="_rlnAmplitudeContrast"
	modified_metadata_lable[c+1]="_rlnSphericalAberration"
	modified_metadata_lable[c+2]="_rlnVoltage"
	modified_metadata_lable[c+3]="_rlnMagnification"
	modified_metadata_lable[c+4]="_rlnDetectorPixelSize"
	modified_metadata_lable[c+5]="_rlnImageSize"
	modified_metadata_lable[c+6]="_rlnImageDimensionality"
	modified_metadata_lable[c+7]="_rlnOriginX"
	modified_metadata_lable[c+8]="_rlnOriginY"
	modified_metadata_lable_num[c+0]=ac
	modified_metadata_lable_num[c+1]=cs
	modified_metadata_lable_num[c+2]=voltage
	modified_metadata_lable_num[c+3]=10000.0
	modified_metadata_lable_num[c+4]=apix
	modified_metadata_lable_num[c+5]=imagesize
	modified_metadata_lable_num[c+6]=imagediamention
	modified_metadata_lable_num[c+7]=OXA_index
	modified_metadata_lable_num[c+8]=OYA_index
	c=len(modified_metadata_lable)
	if(BTX_index>=0):
		for i in range(0,2):
			modified_metadata_lable.append([])
			modified_metadata_lable_num.append([])
			modified_metadata_lable_num[c+i]=-1
		modified_metadata_lable[c+0]="_rlnBeamTiltX"
		modified_metadata_lable[c+1]="_rlnBeamTiltY"
		modified_metadata_lable_num[c+0]=btx
		modified_metadata_lable_num[c+1]=bty
	
			
	c=len(modified_metadata_lable)
	
	o1.write("#modified to fit relion3.0\n\ndata_\n\nloop_\n")
	tmp=""
	for i in range(0,c):
		tmp+=str(modified_metadata_lable[i])
		tmp+=" #"
		tmp+=str(i+1)
		tmp+="\n"
	o1.write(tmp)
	tmp=""
	for i in range(mline1+1,len(instar_line)):
		if(instar_line[i].split()):
			tmp=""
			for j in range(0,CCC):
				tmp+=str(instar_line[i].split()[int(modified_metadata_lable_num[j])])
				tmp+="\t"
			for j in range(CCC,c):
				if(str(modified_metadata_lable[j])=="_rlnOriginX" or str(modified_metadata_lable[j])=="_rlnOriginY"):
					tmp+=str(float(instar_line[i].split()[int(modified_metadata_lable_num[j])])/apix)
				else:
					tmp+=str(modified_metadata_lable_num[j])
				if(j!=c-1):
					tmp+="\t"
				else:
					tmp+="\n"
			o1.write(tmp)
	
	g.close()
	o1.close()
	

def parse_command_line():
	usage="%prog <input relion 3.1 star> <output relion 3.0 star>"
	parser = OptionParser(usage=usage, version="%1")
	
	if len(sys.argv)<3: 
		print "<input relion 3.1 star> <output relion 3.0 star>"
		sys.exit(-1)
	
	(options, args)=parser.parse_args()
	instar = args[0]
	output=args[1]
	return (instar,output)
	
def judge_mline0(inline):
	trys=50
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

def judge_mline1(mline0,inline):
	trys=100
	intarget=-1
	for i in range (mline0,trys):
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


			

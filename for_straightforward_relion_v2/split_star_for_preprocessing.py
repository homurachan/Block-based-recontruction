#!/usr/bin/env python

import math, os, sys
try:
	from optparse import OptionParser
except:
	from optik import OptionParser
	
def main():
	(lstfile, patch,newlst,b_boxsize,runort_name) =  parse_command_line()
	a=open(lstfile,"r")
	
	newlst_name=newlst+".00.star"
	b=open(newlst_name,"w")
	line_a=a.readlines()
	mline=judge_mline0(line_a)
	j=0
	patch_num=0
	for i in range(0,mline):
		b.write(line_a[i])
	x=open(runort_name,"a")
	tmp=newlst_name.split('.star')[0]
	x.write("relion_preprocess --operate_on "+newlst_name+" --operate_out "+tmp+".split.star --recenter_subparticle 1 --window "+b_boxsize+"\n")
	for i in range (mline,len(line_a)):
		b.write(str(line_a[i]))		
		j+=1
		if(j>=patch):
			j=0
			b.close()
			patch_num+=1
			newlst_name=newlst+"."+('%02d' % patch_num)+".star"
			newlst_name_prefix=newlst+"."+str('%02d' % patch_num)
			x.write("relion_preprocess --operate_on "+newlst_name+" --operate_out "+newlst_name_prefix+".split.star --recenter_subparticle 1 --window "+b_boxsize+"\n")
	#		x.write("e2proc2d.py "+newlst_name+" "+newlst_name_prefix+"."+file_type+" --process=xform.centerbyxform --clip="+b_boxsize+","+b_boxsize+"\n")
			b=open(newlst_name,"w")
	#		b.write("#LST\n")
			for k in range(0,mline):
				b.write(line_a[k])

	a.close()
	b.close()
	x.close()
	
	xx=open(runort_name,"r")
	xx_d=xx.readlines()
	tmp=""
	for i in range(0,len(xx_d)):
		NAME=str(xx_d[i].split()[4])
		tmp+=(NAME+" ")
	print ("Suggested use this command below to produce full stack starfile after preprocessing.")
	print ("relion_star_handler --i \""+tmp+"\" \t--o combine.star --combine")	
	xx.close()
	
def parse_command_line():
	usage="%prog <input starfile> <split patch per lst> <new starfile root name> <block boxsize> <runort filename>"
	parser = OptionParser(usage=usage, version="%1")
	
	if len(sys.argv)<6: 
		print "<input starfile> <split patch per lst> <new starfile root name> <block boxsize> <runort filename>"
		sys.exit(-1)
	(options, args)=parser.parse_args()
	lstfile = args[0]
	patch=int(args[1])
	newlst = str(args[2])
	b_boxsize=str(args[3])
	runort_name=str(args[4])
#	file_type=str(args[5])
	return (lstfile, patch,newlst,b_boxsize,runort_name)
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

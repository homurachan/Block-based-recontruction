#!/usr/bin/env python

import math, os, sys, random
try:
	from optparse import OptionParser
except:
	from optik import OptionParser

def main():
	(inlst,x_coord,y_coord,z_coord,apix,ysize,output,C_OR_D,sym_num,debug_) =  parse_command_line()
	g = open(inlst, "r")
	r=open(output,"w")
	inlst_line=g.readlines()
	scale=1.0000000000000
	r.write("#LST\n")
	PI=3.14159265359
	Cn=[]
	Dn=[]
	n=sym_num
	DN=2*sym_num

	for i in range(0,n):
		Cn.append([])
		Cn[i]=i*360./n
	
	for i in range(0,DN):
		Dn.append([])
		if (i>=n):
			Dn[i]=(i-n)*360./(n)
		else:
			Dn[i]=i*360./(n)
	if(C_OR_D=="D" or C_OR_D=="d"):
		sym_num=DN

	test=str(inlst_line[0].split()[0])
	start=3
	if(test=="#LST"):
		start=1
	len_len=int(len(inlst_line[start].split()))
	warning=0
	for j in range (2,len_len):
		tmp=str((inlst_line[start].split()[j]).split('=')[0])
		if(tmp=="defocus"):
			defocus_pos=j
			warning+=1
		elif(tmp=="dfdiff"):
			dfdiff_pos=j
			warning+=1
		elif(tmp=="dfang"):
			dfang_pos=j
			warning+=1
		elif(tmp=="euler"):
			euler_pos=j
			warning+=1
		elif(tmp=="center"):
			center_pos=j
			warning+=1
	if(warning<5):
		print("Your list file lacks of critical component such as defocus values. EXIT now.")
		os._exit(0)

	for i in range(start,len(inlst_line)):
#	for i in range(3,4):
		df_old=float((inlst_line[i].split()[defocus_pos]).split('=')[1])

		euler_tmp=(inlst_line[i].split()[euler_pos]).split('=')[1]
		euler1=float(euler_tmp.split(',')[0])/180*PI
		euler2=float(euler_tmp.split(',')[1])/180*PI
		euler3=float(euler_tmp.split(',')[2])/180*PI
		center_tmp=(inlst_line[i].split()[center_pos]).split('=')[1]
		center1=float(center_tmp.split(',')[0])
		center2=float(center_tmp.split(',')[1])

	
		mx0=scale*(math.cos(euler3)*math.cos(euler2)-math.cos(euler1)*math.sin(euler2)*math.sin(euler3))
		mx3=-scale*(math.sin(euler3)*math.cos(euler2)+math.cos(euler1)*math.sin(euler2)*math.cos(euler3))
		mx6=scale*math.sin(euler1)*math.sin(euler2)
		mx1=scale*(math.cos(euler3)*math.sin(euler2)+math.cos(euler1)*math.cos(euler2)*math.sin(euler3))
		mx4=scale*(-1*math.sin(euler3)*math.sin(euler2)+math.cos(euler1)*math.cos(euler2)*math.cos(euler3))
		mx7=-scale*math.sin(euler1)*math.cos(euler2)
		mx2=scale*math.sin(euler1)*math.sin(euler3)
		mx5=scale*math.sin(euler1)*math.cos(euler3)
		mx8=scale*math.cos(euler1)

		for k in range (0,sym_num):
			#	Dn symmetry:
			if(C_OR_D=="D" or C_OR_D=="d"):
				if(k>=n):
					icos_euler1=PI
					icos_euler2=float(str(Dn[k]))/180*PI
					icos_euler3=0.	
				else:
					icos_euler1=0.
					icos_euler2=float(str(Dn[k]))/180*PI
					icos_euler3=0.	
			#	Cn symmetry
			if(C_OR_D=="C" or C_OR_D=="c"):
				icos_euler1=0.
				icos_euler2=float(str(Cn[k]))/180*PI
				icos_euler3=0.
		
			icos_mx0=(math.cos(icos_euler3)*math.cos(icos_euler2)-math.cos(icos_euler1)*math.sin(icos_euler2)*math.sin(icos_euler3))
			icos_mx1=-1*(math.sin(icos_euler3)*math.cos(icos_euler2)+math.cos(icos_euler1)*math.sin(icos_euler2)*math.cos(icos_euler3))
			icos_mx2=math.sin(icos_euler1)*math.sin(icos_euler2)
			icos_mx3=(math.cos(icos_euler3)*math.sin(icos_euler2)+math.cos(icos_euler1)*math.cos(icos_euler2)*math.sin(icos_euler3))
			icos_mx4=(-1*math.sin(icos_euler3)*math.sin(icos_euler2)+math.cos(icos_euler1)*math.cos(icos_euler2)*math.cos(icos_euler3))
			icos_mx5=-1*math.sin(icos_euler1)*math.cos(icos_euler2)
			icos_mx6=math.sin(icos_euler1)*math.sin(icos_euler3)
			icos_mx7=math.sin(icos_euler1)*math.cos(icos_euler3)
			icos_mx8=math.cos(icos_euler1)
	
			icos_mult_mx0 = mx0*icos_mx0 + mx1*icos_mx3 + mx2*icos_mx6
			icos_mult_mx1 = mx0*icos_mx1 + mx1*icos_mx4 + mx2*icos_mx7
			icos_mult_mx2 = mx0*icos_mx2 + mx1*icos_mx5 + mx2*icos_mx8
			icos_mult_mx3 = mx3*icos_mx0 + mx4*icos_mx3 + mx5*icos_mx6
			icos_mult_mx4 = mx3*icos_mx1 + mx4*icos_mx4 + mx5*icos_mx7
			icos_mult_mx5 = mx3*icos_mx2 + mx4*icos_mx5 + mx5*icos_mx8
			icos_mult_mx6 = mx6*icos_mx0 + mx7*icos_mx3 + mx8*icos_mx6
			icos_mult_mx7 = mx6*icos_mx1 + mx7*icos_mx4 + mx8*icos_mx7
			icos_mult_mx8 = mx6*icos_mx2 + mx7*icos_mx5 + mx8*icos_mx8
			
			new_euler1=math.acos(icos_mult_mx8)
			new_euler2=math.atan2(icos_mult_mx6,-1*icos_mult_mx7)
			new_euler3=math.atan2(icos_mult_mx2,icos_mult_mx5)
			if(icos_mult_mx8>0.999999):
				new_euler1=0
				new_euler2=math.atan2(icos_mult_mx1,icos_mult_mx4)
				new_euler3=0
			if(icos_mult_mx8<-0.999999):
				new_euler1=PI
				new_euler2=math.atan2(icos_mult_mx1,-1*icos_mult_mx4)
				new_euler3=0
	
			new_x=icos_mult_mx0*(x_coord-ysize/2)+icos_mult_mx1*(y_coord-ysize/2)+icos_mult_mx2*(z_coord-ysize/2)
			new_y=icos_mult_mx3*(x_coord-ysize/2)+icos_mult_mx4*(y_coord-ysize/2)+icos_mult_mx5*(z_coord-ysize/2)
			new_z=icos_mult_mx6*(x_coord-ysize/2)+icos_mult_mx7*(y_coord-ysize/2)+icos_mult_mx8*(z_coord-ysize/2)

			pic_x=new_x+center1
			pic_y=new_y+center2
#	Output x-y coordinates are INTs, since we don't want to interpolate the blocks after moving them to center.			
			if(debug_==1):
				new_z_df=new_z*apix/10000+df_old
			elif(debug_==0):
				new_z_df=-1*new_z*apix/10000+df_old
			else:
				new_z_df=df_old
	#		new_z_df=df_old
			for j in range (0,len_len):
				if(j==defocus_pos):
					r.write("defocus="+str(new_z_df))
				elif(j==euler_pos):
					r.write("euler="+str(new_euler1/PI*180)+","+str(new_euler2/PI*180)+","+str(new_euler3/PI*180))
				elif(j==center_pos):
					r.write("center="+str(pic_x)+","+str(pic_y))
				else:
					r.write(str(inlst_line[i].split()[j]))
				if(j!=len_len-1):
					r.write("\t")
				else:
					r.write("\n")


	g.close()
	r.close()

	
def parse_command_line():
	usage="%prog <input lst> <point x> <point y> <point z> <apix> <ySize> <output> <C or D> <symmetry n> <DEBUG, plus=1, minus=0, otherwise no change>"
	parser = OptionParser(usage=usage, version="%1")
	
	if len(sys.argv)<11: 
		print "<input lst> <point x> <point y> <point z> <apix> <ySize> <output> <C or D> <symmetry n> <DEBUG, plus=1, minus=0, otherwise no change>"
		sys.exit(-1)
	
	(options, args)=parser.parse_args()
	
	inlst = args[0]
	x_coord = float(args[1])
	y_coord = float(args[2])
	z_coord = float(args[3])
	apix = float(args[4])
	ysize= int(args[5])
	output = args[6]
	C_OR_D=str(args[7])
	sym_num=int(args[8])
	debug_=int(args[9])
	return (inlst,x_coord,y_coord,z_coord,apix,ysize,output,C_OR_D,sym_num,debug_)

if __name__== "__main__":
	main()


			

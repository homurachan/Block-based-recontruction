#!/usr/bin/env python

import math, os, sys, random
try:
	from optparse import OptionParser
except:
	from optik import OptionParser

def main():
	(inlst,x_coord,y_coord,z_coord,apix,ysize,output,debug_) =  parse_command_line()
	g = open(inlst, "r")
	r=open(output,"w")
	inlst_line=g.readlines()
	scale=1.0000000000000
	r.write("#LST\n")
	PI=3.14159265359
	ICOS=[]
	for i in range (0,180):
		ICOS.append([])
		
	ICOS[0]=0
	ICOS[1]=0
	ICOS[2]=0
	ICOS[3]=0
	ICOS[4]=0
	ICOS[5]=288
	ICOS[6]=0
	ICOS[7]=0
	ICOS[8]=216
	ICOS[9]=0
	ICOS[10]=0
	ICOS[11]=144
	ICOS[12]=0
	ICOS[13]=0
	ICOS[14]=72
	
	ICOS[15]=0
	ICOS[16]=63.4349
	ICOS[17]=36
	ICOS[18]=0
	ICOS[19]=63.4349
	ICOS[20]=324
	ICOS[21]=0
	ICOS[22]=63.4349
	ICOS[23]=252
	ICOS[24]=0
	ICOS[25]=63.4349
	ICOS[26]=180
	ICOS[27]=0
	ICOS[28]=63.4349
	ICOS[29]=108
	
	ICOS[30]=72
	ICOS[31]=63.4349
	ICOS[32]=36
	ICOS[33]=72
	ICOS[34]=63.4349
	ICOS[35]=324
	ICOS[36]=72
	ICOS[37]=63.4349
	ICOS[38]=252
	ICOS[39]=72
	ICOS[40]=63.4349
	ICOS[41]=180
	ICOS[42]=72
	ICOS[43]=63.4349
	ICOS[44]=108
	
	ICOS[45]=144
	ICOS[46]=63.4349
	ICOS[47]=36
	ICOS[48]=144
	ICOS[49]=63.4349
	ICOS[50]=324
	ICOS[51]=144
	ICOS[52]=63.4349
	ICOS[53]=252
	ICOS[54]=144
	ICOS[55]=63.4349
	ICOS[56]=180
	ICOS[57]=144
	ICOS[58]=63.4349
	ICOS[59]=108
	
	ICOS[60]=216
	ICOS[61]=63.4349
	ICOS[62]=36
	ICOS[63]=216
	ICOS[64]=63.4349
	ICOS[65]=324
	ICOS[66]=216
	ICOS[67]=63.4349
	ICOS[68]=252
	ICOS[69]=216
	ICOS[70]=63.4349
	ICOS[71]=180
	ICOS[72]=216
	ICOS[73]=63.4349
	ICOS[74]=108
	
	ICOS[75]=288
	ICOS[76]=63.4349
	ICOS[77]=36
	ICOS[78]=288
	ICOS[79]=63.4349
	ICOS[80]=324
	ICOS[81]=288
	ICOS[82]=63.4349
	ICOS[83]=252
	ICOS[84]=288
	ICOS[85]=63.4349
	ICOS[86]=180
	ICOS[87]=288
	ICOS[88]=63.4349
	ICOS[89]=108
	
	ICOS[90]=36
	ICOS[91]=116.5651
	ICOS[92]=0
	ICOS[93]=36
	ICOS[94]=116.5651
	ICOS[95]=288
	ICOS[96]=36
	ICOS[97]=116.5651
	ICOS[98]=216
	ICOS[99]=36
	ICOS[100]=116.5651
	ICOS[101]=144
	ICOS[102]=36
	ICOS[103]=116.5651
	ICOS[104]=72
	
	ICOS[105]=108
	ICOS[106]=116.5651
	ICOS[107]=0
	ICOS[108]=108
	ICOS[109]=116.5651
	ICOS[110]=288
	ICOS[111]=108
	ICOS[112]=116.5651
	ICOS[113]=216
	ICOS[114]=108
	ICOS[115]=116.5651
	ICOS[116]=144
	ICOS[117]=108
	ICOS[118]=116.5651
	ICOS[119]=72
	
	ICOS[120]=180
	ICOS[121]=116.5651
	ICOS[122]=0
	ICOS[123]=180
	ICOS[124]=116.5651
	ICOS[125]=288
	ICOS[126]=180
	ICOS[127]=116.5651
	ICOS[128]=216
	ICOS[129]=180
	ICOS[130]=116.5651
	ICOS[131]=144
	ICOS[132]=180
	ICOS[133]=116.5651
	ICOS[134]=72
	
	ICOS[135]=252
	ICOS[136]=116.5651
	ICOS[137]=0
	ICOS[138]=252
	ICOS[139]=116.5651
	ICOS[140]=288
	ICOS[141]=252
	ICOS[142]=116.5651
	ICOS[143]=216
	ICOS[144]=252
	ICOS[145]=116.5651
	ICOS[146]=144
	ICOS[147]=252
	ICOS[148]=116.5651
	ICOS[149]=72
	
	ICOS[150]=324
	ICOS[151]=116.5651
	ICOS[152]=0
	ICOS[153]=324
	ICOS[154]=116.5651
	ICOS[155]=288
	ICOS[156]=324
	ICOS[157]=116.5651
	ICOS[158]=216
	ICOS[159]=324
	ICOS[160]=116.5651
	ICOS[161]=144
	ICOS[162]=324
	ICOS[163]=116.5651
	ICOS[164]=72
	
	ICOS[165]=0
	ICOS[166]=180
	ICOS[167]=0
	ICOS[168]=0
	ICOS[169]=180
	ICOS[170]=288
	ICOS[171]=0
	ICOS[172]=180
	ICOS[173]=216
	ICOS[174]=0
	ICOS[175]=180
	ICOS[176]=144
	ICOS[177]=0
	ICOS[178]=180
	ICOS[179]=72
	sym_num=60
#	This euler angle list comes from EMAN lib. If you use relion to do a binX icoshedral virus refinemenet, please use I3 sym.
#	To convert I3 sym into EMAN's ZXZ icoshedral system, just use a script called relion2lst.py in Wen Jiang's JSPR package, then doing these:
#	change b in every particle in the list: "euler=a,b,c" into "euler=a,b+-180,c", since relion2lst.py cannot distiguish symmetry.
#	You can also let relion2lst.py output "dfdiff" and "dfang" parameters to list file.
#	And use relion2lst_even_odd.py to split the list into e-list and o-list.

#	To run this, you need an EMAN or EMAN2 input list file, or you can simply use JSPR package.
#	df_old is the parameter "defocus=df", euler_tmp is "euler=a,b,c", and center_tmp is "center=x,y" in the input list.
#	The debug option is for handness, to our experiences, if the handness is correct, use "1", else use "0".
#	Because handness comes from intergration along z-axis, and defocus is in fact a Z-direction distance.
#	It's easier to check the handness just by using the output to do a 3d reconstruction, then calculate FSC.
#	If handness is wrong, FSC in high frequency range should oscillate significantly (Since you use the wrong defocus).
#	Input x,y,z is a set of 3d coordinate which you can pick one from 3d model.
#	ysize is the original 3d model's size in pixel. For example, for an 1200*1200*1200 model you should use 1200.
#	If the model is not icoshedral symmetry, use these euler angle list below:
#		Cn=[]	
#	if model is Cx symmetry
#	for i in range(0,n):
#		Cn.append([])
#		Cn[i]=i*360./n
#	sym_num=n
#	or Dx symmetry:
#	Dn=[]
#	DN=2*n
#	for i in range(0,DN):
#		Dn.append([])
#		if (i>=n):
#			Dn[i]=(i-n)*360./(n)
#		else:
#			Dn[i]=i*360./(n)
#	sym_num=DN

	for i in range(3,len(inlst_line)):
#	for i in range(3,4):
		df_old=float((inlst_line[i].split()[2]).split('=')[1])

		euler_tmp=(inlst_line[i].split()[9]).split('=')[1]
		euler1=float(euler_tmp.split(',')[0])/180*PI
		euler2=float(euler_tmp.split(',')[1])/180*PI
		euler3=float(euler_tmp.split(',')[2])/180*PI
		center_tmp=(inlst_line[i].split()[10]).split('=')[1]
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
			icos_euler1=float(str(ICOS[3*k+1]))/180*PI
			icos_euler2=float(str(ICOS[3*k+2]))/180*PI-PI/2
			icos_euler3=float(str(ICOS[3*k]))/180*PI+PI/2
			
			#	Dn symmetry:
		#	if(k>=n):
		#		c_euler1=PI
		#		c_euler2=float(str(Dn[k]))/180*PI
		#		c_euler3=0.	
		#	else:
		#		c_euler1=0.
		#		c_euler2=float(str(Dn[k]))/180*PI
		#		c_euler3=0.	
			#	Cn symmetry
		#	c_euler1=0.
		#	c_euler2=float(str(Cn[k]))/180*PI
		#	c_euler3=0.
		
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

			pic_x=int(math.floor(new_x+center1+0.5))
			pic_y=int(math.floor(new_y+center2+0.5))
#	Output x-y coordinates are INTs, since we don't want to interpolate the blocks after moving them to center.			
			if(debug_==1):
				new_z_df=new_z*apix/10000+df_old
			else:
				new_z_df=-1*new_z*apix/10000+df_old
	#		new_z_df=df_old
			for j in range (0,2):
				r.write(str(inlst_line[i].split()[j])+"\t")
			r.write("defocus="+str(new_z_df)+"\t")
			for j in range (3,9):
				r.write(str(inlst_line[i].split()[j])+"\t")
			r.write("euler="+str(new_euler1/PI*180)+","+str(new_euler2/PI*180)+","+str(new_euler3/PI*180)+"\t")
			r.write("center="+str(pic_x)+","+str(pic_y)+"\t")
			for j in range (11,14):
				r.write(str(inlst_line[i].split()[j])+"\t")
			r.write(str(inlst_line[i].split()[14])+"\n")

	g.close()
	r.close()

	
def parse_command_line():
	usage="%prog <input lst> <point x> <point y> <point z> <apix> <ySize> <output> <DEBUG, plus=1, minus=0>"
	parser = OptionParser(usage=usage, version="%1")
	
	if len(sys.argv)<9: 
		print "<input lst> <point x> <point y> <point z> <apix> <ySize> <output> <DEBUG, plus=1, minus=0>"
		sys.exit(-1)
	
	(options, args)=parser.parse_args()
	
	inlst = args[0]
	x_coord = float(args[1])
	y_coord = float(args[2])
	z_coord = float(args[3])
	apix = float(args[4])
	ysize= int(args[5])
	output = args[6]
	debug_=int(args[7])
	return (inlst,x_coord,y_coord,z_coord,apix,ysize,output,debug_)

if __name__== "__main__":
	main()


			

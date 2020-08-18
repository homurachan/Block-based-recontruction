#!/usr/bin/env python
#v2, add check position function to avoid subparticle out of micrograph
#v3, add Cn and Dn symmetry.
import math, os, sys, random
try:
	from optparse import OptionParser
except:
	from optik import OptionParser

def main():
	(inlst,x_coord,y_coord,z_coord,ysize,output,debug_,NX,NY,SYMMETRY) =  parse_command_line()
	sym_num=0
	(symmetry_type,sym_num)=determin_symmetry(SYMMETRY)
	if(sym_num==0):
		print("Non-supported symmetry found, make your you input Cn, Dn or I3. EXIT.")
		print("Cn is like C3, Dn is like D4, btw")
		os._exit(0)

	Cn=[]
	Dn=[]
	if(symmetry_type=="C"):
		for i in range(0,sym_num):
			Cn.append([])
			Cn[i]=i*360./sym_num
	if(symmetry_type=="D"):
		for i in range(0,sym_num):
			Dn.append([])
			if (i>=sym_num/2):
				Dn[i]=(i-sym_num/2)*360./(sym_num/2)
			else:
				Dn[i]=i*360./(sym_num/2)	
			
		
	g = open(inlst, "r")
	r=open(output,"w")
	inlst_line=g.readlines()
	scale=1.0000000000000
	PI=3.14159265359
	DROPPED_SUBPARTICLE=0
	mline=judge_mline0(inlst_line)
	print "mline="+str(mline)
	for i in range(0,mline):
		r.write(str(inlst_line[i]))
	LAST_METADATA_NUM=int(inlst_line[mline-1].split()[1].split('#')[1])
	r.write("_rlnDeltaZ #"+str(LAST_METADATA_NUM+1)+"\n")
	r.write("_rlnParticleSerialNumber #"+str(LAST_METADATA_NUM+2)+"\n")
	for i in range(0,mline):
		if (inlst_line[i].split()):
			if (str(inlst_line[i].split()[0])=="_rlnImageName"):
				IMG_index=int(inlst_line[i].split('#')[1])-1
			if (str(inlst_line[i].split()[0])=="_rlnDetectorPixelSize"):
				DPS_index=int(inlst_line[i].split('#')[1])-1
			if (str(inlst_line[i].split()[0])=="_rlnMagnification"):
				MAG_index=int(inlst_line[i].split('#')[1])-1
			if (str(inlst_line[i].split()[0])=="_rlnDefocusU"):
				DFU_index=int(inlst_line[i].split('#')[1])-1
			if (str(inlst_line[i].split()[0])=="_rlnDefocusV"):
				DFV_index=int(inlst_line[i].split('#')[1])-1
			if (str(inlst_line[i].split()[0])=="_rlnDefocusAngle"):
				DFA_index=int(inlst_line[i].split('#')[1])-1
			if (str(inlst_line[i].split()[0])=="_rlnAngleRot"):
				ROT_index=int(inlst_line[i].split('#')[1])-1
			if (str(inlst_line[i].split()[0])=="_rlnAngleTilt"):
				TILT_index=int(inlst_line[i].split('#')[1])-1
			if (str(inlst_line[i].split()[0])=="_rlnAnglePsi"):
				PSI_index=int(inlst_line[i].split('#')[1])-1
			if (str(inlst_line[i].split()[0])=="_rlnOriginX"):
				OX_index=int(inlst_line[i].split('#')[1])-1
			if (str(inlst_line[i].split()[0])=="_rlnOriginY"):
				OY_index=int(inlst_line[i].split('#')[1])-1
			if (str(inlst_line[i].split()[0])=="_rlnCoordinateX"):
				crdX_index=int(inlst_line[i].split('#')[1])-1
			if (str(inlst_line[i].split()[0])=="_rlnCoordinateY"):
				crdY_index=int(inlst_line[i].split('#')[1])-1
#	print IMG_index,DPS_index,MAG_index,DFU_index,DFV_index,DFA_index,ROT_index,TILT_index,PSI_index,OX_index,OY_index
	STAR_APIX=float(inlst_line[mline].split()[DPS_index])/float(inlst_line[mline].split()[MAG_index])*1e4
#	if(apix!=STAR_APIX):
#		print("Pixel size in the star file is different from input, make sure your star is unbinned. EXIT.")
#		os._exit(0)
	apix=STAR_APIX
	particle_serial_num=0
	for i in range(mline,len(inlst_line)):
#	for i in range(3,4):
		if (inlst_line[i].split()):
			particle_serial_num+=1
			dfu=float(inlst_line[i].split()[DFU_index])
			dfv=float(inlst_line[i].split()[DFV_index])
		#	df_old=(dfu+dfv)/2.0
			rot=float(inlst_line[i].split()[ROT_index])
			tilt=float(inlst_line[i].split()[TILT_index])
			psi=float(inlst_line[i].split()[PSI_index])
			ox=float(inlst_line[i].split()[OX_index])
			oy=float(inlst_line[i].split()[OY_index])
			crdx=float(inlst_line[i].split()[crdX_index])
			crdy=float(inlst_line[i].split()[crdY_index])
			(euler1_eman,euler2_eman,euler3_eman)=EULER_EMAN(rot,tilt,psi)
	#		NEED rot=0,180,0 here if full-particles match I3 sym
			if(symmetry_type=="I" and sym_num==60):
				euler2_eman=math.fmod(euler2_eman+180.0,360.0)
			(center1_eman,center2_eman)=CENTER_EMAN(ox,oy,ysize)
			
			euler1=float(euler1_eman)/180*PI
			euler2=float(euler2_eman)/180*PI
			euler3=float(euler3_eman)/180*PI
		
			center1=float(center1_eman)
			center2=float(center2_eman)
		
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
				#	I3 symmetry
				if(symmetry_type=="I" and sym_num==60):
					icos_euler1=float(str(ICOS[3*k+1]))/180.0*PI
					icos_euler2=float(str(ICOS[3*k+2]))/180.0*PI-PI/2
					icos_euler3=float(str(ICOS[3*k]))/180.0*PI+PI/2
				#	Dn symmetry
				if(symmetry_type=="D"):
					if(k>=sym_num/2):
						icos_euler1=PI
						icos_euler2=float(str(Dn[k]))/180.0*PI
						icos_euler3=0.	
					else:
						icos_euler1=0.
						icos_euler2=float(str(Dn[k]))/180.0*PI
						icos_euler3=0.	
				#	Cn symmetry
				if(symmetry_type=="C"):
					icos_euler1=0.
					icos_euler2=float(str(Cn[k]))/180.0*PI
					icos_euler3=0.
				#	Oct symmetry
				if(symmetry_type=="O"):
					icos_euler1=float(str(OCT[3*k]))/180.0*PI
					icos_euler2=float(str(OCT[3*k+1]))/180.0*PI
					icos_euler3=float(str(OCT[3*k+2]))/180.0*PI

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
				DELTAZ=0.0
				if(debug_==1):
					new_dfu=dfu+new_z*apix
					new_dfv=dfv+new_z*apix
					DELTAZ=+new_z*apix
		#			print "here "+str(dfu)+" "+str(new_dfu)
				elif(debug_==0):
					new_dfu=dfu-new_z*apix
					new_dfv=dfv-new_z*apix
					DELTAZ=-1.0*new_z*apix
				else:
				#nochange
					new_dfu=dfu
					new_dfv=dfv
				#check subparticle center position is inside of the micrograph
				new_ox=ysize/2.0-pic_x
				new_oy=ysize/2.0-pic_y
				tmpx=crdx-new_ox
				tmpy=crdy-new_oy
				if(tmpx<0.0 or tmpx>NX or tmpy<0.0 or tmpy>NY):
					DROPPED_SUBPARTICLE+=1
					continue
				tmp=""
				xx=len(inlst_line[i].split())
				for j in range(0,xx):
					if(j!=DFU_index and j!=DFV_index and j!=ROT_index and j!=TILT_index and j!=PSI_index and j!=OX_index and j!=OY_index and j!=crdX_index and j!=crdY_index):
						tmp+=str(inlst_line[i].split()[j])
					if(j==DFU_index):
						tmp+=str(new_dfu)
					if(j==DFV_index):
						tmp+=str(new_dfv)
					if(j==ROT_index):
						new_rot=math.fmod(new_euler2/PI*180.0-90.0,360.0)
						tmp+=str(new_rot)
					if(j==TILT_index):
						new_tilt=new_euler1/PI*180.0
						tmp+=str(new_tilt)
					if(j==PSI_index):
						new_psi=math.fmod(new_euler3/PI*180.0+90.0,360.0)
						tmp+=str(new_psi)
					if(j==OX_index):
						tmp+=str(round(new_ox))
					if(j==OY_index):
						tmp+=str(round(new_oy))
					if(j==crdX_index):
						tmp+=str(crdx)
					if(j==crdY_index):
						tmp+=str(crdy)
					if(j!=xx-1):
						tmp+="\t"
					if(j==xx-1):
						tmp+="\t"+str(DELTAZ)+"\t"+str(particle_serial_num)+"\n"
				r.write(tmp)
	print ("Total number of dropped out-of-bound-subparticle is "+str(DROPPED_SUBPARTICLE))
	g.close()
	r.close()

	
def parse_command_line():
	usage="%prog <input star> <point x> <point y> <point z> <whole particle boxsize> <output> <DEBUG, plus=1, minus=0, nochange=2> <micrograph nx> <micrograph ny> <Symmetry>\nSupported symmetry is Cn, Dn, O and I3"
	parser = OptionParser(usage=usage, version="%1")
	
	if len(sys.argv)<11: 
		print "<input star> <point x> <point y> <point z> <whole particle boxsize> <output> <DEBUG, plus=1, minus=0, nochange=2> <micrograph nx> <micrograph ny> <Symmetry>\nSupported symmetry is Cn, Dn, O and I3"
		sys.exit(-1)
	
	(options, args)=parser.parse_args()
	
	inlst = args[0]
#	mline=int(args[1])
	x_coord = float(args[1])
	y_coord = float(args[2])
	z_coord = float(args[3])
#	apix = float(args[4])
	ysize= int(args[4])
	output = args[5]
	debug_=int(args[6])
	NX=int(args[7])
	NY=int(args[8])
	SYMMETRY=str(args[9])
	return (inlst,x_coord,y_coord,z_coord,ysize,output,debug_,NX,NY,SYMMETRY)
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
def EULER_EMAN(rot,tilt,psi):

	phi=rot
	theta=tilt
	psi=psi
	az =  phi + 90.0
	alt = theta + 0.0
	phi = psi - 90.0

	return(alt,az,phi)	

def CENTER_EMAN(ox,oy,ysize):
	x = -ox + ysize/2.0
	y = -oy + ysize/2.0
	return(x,y)
def determin_symmetry(SYMMETRY):
	a=str(SYMMETRY[0])
	sym_num=0
	if(a=="C"):
		sym_num=int(SYMMETRY[1:])
	if(a=="D"):
		sym_num=2*int(SYMMETRY[1:])
	if(a=="O"):
		sym_num=24
	if(a=="I" and b==3):
		sym_num=60

	return (a,sym_num)
OCT=[]
for i in range (0,72):
	OCT.append([])
OCT[0]= 0
OCT[1]= 90
OCT[2]= 90
OCT[3]= 90
OCT[4]= 90
OCT[5]= 180
OCT[6]= 0
OCT[7]= 0
OCT[8]= 90
OCT[9]= 0
OCT[10]= 0
OCT[11]= -180
OCT[12]= 0
OCT[13]= 0
OCT[14]= -90
OCT[15]= 90
OCT[16]= 90
OCT[17]= 90
OCT[18]= 180
OCT[19]= 90
OCT[20]= 180
OCT[21]= 90
OCT[22]= 90
OCT[23]= -90
OCT[24]= 0
OCT[25]= 90
OCT[26]= 180
OCT[27]= 180
OCT[28]= 90
OCT[29]= 90
OCT[30]= -90
OCT[31]= 90
OCT[32]= 180
OCT[33]= 90
OCT[34]= 90
OCT[35]= 0
OCT[36]= 0
OCT[37]= 90
OCT[38]= -90
OCT[39]= -90
OCT[40]= 90
OCT[41]= 90
OCT[42]= 0
OCT[43]= 90
OCT[44]= 0
OCT[45]= 180
OCT[46]= 90
OCT[47]= -90
OCT[48]= 180
OCT[49]= 90
OCT[50]= 0
OCT[51]= 0
OCT[52]= 180
OCT[53]= 0
OCT[54]= 0
OCT[55]= 180
OCT[56]= 90
OCT[57]= 0
OCT[58]= 180
OCT[59]= 180
OCT[60]= -90
OCT[61]= 90
OCT[62]= -90
OCT[63]= -90
OCT[64]= 90
OCT[65]= 0
OCT[66]= 0
OCT[67]= 180
OCT[68]= -90
OCT[69]= 0
OCT[70]= 0
OCT[71]= 0

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

if __name__== "__main__":
	main()
	

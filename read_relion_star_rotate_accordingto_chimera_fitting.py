#Programmed by M.J. Zhao and D.J. Zhu
import numpy as np
import math,os,sys
try:
	from optparse import OptionParser
except:
	from optik import OptionParser
def main():
	(star,chimera_txt,apix,output,output2) = parse_command_line()
	aa=open(star,"r")
	instar_line=aa.readlines()
	out=open(output,"w")
	ccc=open(output2,"w")
	relion30=1
	relion30=judge_relion30_or_relion31(inline=instar_line)
	print "Is relion3.0? = "+str(relion30)
	mline=-1
	if(relion30):
		mline=judge_mline0(inline=instar_line)
	else:
		MLINE=judge_mline0(inline=instar_line)
		mline=judge_mline1(inline=instar_line,start=MLINE)
	if(mline<0):
		print "starfile error or this script cannot handle it. EXIT."
		quit()
	Rot_index=find_relion_metadata(instar_line,mline,"_rlnAngleRot")
	Tilt_index=find_relion_metadata(instar_line,mline,"_rlnAngleTilt")
	Psi_index=find_relion_metadata(instar_line,mline,"_rlnAnglePsi")
	if(relion30):
		X_index=find_relion_metadata(instar_line,mline,"_rlnOriginX")
		Y_index=find_relion_metadata(instar_line,mline,"_rlnOriginY")
	if(relion30<1):
		X_index=find_relion_metadata(instar_line,mline,"_rlnOriginXAngst")
		Y_index=find_relion_metadata(instar_line,mline,"_rlnOriginYAngst")
	f=open(chimera_txt,"r")
	fl=f.readlines()
	C=[]
	for line in fl:
		curline=line.strip().split()
		floatline=map(float,curline)
		C.append(floatline[3:4])
	C=np.array(C)
	C=C/apix
	C_int=np.trunc(C)
	C_float=C-C_int
	C_int_str1=str(C_int[0])
	C_int_str2=str(C_int[1])
	C_int_str3=str(C_int[2])
	ccc.write(C_int_str1)
	ccc.write(C_int_str2)
	ccc.write(C_int_str3)
	B=[]
	for line in fl:
		curline=line.strip().split()
		floatline=map(float,curline)
		B.append(floatline[0:3])   
	B=np.array(B)
	print B
	print ""
	Bt=np.transpose(B)
	for i in range(0,mline):
		out.write(instar_line[i])
	for i in range(mline,len(instar_line)):
		if (instar_line[i].split()):
			xx=len(instar_line[i].split())
			Rot=float(instar_line[i].split()[Rot_index])
			Tilt=float(instar_line[i].split()[Tilt_index])
			Psi=float(instar_line[i].split()[Psi_index])
			if(relion30):
				originX=float(instar_line[i].split()[X_index])
				originY=float(instar_line[i].split()[Y_index])
			if(relion30<1):
				originX=float(instar_line[i].split()[X_index])/apix
				originY=float(instar_line[i].split()[Y_index])/apix
			Rot=math.radians(Rot)
			Tilt=math.radians(Tilt)
			Psi=math.radians(Psi)
			A=np.zeros((3,3),dtype=float)
			ca = math.cos(Rot)
			cb = math.cos(Tilt)
			cg = math.cos(Psi)
			sa = math.sin(Rot)
			sb = math.sin(Tilt)
			sg = math.sin(Psi)
			cc = cb * ca
			cs = cb * sa
			sc = sb * ca
			ss = sb * sa
			A=([[cg*cc-sg*sa,cg*cs+sg*ca, -cg*sb],[-sg*cc-cg*sa,-sg*cs+cg*ca,sg*sb],[sc,ss,cb]])
			A=np.array(A)
			A[0, 0] = cg*cc-sg*sa
			A[0, 1] = cg*cs+sg*ca
			A[0, 2] = -cg*sb
			A[1, 0] = -sg*cc-cg*sa
			A[1, 1] = -sg*cs+cg*ca
			A[1, 2] = sg*sb
			A[2, 0] = sc
			A[2, 1] = ss
			A[2, 2] = cb
			At=np.transpose(A)
			index=3
			if index==0:
				temp=np.dot(B,A)
			if index==1:
				temp=np.dot(Bt,A)
			if index==2:
				temp=np.dot(A,B)
			if index==3:
				temp=np.dot(A,Bt)
			a = math.sqrt(temp[0,2] * temp[0,2] +  temp[1,2] * temp[1,2])
			if  a >16*1e-6 :
				Psi = math.atan2(temp[1,2] , -temp[0,2])
				Rot = math.atan2(temp[2,1], temp[2,0])
				if abs(math.sin(Psi)) < 1e-6:
					sign_sb =np.sign(-temp[0,2] / math.cos(Psi))
				else:
					if math.sin(Psi) > 0:
						sign_sb=np.sign(temp[1, 2]) 
					else :
						sign_sb=-np.sign(temp[1, 2])
				Tilt  = math.atan2(sign_sb * a, temp[2, 2])
			else :
				if np.sign(temp[2, 2]) > 0:	
					Rot = 0
					Tilt  = 0
					Psi = math.atan2(-temp[1,0], temp[0, 0])
				else :	
					Rot = 0
					Tilt  = math.pi
					Psi = math.atan2(temp[1,0], -temp[0, 0]) 
			Rot=math.degrees(Rot)
			Tilt=math.degrees(Tilt)
			Psi=math.degrees(Psi)
			
			xy=np.dot(temp,C_float)
			NEW_X=xy[0,0]+originX
			NEW_Y=xy[1,0]+originY
			if(relion30<1):
				NEW_X=NEW_X*apix
				NEW_Y=NEW_Y*apix   
			tmp=""
			for j in range(0,xx):
				if(j!=Rot_index and j!=Tilt_index and j!=Psi_index and j!=X_index and j!=Y_index):
					tmp+=str(instar_line[i].split()[j])
				if(j==Rot_index):
					tmp+=str(Rot)
				if(j==Tilt_index):
					tmp+=str(Tilt)	
				if(j==Psi_index):
					tmp+=str(Psi)  
				if(j==X_index):  
					tmp+=str(NEW_X)
				if(j==Y_index):  
					tmp+=str(NEW_Y)
				if(j!=xx-1):
					tmp+="\t"
				if(j==xx-1):
					tmp+=("\n")
			out.write(tmp)
	out.close()
	aa.close()


def parse_command_line():
	usage="%prog <input star> <chimera txt> <pixel size> <output star> <output INT translation txt>"
	parser = OptionParser(usage=usage, version="%1")
	if len(sys.argv)<6: 
		print "<input star> <chimera txt> <pixel size> <output star> <output INT translation txt>"
		sys.exit(-1)
	
	(options, args)=parser.parse_args()
	star = str(args[0])
	chimera_txt=str(args[1])
	apix=float(args[2])
	output=str(args[3])
	output2=str(args[4])
	return (star,chimera_txt,apix,output,output2)

def find_relion_metadata(line,mline,tofind):
	for i in range(0,mline):
		if (line[i].split()):
			if (str(line[i].split()[0])==tofind):
				INDEX=int(line[i].split('#')[1])-1
				
	return (INDEX)
def SQR(x):
	y=float(x)
	return(y*y)
def judge_relion30_or_relion31(inline):
	trys=3
	RELION30=1
	for i in range (0,trys):
		if(inline[i].split()):
			if(len(inline[i].split())>=2):
				if(inline[i].split()[0][0]=="#" and int(str(inline[i].split()[2]))>30000):
					RELION30=0
					break
	return RELION30
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
def judge_mline1(inline,start):
	trys=70
	intarget=-1
	for i in range (start,trys):
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

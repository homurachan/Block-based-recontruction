/*	This prog just adds up 4 blocks into a whole icoshedral model.
	You can add as many blocks as possible by editing the code like using arrays, but I'm quite lazy.
	The output is a series of mrc files. This because if ny is very big, it takes several hours to calculate the whole 3d model.
	Now you can do a paralle calculation to save much time.
	To add these mrc files up using make_mrc_slice_into_3d_mrc
	if ny is more than 1290, using e2proc3d.py in JSPR package, which can handle very large 3d mrc files.
*/
#include <cstdlib>
#include <cmath>
#include <ctype.h>   // for toupper()  */
#include <string.h>  /* for strings */
#include <time.h>
#include <ctime>
#include <string>
#include <iostream>  //  C++ stream IO
#include <sstream>   // string streams
#include <fstream>
#include <iomanip>   //  to format the output
#include <vector>
#include "EMData.h"
#include <math.h>
#include "List.h"
#include "util.h"
#include "XYData.h"
#include <cstdio>
#include <stdlib.h>

using namespace std;
static float ICOS[180]={
	0.,0.  ,   0., 0.,0. ,  288., 0.,0. ,  216., 0.,0. ,  144., 0.,0. ,   72., \
	0.,63.4349 , 36., 0.,63.4349 , 324., 0.,63.4349 , 252., 0.,63.4349 , 180., 0.,63.4349 , 108., \
	72.,63.4349 , 36., 72.,63.4349 , 324., 72.,63.4349 , 252., 72.,63.4349 , 180., 72.,63.4349 , 108.,\
	144.,63.4349,36.,144.,63.4349 ,324.,144.,63.4349 , 252.,144.,63.4349 , 180., 144.,63.4349, 108., \
	216.,63.4349 , 36., 216.,63.4349,324., 216.,63.4349 ,252.,216.,63.4349 ,180., 216.,63.4349 ,108., \
	288.,63.4349 , 36., 288.,63.4349,324., 288.,63.4349,252., 288.,63.4349,180.,288.,63.4349 ,108.,\
	36.,116.5651 ,0., 36.,116.5651,288., 36.,116.5651 ,216., 36.,116.5651 ,144., 36.,116.5651 ,72.,\
	108.,116.5651 ,0.,108.,116.5651 ,288., 108.,116.5651 ,216.,108.,116.5651 ,144., 108.,116.5651 ,72.,\
	180.,116.5651 ,0.,180.,116.5651 ,288., 180.,116.5651 ,216., 180.,116.5651 ,144., 180.,116.5651 ,72.,\
	252.,116.5651 ,0., 252.,116.5651 ,288., 252.,116.5651 ,216., 252.,116.5651 ,144., 252.,116.5651 ,72.,\
	324.,116.5651 ,0.,324.,116.5651 ,288., 324.,116.5651 ,216., 324.,116.5651 ,144., 324.,116.5651 ,72.,\
	0.,180.,0., 0.,180.,288., 0.,180.,216., 0.,180.,144., 0.,180.,72.  
};

int main(){
	string image1,image2,image3,image4,output,outname;
	std::stringstream stream0;
	int nx,ny,nz,ny0;
	int i=0,j=0,k=0,cx1,cy1,cz1,cx2,cy2,cz2,max_radius,min_radius,tmp_int_x,tmp_int_y,tmp_int_z,tmp_int_x2,tmp_int_y2,tmp_int_z2,count=0,n,nn;
	float temp_nx,temp_ny,temp_nz,tmp_radius1,tmp_radius2,tmp_radius3,tmp_radius4;
	int cx3,cy3,cz3,cx4,cy4,cz4;
	int start,eend;
	float e1,e2,e3;
	cout<<"Enter full size image name"<<endl;
	cin>>image1;
	cout<<"Enter ny of full size output image:"<<endl;
	cin>>ny;
	cout<<"Enter center of image1, image2, image3, image4. Like 326 326 694."<<endl;
	cin>>cx1>>cy1>>cz1>>cx2>>cy2>>cz2>>cx3>>cy3>>cz3>>cx4>>cy4>>cz4;
	float dx=(float)(ny/2),dy=(float)(ny/2),dz=(float)(ny/2);
	cout<<"Enter maxium, minium radius in pixel, like 100 30:"<<endl;
	cin>>max_radius>>min_radius;
	cout<<"Enter start num, end num in Z axis:"<<endl;
	cin>>start>>eend;
	cout<<"Enter output root name"<<endl;
	cin>>output;
	float k1,k2;
	float i1x[60],i1y[60],i1z[60],i2x[60],i2y[60],i2z[60],i3x[60],i3y[60],i3z[60],i4x[60],i4y[60],i4z[60];
	float mx[9];
	for(i=0;i<60;i++){
		i1x[i]=0.;i1y[i]=0.;i1z[i]=0.;
		i2x[i]=0.;i2y[i]=0.;i2z[i]=0.;
		i3x[i]=0.;i3y[i]=0.;i3z[i]=0.;
		i4x[i]=0.;i4y[i]=0.;i4z[i]=0.;
	}
//	cout<<"debug"<<endl;
	for(n=0;n<60;n++){
		e1=ICOS[n*3+1]*PI/180.0;
		e2=ICOS[n*3+2]*PI/180.0-PI/2.;
		e3=ICOS[n*3]*PI/180.0+PI/2.;

		mx[0]=(cos(e3)*cos(e2)-cos(e1)*sin(e2)*sin(e3));
		mx[1]=-1*(sin(e3)*cos(e2)+cos(e1)*sin(e2)*cos(e3));
		mx[2]=sin(e1)*sin(e2);
		mx[3]=(cos(e3)*sin(e2)+cos(e1)*cos(e2)*sin(e3));
		mx[4]=(-sin(e3)*sin(e2)+cos(e1)*cos(e2)*cos(e3));
		mx[5]=-1*sin(e1)*cos(e2);
		mx[6]=sin(e1)*sin(e3);
		mx[7]=sin(e1)*cos(e3);
		mx[8]=cos(e1);

		i1x[n]=(mx[0]*(cx1-dx)+mx[1]*(cy1-dy)+mx[2]*(cz1-dz))+dx;
		i1y[n]=(mx[3]*(cx1-dx)+mx[4]*(cy1-dy)+mx[5]*(cz1-dz))+dy;
		i1z[n]=(mx[6]*(cx1-dx)+mx[7]*(cy1-dy)+mx[8]*(cz1-dz))+dz;
		
		i2x[n]=(mx[0]*(cx2-dx)+mx[1]*(cy2-dy)+mx[2]*(cz2-dz))+dx;
		i2y[n]=(mx[3]*(cx2-dx)+mx[4]*(cy2-dy)+mx[5]*(cz2-dz))+dy;
		i2z[n]=(mx[6]*(cx2-dx)+mx[7]*(cy2-dy)+mx[8]*(cz2-dz))+dz;
		
		i3x[n]=(mx[0]*(cx3-dx)+mx[1]*(cy3-dy)+mx[2]*(cz3-dz))+dx;
		i3y[n]=(mx[3]*(cx3-dx)+mx[4]*(cy3-dy)+mx[5]*(cz3-dz))+dy;
		i3z[n]=(mx[6]*(cx3-dx)+mx[7]*(cy3-dy)+mx[8]*(cz3-dz))+dz;
		
		i4x[n]=(mx[0]*(cx4-dx)+mx[1]*(cy4-dy)+mx[2]*(cz4-dz))+dx;
		i4y[n]=(mx[3]*(cx4-dx)+mx[4]*(cy4-dy)+mx[5]*(cz4-dz))+dy;
		i4z[n]=(mx[6]*(cx4-dx)+mx[7]*(cy4-dy)+mx[8]*(cz4-dz))+dz;
//		cout<<i1x[n]<<"\t"<<i1y[n]<<"\t"<<i1z[n]<<"\n"<<i2x[n]<<"\t"<<i2y[n]<<"\t"<<i2z[n]<<"\n"<<i3x[n]<<"\t"<<i3y[n]<<"\t"<<
//		i3z[n]<<"\n"<<i4x[n]<<"\t"<<i4y[n]<<"\t"<<i4z[n]<<endl;
	}

	EMData *map1,*out,*tst;
//	tst=new EMData();
//	tst->setSize(ny,ny,ny);
//	tst->zero(0);
	map1=new EMData();
	map1->readImage(image1.c_str(),-1);
	
	float *map1_data=map1->getDataRO();
//	float *tst_data=tst->getData();
	float tmp_r1_min,tmp_r1,tmp_r2_min,tmp_r2,tmp_r3_min,tmp_r3,tmp_r4_min,tmp_r4,rmin;
	int ii;
	float old_x,old_y,old_z;
	int case0,overlap,overlap_type,nnn1=0,nnn2=0,nnn3=0,nnn4=0;
	float t,u,v,rr;
	double iijj;
	int NEW_X,NEW_Y,NEW_Z;

	for(k=start;k<eend;k++){
		out=new EMData();
		out->setSize(ny,ny,1);
		out->zero(0);
		float *out_data=out->getData();

		for(j=0;j<ny;j++){
			for(i=0;i<ny;i++){
//	for(k=ny/2-40;k<ny/2-39;k++){
//		for(j=ny/2;j<ny/2+1;j++){
//			for(i=0;i<ny;i++){
				tmp_int_x=i-ny/2;
				tmp_int_y=j-ny/2;
				tmp_int_z=k-ny/2;
				rr=sqrt(SQR(tmp_int_x)+SQR(tmp_int_y)+SQR(tmp_int_z));

//				if(rr>=ny/2-4){
//					continue;
//				}
//				cout<<"rr="<<rr<<"\tijk="<<i<<"\t"<<j<<"\t"<<k<<endl;
				nnn1=0;
				nnn2=0;
				nnn3=0;
				nnn4=0;
				tmp_r1_min=1.736*ny;
				tmp_r2_min=1.736*ny;
				tmp_r3_min=1.736*ny;
				tmp_r4_min=1.736*ny;
				overlap=1;
				overlap_type=0;
				for(nn=0;nn<60;nn++){
					tmp_r1=sqrt(SQR(i-i1x[nn])+SQR(j-i1y[nn])+SQR(k-i1z[nn]));
					if(tmp_r1<tmp_r1_min){
						tmp_r1_min=tmp_r1;
						nnn1=nn;
					}
					tmp_r2=sqrt(SQR(i-i2x[nn])+SQR(j-i2y[nn])+SQR(k-i2z[nn]));
					if(tmp_r2<=tmp_r2_min){
						tmp_r2_min=tmp_r2;
						nnn2=nn;
					}
					tmp_r3=sqrt(SQR(i-i3x[nn])+SQR(j-i3y[nn])+SQR(k-i3z[nn]));
					if(tmp_r3<tmp_r3_min){
						tmp_r3_min=tmp_r3;
						nnn3=nn;
					}
					tmp_r4=sqrt(SQR(i-i4x[nn])+SQR(j-i4y[nn])+SQR(k-i4z[nn]));
					if(tmp_r4<tmp_r4_min){
						tmp_r4_min=tmp_r4;
						nnn4=nn;
					}
	//				cout<<nn<<"\tdebug 1min="<<tmp_r1<<" nnn1="<<nnn1<<"\n"<<"debug 2min="<<tmp_r2<<" nnn2="<<nnn2<<"\n"
	//			<<"debug 3min="<<tmp_r3<<" nnn3="<<nnn3<<"\n"<<"debug 4min="<<tmp_r4<<" nnn4="<<nnn4<<"\n"<<endl;
				}
//				cout<<"debug 1min="<<tmp_r1_min<<" nnn1="<<nnn1<<"\n"<<"debug 2min="<<tmp_r2_min<<" nnn2="<<nnn2<<"\n"
//				<<"debug 3min="<<tmp_r3_min<<" nnn3="<<nnn3<<"\n"<<"debug 4min="<<tmp_r4_min<<" nnn4="<<nnn4<<"\n"<<endl;
				if(tmp_r1_min<=tmp_r2_min && tmp_r1_min<=tmp_r3_min && tmp_r1_min<=tmp_r4_min){
					rmin=tmp_r1_min;
					overlap_type+=1;
					if(rmin==tmp_r2_min){
						overlap+=1;
						overlap_type+=2;
					}
					if(rmin==tmp_r3_min){
						overlap+=1;
						overlap_type+=4;
					}
					if(rmin==tmp_r4_min){
						overlap+=1;
						overlap_type+=8;
					}
					
			//		case0=1;
				}
				else if(tmp_r2_min<tmp_r1_min && tmp_r2_min<=tmp_r3_min && tmp_r2_min<=tmp_r4_min){
					rmin=tmp_r2_min;
					overlap_type+=2;
					if(rmin==tmp_r3_min){
						overlap+=1;
						overlap_type+=4;
					}
					if(rmin==tmp_r4_min){
						overlap+=1;
						overlap_type+=8;
					}
			//		case0=2;
				}
				else if(tmp_r3_min<tmp_r1_min && tmp_r3_min<tmp_r2_min && tmp_r3_min<=tmp_r4_min){
					rmin=tmp_r3_min;
					overlap_type+=4;
					if(rmin==tmp_r4_min){
						overlap+=1;
						overlap_type+=8;
					}
			//		case0=3;
				}
				else if(tmp_r4_min<tmp_r1_min && tmp_r4_min<tmp_r2_min && tmp_r4_min<tmp_r3_min){
					rmin=tmp_r4_min;
					overlap_type+=8;
			//		case0=4;
				}				
				else{
					
				}
//				cout<<"debug type="<<overlap_type<<"\toverlap="<<overlap<<"\trmin="<<rmin<<endl;
				if (rmin>max_radius){
						continue;
					}
				if(overlap_type>=8){
					e1=ICOS[nnn4*3+1]*PI/180.0;
					e2=ICOS[nnn4*3+2]*PI/180.0-PI/2.;
					e3=ICOS[nnn4*3]*PI/180.0+PI/2.;
					mx[0]=(cos(e3)*cos(e2)-cos(e1)*sin(e2)*sin(e3));
					mx[3]=-1*(sin(e3)*cos(e2)+cos(e1)*sin(e2)*cos(e3));
					mx[6]=sin(e1)*sin(e2);
					mx[1]=(cos(e3)*sin(e2)+cos(e1)*cos(e2)*sin(e3));
					mx[4]=(-sin(e3)*sin(e2)+cos(e1)*cos(e2)*cos(e3));
					mx[7]=-1*sin(e1)*cos(e2);
					mx[2]=sin(e1)*sin(e3);
					mx[5]=sin(e1)*cos(e3);
					mx[8]=cos(e1);		

					old_x=(mx[0]*(i-i4x[nnn4])+mx[1]*(j-i4y[nnn4])+mx[2]*(k-i4z[nnn4]))+cx4;
					old_y=(mx[3]*(i-i4x[nnn4])+mx[4]*(j-i4y[nnn4])+mx[5]*(k-i4z[nnn4]))+cy4;
					old_z=(mx[6]*(i-i4x[nnn4])+mx[7]*(j-i4y[nnn4])+mx[8]*(k-i4z[nnn4]))+cz4;
					t=old_x-floor(old_x);
					u=old_y-floor(old_y);
					v=old_z-floor(old_z);
					NEW_X=floor(old_x);
					NEW_Y=floor(old_y);
					NEW_Z=floor(old_z);
		//			ii=(int)(floor(old_x+old_y*ny+old_z*ny*ny)+0.5-1);
		//			ii=int(floor(old_x+0.5-1))+int(floor(old_y+0.5-1))*ny+int(floor(old_z+0.5-1))*ny*ny;
					iijj=NEW_X+NEW_Y*ny+NEW_Z*ny*ny;
					ii=(int)(floor(iijj+0.5)-1);
	//				cout<<i<<"\t"<<j<<"\t"<<k<<"\t"<<i+j*ny+k*ny*ny<<"\t"<<"\tOLD\t"<<NEW_X+NEW_Y*ny+NEW_Z*ny*ny<<"\t"<<ii<<"\t"<<setprecision(10)<<iijj<<"\t"<<old_x<<"\t"<<old_y<<"\t"<<old_z<<endl;
					if(ii<=(ny*ny*ny) && ii >=0){
		//				out_data[i+ny*j]+=(map1_data[ii]/overlap);

					
					out_data[i+ny*j]+=trilin(map1_data[ii],map1_data[ii+1],map1_data[ii+ny],map1_data[ii+ny+1],
						map1_data[ii+ny*ny],map1_data[ii+ny*ny+1],map1_data[ii+ny*ny+ny],map1_data[ii+ny*ny+ny+1],
							t,u,v)/overlap;
					}
					overlap_type-=8;
				}
				if(overlap_type>=4){
					e1=ICOS[nnn3*3+1]*PI/180.0;
					e2=ICOS[nnn3*3+2]*PI/180.0-PI/2.;
					e3=ICOS[nnn3*3]*PI/180.0+PI/2.;
					mx[0]=(cos(e3)*cos(e2)-cos(e1)*sin(e2)*sin(e3));
					mx[3]=-1*(sin(e3)*cos(e2)+cos(e1)*sin(e2)*cos(e3));
					mx[6]=sin(e1)*sin(e2);
					mx[1]=(cos(e3)*sin(e2)+cos(e1)*cos(e2)*sin(e3));
					mx[4]=(-sin(e3)*sin(e2)+cos(e1)*cos(e2)*cos(e3));
					mx[7]=-1*sin(e1)*cos(e2);
					mx[2]=sin(e1)*sin(e3);
					mx[5]=sin(e1)*cos(e3);
					mx[8]=cos(e1);		

					old_x=(mx[0]*(i-i3x[nnn3])+mx[1]*(j-i3y[nnn3])+mx[2]*(k-i3z[nnn3]))+cx3;
					old_y=(mx[3]*(i-i3x[nnn3])+mx[4]*(j-i3y[nnn3])+mx[5]*(k-i3z[nnn3]))+cy3;
					old_z=(mx[6]*(i-i3x[nnn3])+mx[7]*(j-i3y[nnn3])+mx[8]*(k-i3z[nnn3]))+cz3;
		//			cout<<i<<"\t"<<j<<"\t"<<k<<"\t"<<old_x<<"\t"<<old_y<<"\t"<<old_z<<endl;
					t=old_x-floor(old_x);
					u=old_y-floor(old_y);
					v=old_z-floor(old_z);
					NEW_X=floor(old_x);
					NEW_Y=floor(old_y);
					NEW_Z=floor(old_z);
		//			ii=int(floor(old_x+0.5-1))+int(floor(old_y+0.5-1))*ny+int(floor(old_z+0.5-1))*ny*ny;
					iijj=NEW_X+NEW_Y*ny+NEW_Z*ny*ny;
					ii=(int)(floor(iijj+0.5)-1);
	//				cout<<i<<"\t"<<j<<"\t"<<k<<"\t"<<i+j*ny+k*ny*ny<<"\t"<<"\tOLD\t"<<NEW_X+NEW_Y*ny+NEW_Z*ny*ny<<"\t"<<ii<<"\t"<<setprecision(10)<<iijj<<"\t"<<old_x<<"\t"<<old_y<<"\t"<<old_z<<endl;
					if(ii<=(ny*ny*ny) && ii >=0){
		//				out_data[i+ny*j]+=(map1_data[ii]/overlap);

					
					out_data[i+ny*j]+=trilin(map1_data[ii],map1_data[ii+1],map1_data[ii+ny],map1_data[ii+ny+1],
						map1_data[ii+ny*ny],map1_data[ii+ny*ny+1],map1_data[ii+ny*ny+ny],map1_data[ii+ny*ny+ny+1],
							t,u,v)/overlap;
					}
					overlap_type-=4;
				}
				if(overlap_type>=2){

					e1=ICOS[nnn2*3+1]*PI/180.0;
					e2=ICOS[nnn2*3+2]*PI/180.0-PI/2.;
					e3=ICOS[nnn2*3]*PI/180.0+PI/2.;
					mx[0]=(cos(e3)*cos(e2)-cos(e1)*sin(e2)*sin(e3));
					mx[3]=-1*(sin(e3)*cos(e2)+cos(e1)*sin(e2)*cos(e3));
					mx[6]=sin(e1)*sin(e2);
					mx[1]=(cos(e3)*sin(e2)+cos(e1)*cos(e2)*sin(e3));
					mx[4]=(-sin(e3)*sin(e2)+cos(e1)*cos(e2)*cos(e3));
					mx[7]=-1*sin(e1)*cos(e2);
					mx[2]=sin(e1)*sin(e3);
					mx[5]=sin(e1)*cos(e3);
					mx[8]=cos(e1);		

					old_x=(mx[0]*(i-i2x[nnn2])+mx[1]*(j-i2y[nnn2])+mx[2]*(k-i2z[nnn2]))+cx2;
					old_y=(mx[3]*(i-i2x[nnn2])+mx[4]*(j-i2y[nnn2])+mx[5]*(k-i2z[nnn2]))+cy2;
					old_z=(mx[6]*(i-i2x[nnn2])+mx[7]*(j-i2y[nnn2])+mx[8]*(k-i2z[nnn2]))+cz2;
		//			cout<<i<<"\t"<<j<<"\t"<<k<<"\t"<<old_x<<"\t"<<old_y<<"\t"<<old_z<<endl;
					t=old_x-floor(old_x);
					u=old_y-floor(old_y);
					v=old_z-floor(old_z);
					NEW_X=floor(old_x);
					NEW_Y=floor(old_y);
					NEW_Z=floor(old_z);
		//			ii=(int)(old_x+old_y*ny+old_z*ny*ny);
		//			ii=int(floor(old_x+0.5-1))+int(floor(old_y+0.5-1))*ny+int(floor(old_z+0.5-1))*ny*ny;
					iijj=NEW_X+NEW_Y*ny+NEW_Z*ny*ny;
					ii=(int)(floor(iijj+0.5)-1);
	//				cout<<i<<"\t"<<j<<"\t"<<k<<"\t"<<i+j*ny+k*ny*ny<<"\t"<<"\tOLD\t"<<NEW_X+NEW_Y*ny+NEW_Z*ny*ny<<"\t"<<ii<<"\t"<<setprecision(10)<<iijj<<"\t"<<old_x<<"\t"<<old_y<<"\t"<<old_z<<endl;
					if(ii<=(ny*ny*ny) && ii >=0){
		//				out_data[i+ny*j]+=(map1_data[ii]/overlap);

					
					out_data[i+ny*j]+=trilin(map1_data[ii],map1_data[ii+1],map1_data[ii+ny],map1_data[ii+ny+1],
						map1_data[ii+ny*ny],map1_data[ii+ny*ny+1],map1_data[ii+ny*ny+ny],map1_data[ii+ny*ny+ny+1],
							t,u,v)/overlap;
					}
					overlap_type-=2;
				}
				if(overlap_type>=1){
					e1=ICOS[nnn1*3+1]*PI/180.0;
					e2=ICOS[nnn1*3+2]*PI/180.0-PI/2.;
					e3=ICOS[nnn1*3]*PI/180.0+PI/2.;
					mx[0]=(cos(e3)*cos(e2)-cos(e1)*sin(e2)*sin(e3));
					mx[3]=-1*(sin(e3)*cos(e2)+cos(e1)*sin(e2)*cos(e3));
					mx[6]=sin(e1)*sin(e2);
					mx[1]=(cos(e3)*sin(e2)+cos(e1)*cos(e2)*sin(e3));
					mx[4]=(-sin(e3)*sin(e2)+cos(e1)*cos(e2)*cos(e3));
					mx[7]=-1*sin(e1)*cos(e2);
					mx[2]=sin(e1)*sin(e3);
					mx[5]=sin(e1)*cos(e3);
					mx[8]=cos(e1);		

					old_x=(mx[0]*(i-i1x[nnn1])+mx[1]*(j-i1y[nnn1])+mx[2]*(k-i1z[nnn1]))+cx1;
					old_y=(mx[3]*(i-i1x[nnn1])+mx[4]*(j-i1y[nnn1])+mx[5]*(k-i1z[nnn1]))+cy1;
					old_z=(mx[6]*(i-i1x[nnn1])+mx[7]*(j-i1y[nnn1])+mx[8]*(k-i1z[nnn1]))+cz1;
			//		cout<<i<<"\t"<<j<<"\t"<<k<<"\t"<<old_x<<"\t"<<old_y<<"\t"<<old_z<<endl;
					t=old_x-floor(old_x);
					u=old_y-floor(old_y);
					v=old_z-floor(old_z);
					NEW_X=floor(old_x);
					NEW_Y=floor(old_y);
					NEW_Z=floor(old_z);
		//			ii=int(floor(old_x+0.5-1))+int(floor(old_y+0.5-1))*ny+int(floor(old_z+0.5-1))*ny*ny;
					iijj=NEW_X+NEW_Y*ny+NEW_Z*ny*ny;
					ii=(int)(floor(iijj+0.5)-1);		//maybe ii=(int)(floor(iijj+0.5));
		//			cout<<i<<"\t"<<j<<"\t"<<k<<"\t"<<i+j*ny+k*ny*ny<<"\t"<<"\tOLD\t"<<NEW_X+NEW_Y*ny+NEW_Z*ny*ny<<"\t"<<ii<<"\t"<<setprecision(10)<<iijj<<"\t"<<old_x<<"\t"<<old_y<<"\t"<<old_z<<endl;
					if(ii<=(ny*ny*ny) && ii >=0){
		//				out_data[i+ny*j]+=(map1_data[ii]/overlap);
						out_data[i+ny*j]+=trilin(map1_data[ii],map1_data[ii+1],map1_data[ii+ny],map1_data[ii+ny+1],
							map1_data[ii+ny*ny],map1_data[ii+ny*ny+1],map1_data[ii+ny*ny+ny],map1_data[ii+ny*ny+ny+1],
								t,u,v)/overlap;
					}
				}
			}
		}
		stream0 << setfill('0');
		stream0 << setw(4);
		stream0 << (k);
		outname=output+"_"+stream0.str()+".mrc";
		stream0.str("");
		out->doneData();
		out->update();
		out->writeMRC(outname.c_str());
		delete out;
		
	}
	delete map1;


	return 0;
	}
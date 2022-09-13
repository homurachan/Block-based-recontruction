/*	This prog adds up many small blocks by using a quite straightforwad method:
	1. keep signal within minium radius
	2. drop signal outside maxium radius
	3. doing averaging between min-max radius
	You should memorize the coordinates in original model.
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

int main(){
	string image1,image2,image3,image4,output;
	int nx,ny,nz,ny0;
	int i=0,j=0,k=0,cx1,cy1,cz1,cx2,cy2,cz2,max_radius,min_radius,tmp_int_x,tmp_int_y,tmp_int_z,tmp_int_x2,tmp_int_y2,tmp_int_z2;
	int temp_nx,temp_ny,temp_nz,tmp_radius,tmp_radius2,tmp_radius3,tmp_radius4;
	int cx3,cy3,cz3,cx4,cy4,cz4;
	int total=0;
	int ny_2large=0,n,NEW_NY=0,KX=0,KY=0,KZ=0;
	cout<<"Total number of images:"<<endl;
	cin>>total;
	string image[total];
	cout<<"Enter image name, split by SPACE:"<<endl;
	for (i=0;i<total;i++){
		cin>>image[i];
	}
	cout<<"Enter ny0 of input images, ny of full size output image:"<<endl;
	cin>>ny0>>ny;
	if(ny>1290){
		cout<<"ny is too large to make a full 3d volume. Use ny/2 instead, and change the original coordinates."<<endl;
		ny_2large=1;
		NEW_NY=ny/2;
		cout<<"Enter vector coordinates that you try to translate to (0,0,0), like 700 900 900."<<endl;
		cin>>KX>>KY>>KZ;
	}
	int cx[total],cy[total],cz[total];
	cout<<"Enter center of images, split by SPACE. Like 326 326 694."<<endl;
	for (i=0;i<total;i++){
		cin>>cx[i]>>cy[i]>>cz[i];
	}
	
	cout<<"Enter maxium, minium radius in pixel, like 100 30:"<<endl;
	cin>>max_radius>>min_radius;
	cout<<"Enter output"<<endl;
	cin>>output;
	float k1;
	EMData *map,*out,*tst;

	out=new EMData();
	if(ny_2large==0){
		out->setSize(ny,ny,ny);
		out->zero(0);
		tst=new EMData();
		tst->setSize(ny,ny,ny);
		tst->zero(0);
	}
	else{
		out->setSize(NEW_NY,NEW_NY,NEW_NY);
		out->zero(0);
		tst=new EMData();
		tst->setSize(NEW_NY,NEW_NY,NEW_NY);
		tst->zero(0);
	}
	float *out_data=out->getData();
	float *tst_data=tst->getData();
	for(n=0;n<total;n++){
		map=new EMData();
		map->readImage(image[n].c_str(),-1);
		float *map_data=map->getDataRO();
		for(k=0;k<ny0;k++){
			for(j=0;j<ny0;j++){
				for(i=0;i<ny0;i++){
					if(ny_2large==0){
						tmp_int_x=(i-ny0/2)+cx[n];
						tmp_int_y=(j-ny0/2)+cy[n];
						tmp_int_z=(k-ny0/2)+cz[n];
						tmp_radius=sqrt(SQR(tmp_int_x-cx[n])+SQR(tmp_int_y-cy[n])+SQR(tmp_int_z-cz[n]));
						
						if(tmp_radius<=max_radius && tmp_radius>min_radius){
							k1=-1*float(tmp_radius-max_radius)/float(max_radius-min_radius);
							out_data[tmp_int_x+ny*tmp_int_y+ny*ny*tmp_int_z]+=k1*map_data[i+ny0*j+ny0*ny0*k];
							tst_data[tmp_int_x+ny*tmp_int_y+ny*ny*tmp_int_z]+=k1;
						}
						if(tmp_radius<=min_radius){
							out_data[tmp_int_x+ny*tmp_int_y+ny*ny*tmp_int_z]+=map_data[i+ny0*j+ny0*ny0*k];
							tst_data[tmp_int_x+ny*tmp_int_y+ny*ny*tmp_int_z]+=1;
						}
					}
					else{
						tmp_int_x=(i-ny0/2)+cx[n]-KX;
						tmp_int_y=(j-ny0/2)+cy[n]-KY;
						tmp_int_z=(k-ny0/2)+cz[n]-KZ;
						tmp_radius=sqrt(SQR(tmp_int_x-cx[n]+KX)+SQR(tmp_int_y-cy[n]+KY)+SQR(tmp_int_z-cz[n]+KZ));
						if(tmp_radius<=max_radius && tmp_radius>min_radius){
							k1=-1*float(tmp_radius-max_radius)/float(max_radius-min_radius);
							out_data[tmp_int_x+NEW_NY*tmp_int_y+NEW_NY*NEW_NY*tmp_int_z]+=k1*map_data[i+ny0*j+ny0*ny0*k];
							tst_data[tmp_int_x+NEW_NY*tmp_int_y+NEW_NY*NEW_NY*tmp_int_z]+=k1;
						}
						if(tmp_radius<=min_radius){
							out_data[tmp_int_x+NEW_NY*tmp_int_y+NEW_NY*NEW_NY*tmp_int_z]+=map_data[i+ny0*j+ny0*ny0*k];
							tst_data[tmp_int_x+NEW_NY*tmp_int_y+NEW_NY*NEW_NY*tmp_int_z]+=1;
						}
					}
				}
			}
		}
		delete map;
	
	}
	
	
	
	if(ny_2large==0){
		for(k=0;k<ny;k++){
			for(j=0;j<ny;j++){
				for(i=0;i<ny;i++){
					if(tst_data[i+ny*j+ny*ny*k]!=0){
						out_data[i+ny*j+ny*ny*k]=out_data[i+ny*j+ny*ny*k]/tst_data[i+ny*j+ny*ny*k];
					}
				}
			}
		}
	}
	else{
		for(k=0;k<NEW_NY;k++){
			for(j=0;j<NEW_NY;j++){
				for(i=0;i<NEW_NY;i++){
					if(tst_data[i+NEW_NY*j+NEW_NY*NEW_NY*k]!=0){
						out_data[i+NEW_NY*j+NEW_NY*NEW_NY*k]=out_data[i+NEW_NY*j+NEW_NY*NEW_NY*k]/tst_data[i+NEW_NY*j+NEW_NY*NEW_NY*k];
					}
				}
			}
		}
	}

	
	
	
	tst->doneData();
	tst->update();
//	tst->writeMRC("tst.mrc");
	delete tst;
	out->doneData();
	out->update();
	out->writeMRC(output.c_str());
	delete out;

	return 0;
	}
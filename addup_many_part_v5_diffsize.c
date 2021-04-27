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
	int nx,ny,nz,ny0,ny1,ny_tmp;
	int i=0,j=0,k=0,cx1,cy1,cz1,cx2,cy2,cz2,max_radius,min_radius,max_r_tmp,min_r_tmp,tmp_int_x,tmp_int_y,tmp_int_z,tmp_int_x2,tmp_int_y2,tmp_int_z2;
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
	int ny_i[total];
	cout<<"Enter nyi of input images, ny of full size output image:"<<endl;
	
	for (i=0;i<total;i++){
		cin>>ny_i[i];
	}
	cin>>ny;
	if(ny>1290){
		cout<<"ny is too large to make a full 3d volume."<<endl;
		return 0;
	}
	int cx[total],cy[total],cz[total];
	cout<<"Enter center of images, split by SPACE. Like 326 326 694."<<endl;
	for (i=0;i<total;i++){
		cin>>cx[i]>>cy[i]>>cz[i];
	}
	int max_r[total], min_r[total];
	cout<<"Enter maxium, minium radius in pixel, like 100 30:"<<endl;
	for (i=0;i<total;i++){
		cin>>max_r[i]>>min_r[i];
	}
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
	
	float *out_data=out->getData();
	float *tst_data=tst->getData();
	for(n=0;n<total;n++){
		map=new EMData();
		map->readImage(image[n].c_str(),-1);
		float *map_data=map->getDataRO();
		ny_tmp=ny_i[n];
		max_radius=max_r[n];
		min_radius=min_r[n];
		for(k=0;k<ny_tmp;k++){
			for(j=0;j<ny_tmp;j++){
				for(i=0;i<ny_tmp;i++){
					if(ny_2large==0){
						tmp_int_x=(i-ny_tmp/2)+cx[n];
						tmp_int_y=(j-ny_tmp/2)+cy[n];
						tmp_int_z=(k-ny_tmp/2)+cz[n];
						tmp_radius=sqrt(SQR(tmp_int_x-cx[n])+SQR(tmp_int_y-cy[n])+SQR(tmp_int_z-cz[n]));
						
						if(tmp_radius<=max_radius && tmp_radius>min_radius){
							k1=-1*float(tmp_radius-max_radius)/float(max_radius-min_radius);
							out_data[tmp_int_x+ny*tmp_int_y+ny*ny*tmp_int_z]+=k1*map_data[i+ny_tmp*j+ny_tmp*ny_tmp*k];
							tst_data[tmp_int_x+ny*tmp_int_y+ny*ny*tmp_int_z]+=k1;
						}
						if(tmp_radius<=min_radius){
							out_data[tmp_int_x+ny*tmp_int_y+ny*ny*tmp_int_z]+=map_data[i+ny_tmp*j+ny_tmp*ny_tmp*k];
							tst_data[tmp_int_x+ny*tmp_int_y+ny*ny*tmp_int_z]+=1;
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
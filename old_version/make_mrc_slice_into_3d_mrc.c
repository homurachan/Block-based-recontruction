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
	string image1,output,name;
	int nx,ny,nz;
	int i=0,j=0,k=0,n;
	std::stringstream stream0;

	cout<<"Enter images root name"<<endl;
	cin>>name;
	cout<<"Enter ny of full size output image:"<<endl;
	cin>>ny;
	cout<<"Enter output"<<endl;
	cin>>output;
	float k1,k2;
	EMData *map,*out;
	out=new EMData();
	out->setSize(ny,ny,ny);
	out->zero(0);
	float *out_data=out->getData();
	for (n=0;n<ny;n++){
		stream0 << setfill('0');
		stream0 << setw(4);
		stream0 << (n);
		image1=name+"_"+stream0.str()+".mrc";
		stream0.str("");
		map=new EMData();
		map->readImage(image1.c_str(),0);
		float *map_data=map->getDataRO();
		
		for(j=0;j<ny;j++){
			for(i=0;i<ny;i++){
				out_data[i+ny*j+ny*ny*n]=map_data[i+ny*j];


			}
		}
		delete map;
	}

	out->doneData();
	out->update();
	out->writeMRC(output.c_str());
	delete out;

	return 0;
	}

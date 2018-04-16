// Compiles as: g++ -g -std=c++11 Skeleton_client.cpp  dmx512.c++  $(pkg-config --cflags --libs libola) -o C                                                     
// Skeleton Code for Jack's TCP client requirement, Jorge's OLA, and Taylors sensor
#include <iostream>
#include <cstdlib>
#include <cstring>
#include <string>		//for strings
#include <fstream>		//for C++ file IO
#include <sstream>		//for stream string
#include <cstdio>
#include <ctime>		//for timestamps
#include <sys/time.h>	//timeval and timespec (tv_nsec) for nanoseconds but im just using micro for early testing
#include <sys/types.h>	//setsockopt()
#include <sys/socket.h> //socket SOMAXCOMM
#include <netinet/in.h> //needed for domain addressses
#include <sys/select.h>
#include <arpa/inet.h>	//inet_ntop for IP address resolution
#include <stdlib.h>		//standard C library
#include <unistd.h>
#include <netdb.h>
#include <errno.h>
#include <time.h>
#include <stdlib.h>
#include <stdio.h>

//OLA
#include "dmx512.hpp"

#define port 9999
#define buff 128
//#define HOST "127.0.0.1"
#define HOST "192.168.1.12"

using namespace std;
int connect_to_server(void);
string time_processed(void); //timestamping


int sockfd, reuse = 1; //only need the one socket on client side
struct sockaddr_in sADDR;
struct hostent *host; //this is typically needed for clients to get server information
string message = "SLNS Client ACK";

int main()
{

  DMX512 ola;
  
	connect_to_server();
	cout << "Connection made\n"; //connect to server success
	send(sockfd, message.c_str(), sizeof(message),0);

	while(1)
	{
		char recv_data[buff];
		stringstream ss;
		string CMD, DATA;
		int n = recv(sockfd, recv_data, sizeof(recv_data), 0);
		ss << recv_data;
		ss >> CMD >> DATA;

		if(n == 0) // if connection is broken attempt to reconnect to server
		{
			cout << "Server Connection lost, Attempting to Reestablish\n";
			connect_to_server();
			cout << "Connection Reestablished\n"; //connect to server success
			send(sockfd, message.c_str(), sizeof(message),0);
		}
		else if(n != 0) //process server commands
		{
			cout << "Server Says:" << recv_data << endl;
			if (sizeof(CMD) != 0)
			{
					if((CMD == "SET")) //server sending GUI CR values or user defined values
					{
					  cout << "Setting lights to:" << DATA << endl;
					  //OLA(DATA);
					  ola.setData(DATA);
					  DATA = ola.sendOLA(); // The returned value is based on success
					  send(sockfd,DATA.c_str(), sizeof(DATA), 0); //Send Response
					  DATA.clear();
					  
					}
					else if(CMD == "GET")  //server fetching client sensor values for GUI request
					{
						string sensor_data = "EIGHTLET"; //ARGB(); dummy values
						cout << "Send To Server:" << sensor_data << endl;
						send(sockfd,sensor_data.c_str(),sizeof(sensor_data),0); //Send Sensor data to Server
						sensor_data.clear();
					}
					else if(CMD == "PNG")  //echo when server checks that client is still connected
					{
						cout << "Send To Server:" << CMD << endl;
						send(sockfd, CMD.c_str(), sizeof(CMD),0);
					}
					else if(CMD == "TBS")
					{
						cout << "troubleshooting\n"; 
					}
					else if(CMD == "SHD") //In case we want to add a test function, still pending
					{
						cout << "Shutting down" <<  time_processed() << endl;
						//set OLA to "00000000" to update DMX driver here BEFORE shutting down client
						close(sockfd);
						break; //just to shut down client
					}

				memset(recv_data, 0, sizeof(recv_data));
				ss.clear();
				CMD.clear();
			}
		}
	}
return 0;
}

int connect_to_server()
{
	if((sockfd = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP)) < 0)
	{
		perror("Error: Socket Not created");
		exit(EXIT_FAILURE);
	}

	host = gethostbyname(HOST); //Address for testing on localhost
	//host = gethostbyname("192.168.1.100"); //Address for testing on remote client

	if(host == NULL)
	{
		perror("Host does not exist\n");
		exit(EXIT_FAILURE);
	}
	if (setsockopt(sockfd, SOL_SOCKET, SO_REUSEPORT, (const char*)&reuse, sizeof(int)) < 0)
	{
		perror("setsockopt(SO_REUSEADDR) failed");
		exit(EXIT_FAILURE);
	}
	bzero((char *) &sADDR, sizeof(sADDR));
	sADDR.sin_family = AF_INET;
	bcopy((char *) host->h_addr, (char *) &sADDR.sin_addr.s_addr, host->h_length);
	sADDR.sin_port = htons(port);
	bcopy((char *)host->h_addr,(char *)&sADDR.sin_addr.s_addr,host->h_length);

	cout << "Created Socket\n";

	int cnt = 0;
	while(connect(sockfd,(struct sockaddr*)&sADDR, sizeof(sADDR)) < 0)  //connect to server failure, try again
	{
		sleep(1);
		if (cnt == 10)
			exit(EXIT_FAILURE);
		cnt++;
		perror("Error: Failed to connect");
	}
	return sockfd;
}

string time_processed() //return time in format YYYY/MM/DD_HH:MM:SS:milliseconds
{
	char buf[40];
	char time_buff[40];
	struct timeval ts;
	time_t curtime;
	gettimeofday(&ts, NULL);
	curtime=ts.tv_sec;
	strftime(time_buff,40,"%Y-%m-%d_%T:",localtime(&curtime));
	sprintf(buf,"[%s%ld]",time_buff, ts.tv_usec);
	return buf;
}

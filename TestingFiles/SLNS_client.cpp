/* Spacecraft lighting network system Client
 * Takes input from the SLNS server and commands OLA to change light values.
 * Sends sensor values back
 * compile: g++ -g -Wall -std=c++11 SLNS_client.cpp dmx512.cpp $(pkg-config --cflags --libs libola) -o Client
 */
#include <iostream>
#include <cstdlib>
#include <cstring>
#include <string>
#include <fstream>
#include <sstream>
#include <cstdio>
#include <ctime>
#include <sys/time.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <sys/select.h>
#include <arpa/inet.h>
#include <stdlib.h>
#include <unistd.h>
#include <netdb.h>
#include <errno.h>
#include <time.h>
#include <stdlib.h>
#include <stdio.h>
#include <signal.h>
#include <linux/i2c-dev.h>
#include <sys/ioctl.h>
#include <fcntl.h>

//OLA
#include "dmx512.hpp"

//Macros
#define port 9999
#define buff 128
#define HOST "192.168.1.12"

using namespace std;

//Fucntion Prototypes
int connect_to_server(void);
string time_processed(void); //timestamping
void display_RGB(int);

//Globals
int sockfd, reuse = 1,file;	//only need the one socket on client side
struct sockaddr_in sADDR;
struct hostent *host; 		//this is typically needed for clients to get server information
char aRGB[50];
string message = "SLNS Client ACK";
 
int main()
{
	DMX512 ola;
	connect_to_server();
	cout << "Connection made\n"; //connect to server success
	send(sockfd, message.c_str(), sizeof(message),0);
	const char *bus = "/dev/i2c-1";
	if ((file = open(bus, O_RDWR)) < 0)
	{
		cout << "Failed to open the bus\n";
		exit(1);
	}
	ioctl(file, I2C_SLAVE, 0x29);
	signal(SIGALRM, display_RGB);
	alarm(1);

	while(1)
	{
		char recv_data[buff];
		stringstream ss;
		string CMD, DATA;
		if((recv(sockfd, recv_data, sizeof(recv_data), 0))== 0) // if connection is broken attempt to reconnect to server
		{
			cout << "Server Connection lost, Attempting to Reestablish\n";
			connect_to_server();
			cout << "Connection Reestablished\n"; //connect to server success
			send(sockfd, message.c_str(), sizeof(message),0);
		}
		else //process server commands
		{
			ss << recv_data;
			ss >> CMD >> DATA;
			cout << "Server Says:" << recv_data << endl;
			if (sizeof(CMD) != 0)
			{
				if((CMD == "SET")) //server sending GUI CR values or user defined values
				{
					ola.setData(DATA);
					cout << "Setting lights to:" << DATA << endl;
					cout << "Send To Server:" << aRGB << endl;
					send(sockfd,DATA.c_str(),sizeof(DATA),0); //Send Response
				}
				else if(CMD == "GET")  //server fetching client sensor values for GUI request
				{
					cout << "Send To Server:" << aRGB << endl;
					send(sockfd,aRGB,sizeof(aRGB),0); //Send Sensor data to Server
				}
				else if(CMD == "PNG")  //echo when server checks that client is still connected
				{
					cout << "Send To Server:" << CMD << endl;
					send(sockfd, CMD.c_str(), sizeof(CMD),0);
				}
				else if(CMD == "SHD") //In case we want to add a test function, still pending
				{
					string shutdown = "0000000"; //set OLA to "00000000" to update DMX driver here BEFORE shutting down client
					cout << "Shutting down" <<  time_processed() << endl;
					ola.setData(shutdown);
					shutdown = ola.sendOLA(); // The returned value is based on success
					cout << "Setting lights to:" << shutdown << endl;//OLA(DATA);
					send(sockfd,shutdown.c_str(),sizeof(shutdown),0); //Send Response
				}
				memset(recv_data, 0, sizeof(recv_data));
				ss.clear();
				CMD.clear();
				DATA.clear();
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

	host = gethostbyname(HOST); //Address assignment of server

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

	while(connect(sockfd,(struct sockaddr*)&sADDR, sizeof(sADDR)) < 0)  //connect to server failure, try again
	{
		sleep(1);
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
	strftime(time_buff,40,"%Y/%m/%d_%T:",localtime(&curtime));
	sprintf(buf,"[%s%ld]",time_buff, ts.tv_usec);
	return buf;
}

void display_RGB(int s)
{
	cout << endl;
	// Select enable register(0x80)
	// Power ON, RGBC enable, wait time disable(0x03)
	char config[2] = {0};
	config[0] = 0x80;
	config[1] = 0x03;
	write(file, config, 2);
	// Select ALS time register(0x81)
	// Atime = 700 ms(0x00)
	config[0] = 0x81;
	config[1] = 0x00;
	write(file, config, 2);
	// Select Wait Time register(0x83)
	// WTIME : 2.4ms(0xFF)
	config[0] = 0x83;
	config[1] = 0xFF;
	write(file, config, 2);
	// Select control register(0x8F)
	// AGAIN = 1x(0x00)
	config[0] = 0x8F;
	config[1] = 0x00;
	write(file, config, 2);
	usleep(1000000);

	// Read 8 bytes of data from register(0x94)
	// cData lsb, cData msb, red lsb, red msb, green lsb, green msb, blue l$
	char reg[1] = {0x94};
	write(file, reg, 1);
	char data[8] = {0};
	if(read(file, data, 8) != 8)
	{
		cout << "Error : Input/output Error\n";
	}
	else
	{
		// Convert the data
		int red = (data[3] | data[2]);
		int green = (data[5]| data[4]);
		int blue = (data[7] | data[6]);

		// Calculate luminance
		int luminance = (.2126) * (red) + (.7152) * (green) + (.0722) * (blue);

		//cout <<std::uppercase << std::hex << luminance << " "$
		if(luminance < 0)
		{
			luminance = 0;
		}

		sprintf(aRGB, "%02X%02X%02X%02X", luminance, red, green, blue);
		cout << aRGB << endl;
	}
	alarm(1);    //for every second
	signal(SIGALRM, display_RGB);
}

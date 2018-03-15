// Compiles as:g++ -g -std=c++11 OLA_sensor_client.cpp dmx512.c++ $(pkg-config --cflags --libs libola) -o OSC
// Skeleton Code for Jack's TCP client requirement, Jorge's OLA, and Taylors sensor

//Regular Stuff
#include <stdlib.h>
#include <string>
#include <sstream>
#include <iostream>
#include <time.h>
#include <stdio.h>

//Sockets
#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <netdb.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>

//OLA
#include "dmx512.hpp" 

//Sensor and timer
#include <signal.h>
#include <linux/i2c-dev.h>
#include <sys/ioctl.h>
#include <fcntl.h>


#define port 9999
#define buff 128
using namespace std;

//function prototypes
int sendOLA(int, int, int, int);
void display_RGB(int);

//globals variables
int file;

int main()
{

    //Jack you're missing these:
    string server, CMD, DATA, sensor_data = "FFFFFFFF";

	int sockfd;
	char recv_data[buff];
	struct hostent *host;
	struct sockaddr_in server_addr;
	host = gethostbyname("127.0.0.1");
	sockfd = socket(AF_INET, SOCK_STREAM, 0);
	server_addr.sin_family = AF_INET;
	server_addr.sin_port = htons(port);
	server_addr.sin_addr = *((struct in_addr *)host->h_addr);


	if(connect(sockfd, (struct sockaddr *)&server_addr,sizeof(struct sockaddr)) <0);  //connect to server
	{
		perror("Error: Failed to connect");
		exit(EXIT_FAILURE);
	}
	cout << "Connection made" << endl;
	string client_ack = "HELLO";
	send(sockfd, client_ack.c_str(), sizeof(client_ack), 0);
	//once connection is made start sending signal for data
	signal(SIGALRM, display_RGB);
	alarm(5);
	
	// Create I2C bus
	//int file;
	const char *bus = "/dev/i2c-1";
	if ((file = open(bus, O_RDWR)) < 0) 
	{
		//printf("Failed to open the bus. \n");
		cout << "Failed to open the bus" << endl;
		exit(1);
	}
	// Get I2C device, TCS34725 I2C address is 0x29(41)
	ioctl(file, I2C_SLAVE, 0x29);

	while(true)  //Run forever
	{
		sleep(3000); // wait 3 seconds for avoid network conjection
		recv(sockfd, recv_data, buff, 0);
		cout << "Server says: " << recv_data << endl;
		server = recv_data;
		stringstream ss(server);
		ss >> CMD >> DATA;  


	    if(CMD == "SET") //server sending GUI CR values or user defined values
	    {
	                DMX512 j(DATA);
                        char ack;
                        ack = j.sendOLA();
			send(sockfd, ack, sizeof(ack), 0);
	
	    }
	
	    else if(CMD == "GET")  //server fetching client sensor values for GUI request
	    {
			cout << "Send To Server :" << sensor_data << endl;
	        send(sockfd, sensor_data.c_str(), sizeof(sensor_data), 0);
	        //TODO: Work your sensor magic here as needed
	    }
	    else if(CMD == "PNG")  //echo when server checks that client is still connected
	    {
			cout << "Send To Server :" << CMD << endl;
	        send(sockfd, CMD.c_str(), sizeof(CMD), 0);
	        //This is so the server can keep track of connected clients, please keep and expand on
	    }
	    //else if( CMD == "TST") //In case we want to add a test function, still pending
	
	}

return 0;
}


void display_RGB(int s) 
{
    printf("\n" );

	char aRGB[50];

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
	// cData lsb, cData msb, red lsb, red msb, green lsb, green msb, blue lsb, blue msb
	char reg[1] = {0x94};
	write(file, reg, 1);
	char data[8] = {0};
	if(read(file, data, 8) != 8)
	{
		//printf("Erorr : Input/output Erorr \n");
		cout << "Error : Input/output Error" << endl;
	}
	else
	{       
		// Convert the data
		int cData = (data[1]/* * 256 */| data[0]);
		int red = (data[3] /* * 256*/ | data[2]);
		int green = (data[5]/* * 256*/ | data[4]);
		int blue = (data[7]/* * 256*/ | data[6]);
	
		// Calculate luminance
		int luminance = (.2126) * (red) + (.7152) * (green) + (.0722) * (blue);
	
		//cout <<std::uppercase << std::hex << luminance << " " <<std::uppercase << $
		if(luminance < 0)
		{
			luminance = 0;
		}
	
		sprintf(aRGB, "%02X %02X %02X %02X", luminance, red, green, blue);
		printf("%s", aRGB);

	}
	alarm(5);    //for every second
	signal(SIGALRM, display_RGB);
}


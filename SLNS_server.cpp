/* SLNS server
 * Written by John Austin Todd 2018
 * Usage: g++ -g -std=c++11 SLNS_server.cpp -o SLNS
 * Run: ./SLNS
 * boots up on startup: rc.local ./home/pi/UNT-NASA/SLNS &
 * A single threaded synchronous server which reads/writes from a shared command file with the graphical interface
 * The server accepts new clients, periodically checks to see if any have been removed, and updates the graphical interface
 */
#include <iostream>
#include <cstdlib>
#include <cstring>		//IDK if i actually nead this
#include <string>		//for strings
#include <map>			//for mapping an IP to kernel assigned sockerFD and maintaining connections
#include <fstream>		//for C++ file IO
#include <sstream>		//for stream string
#include <mutex> 		//for atomic locking
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
#include <fcntl.h>
#define PORT 9999
#define buff 128
#define WFpath "/home/pi/UNT-NASA/workfile.txt"
#define TFpath "/home/pi/UNT-NASA/temp.txt"

using namespace std;

//Function Prototypes
void parser(void);		     // processes GUI commands and is super amazing, like, totally bro
char *get_IP(int) ;          //returns new client IP address for storage
string time_processed(void); //timestamping

//Frequently Used
struct timeval tv;			//currently set to 5 seconds 
fstream wf("/home/pi/UNT-NASA/workfile.txt"); //create primary workfile 
mutex parselock, addlock, rmvlock;

//Globals
int listener, sockfd, newfd, fdmax, reuse = 1;	// maximum file descriptor number (nfds) + 1;
string guiFlag = "G", processedFlag = "P", time_issued;

//Global Containers
map <string, int> IPmap; // map container for resolving IP addresses to client sockets
map <string, int>::iterator fd;
fd_set master, rset, wset;

int main()
{
	struct sockaddr_in sADDR;
	int count = 0;
	FD_ZERO(&master);
	FD_ZERO(&rset);
	FD_ZERO(&wset);

	cout<<"**************************************************\n";
	cout<<"******SSSSS*****L*********NN*****N*****SSSSS******\n";
	cout<<"*****S*****S****L*********N*N****N****S*****S*****\n";
	cout<<"*****S**********L*********N**N***N****S***********\n";
	cout<<"******SSSSS*****L*********N***N**N*****SSSSS******\n";
	cout<<"***********S****L*********N****N*N**********S*****\n";
	cout<<"*****S*****S****L*********N*****NN****S*****S*****\n";
	cout<<"******SSSSS*****LLLLLLLL**N******N*****SSSSS******\n";
	cout<<"***********"<<time_processed() <<"***********\n";

	if ((listener = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP)) < 0) //TCP socket created, attach to port and address
	{
		perror("Error: socket failed");
		exit(1);
	}
	else
	{
		cout << "<< Socket Created >>\n";
	}

	fcntl(listener, F_SETFL, O_NONBLOCK); //sets accept to non blocking so it doesn not freeze when there are no new pending clients, continues main while loop
	sADDR.sin_family = AF_INET;
	sADDR.sin_port = htons(PORT);
	sADDR.sin_addr.s_addr = INADDR_ANY; //using any IP address but we are 192.168.1.100

	//Options for the socket to prevent "address already in use" error 
	if (setsockopt(listener, SOL_SOCKET, SO_REUSEPORT, (const char*)&reuse, sizeof(int)) < 0)
	{
		perror("setsockopt(SO_REUSEADDR) failed");
		exit(1);
	}
	// Forcefully attaching socket to the port 9999
	if (bind(listener, (struct sockaddr *)&sADDR, sizeof(sADDR)) < 0)
	{
		perror("Error: bind failed"); //ECONNREFUSED
		exit(1);
	}

	FD_SET(listener, &master); //adds listener to master set
	fdmax = listener; //keep track of the biggest file descriptor. So far, it's this one 
	system("touch /home/pi/UNT-NASA/workfile.txt");
	while(1) // run forever
	{
		if (listen(listener, SOMAXCONN) < 0) //keep listening for new connection to add, must be in the while loop
		{
			perror("Error: listen");
			exit(1);
		}
		else
		{
			cout << "<< Now Accepting Connections >>\n";
		}

		newfd = accept(listener, (struct sockaddr*) NULL, NULL); //allow for remote client connecion

		if (newfd < 0)
		{
			perror("ERROR: accept");
		}
		else if (newfd > 0)
		{
			char ack[buff];
			if (recv(newfd, ack, sizeof(ack),0) != 0)
			{
				char *connected_ip = get_IP(newfd);
				cout << "<< Connection Accepted >>" << ack << endl;
				cout << "[IP: " << connected_ip << " " << newfd << "]\n" ; 
				IPmap.insert(make_pair(connected_ip, newfd));	//add to the IPmap container
				FD_SET(newfd, &master);	//add the new file descriptor to the set cause we need it later
				fstream wf;
				wf.open( WFpath, ios::app); 		//opens file +
				string addrmverr =  guiFlag + " " + connected_ip + " ADD"+ " 00000000 " +  time_processed();
				addlock.lock();
				wf << addrmverr;
				wf.close();
				addlock.unlock();
				if (newfd > fdmax) // keep track of the largest FD
				{
					fdmax = newfd;
					cout << "fdmax: " << fdmax << endl;
				}
			}
		}
		fd = IPmap.begin();
		if (count == 5) //remove dead clients from workfile
		{
			cout << "Reaper Active\n" ;
			string PING = "PNG";
			for(fd = IPmap.begin(); fd != IPmap.end(); fd++)//in case a light is removed
			{
				char echo[buff];
				string addrmverr;
				string current_IP = fd->first; //Human readable IP address
				int current_sock = fd->second; //File descriptor of individual client connection
				cout << current_IP << " " << current_sock << endl;
				cout << "Sending PNG message to "<< "IP: " <<  current_IP << " " << current_sock << endl; 
				send(current_sock, PING.c_str(), sizeof(PING), 0); //send PNG

				if((recv(current_sock, echo, sizeof(echo),0)) == 0)
				{
					cout << "Connection Dropped\n";
					cout << "[IP:" <<  current_IP << " " << current_sock << "]" << endl;  // IP and file descriptor for 
					IPmap.erase(fd); //IP and fd from map at location
					cout << "Pair Erased\n";
					wf.open(WFpath, ios::app); //opens file in append mode
					if(wf.is_open())
					{
						addrmverr =  guiFlag + " " + current_IP + " RMV" + " 00000000 " + time_processed();
						rmvlock.lock();
						wf << addrmverr;
						wf.close();
						rmvlock.unlock(); //remove from workfile
						break;
					}
				}
				else
				{
					cout << current_IP << " still connected\n";
				}
			}
			count = 0; //reset counter
		}
		else
		{
			count++;
			cout << "Loop Counter: " << count << endl;
		}
		parser(); // call the parser to process and forward commands
	}//end while loop
return 0; //end program
}

void parser()
{
	cout << "Parser activated\n";
	sleep(3);
	parselock.lock();
	fstream wf, tf;
	system("touch /home/pi/UNT-NASA/temp.txt");
	wf.open(WFpath);
	if(wf.is_open()) //if workfile exists and is open
	{
		string line;
		while(getline(wf, line)) //while reading workfile and lines in
		{
			string setLINE, getLINE, flag, IP, CMD, data, set_RGB,sensor_data, time_issued;
			stringstream stream, client_respond; // easy manipulation of each line
			rset = master;
			wset = master;
			if(line[0] != 'S') //If the flag is not ment for the server, write processed command into temp and continue
			{
				cout << "Do not process:" + line << endl; //write the unprocessed line back into the file
				tf.open(TFpath, ios::app);//create file and allow appending 
				tf << line << endl;
				tf.close();
			}
			else //if flag is "S" for the server
			{
				cout << "\nProcessing Line: " << line << endl;
				stream.clear();
				client_respond.clear();
				stream << line;
				stream >> flag >> IP >> CMD >> data >> time_issued;  //parses the string
				int currentFD = IPmap.find(IP)->second;
				cout << "IP: "<< IP << endl;
				cout << "Command: " << CMD <<endl;
				cout << "Data: "<< data  << endl;
				cout << "CurrentFD: "<< currentFD << endl;

				if(currentFD <= fdmax)//set current client to forward messages to
				{
					if((FD_ISSET(currentFD, &rset)) || (FD_ISSET(currentFD, &wset)))
					{
						if(CMD == "SET")  //if command is SET either circadian or user defined RGB values
						{
							char response[buff];
							cout << "Setting "+ data + " to " << IP << endl;
							setLINE = CMD + " " + data;	
							send(currentFD,setLINE.c_str(),sizeof(setLINE),0); //this works
							cout << "Response from SET command: " << response << endl;
							if((recv(currentFD,response,sizeof(response),0)) == 0)
							{
								perror("Error: Did not Receive SET ack");
								tf.open(TFpath, ios::app); 
								tf << line;
								tf.close();
								line.clear();
							}
							else // command has been executed on client and update the temp file
							{
								string proc_str2 = processedFlag + " " + IP + " " + CMD + " " + response + "0000000 " + time_issued + " " + time_processed() + "\n";
								cout << "Processed :" << proc_str2 << endl;
								tf.open(TFpath, ios::app);//create file and allow appending 
								tf << proc_str2;
								tf.close();
							}
						}
						else if(CMD == "GET")  //if command is GET sensor values
						{
							char sensor_data[buff];
							cout << "Sending sensor request to Client " << IP << endl;
							getLINE = CMD;
							send(currentFD,getLINE.c_str(),sizeof(getLINE),0);  //send GET request


							if((recv(currentFD,sensor_data,sizeof(sensor_data),0)) == 0)
							{
								perror("Error: Did not Receive GET set");
								tf.open(TFpath, ios::app); 
								tf << line;
								tf.close();
							}
							else // command has been executed on client and update the temp file
							{
								cout << "Client Sensor Value: " << sensor_data << endl;
								string proc_str3 = guiFlag+ " " + IP + " " + CMD + " " + sensor_data + " " + time_issued + " " + time_processed() + "\n";
								cout << "Processed :" << proc_str3 << endl;
								tf.open(TFpath, ios::app); 
								tf << proc_str3;
								tf.close();
							}
						}
						else if(CMD == "SHD") //In case we want to add a test function, still pending
						{
							send(currentFD, CMD.c_str(), sizeof(CMD), 0);
							string proc_str4 = guiFlag + " " + IP + " " + CMD + " " + "00000000" + " " + time_issued + " " + time_processed() + "\n";
							tf.open(TFpath, ios::app); 
							tf << proc_str4;
							cout << "Processed :" << proc_str4 << endl;
							tf.close();
						}
						else if( CMD == "TBS")// Future troubleshooting 
						{
							char sensor_data[buff];
							cout << "Sending sensor request to Client " << IP << endl;
							getLINE = CMD;
							send(currentFD,getLINE.c_str(),sizeof(getLINE),0);  //send GET request
							int n = recv(currentFD,sensor_data, sizeof(sensor_data),0);
							cout << sensor_data << endl;

							if(n == 0)
							{
								perror("Error: Did not Receive GET set");
								tf.open(TFpath, ios::app); 
								tf << line;
								tf.close();
							}
							else // command has been executed on client and update the temp file
							{
								string proc_str3 = guiFlag+ " " + IP + " " + CMD + " " + sensor_data + " " + time_issued + " " + time_processed() + "\n";
								cout << "Processed :" << proc_str3 << endl;
								tf.open(TFpath, ios::app); 
								tf << proc_str3;
								tf.close();
							}
						}
					}
					else
					{
						perror("Client not found\n");
						tf.open(TFpath, ios::app);//create file and allow appending 
						tf << line << endl;
						tf.close();
					}
				}
				else
				{
					perror("fd than fdmax\n");
					tf.open(TFpath, ios::app);//create file and allow appending 
					tf << line << endl;
					tf.close();
				}
			}
			line.clear();
		}
		system("cat /home/pi/UNT-NASA/temp.txt > /home/pi/UNT-NASA/workfile.txt ; rm /home/pi/UNT-NASA/temp.txt"); //system call to overwrite workfile with temp file and then remove temp file
		wf.close();
		parselock.unlock();
	}
	else //could not access temp file
		cout << "Workfile not open\n";
	cout << "\n\nLEAVING PARSER\n\n";
}//end of parser

char *get_IP(int fd) //returns IP address of freshly connected client as a character array pointer
{
	struct sockaddr_in addr;
	socklen_t addr_size = sizeof(struct sockaddr_in);
	int res = getpeername(newfd, (struct sockaddr *)&addr, &addr_size);
	res++;
	char *client_ip = new char[15];
	strcpy(client_ip, inet_ntoa(addr.sin_addr));
	return client_ip;
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


/* SLNS server
 * Written by John Austin Todd 2018
 * Usage: g++ -g -std=c++11 SLNS_server.cpp -o SLNS
 * Run: ./SLNS
 * boots up on startup: rc.local ./home/pi/archive/SLNS &
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
using namespace std;

//Function Prototypes
void parser(void);		     // processes GUI commands and is super amazing, like, totally bro
char *get_IP(int) ;          //returns new client IP address for storage
string time_processed(void); //timestamping

//Frequently Used
struct timeval tv;			//currently set to 5 seconds 
//fstream wf("/home/pi/archive/workfile.txt"); //create primary workfile
fstream wf("workfile.txt"); //create primary workfile 
mutex parselock, addlock, rmvlock;

//Globals
int listener, sockfd, newfd, fdmax, reuse = 1;	// maximum file descriptor number (nfds) + 1;
string guiFlag = "G", processedFlag = "P", time_issued;

//Global Containers
map <string, int> IPmap; // map container for resolving IP addresses to client sockets
fd_set master;	// master file descriptor set
fd_set rset;	// temp fd set for reading sockets
fd_set wset;	// temp fd set for writing sockets

int main()
{
	struct sockaddr_in sADDR;// cADDR; 
	int count = 0;
	tv.tv_sec = 2;			// seconds
	tv.tv_usec = 500000;	// microseconds
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
	system("touch /home/pi/archive/workfile.txt");
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

		//while((errno == EAGAIN) || (errno == EWOULDBLOCK) || (errno == 0)) // I need the accept() socket to go forward regardless of pending connections

		if (newfd < 0)
		{
			perror("ERROR: accept");
		}
		else if (newfd > 0)
		{
			char ack[buff];
			int n = recv(newfd, ack, sizeof(ack),0); //read ack from client
			if (n != 0)
			{
				char *connected_ip = get_IP(newfd);
				cout << "<< Connection Accepted >>" << ack << endl;
				cout << "[IP: " << connected_ip << " " << newfd << "]\n" ; 
				IPmap.insert(make_pair(connected_ip, newfd));	//add to the IPmap container
				FD_SET(newfd, &master);	//add the new file descriptor to the set cause we need it later
				fstream wf;
				wf.open("/home/pi/archive/workfile.txt", ios::app); 		//opens file +
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

		if (count == 5) //remove dead clients from workfile
		{
			cout << "Reaper Active\n" ;
			string PING = "PNG";
			map <string, int>::iterator fd;
			for(fd = IPmap.begin(); fd != IPmap.end(); fd++)//in case a light is removed
			{
				rset = master;
				wset = master;
				string addrmverr;
				string current_IP = fd->first; //Human readable IP address
				int current_sock = fd->second; //File descriptor of individual client connection
				cout << current_IP << " " << current_sock << endl;

				cout << "Sending PNG message to "<< "IP: " <<  current_IP << " " << current_sock << endl; 
				send(current_sock, PING.c_str(), PING.size(), 0); //send PNG
				char echo[buff];
				int n = recv(current_sock, echo, sizeof(echo),0);
				if(n == 0)
				{
					cout << "Connection Dropped\n";
					cout << "[IP:" <<  current_IP << " " << current_sock << "]" << endl;  // IP and file descriptor for 
					IPmap.erase(fd); //IP and fd from map at location
					cout << "Pair Erased\n";
					fstream wf;
					wf.open("/home/pi/archive/workfile.txt", ios::app); //opens file in append mode
					if(wf.is_open())
					{
						addrmverr =  guiFlag + " " + current_IP + " RMV" + " 00000000 " + time_processed();
						rmvlock.lock();
						wf << addrmverr;
						wf.close();
						rmvlock.unlock(); //remove from workfile
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
	cout << "Parser activated" << endl;
	sleep(5); //sleep 5 seconds
	parselock.lock();
	fstream wf, tf;
	tv.tv_sec = 5;			// seconds
	tv.tv_usec = 000000;	// microseconds
	system("touch temp.txt");
	wf.open("workfile.txt");
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
				tf.open("temp.txt", ios::app);//create file and allow appending 
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
							char response[buff]; //change this ASAP
							//int ready = select(fdmax+1, &rset, &wset, nullptr, &tv);
							cout << "Setting "+ data + " to " << IP << endl;
							setLINE = CMD + " " + data;								//SET ABCDEFEA
							send(currentFD,setLINE.c_str(),sizeof(setLINE),0); //this works

							int n = recv(currentFD,response,sizeof(response),0);
							
							client_respond << response;
							client_respond >> set_RGB;
							
							if(n == 0)
							{
								perror("Error: Did not Receive SET ack");
								tf.open("temp.txt", ios::app); 
								tf << line;
								tf.close();
								line.clear();
							}
							else // command has been executed on client and update the temp file
							{
								string proc_str2 = processedFlag + " " + IP + " " + CMD + " " + set_RGB+ " " + time_issued + " " + time_processed() + "\n";
								cout << "Processed :" << proc_str2 << endl;
								tf.open("temp.txt", ios::app);//create file and allow appending 
								tf << proc_str2;
								tf.close();
							}
						}
						else if(CMD == "GET")  //if command is GET sensor values
						{
							//int ready = select(fdmax+1, &rset, &wset, nullptr, &tv);
							char sensor_data[buff];
							cout << "Sending sensor request to Client " << IP << endl;
							getLINE = CMD;
							send(currentFD,getLINE.c_str(),sizeof(getLINE),0);  //send GET request
							int n = recv(currentFD,sensor_data, sizeof(sensor_data),0);
							cout << sensor_data << endl;

							if(n == 0)
							{
								perror("Error: Did not Receive GET set");
								tf.open("temp.txt", ios::app); 
								tf << line;
								tf.close();
							}
							else // command has been executed on client and update the temp file
							{
								string proc_str3 = guiFlag+ " " + IP + " " + CMD + " " + sensor_data + " " + time_issued + " " + time_processed() + "\n"; //WHAT THE MOTHERF!?
								cout << "Processed :" << proc_str3 << endl;
								tf.open("temp.txt", ios::app); 
								tf << proc_str3;
								tf.close();
							}
						}
						else if( CMD == "SHD") //In case we want to add a test function, still pending
						{
							cout << "This is an easter egg, I wanted to make one so here it is, yay! NOW KILLING CLIENT\n";
							send(currentFD, CMD.c_str(), sizeof(CMD), 0);  //send GET request
							string proc_str4 = guiFlag+ " " + IP + " " + CMD + " " + "00000000" + " " + time_issued + " " + time_processed() + "\n";
							tf.open("temp.txt", ios::app); 
							tf << proc_str4;
							cout << "Processed :" << proc_str4 << endl;
							tf.close();
						}
						//else if( CMD == "TBS") Future troubleshooting 
					}
					else
					{
						perror("Client not found\n");
						tf.open("temp.txt", ios::app);//create file and allow appending 
						tf << line << endl;
						tf.close();
					}
				}
				else
				{
					perror("fd than fdmax\n");
					tf.open("temp.txt", ios::app);//create file and allow appending 
					tf << line << endl;
					tf.close();
				}
			}
			line.clear();
		}
		system("cat temp.txt > workfile.txt ; rm temp.txt"); //system call to overwrite workfile with temp file and then remove temp file
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


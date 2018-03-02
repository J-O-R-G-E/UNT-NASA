

// Usage: g++ -g -std=c++11 -pthread serverAndParcer.c++ -lpthread -o server 
// Run: ./server

#include <iostream>
#include <cstdlib> //system()
#include <fstream> // FILE IO
#include <sstream>
#include <string>
#include <mutex>
#include <map>
#include<thread>


// C Goodies
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <netdb.h>
#include <netinet/in.h>
#include <net/if.h>
#include <arpa/inet.h>
#include <pthread.h>
#define PORT 12123

using namespace std;

// Global to be used across all funtions, if needed.
mutex gard_file;
int tempFD;
map<string, int> fdMap;


// Command controll
string cmdLine, fileWorker, fileIP, fileCMD, fileValues;
string nowP, gotFromClient, nowG;
stringstream ss;
  

// TCP/IP
int localFD; // Returned fd from map
char buffer[1024] = {0};
int clientReceiver;
int *threadedFD;
pthread_t myThread;
pthread_t myThread2;

int tcpMaker(); // It could take a port number as argument
void populateMap(int fd);
void *threadedClient(void *new_socket);
void *threadedPartser(void *some);

//void threadedClient(int new_fd);
//void threadedPartser();

int main(){
  
  system("touch workfile.txt");

  int server_fd, new_socket;
  struct sockaddr_in address;
  int addrlen = sizeof(address);  
  
  // This fd is the one that the server will bind to..
  if( (server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0 ){
    perror("Could Not Create Socket!");
    exit(EXIT_FAILURE);
  }
  
  address.sin_family = AF_INET;
  address.sin_addr.s_addr = INADDR_ANY;
  address.sin_port = htons( PORT );
  
  if( bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0 ){
    perror("Could Not Bind!");
    exit(EXIT_FAILURE);
  }
  
  listen(server_fd, 5); 
  int t;
  while(true){
    while( tempFD = accept(server_fd, (struct sockaddr *)&address, (socklen_t*)&addrlen)){
      
      if(tempFD < 0)
	break;
    
      populateMap(tempFD);
      
      cout << "New Client Was Connected" << endl;
      
      t = pthread_create(&myThread, NULL, &threadedClient, (void *)&tempFD);
      if(t != 0){
	perror("Unable to Create Client's Thread!");
	return 1;
      }
      
      
       
      t = pthread_create(&myThread2, NULL, &threadedPartser, (void *)&t);
      if(t != 0 ){
	perror("Unable to Create Parser's Thread!");
	return 1;
       }
      

      
      pthread_join( myThread, NULL);
      pthread_join( myThread2, NULL); 
      
    }
  }
  
  
  return 0;
  
  
}

void populateMap(int fd){

  struct sockaddr_in cliAddress;
  socklen_t addressSize = sizeof(struct sockaddr_in);
  int temp;
  char *clientIP = new char[20];
  
  temp = getpeername(fd, (struct sockaddr *)&cliAddress, &addressSize);
  strcpy( clientIP, inet_ntoa(cliAddress.sin_addr) );
  
  fdMap.insert(pair<string, int>(clientIP, fd));

  // C++ file handling stile
  ofstream file_cout;
  file_cout.open("workfile.txt", ios_base::app);
  file_cout << "G " << clientIP << " ADD 00000000" << endl;
  
  file_cout << "S " << clientIP << " SET AABBCCDD" << endl; //For Testing Only
  file_cout << "P " << clientIP << " SET AABBCCDD" << endl; //For Testing Only
  file_cout << "S " << clientIP << " SET AABBCCDD" << endl; //For Testing Only

  file_cout.close();

  
  /******************************************/
  /*
  //A map-type variable
  map<string, int>::iterator i;
  cout << "fdMap contains:\n";
  for (i=fdMap.begin(); i!=fdMap.end(); i++){
  cout << i->first << " => " << i->second << '\n';
  }
  */
  

}



 void *threadedClient(void *cliFD){
 
   //Redundant, but, Oh well..
    int new_fd = *(int *)cliFD;
   //int msgSize;
   char msg[1024] = {0};
   
   //Initial COnnections....
   read(new_fd, msg, sizeof(msg));
   cout << "Client wrote: " << buffer << endl;
   send(new_fd, msg, sizeof(msg), 0);
   
   //populateMap(new_fd);


   //pthread_exit(NULL);
 }


void *threadedPartser(void *NOTING){
  
  //threadedPartser(NULL);
  
  nowP = "P";
  nowG = "G";
  gotFromClient = "AACCDDFF";
 
  system("touch tempWF");
  
  fstream cmdFile("workfile.txt");
  while(getline(cmdFile, cmdLine)){ // Read file untill EOF
    
    if(cmdLine[0] != 'S'){
      string strTemp1 = "echo '" + cmdLine + "' >> tempWF";
      const char *sysTemp = strTemp1.c_str(); // Converts from C++ string to C char []
      system(sysTemp); // Append the string to that file..
    }
    
    // We only care for Server commands:
    if(cmdLine[0] == 'S'){
      ss.clear();
      ss << cmdLine;
      ss >> fileWorker >> fileIP >> fileCMD >> fileValues;
      
      // Lets handle all commands:
      if(fileCMD == "SET"){
	string clientMSG = "";
	clientMSG = fileCMD + " " + fileValues;
	
	//Lets get the fd from our map
	map<string, int>::iterator fd;
	
	if(fd != fdMap.end())
	  localFD =  fdMap.find(fileIP)->second;
	
	int response = 0;
	while(response <= 0){
	  send(localFD, clientMSG.c_str(), sizeof(clientMSG), 0);
	  response = read(localFD, buffer, sizeof(buffer));
	  
	  // We need to send over and over again until client has sent a value > 0
	  // The client should always reply with 1 or greater on seccess or <= 0 when fails 
	}
	
	
	// The command has been successfully processed.
	cmdLine = nowP + " " + fileIP + " " + fileCMD + " " + fileValues;
	string strTemp2 = "echo '" + cmdLine + "' >> tempWF";
	const char *sysTemp2 = strTemp2.c_str();
	system(sysTemp2);
      }
      
      else if(fileCMD == "GET"){
	string clientMSG = "";
	clientMSG = fileCMD;
	//Lets get the fd from our map
	map<string, int>::iterator fd;
	
	if(fd != fdMap.end())
	  localFD =  fdMap.find(fileIP)->second;
	
	int response = 0;
	while(response <= 0){
	  send(localFD, clientMSG.c_str(), sizeof(clientMSG), 0);
	  response = read(localFD, buffer, sizeof(buffer));
	  
	  // We need to send over and over again until client has sent a value > 0
	  // The client should always reply with 1 or greater on seccess or <= 0 when fails 
	}
	
	
	clientReceiver = read(localFD, buffer, sizeof(buffer));
	
	cmdLine = nowG + " " + fileIP + " " + fileCMD + " " + buffer;
	cout << "----> " <<cmdLine << endl;
	string strTemp3 = "echo '" + cmdLine + "' >> tempWF";
	const char *sysTemp3 = strTemp3.c_str();
	system(sysTemp3);
      }
      else{
	string strTemp4 = "echo '" + cmdLine + "' >> tempWF";
	const char *sysTemp4 = strTemp4.c_str();
	system(sysTemp4);
      }
    }// if 'S'
  }// reading file
  
  //Make sure we have control of the file before we update it.
  gard_file.lock();
  system("cat tempWF > workfile.txt ; rm tempWF");
  gard_file.unlock();
  
  sleep(5);
  cmdFile.close();
  
  //threadedPartser(NULL);
  
}


// Usage: g++ -g -std=c++11 serverAndParcer.c++ -o server
// Run: ./server

#include <iostream>
#include <cstdlib> //system()
#include <fstream> // FILE IO
#include <sstream>
#include <string>
#include <mutex>
#include <map>


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
#define PORT 9999

using namespace std;

// Global to be used across all funtions, if needed.
mutex gard_file;
int tempFD;
map<string, int> fdMap;


int tcpMaker(); // It could take a port number as argument
void populateMap(int fd);

int main(){
  
  // Command controll
  system("touch workfile.txt");
  string cmdLine, fileWorker, fileIP, fileCMD, fileValues;
  string nowP, gotFromClient, nowG;
  nowP = "P";
  nowG = "G";
  gotFromClient = "AACCDDFF";
  stringstream ss;
  

  // TCP/IP
  int localFD; // Returned fd from map
  char buffer[1024] = {0};
  int clientReceiver;
  
  
  tempFD = tcpMaker();
  cout << "New Client Was Connected" << endl;
  read(tempFD, buffer, sizeof(buffer));
  cout << "Client wrote: " << buffer << endl;
  send(tempFD, buffer, sizeof(buffer), 0);

  populateMap(tempFD);
  
  //A map-type variable
  map<string, int>::iterator i;
  cout << "fdMap contains:\n";
  for (i=fdMap.begin(); i!=fdMap.end(); i++){
    cout << i->first << " => " << i->second << '\n';
  }
  
  sleep(2);
  
  fstream cmdFile("workfile.txt");
  while(getline(cmdFile, cmdLine)){ // Read file untill EOF
    
    //Lets create a temp work file.
    ifstream ifile("tempWF");
    if (ifile) {
      if(cmdLine[0] != 'S'){
	string strTemp1 = "echo '" + cmdLine + "' >> tempWF";
	const char *sysTemp = strTemp1.c_str(); // Converts C++ string to C string aka char []
	system(sysTemp);
      }
    }
    else{
      //The file doesnt exit
      system("touch tempWF");
      if(cmdLine[0] != 'S'){
	string strTemp1 = "echo '" + cmdLine + "' >> tempWF";
	const char *sysTemp = strTemp1.c_str(); // Converts from C++ string to C char []
      	system(sysTemp); // Append the string to that file..
      }
    }//file exists now

    
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
  
  
  //end of some function that does all of above
  
  return 0;
  
  
}


// SERVER...
int  tcpMaker(){
  
  int server_fd, new_socket;
  struct sockaddr_in address;
  int addrlen = sizeof(address);  
    
  // This fd is the one that the server will bind to..
  if( (server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0 ){
    perror("Could Not Create Socket!\n");
    exit(EXIT_FAILURE);
  }
    
  address.sin_family = AF_INET;
  address.sin_addr.s_addr = INADDR_ANY;
  address.sin_port = htons( PORT );
  
  if( bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0 ){
    perror("Could Not Bind!\n");
    exit(EXIT_FAILURE);
  }
  
  listen(server_fd, 5); 
  
  
  if( (new_socket = accept(server_fd, (struct sockaddr *)&address, (socklen_t*)&addrlen)) < 0 ){
    perror("Unable To Stablish Connection!\n");
      exit(EXIT_FAILURE);
  }
  
  return new_socket;
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

  file_cout.close();
}

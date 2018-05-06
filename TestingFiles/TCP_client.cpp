// Compiles as: g++ -g -std=c++11 TCP_client.cpp -o Cli
// Skeleton Code for Jack's TCP client requirement, Jorge's OLA, and Taylors sensor

#include <string>
#include <sstream>
#include <iostream>
#include <stdlib.h>
#include <time.h>
#include <stdio.h>
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

#include <ola/DmxBuffer.h>
#include <ola/Logging.h>
#include <ola/client/StreamingClient.h>


#define port 9999
#define buff 128
using namespace std;


//Prototypes
int sendOLA(int, int, int, int);


int main() 
{
  
  int socket;
  char recv_data[buff];
  struct hostent *host;
  struct sockaddr_in server_addr;
  
  host = gethostbyname("127.0.0.1");
  socket = socket(AF_INET, SOCK_STREAM,0);
  server_addr.sin_family = AF_INET;
  server_addr.sin_port = htons(port);
  server_addr.sin_addr = *((struct in_addr *)host->h_addr);
  
  
  if(connect(socket, (struct sockaddr *)&server_addr,sizeof(struct sockaddr)) <0);  //connect to server
  {
    perror("Error: Failed to connect");
    exit(EXIT_FAILURE);
  }
  cout << "Connection made" << endl;
	
  
  while(true)  //Run forever
    {
      sleep(3000); // wait 3 seconds for avoid network conjection
      recv(socket, recv_data, buff, 0);
      cout << "Server says: " << recv_data << endl;
      string  server = recv_data;
      stringstream ss(server);
      ss >> CMD >> DATA;
      
      
      if(CMD == "SET") //server sending GUI CR values or user defined values
	{
	  cout << "Settin lights to :" << DATA << endl;

	  /************* DO NOT EDIT *****************/
	  string A, R, G, B, OLA;
	  unsigned int Ai, Ri, Gi, Bi;
	  char ack;
	  const char *OLAFailure;
	  
	  A = DATA.substr(0, 2); 
	  R = DATA.substr(2, 2); 
	  G = DATA.substr(4, 2); 
	  B = DATA.substr(6, 7); 
	  
	  ss.clear();
	  
	  ss << hex << A << " " <<  hex << B << " " <<  hex << G <<" " << hex << B;
	  ss >> Ai >> Ri >> Gi >> Bi;
	  cout <<"Int Equivalent: " << Ai <<" " <<  Ri << " " <<  Gi << " " <<  Bi << endl;
	  
	  try{
	    ack = sendOLA(Ai, Ri, Gi, Bi);
	    send(socket, ack, sizeof(ack), 0);
	  }
	  catch( OLAFailure ){
	    strcpy(OLAFailure, ack);
	    send(socket, OLAFailure, sizeof(OLAFailure), 0);
	  }
	  
	  ss.clear();
	  /************* DO NOT EDIT *****************/
	}
      
      else if(CMD == "GET")  //server fetching client sensor values for GUI request
	{ 
	  cout << "Send To Server :" << sensor_data << endl;
	  send(socket, sensor_data.c_str(), sizeof(sensor_data) + 1, 0);
	  //TODO: Work your sensor magic here as needed
	}
      else if(CMD == "PING")  //echo when server checks that client is still connected
	{ 
	  cout << "Send To Server :" << CMD << endl;
	  send(socket, CMD.c_str(), sizeof(CMD) + 1, 0);
	  //This is so the server can keep track of connected clients, please keep and expand on
	}
      //else if( CMD == "TST") //In case we want to add a test function, still pending
      
    }
  
  return 0; 
}


char sendOLA(int olaA, int olaR, int olaG, int olaB){
  
  //OLA
  unsigned int universe = 1;
  ola::DmxBuffer buffer; // A DmxBuffer to hold the data.
  ola::client::StreamingClient ola_client((ola::client::StreamingClient::Options()));
  
  if (!ola_client.Setup()){
    cerr << "Setup failed" << endl;
    return '-1';
  }
  
  buffer.SetChannel(0, olaA); // Intensity or Alpha
  buffer.SetChannel(1, olaR); // Red
  buffer.SetChannel(2, olaG); // Green
  buffer.SetChannel(3, olaB); // Blue
  
  if (!ola_client.SendDmx(universe, buffer)){
    //cout << "Send DMX failed" << endl;
    return '-1';
  }
  
  //cout << "\nColor Sent!\n";
  return '1';
}


//Regular stuff

#include <stdlib.h>
#include <iostream>
#include <time.h>
#include <string>
#include <sstream>

//OLA

#include <ola/DmxBuffer.h>
#include <ola/Logging.h>
#include <ola/client/StreamingClient.h>

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


using namespace std;


void sendOLA(int, int, int, int);

int main(int, char *[]) {

  //Sockets
  
  int sock;
  char send_data[1024], recv_data[1024];
  struct hostent *host;
  struct sockaddr_in server_addr;
  
  //host = gethostbyname("192.168.1.12"); FOR OUR NETWORK
  host = gethostbyname("127.0.0.0");
  sock = socket(AF_INET, SOCK_STREAM,0);
  server_addr.sin_family = AF_INET;
  //server_addr.sin_port = htons(6454); FOR OUR NETWORK
  server_addr.sin_port = htons(9999);
  server_addr.sin_addr = *((struct in_addr *)host->h_addr);
  bzero(&(server_addr.sin_zero), 8);


  /*Connects to Server*/

  int conned;
  conned = connect(sock, (struct sockaddr *)&server_addr,sizeof(struct sockaddr));
  if(conned == 0){
    puts("Connection Created");
  }
  

  /*Handle incomming commands*/

  string serverCMD;
  string executeCMD;
  string tempSTR, x;
  string serverVals;
  string serverTemp;
  int rgbVals[4];
  
  
  string::size_type base16; //The base to convert to
  while(true){

    *recv_data = '\0';
    
    printf("\nSend To Server :");
    fgets(send_data, 1040, stdin);
    
    write(sock, send_data, strlen(send_data));
    
    
    recv(sock, recv_data, 1024, 0);
    cout << "\nData From Server = " << recv_data << " .\n";
    
    serverCMD = recv_data;
    stringstream ss(serverCMD);
    
    ss >> executeCMD;
    
    cout << "---> " << executeCMD << endl;
    
    if(executeCMD == "SET"){
      
      ss >> serverVals;
      
      int flag = 1; //Control of index
      for(int i = 0; i < serverVals.length(); (i+=2)){
	if(i == 0){
	  serverTemp = (serverVals.substr(i, 2));
	  rgbVals[i] = stoi(serverTemp, &base16, 16);
	}
	
	else{
	  serverTemp = (serverVals.substr(i, 2));
	  rgbVals[i-flag] = stoi(serverTemp, &base16, 16);
	  flag++;
	}
	
      }

      /*Send the payload*/
      
      sendOLA(rgbVals[0], rgbVals[1], rgbVals[2], rgbVals[3]);
      
    }

    else if(executeCMD == "GET"){
      /*Taylor, get the sensor values from here. and send back to the server*/
      /*write(socket, sensor_values_or_variable, sizeof_data)*/
    }

    else
      /*We did not got a SET nor a GET request from server*/
      /*echo "What was that?"*/
  }
  
    
  return 0;
}


void sendOLA(int olaA, int olaR, int olaG, int olaB){
  
  //OLA
  
  unsigned int universe = 1; 
  ola::DmxBuffer buffer; // A DmxBuffer to hold the data.
  ola::client::StreamingClient ola_client((ola::client::StreamingClient::Options()));
  
  if (!ola_client.Setup()) {
    cerr << "Setup failed" << endl;
    exit(1);
  }
  
  buffer.SetChannel(0, olaA); // Intensity or Alpha
  buffer.SetChannel(1, olaR); // Red
  buffer.SetChannel(2, olaG); // Green
  buffer.SetChannel(3, olaB); // Blue
  
  if (!ola_client.SendDmx(universe, buffer)) {
    cout << "Send DMX failed" << endl;
    exit(1);
  }
  
  cout << "\nColor Sent!\n";
  
}


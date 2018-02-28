//Regular stuff

#include <stdlib.h>
//#include <iostream>
#include <time.h>
#include <string>
#include <sstream>
#include <stdio.h>
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

//Sensor & timer
#include <signal.h>
#include <linux/i2c-dev.h>
#include <sys/ioctl.h>
#include <fcntl.h>



using namespace std;

int file;

//char aRGB[50];

void sendOLA(int, int, int, int);

int main(int, char *[]) {

  //Sockets
  
  int sock, bytes_recieved;
  char send_data[1024], recv_data[1024];
  struct hostent *host;
  struct sockaddr_in server_addr;

  //host = gethostbyname("192.168.1.12"); FOR OUR NETWORK
  host = gethostbyname("127.0.0.1");
  sock = socket(AF_INET, SOCK_STREAM,0);
  server_addr.sin_family = AF_INET;
  //server_addr.sin_port = htons(6454); FOR OUR NETWORK
  server_addr.sin_port = htons(5000);
  server_addr.sin_addr = *((struct in_addr *)host->h_addr);
  bzero(&(server_addr.sin_zero), 8);

  connect(sock, (struct sockaddr *)&server_addr,sizeof(struct sockaddr));

  string serverCMD;
  string executeCMD;
  string tempSTR, x;

  string A,  R, G, B;
  std::string::size_type baseN;

//Once connection is made start getting data

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

  while(true){
    
    recv(sock, recv_data, 1024, 0);
       
    //cout << "\nData From Server = " << recv_data << " .\n";

    serverCMD = recv_data;

    stringstream ss(serverCMD);
    
    ss >> executeCMD;
    
    //cout << "---> " << executeCMD << endl;
    
    if(executeCMD == "ARGB"){

      ss >> A >> R >> G >> B;
      int olaA = stoi(A, &baseN);
      //cout << olaA << endl;

      int olaR = stoi(R, &baseN);
      //cout << olaR << endl;

      int olaG = stoi(G, &baseN);
      //cout << olaG << endl;

      int olaB = stoi(B, &baseN);
      //cout << olaB << endl;
      
      sendOLA(olaA, olaR, olaG, olaB);
    }

        
    *recv_data = '\0';
    
    printf("\nSend To Server :");
    
    fgets(send_data, 1040, stdin);
    
    write(sock, send_data, strlen(send_data));
    
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
    //cout << "Send DMX failed" << endl;
    exit(1);
  }
  
  //cout << "\nColor Sent!\n";
  
}

void display_RGB(int s) {
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


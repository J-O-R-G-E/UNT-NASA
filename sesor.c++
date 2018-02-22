//MADE BY TAYLOR

#include <stdio.h>
#include <signal.h>
#include <unistd.h>
#include <linux/i2c-dev.h>
#include <sys/ioctl.h>
#include <fcntl.h>
#include <sstream>
#include <iostream>
#include <string>
#include <stdlib.h>

using namespace std;

int file;

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

      //cout <<std::uppercase << std::hex << luminance << " " <<std::uppercase << std::hex << red << " " <<std::uppercase << std::hex << green << " " <<std::uppercase << std::hex << blue << endl;
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

int main(void) {
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



  int n = 0;
  while (1) {
    ++n;
  }
  return 0;
}

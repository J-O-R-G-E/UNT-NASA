	/**
	   By Jorge Cardona
	   jac0656@unt.edu

	   Compiles with: g++ testDMX512.c++ dmx512.c++ $(pkg-config --cflags --libs libola) -std=c++11 -Wall
	   Here testDMX.c++ is a file that includes this library
	*/


	#include <iostream>
	#include <string>
	#include <sstream>
	#include <fstream>
	#include <vector>
	#include <ctype.h> //isxdigit()
	#include <unistd.h> //sleep

	#include "dmx512.hpp"

	//OLA

	#include <ola/DmxBuffer.h>
	#include <ola/Logging.h>
	#include <ola/client/StreamingClient.h>

	///Constructor. It checks that OLA is up and running. If not, it brings it back up.
	DMX512::DMX512(){

	  // Lets make sure OLA is up and running
	  std::string line = "";
	  std::string line2 = "";
	  std::string lines;
	  std::vector<std::string> i;
	  std::vector<std::string> usb;

	  system("pidof olad  > tempFile-1");

	  //  Check to see if the USB is on
	  system("lsusb | grep 'Future Technology Devices International, Ltd FT232 USB-Serial (UART) IC' > usbFlag");

	  std::ifstream fd("tempFile-1");
	  if(!fd)
	    std::cerr << "CANT OPEN FILE\n";

	  while(std::getline(fd, line)){
	    i.push_back(line);
	  }

	  std::ifstream fd2("usbFlag");
	  if(!fd2)
	    std::cerr << "CANT OPEN FILE\n";

	  while(std::getline(fd2, line2)){
	    usb.push_back(line2);
	  }

	  // If OLA went down, it is not run  by root anymore.
	  if(i.size() <= 0){
	    std::cout << "\n\nOLA IS DOWN\n\n";

	    system("sudo ola_dev_info > /dev/null 2>&1 &");
	    for(int i=0; i<10; i++){
	      std::cout << "\nOLA is Starting Up..";
	      sleep(1);
	    }

	  // FTDI USB was removed....	
	  if(usb.size() <= 0){

	    system("sudo kill -9 $(pidof olad)");	  
	    system("sudo ola_dev_info > /dev/null 2>&1 &");
	    for(int i=0; i<10; i++){
	      std::cout << "\nReconnecting USB and Restarting OLA..";
	      sleep(1);
	    }

	    system("ola_patch -d 8 -p 1 -u 1 > /dev/null 2>&1 &");
	    system("ola_patch -d 2 -p 1 -u 1 > /dev/null 2>&1 &");	  
	    std::cout << "Sending dummy data 2:\n";
	    system("ola_streaming_client  -u 1 -d 1,2,255,255 > /dev/null 2>&1 &");
	    sleep(1);
	  }

	    std::cout << "\nPatching device 2's port 1 to Universe 1\n";
	    std::cout << "\tdevice 2 is our FTDI USB Adapter\n";
	    std::cout << "\tsee ola_dev_info\n";
	    sleep(3);
	    system("ola_patch -d 2 -p 1 -u 1 > /dev/null 2>&1 &");
	    system("ola_patch -d 8 -p 1 -u 1 > /dev/null 2>&1 &");

	    std::cout << "Sending dummy data 1:\n";
	    system("ola_streaming_client  -u 1 -d 1,2,255,255 > /dev/null 2>&1 &");
	    sleep(2);	  

	  }// END OF OLA DOWN
	  else{
	    system("sudo ola_dev_info > /dev/null 2>&1 &");
	    system("ola_patch -d 2 -p 1 -u 1 > /dev/null 2>&1 &");
	    system("ola_patch -d 8 -p 1 -u 1 > /dev/null 2>&1 &");
	    //std::cout << "OLA IS UP\n";
	  }

	  system("rm tempFile-1 usbFlag");
	  std::cout << "OLA IS UP\n";

	}


	/// This method acts as flag to ensure we got 8 character.
	void DMX512::setOutOfRange(int i ){
	  outOfRange = i;
	}

	/// This method gets called after the data has been processed
	int DMX512::getOutOfRange( ){
	  return outOfRange;
	}


	/** This method splits the string of data received from the server 
	    into 4 pieces that will become Alpha or intensity, Red, Gree, and Blue
	*/
	void DMX512::setData(std::string DATA){
	  try{
	    A = DATA.substr(0, 2);
	    R = DATA.substr(2, 2);
	    G = DATA.substr(4, 2);
	    B = DATA.substr(6, 7);
	  }
	  catch(std::out_of_range ){
	    A = "00";
	    R = "00";
	    G = "00";
	    B = "00";

	    setOutOfRange(1);
	  }

	  //std::cout << A << R << G << B << std::endl;
	  clientHandler();
	}

	/// This method converts the HEX value to INT
	void DMX512::clientHandler(){

	  std::stringstream ssOLA;
	  ssOLA.clear();
	  ssOLA << std::hex << A << " " <<  std::hex << R << " " <<  std::hex << G <<" " << std::hex << B;
	  ssOLA >> Ai >> Ri >> Gi >> Bi;
	  /// Since we are having some flickering issue, let's avoid that range. Usually (120 - 220)
	  ( Ai <= 110) ? Ai = Ai : Ai = 255;

	  std::cout <<"Int Equivalent: " << Ai <<"*  " <<  Ri << " " <<  Gi << " " <<  Bi << std::endl;
	  /**
	     A similar implementation will be:
	     std::stringstream ssOLA;
	     ssOLA.clear();
	     ssOLA << stoi(A.c_str(), nullptr, 16) << " " << stoi(R.c_str(), nullptr, 16) << " " <<  stoi(G.c_str(), nullptr, 16)  <<" " << stoi(B.c_str(), nullptr, 16);
	     ssOLA >> Ai >> Ri >> Gi >> Bi;

	     OR:
	     Ai = stoi(A.c_str(), nullptr, 16);
	     Ri = stoi(R.c_str(), nullptr, 16);
	     Gi = stoi(G.c_str(), nullptr, 16);
	     Bi = stoi(B.c_str(), nullptr, 16);
	  */

	}


	/** This method will get called one last time before we attemp to send our values 
	    to the LED lights in the event that OLA went down while we were processing the data */
	void DMX512::checkOLA(){

	  std::string line = "";
	  std::string line2 = "";
	  std::vector<std::string> i;
	  std::vector<std::string> usb;
	  system("pidof olad  > tempFile-1");
	  system("lsusb | grep 'Future Technology Devices International, Ltd FT232 USB-Serial (UART) IC' > usbFlag");

	  std::ifstream fd("tempFile-1");
	  if(!fd)
	    std::cerr << "CANT OPEN FILE\n";
	  while(std::getline(fd, line)){
	    i.push_back(line);
	  }

	  std::ifstream fd2("usbFlag");
	  if(!fd2)
	    std::cerr << "CANT OPEN FILE\n";
	  while(std::getline(fd2, line2)){
	    usb.push_back(line2);
	  }

	  // FTDI USB was removed....	
	  if(usb.size() <= 0){

	    system("sudo kill -9 $(pidof olad)");	  
	    system("sudo ola_dev_info > /dev/null 2>&1 &");

	    for(int i=0; i<10; i++){
	      std::cout << "\nReconnecting USB and Restarting OLA..";
	      sleep(1);
	    }

	    system("ola_patch -d 8 -p 1 -u 1 > /dev/null 2>&1 &");
	    system("ola_patch -d 2 -p 1 -u 1 > /dev/null 2>&1 &");	  
	    std::cout << "Sending dummy data 2:\n";
	    system("ola_streaming_client  -u 1 -d 1,2,255,255 > /dev/null 2>&1 &");
	    sleep(1);
	  }

	  if(i.size() <= 0){
	    std::cout << "\n\nOLA IS DOWN\n\n";
	    //system("sudo olad -l 4 > /dev/null 2>&1 &");
	    //system("sudo ola_dev_info > /dev/null 2>&1 &");
	    //system("ola_patch -d 2 -p 1 -u 1 > /dev/null 2>&1 &"); 
	    //system("ola_streaming_client  -u 1 -d 1,2,255,255 > /dev/null 2>&1 &");


	    // FTDI falls to this device when OLA recovers or if the USB was unpluged
	    system("sudo ola_dev_info > /dev/null 2>&1 &");
	    system("ola_patch -d 8 -p 1 -u 1 > /dev/null 2>&1 &");
	    system("ola_streaming_client  -u 1 -d 1,2,255,255 > /dev/null 2>&1 &");
	    sleep(1);
	  }
	  else
	    std::cout << "OLA IS UP\n";
	  system("rm tempFile-1 usbFlag");
	}


	/** This is the method that sends the data through the FTDI USB to the LED Light. 
	    Return types:
		1 OLA Success
		-1 OLA Failure
		-2 Wrong Data Type
		-3 Empty String
	*/
	std::string  DMX512::sendOLA(){

	  /// This is the univer ID when the universe was created
	  unsigned int universe = 1;

	  /// A DmxBuffer to hold the ARGB values.
	  ola::DmxBuffer buffer;

	  /// This object makes the connection to the OLA server
	  ola::client::StreamingClient ola_client((ola::client::StreamingClient::Options()));


	  /** Because we want to avoid errors, lets check each character
	      by making sure it is a HEX value
	   */
	  int temp = 0;
	  OLA = A+R+G+B;
	  std::vector<char> cDATA(OLA.c_str(), OLA.c_str() +(OLA.size()));

	  //Syntesize data
	  for (auto i: cDATA){ //C++11 for range
	    std::cout << i << ' ';
	    if(isxdigit(i) == 0){
	      std::cout << "Wrong data type at possition: " << temp<< "\n";
	      return "-2";
	    }
	    temp += 1;
	  }

	  if (temp > 0){
	    std::cout << "Data processed\n";
	    temp = 0;
	  }

	  // In case it went down while we are running...
	  checkOLA();

	  if (!ola_client.Setup()){
	    std::cerr << "Setup failed" << std::endl;
	    return "-1";
	  }


	  /** This is very important. It must match the values given to the LED light
	      using the dip switch selector. Even if eveything, softwarewise, is working,
	      it will be impossible to get correct outout if these dont match
	      NOTE:
		 In this case, the dip switch is set to 1 or 'listening' on chanel 1 aka 0
	  */
	  buffer.SetChannel(0, Ai); // Intensity or Alpha
	  buffer.SetChannel(1, Ri); // Red
	  buffer.SetChannel(2, Gi); // Green
	  buffer.SetChannel(3, Bi); // Blue                                                                                                                                         

	  if(!ola_client.SendDmx(universe, buffer)){
	    return "-1";
	  }

	  //std::cout << "\nColor Sent!\n\n";
	  std::cout << "DMX512: "<< Ai <<" " <<  Ri <<  " " << Gi << " " << Bi <<std::endl;


	  /// If this is true, the light got all 0s
	  if(getOutOfRange()){
	    setOutOfRange(0);
	    return "-3";
	  }

	  return "1";
	}

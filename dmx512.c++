#include <iostream>
#include <string>
#include <sstream>
#include "dmx512.hpp"

//OLA

#include <ola/DmxBuffer.h>
#include <ola/Logging.h>
#include <ola/client/StreamingClient.h>


DMX512::DMX512(std::string DATA){
  A = DATA.substr(0, 2);
  R = DATA.substr(2, 2);
  G = DATA.substr(4, 2);
  B = DATA.substr(6, 7);
  
  clientHandler();
  
}


void DMX512::clientHandler(){
  std::stringstream ssOLA;
  ssOLA.clear();
  ssOLA << std::hex << A << " " <<  std::hex << B << " " <<  std::hex << G <<" " << std::hex << B;
  ssOLA >> Ai >> Ri >> Gi >> Bi;
  //std::cout <<"Int Equivalent: " << Ai <<" " <<  Ri << " " <<  Gi << " " <<  Bi << std::endl;
  
}


char DMX512::sendOLA(){
  unsigned int universe = 1;
  
  ola::DmxBuffer buffer; // A DmxBuffer to hold the data.
  ola::client::StreamingClient ola_client((ola::client::StreamingClient::Options()));
  
  if (!ola_client.Setup()){
    cerr << "Setup failed" << endl;
    return '-1';
  }
  
  buffer.SetChannel(0, Ai); // Intensity or Alpha
  buffer.SetChannel(1, Ri); // Red
  buffer.SetChannel(2, Gi); // Green
  buffer.SetChannel(3, Bi); // Blue                                                                                                                                         
  if (!ola_client.SendDmx(universe, buffer)){
    //cout << "Send DMX failed" << endl;
    return '-1';
  }
  
  
  std::cout << "\nColor Sent!\n";
  std::cout <<  std::endl;
  std::cout << Ai << " " << " " <<  Ri <<  " " << Gi << " " << Bi <<std::endl;
  return '1';
}


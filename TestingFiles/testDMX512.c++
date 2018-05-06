// Compiles with: g++ testDMX512.c++ dmx512.c++ $(pkg-config --cflags --libs libola) -std=c++11

#include <iostream>
#include <string>
#include <unistd.h> //Sleep
#include "dmx512.hpp"

using namespace std;

int main(){


  // This value will be from:
  // ss >> CMD  >> DATA;
  // on the Client side
  string DATA = "64646464"; //100, 100, 100, 100
  string olaBuffer;
    
  // Create an Object
  DMX512 obj;

  //Test Case #1
  cout << "Sending valid data...\n";
  obj.setData(DATA);
  olaBuffer =  obj.sendOLA();
  cout <<"Returned: " << olaBuffer << endl;
  sleep(5);


  //Test Case #2
  cout << "\nTrying to send invalid data...\n";
  DATA = "LWQDSAOR";
  obj.setData(DATA);
  olaBuffer =  obj.sendOLA();
  cout <<"Returned: " << olaBuffer << endl;
  sleep(5);


  //Test Case #3
  cout << "\nTrying to sen not data at all...\n";
  DATA = "";
  obj.setData(DATA);
  olaBuffer =  obj.sendOLA();
  cout <<"Returned: " << olaBuffer << endl;
  sleep(5);


  //Test Case #4
  cout << "\nTrying to send semi-incomplete data...\n";
  DATA = "ff0f0f";
  obj.setData(DATA);
  olaBuffer =  obj.sendOLA();
  cout <<"Returned: " << olaBuffer << endl;
  sleep(5);

  
  //Test Case #5
  cout << "\nTrying to send incomplete data...\n";
  DATA = "fff";
  obj.setData(DATA);
  olaBuffer =  obj.sendOLA();
  cout <<"Returned: " << olaBuffer << endl;
  sleep(5);
  

  
  /*
   * NOTE:
   * sendOLA() return 1 on success and less than 0 on failures.
   * 
   * The Client must handle this returned value as:
   * olaBuffer =  obj.sendOLA();
   * send(socket_fd, olaBuffer.c_str(), (olaBuffer.size()+1))
   * 
   * The Server must handle this received value as:
   * buffer = read(...)
   * if(buffer != '1'){
   *    resend or try to find the source of the issue
   * }
   */

  
  return 0;
}

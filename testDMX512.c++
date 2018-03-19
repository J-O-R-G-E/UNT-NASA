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
    
  // Create an Object and pass the ARGB values to it.
  DMX512 obj;
  obj.setData(DATA);


  olaBuffer =  obj.sendOLA();
  cout <<"Returned: " << olaBuffer << endl;

  sleep(2);
  
  cout << "\nTry to Crash it to get and error...\n";
   DATA = "LWQDSAOR";
  obj.setData(DATA);
  
  olaBuffer =  obj.sendOLA();
  cout <<"Returned: " << olaBuffer << endl;

  sleep(2);

  cout << "\nTry to Crash it to get and error 2...\n";
 
  DATA = "";
  obj.setData(DATA);
  
  olaBuffer =  obj.sendOLA();
  cout <<"Returned: " << olaBuffer << endl;


  sleep(2);

  cout << "\nTry to Crash it to get and error 3...\n";
 
  DATA = "ff00ff00";
  obj.setData(DATA);
  
  olaBuffer =  obj.sendOLA();
  cout <<"Returned: " << olaBuffer << endl;




  
  
  return 0;
}

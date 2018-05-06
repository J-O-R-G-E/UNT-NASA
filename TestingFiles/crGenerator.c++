/**
 * By Jorge Cardona
 * jac0656@unt.edu
 *
 * This program takes the CircadianRhythmValuesHEX file
 * and randomly generates to complete command to [0-9] clients
 * and outputs to a file named CR-Values. This file can be added
 * to the work file or to the GUI to silulate C.R. colors.
 *
 * Usage: g++ crGenerator.c++
 *        ./a.out < CircadianRhythmValuesHEX > CR-Values
 */


#include <iostream>
#include <string>
#include <stdlib.h>     /* srand, rand */
#include <time.h>

using namespace std;

int main(){
  
  string color;
  string cmd = "";
  string s = "S ";
  string set = " SET ";
  string ip0 = "192.168.1.100";
  string ip1 = "192.168.1.101";
  string ip2 = "192.168.1.102";
  string ip3 = "192.168.1.103";
  string ip4 = "192.168.1.104";
  string ip5 = "192.168.1.105";
  string ip6 = "192.168.1.106";
  string ip7 = "192.168.1.107";
  string ip8 = "192.168.1.108";
  string ip9 = "192.168.1.109";
  
  // rand
  int i;
  
  srand (time(NULL));
  
  while(cin >> color){

    // Get some rand Number..
    i = rand() % 10;

    // Check what it was and add complete the command
    switch (i){
    case 0:
      cmd = s + ip0 + set + color;
      cout << cmd << endl;
      break;
      
    case 1:
      cmd = s + ip1 + set + color;
      cout << cmd << endl;
      break;
      
    case 2:
      cmd = s + ip2 + set + color;
      cout << cmd << endl;
      break;
      
    case 3:
      cmd = s + ip3 + set + color;
      cout << cmd << endl;
      break;
      
    case 4:
      cmd = s + ip4 + set + color;
      cout << cmd << endl;
      break;
      
    case 5:
      cmd = s + ip5 + set + color;
      cout << cmd << endl;
      break;
      
    case 6:
      cmd = s + ip6 + set + color;
      cout << cmd << endl;
      break;
      
    case 7:
      cmd = s + ip7 + set + color;
      cout << cmd << endl;
      break;
      
    case 8:
      cmd = s + ip8 + set + color;
      cout << cmd << endl;
      break;
      
    defaut :
      cmd = s + ip9 + set + color;
      cout << cmd << endl;
      break;
      
    }// switch
    
  }// WHILE
  
  return 0;
}

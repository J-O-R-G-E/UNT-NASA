#include <iostream>
#include <string>
#include "dmx512.hpp"


using namespace std;

int main(int argc, char *argv[]){
  
  string temp = "aabbccdd";
  DMX512 j(temp);
  char i;
  i = j.sendOLA();
  cout << i << endl;
  
  return 0;
}

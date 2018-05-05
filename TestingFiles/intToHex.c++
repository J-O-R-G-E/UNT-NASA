/**
 * By Jorge Cardona
 * jac0656@unt.edu
 *
 * This program was made to generate the CircadianRhythmValuesHEX file.
 * Usage:
 *      g++ intToHEX.c++ 
 *      ./a.out < rgbValuesINT > CircadianRhythmValuesHEX
 *
 * The rgbValuesINT file was generated using the RGB.jpg image
 * and a Python file that got lost. But all it did was to open
 * an image, the RGB.jpg, and read all pixel values in it
 * and the output was the file rgbValuesINT
 */


#include <iostream>
#include <string>
#include <sstream>

using namespace std;

int main(int argc, char *argv[]){
  
  stringstream ss;
  string color = "ff";
  int red, blue, green;
  string R, G, B;
  
  while(cin >> red >> green >> blue){
    ss << hex << red << " " << hex << green << " " << hex << blue << "\n";
    ss >> hex >> R >> hex >> G >> hex >> B;
    color +=  R +  G + B;
    cout << color << endl;
    
    ss.clear();
    color = "ff";
    R="";
    G="";
    B="";
  } 
  
  
  return 0;
}


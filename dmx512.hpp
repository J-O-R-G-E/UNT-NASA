/**
   By Jorge Cardona
   jac0656@unt.edu
 */

#pragma once
#include <string>


/// This class handles, checks, and processes the data from the server
class DMX512{
  /// private member that acts as a flag for data validation
  int outOfRange = 0;  
public:

  /// When the data is processed, each variable gets its corresponding value
  std::string A, R, G, B, OLA;

  /// When the data has been splited, these variables get the converted HEX value
  unsigned int Ai, Ri, Gi, Bi;

  /// Constructor
  DMX512();

  /// We need to raise a flag if the data is invalid
  void setOutOfRange(int i);

  /// Check that the data was or was not valid
  int getOutOfRange();

  /// This is the only method used in the Client to transfer the data
  void setData(std::string DATA);

  /// This method handles the data received
  void clientHandler();

  /// This method sends the data to the LED lights
  std::string sendOLA();

  /// This method checks that OLA is up. If not, it brings it back up.
  void checkOLA();
};

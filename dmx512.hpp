#pragma once
#include <string>

class DMX512{
public:
  std::string A, R, G, B, OLA;
  unsigned int Ai, Ri, Gi, Bi;
  char *ack;
  const char *OLAFailure;
  
  DMX512(std::string DATA);
  void clientHandler();
  char sendOLA();
};

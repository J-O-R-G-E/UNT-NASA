#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <mutex>


using namespace std;

// Global to be used across all funtions, if needed.

fstream cmdFile("workfile.txt");
mutex gard_file;

int main(){

  // Command controll
  string cmdLine, fileWorker, fileIP, fileCMD, fileValues;

  // Update lines
  string nowP, gotFromClient, nowG;
  nowP = "P";
  nowG = "G";
  gotFromClient = "AACCDDFF"; //Dummy value
  
  // For easy manipulation of each cmdLine
  stringstream ss;
    
  while(getline(cmdFile, cmdLine)){
    
    //Lets creat a temp file.
    ifstream ifile("tempWF");
    if (ifile) {
      if(cmdLine[0] == 'S'){
	//Nothing to do on tempWF File
	int zz=1-1;
      }
      else{
	//The file exists
	string strTemp1 = "echo \"" + cmdLine + "\" >> tempWF";
	const char *sysTemp = strTemp1.c_str(); // Converts c++ string to c string aka char []
   	system(sysTemp);
      }
    }
    else{
      //The file doesnt exit
      system("touch tempWF");
      if(cmdLine[0] == 'S'){
	//Nothing to do on tempWF File
	int zz = 2-2;
      }
      else{
	string strTemp1 = "echo \"" + cmdLine + "\" >> tempWF";
	const char *sysTemp = strTemp1.c_str();
      	system(sysTemp);
      }
    }//file exists now

    
    // We only care for Server commands:
    if(cmdLine[0] == 'S'){
      ss.clear();
      ss << cmdLine;
      ss >> fileWorker >> fileIP >> fileCMD >> fileValues;
      
      // Lets handle all commands:
      if(fileCMD == "SET"){
	cout << "Ok! I need to send to clients: " << fileValues << endl;
	string clientMSG = "";
	clientMSG = fileCMD + " " + fileValues;
	//send(fd, clientMSG);
	cmdLine = nowP + " " + fileIP + " " + fileCMD + " " + fileValues;
	string strTemp2 = "echo \"" + cmdLine + "\" >> tempWF";
	const char *sysTemp2 = strTemp2.c_str();
	system(sysTemp2);
      }

      else if(fileCMD == "GET"){
	cout << "Awesome! I send a sesor request to the Clients!" << endl;
	//send(fd, flieCMD);
	//Wait for the values:
	//gotFromClient = recv(fd, client);
	cmdLine = nowG + " " + fileIP + " " + fileCMD + " " + gotFromClient;
	cout << "----> " <<cmdLine << endl;
	string strTemp3 = "echo \"" + cmdLine + "\" >> tempWF";
	const char *sysTemp3 = strTemp3.c_str();

	//append prossesed command to tempWF File
	system(sysTemp3);
      }
      else{
	string strTemp4 = "echo \"" + cmdLine + "\" >> tempWF";
	const char *sysTemp4 = strTemp4.c_str();
	system(sysTemp4);
      }
    }// if 'S'
  }// reading file
  
  
  cmdFile.close();
    
  //Make sure we have control of the file before we update it.
  gard_file.lock();
  system("cat tempWF > workfile.txt ; rm tempWF");
  gard_file.unlock();
  
  //end of some function that does all of above
  
  return 0;
  
}

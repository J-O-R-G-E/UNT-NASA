import time
import datetime
from os import system


class VoiceToColor(object):
    def __init__(self):
        pass
    
    def processColor(self, color):
        # Get all IP addresses from database.py
        system('sudo arp-scan 192.168.1.0/24 | grep 192  | awk \'{print $1}\' | tail -n +1 > ipOnly')
        
        # Load on the lines into a buffer
        self.file=open("ipOnly","r")
        self.lines=self.file.readlines()
        self.file.close()
        
        # Format for server
        self.counter = 0
        for i in self.lines:
            self.lines[self.counter] = "S %s SET %s %s\n" %(i[:13], color, datetime.datetime.now())
            self.counter += 1
            
        # Write it back to the file
        self.file=open("ipOnly", "w")
        for i in self.lines:
            self.file.write(i)
            
        self.file.close()
            
        # Append it to the wokfile.txt and delete the temp file
        system('cat ipOnly >> workfile.txt ; rm ipOnly')
        
    #Done
#End of class

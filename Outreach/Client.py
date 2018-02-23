#!/usr/bin/env python
"""
Made By jac0656
"""

#import numpy
from array import*
import pickle
import array
#from ola.ClientWrapper import ClientWrapper
from socket import *
from time import sleep

#OLA Variables and Objects
RGB = '0'
dataFromServer = array.array('B')
#wrapper = ClientWrapper()
#client = wrapper.Client()
universe = 1


# Set the socket parameters
#HOST = '192.168.1.NNN'
HOST = "localhost"
PORT = 9999
buf = 4096
address = (HOST, PORT)

# Create socket and Connet to the given PORT and HOST
UDPSock = socket(AF_INET,SOCK_DGRAM)
#UDPSock.bind(address)

def DmxSent(state):
    if not state:
        #wrapper.Stop()
        print("PLACE HOLDER..")
        
def clientToDMX():
            
    global client
    global universe
    global dataFromServer
    global wrapper
    global address
    
    # Send messages
    msg = "Give me RGB"
    
    
    while True:
        print ("About To Send To Server")
        UDPSock.sendto(msg.encode(), address)

        rgbValues, address = UDPSock.recvfrom(buf)
        #print rgbValues
        
        rgbToDMX = pickle.loads(rgbValues)

        #print(rgbToDMX)
        print(rgbToDMX[0])
        print(rgbToDMX[1])
        print(rgbToDMX[2])
        print(rgbToDMX[3])
        
        if not rgbValues:
            print ("No dat`a from server")
            break
        else:
            #print dataFromServer
            sleep(1)


        #client = wrapper.Client()
        #client.SendDmx(universe, rgbToDMX, DmxSent)
        #wrapper.Run()
                
if __name__ == '__main__':
    clientToDMX()

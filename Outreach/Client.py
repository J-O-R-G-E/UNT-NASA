#!/usr/bin/env python
"""
Made By jac0656
"""

#import numpy
from array import*
import pickle
import array
from ola.ClientWrapper import ClientWrapper
from socket import *
from time import sleep
from threading import Thread

#OLA Variables and Objects
RGB = '0'
dataFromServer = array.array('B')
wrapper = ClientWrapper()
client = wrapper.Client()
universe = 1


# Set the socket parameters
HOST = '192.168.1.100'
#HOST = "localhost"
PORT = 9999
buf = 4096
address = (HOST, PORT)


# Create socket and Connet to the given PORT and HOST
UDPSock = socket(AF_INET,SOCK_DGRAM)
#UDPSock.bind(address)

def DmxSent(state):
    if not state:
        wrapper.Stop()
        

def clientToDMX():
    
    global client
    global universe
    global dataFromServer
    global wrapper
    global address

    
    while True:
        while True:
            #Always send INIT vals
            UDPSock.sendto('0110', address)
            while True:
                rgbValues, address = UDPSock.recvfrom(buf)
                if(rgbValues == '0110'):
                    UDPSock.sendto('1001', address)
                else:
                    # Start over
                    break
                rgbValues, address = UDPSock.recvfrom(buf)
                rgbValues, address = UDPSock.recvfrom(buf)
                rgbToDMX = pickle.loads(rgbValues)
                
                if not rgbValues:
                    break
                else:
                    
                    client = wrapper.Client()
                    client.SendDmx(universe, rgbToDMX, DmxSent)
                    
                    # step back once, it should get back to INIT
                    break
                
if __name__ == '__main__':
    clientToDMX()

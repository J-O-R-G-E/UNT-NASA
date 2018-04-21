"""
By Jorge Cardona

PIR sensor, motion sensor.
It uses pin #12 aka GPIO18 aka GPIO_GEN1
When motion is detected, it turns LED on
usin OLA
"""

from __future__ import print_function
from ola.ClientWrapper import ClientWrapper
import array
import sys

import RPi.GPIO as GPIO
from time import sleep

# GPIO Setup
# Use Broadcom
GPIO.setmode(GPIO.BCM)
sensorPin = 21
GPIO.setup(sensorPin, GPIO.IN)

#OLA SETUP
wrapper = None
universe = 1
data = array.array('B')
            
def DmxSent(status):
    if status.Succeeded():
        #print('Success!')  
        pass
    
    global wrapper
    if wrapper:
        wrapper.Stop()
    
    return 
    
def processOLA(flag):
    
    global wrapper
    global universe
    global data
    
    wrapper = ClientWrapper()
    client = wrapper.Client()
    
    if (flag == 1):
        
        data = []
        data = array.array('B')
        data.append(125) #Intencity
        data.append(255) #R
        data.append(255) #G
        data.append(255) #B

        print(data)

        ledON = 0;
        while (ledON < 10): # 10 == 10 SECONDS
            """
            # THIS IS THE AMOUNT OF TIME WE SHOULD WAIT WHEN WE GET MOTION
            # THIS VALUE WILL BE THE VALUE THE LIGHT SHOULD REMAIN ON AFTER
            # MOTION HAS BEEN DETECTED.
            """
            sleep(1)
            client.SendDmx(universe, data, DmxSent)
            wrapper.Run()
            ledON += 1
        
        return
  
    return
    

def sensor():    

    temp = 0
    counter = 0
    while (temp < 5):
        try: 
            print("Attemp: {}".format(temp))
            sleep(1.5)
            
            global sensorPin
            while True:
                try: # Lets attempt to read from sensor..    
                    if GPIO.input(sensorPin): # True when sensor sends a HIGH or 1
                        print("Motion Detected...")
                        processOLA(1)
                        sleep(4)
                except:
                    print("No Motion...")
                    couter += 1
                    if (motionCounter == 120): 
                        processOLA(-1)
        except:
            print("Exception for Atempt: {}".format(temp))
        temp += 1
    #End of while
    GPIO.cleanup() # If we didnt read from sensor, lets clean up our GPIOs
#End of sensor()

if __name__ == '__main__':
    sensor()
    
    

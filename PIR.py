"""
By Jorge Cardona

PIR sensor, motion sensor.
It uses pin #12 aka GPIO18 aka GPIO_GEN1
"""

import RPo.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BCM)

GPIO.setup(18, GPIO.IN)
#GPIO.setup(12, GPIO.IN)

while True: # Use the sensor forerver...
    
    try: # Lets attempt to read from sensor..
        sleep(1.5)
        while True:
            if(GPIO.input(12)): # True when sensor sends a HIGH or 1
                print("Motion Detected...")
                sleep(5)
                
                #Send some OLA light for testing....
                
                sleep(1) 
    except:
        GPIO.cleanup() # If we didnt read from sensor, lets clean up our GPIOs

# Will never reach here....


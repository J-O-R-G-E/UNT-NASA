#!/usr/bin/env python

from __future__ import print_function
import collections
import pyaudio
import snowboydetect
import time
import wave
import os
import logging
from threading import Thread
from processColors import VoiceToColor as SnowBoy

# OLA SET UP
from ola.ClientWrapper import ClientWrapper
import array
import sys
from time import sleep


# Sensor
# GPIO Setup
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
sensorPin = 21
GPIO.setup(sensorPin, GPIO.IN)


# OLA
wrapper = None
universe = 1
dataArr = array.array('B')
dataArr2 = array.array('B')


# Snowboy set up
logging.basicConfig()
logger = logging.getLogger("snowboy")
logger.setLevel(logging.INFO)
TOP_DIR = os.path.dirname(os.path.abspath(__file__))

# These output sounds could be customized. Record your own voice as feedback
RESOURCE_FILE = os.path.join(TOP_DIR, "resources/common.res")
DETECT_DING = os.path.join(TOP_DIR, "resources/ding.wav")
DETECT_DONG = os.path.join(TOP_DIR, "resources/dong.wav")


# This method is the sensor's timer
def olaTimer():
    # OLA
    universe = 1
    wrapper = ClientWrapper()
    client = wrapper.Client()

    dimmer = []
    dimmer = array.array('B')
    dimmer.append(25) #Intencity
    dimmer.append(250) #R
    dimmer.append(250) #G
    dimmer.append(250) #B                                                          
    print("\nDimming Lights To: {}\n".format(dimmer))
    
    client.SendDmx(universe, dimmer, DmxSent)
    wrapper.Run()
    sleep(4)
    
                    
    

# OLA Callback
def DmxSent(status):
    if status.Succeeded():
        print('Success!')
        global wrapper
        wrapper.Stop()


class RingBuffer(object):
    """Ring buffer to hold audio from PortAudio"""
    def __init__(self, size = 4096):
        self._buf = collections.deque(maxlen=size)

    def extend(self, data):
        """Adds data to the end of buffer"""
        self._buf.extend(data)

    def get(self):
        """Retrieves data from the beginning of buffer and clears it"""
        tmp = bytes(bytearray(self._buf))
        self._buf.clear()
        return tmp


def play_audio_file(fname=DETECT_DING):
    ding_wav = wave.open(fname, 'rb')
    ding_data = ding_wav.readframes(ding_wav.getnframes())
    audio = pyaudio.PyAudio()
    stream_out = audio.open(
        format=audio.get_format_from_width(ding_wav.getsampwidth()),
        channels=ding_wav.getnchannels(),
        rate=ding_wav.getframerate(), input=False, output=True)
    stream_out.start_stream()
    stream_out.write(ding_data)
    time.sleep(0.2)
    stream_out.stop_stream()
    stream_out.close()
    audio.terminate()
    

# Here is where the magic happens
class HotwordDetector(object):
    
    def __init__(self, decoder_model,
                 resource=RESOURCE_FILE,
                 sensitivity=[],
                 audio_gain=1):

        def audio_callback(in_data, frame_count, time_info, status):
            self.ring_buffer.extend(in_data)
            play_data = chr(0) * len(in_data)
            return play_data, pyaudio.paContinue

        
        tm = type(decoder_model)
        ts = type(sensitivity)
        if tm is not list:
            decoder_model = [decoder_model]
        if ts is not list:
            sensitivity = [sensitivity]
        model_str = ",".join(decoder_model)
        
        self.detector = snowboydetect.SnowboyDetect(
            resource_filename=resource.encode(), model_str=model_str.encode())
        self.detector.SetAudioGain(audio_gain)
        self.num_hotwords = self.detector.NumHotwords()

        
        if len(decoder_model) > 1 and len(sensitivity) == 1:
            sensitivity = sensitivity*self.num_hotwords
        if len(sensitivity) != 0:
            assert self.num_hotwords == len(sensitivity), \
                "number of hotwords in decoder_model (%d) and sensitivity " \
                "(%d) does not match" % (self.num_hotwords, len(sensitivity))
        sensitivity_str = ",".join([str(t) for t in sensitivity])
        if len(sensitivity) != 0:
            self.detector.SetSensitivity(sensitivity_str.encode())

        self.ring_buffer = RingBuffer(
            self.detector.NumChannels() * self.detector.SampleRate() * 5)
        self.audio = pyaudio.PyAudio()
        self.stream_in = self.audio.open(
            input=True, output=False,
            format=self.audio.get_format_from_width(
                self.detector.BitsPerSample() / 8),
            channels=self.detector.NumChannels(),
            rate=self.detector.SampleRate(),
            frames_per_buffer=2048,
            stream_callback=audio_callback)


    # Here we hear commands, or detect motion, PIR.
    def start(self, detected_callback=play_audio_file,
              interrupt_check=lambda: False,
              sleep_time=0.03):

        #This object is responsible for writing to the workfile
        sb = SnowBoy()
        
        # OLA and Sensor
        global wrapper
        global universe
        global dataArr
        global dataArr2
        global sesorPin
        wrapper = ClientWrapper()
        client = wrapper.Client()
        
        if interrupt_check():
            logger.debug("detect voice return")
            return
        
        tc = type(detected_callback)
        if tc is not list:
            detected_callback = [detected_callback]
        if len(detected_callback) == 1 and self.num_hotwords > 1:
            detected_callback *= self.num_hotwords

        assert self.num_hotwords == len(detected_callback), \
            "Error: hotwords in your models (%d) do not match the number of " \
            "callbacks (%d)" % (self.num_hotwords, len(detected_callback))


        print("\n\n\n NOW LISTENING FOR HOTWORD\n\n");

        motionCounter = 0;
        dim = 0
        # While we are listening....
        while True:

            try: # Lets attempt to read from sensor..
                if GPIO.input(sensorPin): # True when sensor sends a HIGH or 1
                    print("Motion Detected...")
                    dataArr2 = []
                    dataArr2 = array.array('B')
                    dataArr2.append(255) #Intencity
                    dataArr2.append(255) #R
                    dataArr2.append(255) #G
                    dataArr2.append(255) #B                                                          
                    print(dataArr2)

                    client.SendDmx(universe, dataArr2, DmxSent)
                    wrapper.Run()
                    sleep(4)

                    dim = 1
                    #sb.processColor("FFFFFFFF")
                    #sleep(4)
                else:
                    
                    if(motionCounter <= 1024 and dim == 1):

                        motionCounter += 1

                        # The 'Timer' can be anything. Now is just 1024 interations of the while loop
                        if(motionCounter == 1024):
                        
                            # A timer to turn off the lights after some time
                            tMinus = Thread(target=olaTimer)
                            tMinus.daemon = True
                            dim = 0
                            motionCounter = 0
                            tMinus.start()
                                                                             
            except:
                print("ERROR: Could not read/open Sensor")
                
            
            if interrupt_check():
                logger.debug("detect voice break")
                break
            data = self.ring_buffer.get()
            if len(data) == 0:
                time.sleep(sleep_time)
                continue

            # Detect Voices...
            ans = self.detector.RunDetection(data)
            if ans == -1:
                logger.warning("Error initializing streams or reading audio data")
            elif ans > 0:
                callback = detected_callback[ans-1]
                if callback is not None:
                    callback()
                    
                # Our key command should always be the first one.
                if(ans == 1):
                    print("\nHouston Detected...\n")
            
                    while True:
                        if interrupt_check():
                            logger.debug("detect voice break")
                            break
                        data = self.ring_buffer.get()
                        if len(data) == 0:
                            time.sleep(sleep_time)
                            continue

                        # Now lets check the other commands...
                        cmd = self.detector.RunDetection(data)
                        if cmd == -1:
                            logger.warning("Error initializing streams or reading audio data")
                        elif cmd > 0:
                            callback = detected_callback[cmd-1]

                            if callback is not None:
                                callback()
                           
                            # If we get key command agin, lets break and start over.
                            # However, we could just pass to hear next keyword....
                            if(cmd == 1):
                                print("Got Houston instead of CMD")
                                break

                            # Red Light Command
                            elif(cmd == 2):
                                ARGB = [255, 255, 0, 0]
                                dataArr.extend(ARGB)
                                
                                print("Red Light:{}".format(dataArr))
                                
                                client.SendDmx(universe, dataArr, DmxSent)
                                wrapper.Run()
                                
                                dataArr = []
                                dataArr = array.array('B')
                          
                                # RED
                                sb.processColor("FFFF0000")

                                print("Done...\n")
                                break;

                            # Blue Light Command
                            elif(cmd == 3):
                                ARGB = [255, 0, 255, 0]
                                dataArr.extend(ARGB)
                                print("Green Light:{}".format(dataArr))
                                
                                client.SendDmx(universe, dataArr, DmxSent)
                                wrapper.Run()
                            
                                dataArr = []
                                dataArr = array.array('B')
                                
                                # GREEN
                                sb.processColor("FF00FF00")
                                print("Done...\n")
                                
                                break

                            # Green Light Command
                            elif(cmd == 4):
                                ARGB = [255, 0, 0, 255]
                                dataArr.extend(ARGB)
                                print("Blue Light:{}".format(dataArr))
                                
                                client.SendDmx(universe, dataArr, DmxSent)
                                wrapper.Run()
                                
                                dataArr = []
                                dataArr = array.array('B')

                                # Blue
                                sb.processColor("FF0000FF")
                                print("Done...\n")
                                
                                break


                            # "Emergency Lights" Command
                            elif(cmd == 5):
                                for i in xrange(5):
                                    
                                    dataArr = []
                                    dataArr = array.array('B')
                                    
                                    ARGB = [255, 255, 0, 0]
                                    dataArr.extend(ARGB)
                                    print("EMERGENCY Light:{}".format(dataArr))
                                    
                                    client.SendDmx(universe, dataArr, DmxSent)
                                    wrapper.Run()
                                    
                                    # Red
                                    sb.processColor("FFFF0000")
                                    
                                    dataArr = []
                                    dataArr = array.array('B')
                                    ARGB = [255, 0, 0, 255]
                                    dataArr.extend(ARGB)
                                    print("EMERGENCY Light:{}".format(dataArr))
                                    
                                    client.SendDmx(universe, dataArr, DmxSent)
                                    wrapper.Run()

                                    sb.processColor("FF0000FF")
                                    
                                    dataArr = []
                                    dataArr = array.array('B')
                                
                                    ARGB = [255, 255, 0, 0]
                                    dataArr.extend(ARGB)
                                    print("EMERGENCY Light:{}".format(dataArr))
                                    
                                    client.SendDmx(universe, dataArr, DmxSent)
                                    wrapper.Run()

                                    sb.processColor("FFFF0000")
                                                                    
                                    dataArr = []
                                    dataArr = array.array('B')
                                    ARGB = [255, 0, 0, 255]
                                    dataArr.extend(ARGB)
                                    print("EMERGENCY Light:{}".format(dataArr))
                                    
                                    client.SendDmx(universe, dataArr, DmxSent)
                                    wrapper.Run()

                                    sb.processColor("FF0000FF")
                                                                     
                                    dataArr = []
                                    dataArr = array.array('B')
                                    

                                print("Done...\n")
                                break

                            # Shutdown Command
                            elif(cmd == 6):
                                ARGB = [0, 0, 0, 0]
                                dataArr.extend(ARGB)
                                print("SHUT DOWN Light:{}".format(dataArr))
                                
                                client.SendDmx(universe, dataArr, DmxSent)
                                wrapper.Run()
                                
                                dataArr = []
                                dataArr = array.array('B')

                                sb.processColor("00000000")
                                print("Done...\n")
                                
                                break

                            # Red Alert Command
                            elif(cmd == 7):

                                for i in xrange(10):
                                    
                                    dataArr = []
                                    dataArr = array.array('B')
                                    
                                    #RED 
                                    ARGB = [255, 255, 0, 0]
                                    dataArr.extend(ARGB)
                                    print("RED ALERT:{}".format(dataArr))
                                    
                                    client.SendDmx(universe, dataArr, DmxSent)
                                    wrapper.Run()

                                    sb.processColor("FFFF0000")
                                    
                                    dataArr = []
                                    dataArr = array.array('B')
                                    
                                    # OFF. So that it "flashes" red
                                    ARGB = [0, 0, 0, 0]
                                    dataArr.extend(ARGB)
                                    
                                    client.SendDmx(universe, dataArr, DmxSent)
                                    wrapper.Run()

                                    sb.processColor("00000000")
                                    
                                    dataArr = []
                                    dataArr = array.array('B')
                                    
                                    #RED 
                                    ARGB = [255, 255, 0, 0]
                                    dataArr.extend(ARGB)
                                    print("RED ALERT:{}".format(dataArr))
                                    
                                    client.SendDmx(universe, dataArr, DmxSent)
                                    wrapper.Run()

                                    sb.processColor("FFFF0000")
                                    
                                    dataArr = []
                                    dataArr = array.array('B')
                                    
                                    # OFF. So that it "flashes" red
                                    ARGB = [0, 0, 0, 0]
                                    dataArr.extend(ARGB)
                                    
                                    client.SendDmx(universe, dataArr, DmxSent)
                                    wrapper.Run()
                                    
                                    sb.processColor("00000000")
                                                                   
                                print("Done...\n")
                                     
                                break
                            
                            # It was not.. Lets start over.. aka go back to wait for Hotword
                            else:
                                break
                                 
                                
                else:
                    GPIO.cleanup() # If we didnt read from sensor, lets clean up our GPIOs
                    print("Try Again...")
                    continue

                
    def terminate(self):
        """
        Terminate audio stream. Users cannot call start() again to detect.
        :return: None
        """
        self.stream_in.stop_stream()
        self.stream_in.close()
        self.audio.terminate()

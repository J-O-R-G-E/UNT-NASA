
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.uix.label import Label 
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from socket import *
import pickle
import array
from threading import Thread



RGB = '0'
rgbToClients = array.array('B')


#HOST = '192.168.1.NNN'
HOST = "localhost"
PORT = 9999
address = (HOST, PORT)
UDPSock = socket(AF_INET, SOCK_DGRAM)
UDPSock.bind(address)



def LESD(rgbVals):

    # Split the HEX values
    olaR = rgbVals[0:2]
    olaG = rgbVals[2:4]
    olaB = rgbVals[4:6]
    olaA = rgbVals[6:8]

    # Convert HEX to Int
    olaR = int(olaR, 16)
    olaG = int(olaG, 16)
    olaB = int(olaB, 16)
    olaA = int(olaA, 16)

    # Add them to the array
    global rgbToClients
    rgbToClients.append(olaA)
    rgbToClients.append(olaR)
    rgbToClients.append(olaG)
    rgbToClients.append(olaB)

    
    data,addr = UDPSock.recvfrom(1024)
    
    if not data:
        print ("Client has exited!")
    
    else:
        print("About to send")
        UDPSock.sendto( pickle.dumps(rgbToClients), addr)

    # Clean the array
    rgbToClients.remove(olaA)
    rgbToClients.remove(olaR)
    rgbToClients.remove(olaG)
    rgbToClients.remove(olaB)
    
    

# For Color WHeel Only
class ColorSelector(Popup):
    def on_press_dismiss(self, colorPicker, *args):
        self.dismiss()
        
        RGBA = colorPicker.hex_color[1:]
        print(RGBA)

        thread = Thread(target = LESD, args = (RGBA, ))
        thread.start()
        thread.join()
        print "thread finished...exiting"
        
        return True
    
    
class Setting(Screen, GridLayout, BoxLayout):

    def __init__(self, **kwargs):
        super(Setting, self).__init__(**kwargs)

        
Builder.load_file("testingapp1.kv")

class TestApp(App):
    
    title = "Spacecraft Network Lighting System"
    def build(self):
        self.color_selector = ColorSelector()
        return Setting()

if __name__ == "__main__":
    TestApp().run()
    


from kivy.app import App
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.uix.label import Label 
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.properties import ObjectProperty


"""set of users for login screen"""
usersSet = {"g", "jack", "taylor", "j"}


#HANDLES ALL THE SCREEns
class ScreenManagement(ScreenManager):
    pass


class LoginScreen(Screen):
    def login(self, username, password):
        if username not in usersSet:# and password == "j":
           self.parent.current = 'homepage'
	else:
            box = BoxLayout(orientation = 'vertical', padding = (5))
            box.add_widget(Label(text='Invalid username or password'))
            popup = Popup(title='Login Error',
                          title_size =(30),title_align='center',
                          content=box,size=(25,25),auto_dismiss=True)
            box.add_widget(Button(text='Dismiss', on_press=popup.dismiss))
            popup.open()

class HomePage(Screen):
    pass


####################################################
############### ADD FOR JORGE ######################
####################################################
# For Color WHeel Only
class ColorSelector(Popup):
    def on_press_dismiss(self, colorPicker, *args):
        self.dismiss()
        
        #Gets as it was selected - x
        RGBA = list(colorPicker.hex_color[1:])
        
        R = str(RGBA[0])  +  str(RGBA[1])
        R = int(str(R), 16)
        
        G = str(RGBA[2]) + str(RGBA[3])
        G = int(str(G), 16)
        
        B = str(RGBA[4]) + str(RGBA[5])
        B = int(str(B), 16)
        
        A = str(RGBA[6]) + str(RGBA[7])
        A = int(str(A), 16)
        
        ARGB = (A, R, G, B)
        
        print(ARGB)
        return True
        

class Setting(Screen, GridLayout, BoxLayout):
    newDevControl = 1
    portsCount = 0 #Should be Plug-And-Play Value
    
    def __init__(self, **kwargs):
        super(Setting, self).__init__(**kwargs)
    
    
    def addPorts(self):
        
        self.box = BoxLayout(orientation = 'vertical', padding = (5))

        global newDevControl       
        if(self.newDevControl):
            self.myLabel = Label(text = 'Enter Number Of Ports On New Device', font_size='25sp')
            self.box.add_widget(self.myLabel)
        else:
            self.myLabel = Label(text = 'Number Must Be An Integer Value', font_size='25sp')
            self.box.add_widget(self.myLabel)

        self.popup = Popup(title = 'Add New Device',
                           title_size = (35), title_align = 'center',
                           content = self.box, size = (25,25), auto_dismiss=True)
        
        self.uInput = TextInput(text='', multiline=False, font_size='25sp')
        self.box.add_widget(self.uInput)

        self.okBtn = Button(text='Update', on_press = self.getUser, font_size='20sp', on_release=self.popup.dismiss)
        self.box.add_widget(self.okBtn)

        self.cancelBtn = Button(text='Cancel', font_size='20sp', on_press=self.popup.dismiss)
        self.box.add_widget(self.cancelBtn)
   
        self.popup.open()

   
   
    def getUser(self, arg1):
        if(self.uInput.text.isdigit()):
            global newDevControl, portsCount
            self.portsCount = self.uInput.text
            self.newDevControl = 1
            print("User Entered: {}".format(self.uInput.text))
            
        else:
            global newDeviceControl
            self.newDevControl = 0
            print("Wrong value!")
            return self.addPorts()

        
    def getPorts(self):

        self.box = BoxLayout(orientation = 'vertical', padding = (5))

        global portsCount
        self.myLabel = Label(text = ("There are " + str(self.portsCount) + " Ports Available!"), font_size='25sp')
        self.box.add_widget(self.myLabel)
        #self.box.add_widget(Label(text = ("There are " + str(self.portsCount) + " Ports Available!"), font_size='25sp'))

        self.popup = Popup(title = 'Open Ports',
                        title_size = (35), title_align = 'center',
                        content = self.box, size = (25,25), auto_dismiss=True)
        
        self.popButton = Button(text='OK', font_size='20sp', on_press=self.popup.dismiss)
        self.box.add_widget(self.popButton)
        
        self.popup.open()

        print("{} Ports".format(self.portsCount))


###########################################################
############### END OF ADD FOR JORGE ######################
###########################################################
        

Builder.load_file("testingapp1.kv")

class TestApp(App):

    ###### GLADYS: THIS IS THE NAME OF THE WINDOW AT ALL TIMES.
    title = "Spacecraft Network Lighting System"
    def build(self):

    
        ####################################################
        ############### ADD FOR JORGE ######################
        ####################################################
        self.color_selector = ColorSelector()

        
        return ScreenManagement()

if __name__ == "__main__":
    TestApp().run()

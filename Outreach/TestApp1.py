
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.uix.label import Label 
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout


# For Color WHeel Only
class ColorSelector(Popup):
    def on_press_dismiss(self, colorPicker, *args):
        self.dismiss()
        
        RGBA = colorPicker.hex_color[1:]
        print(RGBA)
        
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

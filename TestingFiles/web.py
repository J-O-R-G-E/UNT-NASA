
"""
from kivy.garden.cefpython import CefBrowser, cefpython
from kivy.app import App
from time import sleep

class CefBrowserApp(App):
    def build(self):
        return CefBrowser(start_url='http://google.com')

CefBrowserApp.run()
sleep(10)
cefpython.Shutdown()
"""

from kivy.garden.cefpython import CefBrowser, cefpython
from kivy.app import App

class CefBrowserApp(App):
    def build(self):
        return CefBrowser(start_url='http://kivy.org')
    
CefBrowserApp().run()

cefpython.Shutdown()

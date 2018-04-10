#!/usr/bin/env python

import webkit
import gtk
import os

win = gtk.Window()
win.resize(800,500)
win.connect('destroy', lambda w: gtk.main_quit())

scroller = gtk.ScrolledWindow()
win.add(scroller)

web = webkit.WebView()
path=os.getcwd()
print path

web.open("https://google.com")

scroller.add(web)

win.show_all()

gtk.main()

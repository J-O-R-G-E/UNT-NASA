#!/usr/bin/env python

# By Jorge Cardona
# jac0656@unt.edu

import os
import gtk    # Must Go First
import webkit # Must Go Second

win = gtk.Window()
win.resize(800,500)
win.connect('destroy', lambda w: gtk.main_quit())

scrollBar = gtk.ScrolledWindow()
win.add(scrollBar)

web = webkit.WebView()

ip = os.sys.argv[1:]
ip = ip[:13]+":9090"

web.open("http://"+ip)

scrollBar.add(web)

win.show_all()

gtk.main()

#!/bin/bash

# By Jorge Cardona
# jac0656@unt.edu

# ISSUE: if OLA gets killed the universe created will change.
# e.g.: kill -9 $(pidof olad)
# Because of that, We need to change the config files in 
# /home/pi/.ola/ instead of /etc/ola/
# thie issue lead to two different configurations.
# That is what this patch fixes.


# Lets configure our files for the FTDI USB
sudo sed -i -e 's/ttyUSB/ttyUSB*/g' /home/pi/.ola/ola-usbserial.conf
sudo sed -i -e 's/ttyU/ttyU*/g'     /home/pi/.ola/ola-usbserial.conf

# Lets make sure the plugin is enabled
sudo sed -i -e 's/false/true/g' /home/pi/.ola/ola-ftdidmx.conf

# Lets change the requency to 44 Hz (MAX)
sudo sed -i -e 's/30/44/g' /home/pi/.ola/ola-ftdidmx.conf
################### Setting up FTDI USB ####################

# Lets make sure there is no conflict with FTDI
sudo sed -i -e 's/true/false/g' /home/pi/.ola/ola-usbserial.conf
sudo sed -i -e 's/true/false/g' /home/pi/.ola/ola-opendmx.conf

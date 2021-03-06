#!/bin/bash

# By Jorge Cardona
# This file is the last file that should be executed
# when setting everything up from scratch

# It places this script to be called from bootup
# which in turn it calls The Serve, Voice Commands, and the GUI

RED=`tput setaf 1`
GREEN=`tput setaf 2`
BOLD=`tput bold`
RESET=`tput sgr0`
BACK_UP_DIR=$HOME/.ipv4-BACK_UP


if [  "$EUID" -ne 0 ] # Root's UID is 0
then
    echo -e "${RED}ERROR:${RESET} ${BOLD}You Must Be root User${RESET}"
    exit
fi

# NOTE: rc.local exit 0 on success
sed -e  "s/\"exit 0\"/ /g" /etc/rc.local


# Lets make some clear Lines
echo -e "\n\n#Below are the SLNS files that run at bootup\n\n " >> /etc/rc.local
echo -e "#Server:\nsudo /home/pi/UNT-NASA/./NLNS & \nsleep 5\n" >> /etc/rc.local
echo -e "#SowBoy:\nsudo python /home/pi/UNT-NASA/voiceOLA.py & \nsleep 5\n" >> /etc/rc.local
echo -e "#The GUI:\nsudo python /home/pi/UNT-NASA/GUI.py &" >> /etc/rc.local
echo -e "\n\n#Remeber to ALWAYS leave clean \nexit 0 \n" >> /etc/rc.local

# Now Next time you bootup the Raspberry pi, Everything will also start up

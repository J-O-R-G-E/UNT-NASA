#!/bin/bash
cd home/pi/UNT-NASA/


#`sudo rm workfile.txt`
#`sudo rm temp.txt`
#`./Server &`           #for powerup to boot server
#`python Gui18.py`      #starts the GUI not as a daemon
#`python voiceOLA.py`   #voice commands


sudo rm /home/pi/UNT-NASA/workfile.txt
sudo rm /home/pi/UNT-NASA/temp.txt

/home/pi/UNT-NASA/./Server & #for powerup to boot server
#python /home/pi/UNT-NASA/Gui18.py  #starts the GUI not as a daemon
python /home/pi/UNT-NASA/voiceOLA.py   #voice commands

exit 0

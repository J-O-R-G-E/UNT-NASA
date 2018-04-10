#!/bin/bash

# By Jorge Cardona     
# jac0656@unt.edu  

# Lets be modern
sudo apt-get update --fix-missing
sudo apt-get upgrade

cd $HOME

deb http://vontaene.de/raspbian-updates/ . main
gpg --recv-keys 0C667A3E
gpg -a --export 0C667A3E | sudo apt-key add -
sudo apt-get update
sudo apt-get install libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
     pkg-config libgl1-mesa-dev libgles2-mesa-dev \
     python-setuptools libgstreamer1.0-dev git-core \
     gstreamer1.0-plugins-{bad,base,good,ugly} \
     gstreamer1.0-{omx,alsa} python-dev
echo -e "\n 1 \n"
sleep 2

# 1: Add APT sources for Gstreamer 1.0 in /etc/apt/sources.list:
deb http://vontaene.de/raspbian-updates/ . main

# 2: Add APT key for vontaene.de:
gpg --recv-keys 0C667A3E
gpg -a --export 0C667A3E | sudo apt-key add -
echo -e "\n 2 \n"
sleep 2


# 3: Install the dependencies:
sudo apt-get update
sudo apt-get install libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
     pkg-config libgl1-mesa-dev libgles2-mesa-dev \
     python-setuptools libgstreamer1.0-dev git-core \
     gstreamer1.0-plugins-{bad,base,good,ugly} \
     gstreamer1.0-{omx,alsa} python-dev
echo -e "\n 3 \n"
sleep 2


# 4: Install pip from source:
wget https://raw.github.com/pypa/pip/master/contrib/get-pip.py
sudo python get-pip.py
echo -e "\n 4 \n"
sleep 2


# 5: Install Cython from sources (debian packages are outdated):
sudo pip install Cython==0.26.1
echo -e "\n 5 \n"

# 6: Install Kivy globally on your system:
sudo pip install git+https://github.com/kivy/kivy.git@master
echo -e "\n 6 \n"
sleep 2


#Or build and use kivy inplace (best for development):
#git clone https://github.com/kivy/kivy
#cd kivy
#make
#echo "export PYTHONPATH=$(pwd):\$PYTHONPATH" >> ~/.profile
#source ~/.profile

sudo pip install pathlib
sleep 2
echo -e "\n\nsudo pip install pathlib for Python\n"


sudo apt-get install sqlite3
echo -e "\n\nsudo apt-get install sqlite3\n\n"

sleep 2
echo -e "\n\nAbout to test kivy.\n"

#cd /usr/local/share/kivy-examples/3Drendering
#python main.py &
cd /usr/local/share/kivy-examples/animation/
python animate.py &

sleep 5
kill -9 $(pidof python animate.py)

exit

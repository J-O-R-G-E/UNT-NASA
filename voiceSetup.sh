#!/bin/bash

# By Jorge Cardona
# jac0656@unt.edu

FILE=$HOME/.asoundrc
LOCAL_FILE=.asoundrc

sudo apt-get update
echo -e "\n\nsudo apt-get update\n"

sudo apt-get upgrade
echo -e "\n\nsudo apt-get upgrade\n\n"

# Lets get all depencies for snowwboy:
sudo apt-get install swig3.0 python-pyaudio python3-pyaudio sox
echo -e "\n\nsudo apt-get install swig3.0 python-pyaudio python3-pyaudio sox\n\n"

sudo apt-get install python-pip python-dev build-essential
echo -e "\n\nsudo apt-get install python-pip python-dev build-essential \n\n"

sudo pip install --upgrade pip
echo -e "\n\nsudo pip install --upgrade pip \n\n"

sudo pip install --upgrade virtualenv 
echo -e "\n\nsudo pip install --upgrade virtualenv  \n\n"

pip install pyaudio
echo -e "\n\npip install pyaudio\n\n"

sudo apt-get install libatlas-base-dev
echo -e "\n\nsudo apt-get install libatlas-base-dev\n\n"

if [ -f $FILE ]
then
    echo -e "\n\n On a new window, type, 'rec t.wav' to test mic\n\n"
else
    cat $LOCAL_FILE > $HOME/$LOCAL_FILE
fi

# We should be golden with our mic stuff
sudo apt-get install libmagic-dev libatlas-base-dev
echo -e "\n\nsudo apt-get install libmagic-dev libatlas-base-dev \n\n"

sudo apt-get install nodejs
echo -e "\n\nsudo apt-get install nodejs \n\n"

# Not easy to get npm on raspberry pi. Thats why so many installs
sudo apt-get install nodejs npm node-semver
echo -e "\n\nsudo apt-get install nodejs npm node-semver\n\n"
sudo apt-get install npm
echo -e "\n\nsudo apt-get install npm \n\n"

sudo apt-get install git-core build-essential
git clone https://github.com/joyent/node.git
cd node
git checkout v0.8.8 -b v0.8.8
curl https://github.com/joyent/node/commit/25c2940a08453ec206268f5e86cc520b06194d88.patch | git am
curl https://github.com/joyent/node/commit/1d52968d1dbd04053356d62dc0804bcc68deed8a.patch | git am
curl https://github.com/joyent/node/commit/f8fd9aca8bd01fa7226e1abe75a5bcf903f287ab.patch | git am
curl https://github.com/joyent/node/commit/7142b260c6c299fc9697e6554620be47a6f622a9.patch | git am
./configure
make
python tools/test.py -t 120 --mode=release simple message
sudo make install

# Make it rain
npm install
echo -e "\n\nnpm install \n\n"

# Make it thunder
npm install --save snowboy
echo -e "\n\nnpm install --save snowboy\n\n"

./node_modules/node-pre-gyp/bin/node-pre-gyp clean configure build
echo -e "\n\n./node_modules/node-pre-gyp/bin/node-pre-gyp clean configure build \n\n"

# We will only install for Python
cd swig/Python
echo -e "\n\ncd swig/Python \n\n"

make
echo -e "\n\nmake \n\n"

# See: https://github.com/Kitt-AI/snowboy
# For additional wrappers...
exit

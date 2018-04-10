#!/bin/bash

# By Jorge Cardona
# jac0656@unt.edu


RED=`tput setaf 1`
GREEN=`tput setaf 2`
BOLD=`tput bold`
RESET=`tput sgr0`


if [  "$EUID" -ne 0 ] # Root's UID is 0
then
    echo -e "${RED}ERROR:${RESET} ${BOLD}You Must Be root User${RESET}"
    exit
fi


# All of these may be redundant, but these are the
# packages that make WebKit and gtk work
# This will set up enviroment for the file that shows the
# OLA control panel

sudo pip install toga
sudo apt-get install gir1.2-webkit-3.0
git clone --depth 1 https://github.com/andresriancho/w3af.git 
cd w3af/
apt install graphviz
pip install pybloomfiltermmap==0.3.14
apt install libssl-dev
apt install libxml2 libxslt
apt install libxml2-dev libxslt
apt install libxml2-dev libxslt-dev
pip install pyopenssl
apt install zlib1g-dev
#./w3af_console
bash /tmp/w3af_dependency_install.sh
wget http://ftp.cn.debian.org/debian/pool/main/p/python-support/python-support_1.0.15_all.deb
dpkg -i python-support_1.0.15_all.deb
wget http://ftp.cn.debian.org/debian/pool/main/p/pywebkitgtk/python-webkit_1.1.8-3_amd64.deb
dpkg -i python-webkit_1.1.8-3_amd64.deb
apt install python-gtk2-dev
wget http://ftp.cn.debian.org/debian/pool/main/p/pywebkitgtk/python-webkit-dev_1.1.8-3_all.deb
dpkg -i python-webkit-dev_1.1.8-3_all.deb
apt --fix-broken install
apt install python-gtksourceview2
#./w3af_gui
bash /tmp/w3af_dependency_install.sh
cd ..
wget http://ftp.cn.debian.org/debian/pool/main/p/python-support/python-support_1.0.15_all.deb
dpkg -i python-support_1.0.15_all.deb
wget http://ftp.cn.debian.org/debian/pool/main/p/pywebkitgtk/python-webkit_1.1.8-3_amd64.deb
dpkg -i python-webkit_1.1.8-3_amd64.deb
apt install python-gtk2-dev
wget http://ftp.cn.debian.org/debian/pool/main/p/pywebkitgtk/python-webkit-dev_1.1.8-3_all.deb
dpkg -i python-webkit-dev_1.1.8-3_all.deb


# This is also on netSetup.sh
sudo apt-get install arp-scan -y

exit

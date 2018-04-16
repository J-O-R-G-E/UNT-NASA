#!/bin/bash

# By Jorge Cardona
# jac0656@unt.edu


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


# Lets change the swap memory
sudo sed -i "s/CONF_SWAPSIZE=100/CONF_SWAPSIZE=1024/g" /etc/dphys-swapfile
sudo /etc/init.d/dphys-swapfile stop
sudo /etc/init.d/dphys-swapfile start

echo "Making backup directory: $BACK_UP_DIR"
mkdir $BACK_UP_DIR
sleep 2
echo -e "${GREEN}OK${RESET} "

echo "Making README.txt file"
touch $BACK_UP_DIR/README.txt
sleep 2
echo -e "${GREEN}OK${RESET} "

echo "Making a backup copy of all files modified here"
cp /proc/sys/net/ipv4/* $BACK_UP_DIR/
sleep 2
echo -e "${GREEN}OK${RESET} "

echo "Making a sysctl.conf backup file"
cat /etc/sysctl.conf > $BACK_UP_DIR/sysctl.conf.BACK_UP
echo -e "${GREEN}OK${RESET} "

echo "This is a copy of all files from: /proc/sys/net/ipv4/" > $BACK_UP_DIR/README.txt
echo "If any issue occures, copy back all these file and reboot" >> $BACK_UP_DIR/README.txt
echo "Also, the original file, /etc/sysctl.conf, has been copied" >> $BACK_UP_DIR/README.txt


echo "Starting setup..."
# Ethernet: For paths with more than 50 ms RTT, lets use a 5k-10k values
ifconfig | grep "txqueuelen:"
sudo ifconfig eth0 txqueuelen 7000
ifconfig | grep "txqueuelen:"
sleep 3
echo -e "${GREEN}OK${RESET} "

# TCP:
# Lets quickly reuse sockets:
# Default is 60
cat /proc/sys/net/ipv4/tcp_fin_timeout
sudo echo 30 > /proc/sys/net/ipv4/tcp_fin_timeout
cat /proc/sys/net/ipv4/tcp_fin_timeout
sleep 3
echo -e "${GREEN}OK${RESET} "

# TCP_KEEP_ALIVE_INTERVAL
# Lets not waste resources...
# Default is 75
cat /proc/sys/net/ipv4/tcp_keepalive_intvl
sudo echo 30 > /proc/sys/net/ipv4/tcp_keepalive_intvl
cat /proc/sys/net/ipv4/tcp_keepalive_intvl
sleep 3
echo -e "${GREEN}OK${RESET} "

# TCP_KEEP_ALIVE_PROBES
# Lets not keep asking the same thing
# Default is 9
cat /proc/sys/net/ipv4/tcp_keepalive_intvl
sudo echo 9 > /proc/sys/net/ipv4/tcp_keepalive_intvl
cat /proc/sys/net/ipv4/tcp_keepalive_intvl
sleep 3
echo -e "${GREEN}OK${RESET} "

# TCP_TW_REUSE
# This allows reusing sockets
# Default is 0  (disabled)
cat /proc/sys/net/ipv4/tcp_tw_reuse
sudo echo 1 > /proc/sys/net/ipv4/tcp_tw_reuse
cat /proc/sys/net/ipv4/tcp_tw_reuse
echo -e "${GREEN}OK${RESET} "
sleep 3

# TCP_FIN_TIMEOUT
# This allows us to quickly finalize a closed connection and use its resources...
# Defaul is 60
cat /proc/sys/net/ipv4/tcp_fin_timeout
sudo  echo 5 > /proc/sys/net/ipv4/tcp_fin_timeout
cat /proc/sys/net/ipv4/tcp_fin_timeout
sleep 3
echo -e "${GREEN}OK${RESET} "

# TCP_MAX_SYN_BACKLOG
# This allows us to handle SYN floods, receiving..
# Default is 256
sysctl  net.ipv4.tcp_max_syn_backlog
sudo sysctl -w net.ipv4.tcp_max_syn_backlog="2048"
sudo echo "net.ipv4.tcp_max_syn_backlog = 2048" >> /etc/sysctl.conf # Prevent loosing it on reboot
sleep 3
echo -e "${GREEN}OK${RESET} "

# TCP_SOMAXCONN
# This is the kernel's socket limmit.
# Default is 128
sysctl net.core.somaxconn
sudo sysctl -w net.core.somaxconn=2048
sudo echo "net.core.somaxconn = 2048" >> /etc/sysctl.conf # Prevent loosing it on reboot
sleep 3
echo -e "${GREEN}OK${RESET} "


# cat /etc/resolv.conf
# cat /etc/dhcpcd.conf

echo -e "Making back up for DHCP Services"
cat /etc/dhcpcd.conf > /etc/dhcpcd.conf.ORIGINAL
echo -e "${GREEN}OK${RESET} "

sudo sed -i -e 's/#interface eth0/interface eth0/g' /etc/dhcpcd.conf
sudo sed -i -e 's/#static ip_address=192.168.0.10\/24/static ip_address=192.168.1.12\/24/g' /etc/dhcpcd.conf 
sudo sed -i -e 's/#static ip6_address=fd51:42f8:caae:d92e::ff\/64/static ip6_address=fd51:42f8:caae:d92e::ff\/64/g' /etc/dhcpcd.conf
sudo sed -i -e 's/#static routers=192.168.0.1/static routers=192.168.1.1/g' /etc/dhcpcd.conf
sudo sed -i -e 's/#static domain_name_servers=192.168.0.1 8.8.8.8 fd51:42f8:caae:d92e::1/static domain_name_servers=192.168.1.1 8.8.8.8 fd51:42f8:caae:d92e::1/g' /etc/dhcpcd.conf
sleep 3
echo "Configured..."
echo -e "${GREEN}OK${RESET} "


# Number of file descriptors
# We may not really need this:
# sysctl fs.file-nr
# RESULT: #1 number of allocated file handles
#         #2 number of unused but allocated file handles
#         #3 system-wide maximum number of file handles
# sudo echo 10000000 > /proc/sys/fs/file-max

sudo apt-get install arp-scan -y
echo -e "\nInstalling artp-scan..."
echo -e "\This is needed for voice commands..."
echo -e "${GREEN}OK${RESET} "

sleep 3
echo -e "${GREEN}Done...${RESET} "

#!/bin/bash
# By Jorge Cardona
#
# We had an issue with the master Pi, and I only needed to install the FTDI USB drivers....

################### Setting up FTDI USB ####################
# http://www.ftdichip.com/Drivers/D2XX.htm
# Lets make sure we are still at Home
cd $HOME

# Lets get the drivers
wget http://www.ftdichip.com/Drivers/D2XX/Linux/libftd2xx-arm-v6-hf-1.4.6.tgz

mkdir FTDIFiles

# Unzip the file and copy it to FTDIFiles
tar -zxvf libftd2xx-arm-v6-hf-1.4.6.tgz -C FTDIFiles/

# Go in
cd FTDIFiles/release/build

# Copy the libs to the Computers
sudo cp libftd2xx.* /usr/local/lib/

# Change permisions
sudo chmod 0755 /usr/local/lib/libftd2xx.so.1.4.6

# Lets make a link
sudo ln -sf /usr/local/lib/libftd2xx.so.1.4.6 /usr/local/lib/libftd2xx.so

# Lets configure our files for the FTDI USB
sudo sed -i -e 's/ttyUSB/ttyUSB*/g' /home/pi/.ola/ola-usbserial.conf
sudo sed -i -e 's/ttyU/ttyU*/g'     /home/pi/.ola/ola-usbserial.conf

# Lets make sure the plugin is enabled
sudo sed -i -e 's/false/true/g' /etc/ola/ola-ftdidmx.conf

# Lets change the requency to 44 Hz (MAX)
sudo sed -i -e 's/30/44/g' /etc/ola/ola-ftdidmx.conf
################### Setting up FTDI USB ####################

# Lets make sure there is no conflict with FTDI
sudo sed -i -e 's/true/false/g' /etc/ola/ola-usbserial.conf
sudo sed -i -e 's/true/false/g' /etc/ola/ola-opendmx.conf


# Lets try to complete the setup by init the OLA deamond
olad -l 3  > /dev/null 2>&1
sleep 5

# Lets send some dummy data
ola_streaming_client  -u 1 -d 1,2,255,255 > /dev/null 2>&1 &

# Lets path the FTDI USB to Universe 1
ola_patch -d 2 -p 1 -u 1

echo -e "\n\nThe Coputer will reboot in 5 seconds.\n"
echo -e "After reboot, please run the command 'olad -l 3 '\n"
echo -e "This command will run the olad deamon...\n\n\n"
echo -e "This command will run the olad deamon...\n\n\n"

IP=`hostname -I | awk '{print $1}'`
echo -e "Use  a web browser and type: $IP:9090 and create a Universe with ID:1"

sleep 10

sudo reboot

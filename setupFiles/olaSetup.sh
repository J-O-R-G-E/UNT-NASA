#!/bin/bash
1;2802;0c
# By Jorge Cardona
# jac0656@unt.edu


RED=`tput setaf 1`
GREEN=`tput setaf 2`
BOLD=`tput bold`
RESET=`tput sgr0`


# Lets check the user is sudoer
if [ $(id -u) -ne 0 ]
then
    echo -e "\nError:  You must be root or:"
    echo -e "\tsudo $0 options"
    echo -e "\twhere options are: install, update\n"
    
    exit 1
fi


if [ $1 == "install" ]
then
    #Lets make sure we are at home
    cd $HOME

    echo -e "\nINSTALLING OLA...\n\n"
    sleep 1
    
    ###################### Dependecies for OLA #################################
    # Lets get Google's Protocol Buffer:
    wget https://github.com/google/protobuf/releases/download/v3.5.1/protobuf-all-3.5.1.tar.gz
    echo -e "\n${GREEN}DOWNLOADED PROTOBUF   ${RESET}\n"

    
    # Lets extract everything:
    tar -zxvf protobuf-all-3.5.1.tar.gz
    echo -e "\n\n${GREEN}UNZIPPED   ${RESET}\n\n"

 
    # Lets go there
    cd protobuf-3.5.1/
    
    ./configure
    echo -e "\n\n${GREEN}./configure       ${RESET}\n\n"

    # Takes a really long time
    make 
    echo -e "\n\n${GREEN}make       ${RESET}\n\n"
    # Takes a while, too
    
    make check  
    echo -e "\n\n${GREEN}make check       ${RESET}\n\n"

    # Make it rain
    sudo make install
    echo -e "\n\n${GREEN}make install       ${RESET}\n\n"
    
    # We also need all of these:
    sudo apt-get install bison -y
    echo -e "\n\n${GREEN}bison -y       ${RESET}\n\n"
    
    sudo apt-get install flex -y
    echo -e "\n\n${GREEN}flex -y       ${RESET}\n\n"
    
    sudo apt-get install lex -y
    echo -e "\n\n${GREEN}lex -y       ${RESET}\n\n"
    
    sudo apt-get install uuid-dev -y
    echo -e "\n\n${GREEN}uuid-dev -y       ${RESET}\n\n"
    
    sudo apt-get install libcppunit-dev -y
    echo -e "\n\n${GREEN}libcppunit-dev -y       ${RESET}\n\n"
    
    sudo apt-get install doxygen -y
    echo -e "\n\n${GREEN}doxygen -y       ${RESET}\n\n" # You should learn about this
    
    sudo apt-get install libcppunit-dev libcppunit-dev uuid-dev pkg-config libncurses5-dev libtool autoconf automake g++ libmicrohttpd-dev
    echo -e "\n\n${GREEN}libcppunit-dev libcppunit-dev uuid-dev pkg-config libncurses5-dev libtool autoconf automake g++ libmicrohttpd-dev ${RESET}\n\n"
    
    libmicrohttpd10 protobuf-compiler libprotobuf-lite10 python-protobuf libprotobuf-dev libprotoc-dev zlib1g-dev bison flex make libftdi-dev libftdi1 libusb-1.0-0-dev liblo-dev libavahi-client-dev python-numpy
    echo -e "\n\n${GREEN}   libmicrohttpd10 protobuf-compiler libprotobuf-lite10 python-protobuf libprotobuf-dev libprotoc-dev zlib1g-dev bison flex make libftdi-dev libftdi1 libusb-1.0-0-dev liblo-dev libavahi-client-dev python-numpy    ${RESET}\n\n"

    sudo ldconfig
    ############### End of Dependecies #####3#############
    
    
    ################### Installing OLA ####################
    # Lets make sure we are still at Home
    cd $HOME
    
    sudo  ldconfig

    # Just in case...
    sudo apt-get install git
    
    # Thanks open source! We love you all
    git clone https://github.com/OpenLightingProject/ola.git ola
    echo -e "\n\n${GREEN}DOWNLOADING OLA   ${RESET}\n\n"

    
    cd ola
    
    autoreconf -i
    echo -e "\n\n${GREEN}autoreconf -i       ${RESET}\n\n"
    #./configure --help        # To see all the options available
    #./configure --enable-all-plugins # Use the command above to disable any plugin not needed

    ./configure --disable-all-plugins
        
    # Lets meka sure we have our FTDI plugin
    ./configure --enable-ftdidmx
    echo -e "\n\n${GREEN}./configure --enable-ftdidmx       ${RESET}\n\n"

    make -j 4 all             # 4 is the numbers of cores used
    make
    make check                # Checks everything on OLA. Takes forever
    sudo make install
    sudo apt-get install ola-python -y
    sudo ldconfig
    
    ################ End of Installing OLA ####################
    
    
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

elif [ $1 == "update" ]
then
    cd $HOME
    cd ola

    echo -e "\nUPDATING OLA...\n\n"
    sleep 1
    
    git pull

    autoreconf

    ./configure --disable-all-plugins
    
    # Lets meka sure we have our FTDI plugin
    ./configure --enable-ftdidmx
    
    make
    sudo make install
    sudo ldconfig

else
    echo -e "\nError: Usage"
    echo -e "\tsudo $0 options"
    echo -e "\twhere options are: install, update\n"
    
    exit 1
    
fi

exit 1

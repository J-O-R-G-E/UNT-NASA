# This Makefile compiles the Client and dmx512.c++
# By Jorge Cardona.

CC = g++

CFLAGS = -Wall -g -std=c++11 

#$(pkg-config --cflags --libs libola)	
OLA_FLAGS = -pthread -I/usr/local/include -L/usr/local/lib -lola -lolacommon -lprotobuf -pthread -lpthread
TARGET = Client

SOURCE_FILES = Skeleton_client.cpp  dmx512.c++

$(TARGET): $(SOURCE_FILE)
	$(CC) $(SOURCE_FILES) $(CFLAGS) $(OLA_FLAGS) -o $(TARGET)

clean:
	$(RM) $(TARGET)

# This Makefile compiles the Client and dmx512.c++
# By Jorge Cardona.

CC = g++

CFLAGS = -Wall -g -std=c++11 

#$(pkg-config --cflags --libs libola)	
OLA_FLAGS = -pthread -I/usr/local/include -L/usr/local/lib -lola -lolacommon -lprotobuf -pthread -lpthread

TARGET1 = Client
TARGET2 = Server

CLIENT_FILES = SLNS_client.cpp  dmx512.c++
SERVER_FILES = SLNS_server.cpp


client:
	$(CC) $(CLIENT_FILES) $(CFLAGS) $(OLA_FLAGS) -o $(TARGET1)

server:
	$(CC) $(SERVER_FILES) $(CFLAGS) -o $(TARGET2)

all:
	$(CC) $(CLIENT_FILES) $(CFLAGS) $(OLA_FLAGS) -o $(TARGET1)
	$(CC) $(SERVER_FILES) $(CFLAGS) -o $(TARGET2)

clean:
	$(RM) $(TARGET1) $(TARGET2)

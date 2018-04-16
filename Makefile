# This Makefile compiles the Client and dmx512.c++
# By Jorge Cardona.

CC = g++

CFLAGS = -Wall -g -std=c++11 $(pkg-config --cflags --libs libola)

TARGET = Client

SOURCE_FILES = Skeleton_client.cpp  dmx512.c++

$(TARGET): $(SOURCE_FILE)
	$(CC) $(CFLAGS) -o $(TARGET) $(SOURCE_FILES)

clean:
	$(RM) $(TARGET)

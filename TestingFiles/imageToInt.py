#!/usr/bin/env python

"""
This program generates the RGB values found
on every pixel on the given picture, RGB.jpg
and stores those values to a file.

Note: The output file will be in the form of a tuple.
      Use 'sed' to remove '(', ',', and ')'
      when finished, use file "intToHEX.c++

Usage:
      python imageToInt.py > rgbValuesINT
      and to remove the tuple notation use:
      sed -i "s/(//g" rgbValuesINT
      sed -i "s/)//g" rgbValuesINT
      sed -i "s/,//g" rgbValuesINT

      Description of first line:
      sed = steam editor. You should learn how to use it.
      -i  = to "insert" the given pattern or to edit or replace
      s/  = substitute
      (/  = the partern to find
       /  = new pattern to be inserted. In this case, nothing.
      /g  = do this globally. aka all matches.
 
How to install PIL:
      #jpeg support
      sudo apt-get install libjpeg-dev
      
      #tiff support
      sudo apt-get install libtiff-dev

      #freetype support
      sudo apt-get install libfreetype6-dev

      #openjpeg200support (needed to compile from source)
      wget http://downloads.sourceforge.net/project/openjpeg.mirror/2.0.1/openjpeg-2.0.1.tar.gz
      tar xzvf openjpeg-2.0.1.tar.gz
      cd openjpeg-2.0.1/
      sudo apt-get install cmake
      cmake .
      sudo make install

      #install pillow
      pip install pillow

 By jac0656
"""
from PIL import Image

im = Image.open("RGB.jpg", "r")

for i in xrange(im.size[0]):
    for y in xrange(im.size[1]):
        print(((im.getpixel((i, y)))))
        
#im.show()


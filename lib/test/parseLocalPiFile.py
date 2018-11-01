#!/home/makijarv/usr/bin/python
# -*- coding: utf-8 -*-

# Find the load path order
import sys
# print sys.path
sys.path.insert(1,r'..')
# print sys.path

from mPuuPersonalInfo import *

# utf8InputPath = 'Jouko_M\xc3\xa4kij\xc3\xa4rvi.xml'
# utf8InputPath = 'Matti_Aataminpoika.xml'
# utf8InputPath = 'Juho_Sikala.xml'
utf8InputPath = 'Ida_Wesander.xml'
myobj = mPuuPersonalInfo ( utf8InputPath, True )



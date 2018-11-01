#!/home/makijarv/usr/bin/python
# -*- coding: utf-8 -*-

# Find the load path order
import sys
# print sys.path
sys.path.insert(1,r'..')
# print sys.path
import glob

from mPuuPersonalInfo import *


xmlFiles = glob.glob('../../../public_html/mPuu/db/pi/*.xml')

myObjs = {}

for file in xmlFiles:
    newObj = mPuuPersonalInfo ( file, False )
    myObjs[newObj.getName()] = ( newObj )

print 'done:'
print myObjs['Jouko M\xc3\xa4kij\xc3\xa4rvi'].getFather()
print myObjs['Jouko M\xc3\xa4kij\xc3\xa4rvi'].getMother()

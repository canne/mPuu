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

#person = 'Petri M\xc3\xa4kij\xc3\xa4rvi'
#person = 'Ida Wesander'
person = 'Emelia Hein\xc3\xa4nen'
while True:
    print person
    father = myObjs[person].getFather()
    if father == '?' or father == '': break
    person = father

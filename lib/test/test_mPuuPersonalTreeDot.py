#!/home/makijarv/usr/bin/python
# -*- coding: utf-8 -*-

# Find the load path order
import sys
# print sys.path
sys.path.insert(1,r'..')
# print sys.path
import glob

from mPuuException import *
from mPuuPersonalTree import *

person = 'Petri M\xc3\xa4kij\xc3\xa4rvi'

try:
    personalTree1 = mPuuPersonalTreeDot ( person, 'father', True )

    fd = open( person+'.gvi', "w" )
    fd.write ( personalTree1.getDotFile() )
    fd.close
    
#    personalTree2 = mPuuPersonalTreeDot ( person, 'mother')

except mPuuException, err:
    print >>sys.stderr, err.msg
    sys.exit( 2 )



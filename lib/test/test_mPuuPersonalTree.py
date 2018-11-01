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

#person = 'Petri M\xc3\xa4kij\xc3\xa4rvi'
person = 'Anna Mattsdotter'

try:
    personalTree1 = mPuuPersonalTree ( person, 'father', True )
#    personalTree2 = mPuuPersonalTree ( person, 'mother', True )

except mPuuException, err:
    print >>sys.stderr, err.msg
    sys.exit( 2 )



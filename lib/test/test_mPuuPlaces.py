#!/home/makijarv/usr/bin/python
# -*- coding: utf-8 -*-

# Find the load path order
import sys
# print sys.path
sys.path.insert(1,r'..')
# print sys.path
import glob

from mPuuException import *
from mPuuPlaces import *

personpath1 = '/home/makijarv/www/mPuu/db/pi/Petri_M\xc3\xa4kij\xc3\xa4rvi.xml'
personpath2 = '/home/makijarv/www/mPuu/db/pi/Ilkka_M\xc3\xa4kij\xc3\xa4rvi.xml'

try:
    places = mPuuPlaces ( True )
    places.nextPersonalInfo ( personpath1 ) 
    places.nextPersonalInfo ( personpath2 ) 
    print places.getTownsDictionary()   
    print places.getHousesDictionary()   
    places.stopDataCollecting()
    print places.getTownsDictionary()   
    print places.getHousesDictionary()   

except mPuuException, err:
    print >>sys.stderr, err.msg
    sys.exit( 2 )



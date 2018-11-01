#!/home/makijarv/usr/bin/python
# -*- coding: utf-8 -*-

# Find the load path order
import sys
# print sys.path
sys.path.insert(1,r'..')
# print sys.path
import glob

from mPuuException import *
from mPuuConfiguration import *
from mPuuPersonalInfo import *
from mPuuCrawler import *

startWith = 'Aatami Abrahaminpoika'
confObj  = mPuuConfiguration ( )
personPath = confObj.getPiPath ( confObj.getDbPersonName ( startWith ) )

try:
    startObj = mPuuPersonalInfo ( personPath, False )
    crawler = mPuuCrawler ( startObj, confObj, False )
    dotFileContents = crawler.getDotFile()
    print dotFileContents
    
except mPuuException, err:
    print >>sys.stderr, err.msg
    sys.exit( 2 )



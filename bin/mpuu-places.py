#!/home/makijarv/usr/bin/python
# -*- coding: utf-8 -*-
# -------------------------------------------------------------------
# Project     : mPuu - Makijarvi family tree database application
# Module      : mpuu-places.py
# Description : Get Personal Information of each person in the XML
#               database and analyze the places information (towns,
#               houses). Build a cumulative list of each place about
#               houses in that place and the persons have lived in
#               that place. Build a cumulative list of each house,
#               about the places it has been declared and the persons
#               who have lived in that house. Create XHTML include
#               files for each place and for each house for the needs
#               of mPuu MediaWiki extension.
#
# Author(s)   : Petri Makijarvi (pmakijarvi@users.sourceforge.net)
#
# License     : See distribution's LICENSE file
#
# This        : $Revision: 1.2 $
#
# Original    : May 2006
# -------------------------------------------------------------------
"""
Make XHTML include files for place and house information
$Revision: 1.2 $
Usage: mpuu-places.py [-h|--help] [-v|--verbose]
       -h, --help    = show this help text
       -v, --verbose = verbose mode (for debugging)
"""

import sys
import os, os.path
# We want to use mPuu Python class libraries.
# - uncomment the path printing if you encounter difficulties
# print sys.path
absPath = os.path.abspath( sys.path[0] )
libPath = absPath.rstrip('/bin')+'/lib'
sys.path.insert ( 1, libPath )
# print sys.path

import shutil
import getopt
import glob

from mPuuException import *
from mPuuConfiguration import *
from mPuuPlaces import *

class Usage( Exception ):
    """Usage class is for wrong or missing options and arguments"""
    def __init__(self, msg):
        """Memorize the given error message for the usage"""
        self.msg = msg

def main( argv = None ):
    """Option and argument parsing followed by the core operation logic"""
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "hv", ['help','verbose'])
        except getopt.error, msg:
            raise Usage( argv[0] )
        # option processing
        verbose = False
        for option, value in opts:
            if option in ("-v", "--verbose"):
                verbose = True
            if option in ("-h", "--help"):
                print __doc__
                return 1
        # argument processing, uncomment if you will use arguments
        # try:
        #    firstArgument = args[0]
        # except:
        #    raise Usage( argv[0] )
        
        # The next section is the application part
        try:
            if verbose: "mpuu-places.main()"
            config = mPuuConfiguration( verbose )
            # Get a list of files in the XML-database
            if verbose:
                print "mpuu-places.main() - reading names from XML database:\n"+\
                      config.getPiDir()
            xmlFiles = glob.glob ( config.getPiDir()+'/*.xml')
            mPuuPlaces = mPuuPlacesXHTML( verbose )
            #getXhtmlOutDir ( self ):
            for fullPath in xmlFiles:
                mPuuPlaces.nextPersonalInfo ( fullPath )
            mPuuPlaces.stopDataCollecting()
            mPuuPlaces.allTowns(  config.getXhtmlOutDir()+'/towns'  )
            mPuuPlaces.allHouses( config.getXhtmlOutDir()+'/houses' )

        except mPuuException, err:
            print >>sys.stderr, err.msg
            return 2

    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, __doc__
        return 2

# Allow execution of main() either from the python interpreter's command line
# or as a script, python being invoked by the firs line's shebang.
if __name__ == "__main__":
    sys.exit( main() )


# end of module

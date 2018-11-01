#!/home/makijarv/usr/bin/python
# -*- coding: utf-8 -*-
# -------------------------------------------------------------------
# Project     : mPuu - Makijarvi family tree database application
# Module      : 
# Description : 
#
# Author(s)   : Petri Makijarvi (pmakijarvi@users.sourceforge.net)
#
# License     : See distribution's LICENSE file
#
# This        : $Revision: 1.9 $
#
# Original    : 
# -------------------------------------------------------------------
"""
Description.
$Revision: 1.9 $
Usage: program.py [--help] [-v] argument
       -h, --help = show this help text
       -v         = verbose mode (for debugging)
"""

import sys
import os, os.path
# We want to use mPUU Python class libraries.
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
            config = mPuuConfiguration( verbose )
            print 'done.'
            
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

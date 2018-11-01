#!/home/makijarv/usr/bin/python
# -*- coding: utf-8 -*-
# -------------------------------------------------------------------
# Project     : mPuu - Makijarvi family tree database application
# Module      : mpuu-pigrahps.py
# Description : Calculate Personal Information based personal
#               family trees for each person in the XML database
#               and create the graphs files out of them.
#
# Author(s)   : Petri Makijarvi (pmakijarvi@users.sourceforge.net)
#
# License     : See distribution's LICENSE file
#
# This        : $Revision: 1.7 $
#
# Original    : April 2006
# -------------------------------------------------------------------
"""
Make Personal Information based family tree graphs for everybody.
$Revision: 1.7 $
Usage: mpuu-pigraphs.py [-h|--help] [-v|--verbose] [-k|--keepall]
                        [-sletter|--select=letter]
       -h, --help    = show this help text
       -v, --verbose = verbose mode (for debugging)
       -k, --keepall = do not delete intermediate files
       -s, --select = select only files starting with 'letter'
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
from time import sleep

from mPuuException import *
from mPuuConfiguration import *
from mPuuPersonalTree import *

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
            opts, args = getopt.getopt(argv[1:], "hvks:",
                                       ['help','verbose','keepall','select='])
        except getopt.error, msg:
            raise Usage( argv[0] )
        # option processing
        verbose = False
        keepall = False
        wildcard = '*'
        for option, value in opts:
            if option in ("-v", "--verbose"):
                verbose = True
            if option in ("-k", "--keepall"):
                keepall = True
            if option in ("-s", "--select"):
                wildcard = value + wildcard
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
            if verbose: "mpuu-pigraphs.main()"
            config = mPuuConfiguration( verbose )
            # Get a list of files in the XML-database
            if verbose:
                print "mpuu-pigraphs.main() - reading names from XML database:\n"+\
                      config.getPiDir()
            if verbose and wildcard != '*':
                print "\nfor wildcard " + wildcard + ".xml\n"
            xmlFiles = glob.glob ( config.getPiDir() + '/' + wildcard + '.xml')
            for fullPath in xmlFiles:
                namePart = os.path.basename( fullPath )
                splitFileName = namePart.split('.')
                dbName = splitFileName[0]
                name = dbName.replace('_',' ')
                # do all the graphs, both for father and mother lines
                parentStrings = [ 'father', 'mother' ]
                for parentLine in parentStrings:
                    if verbose: print "mpuu-pigraphs.main() - making Personal Tree for:\n"+name
                    personalTree = mPuuPersonalTreeDot( name, parentLine, verbose )
                    dbName = personalTree.getDbName()
                    if verbose: print "mpuu-pigraphs.main() - in directory:\n"+config.getPtDir()
                    os.chdir ( config.getPtDir() )
                    gviFileName = dbName+'_'+parentLine+'.gvi'
                    if verbose: print "mpuu-pigraphs.main() - file name:\n"+gviFileName
                    fd = open ( gviFileName, 'w' )
                    fd.write ( personalTree.getDotFile() )
                    fd.close()
                    # make the Graphviz conversion(s)
                    dotoptions  = ' -Tpng -o'+dbName+'_'+parentLine+'.png'
                    dotoptions += ' -Tcmap -o'+dbName+'_'+parentLine+'.map'
                    dotcmdline  = config.getDot()+dotoptions+' '+gviFileName
                    if verbose: print "mpuu-pigraphs.main() - launching Graphviz:\n"+dotcmdline
                    fd = os.popen ( dotcmdline )
                    while 1:
                        oline = fd.readline()
                        if not oline: break
                        if verbose: print oline.strip()
                    fd.close()
                    # Cleanup
                    if not keepall:
                        os.remove( gviFileName )

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

#!/home/makijarv/usr/bin/python
# -*- coding: utf-8 -*-
# -------------------------------------------------------------------
# Project     : mPuu - Makijarvi family tree database application
# Module      : mpuu-ftgrahps.py
# Description : Calculate Personal Information based family tree
#               for selected persons and create the graphs files
#               out of them.
#
# Author(s)   : Petri Makijarvi (pmakijarvi@users.sourceforge.net)
#
# License     : See distribution's LICENSE file
#
# This        : $Revision: 1.5 $
#
# Original    : May 2006
# -------------------------------------------------------------------
"""
Make Personal Information based family tree
$Revision: 1.5 $
Usage: mpuu-ftgraphs.py [-h|--help] [-v|--verbose] [-k|--keepall]
       -h, --help    = show this help text
       -v, --verbose = verbose mode (for debugging)
       -k, --keepall = do not delete intermediate files
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
from mPuuCrawler import *

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
            opts, args = getopt.getopt(argv[1:], "hvk", ['help','verbose','keepall'])
        except getopt.error, msg:
            raise Usage( argv[0] )
        # option processing
        verbose = False
        keepall = False
        for option, value in opts:
            if option in ("-v", "--verbose"):
                verbose = True
            if option in ("-k", "--keepall"):
                keepall = True
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
            if verbose: "mpuu-ftgraphs.main()"
            config = mPuuConfiguration( verbose )
            for ancestor in config.fullTreeList:
                personPath = config.getPiPath ( config.getDbPersonName ( ancestor ) )
                startObj = mPuuPersonalInfo ( personPath, verbose )
                crawler = mPuuCrawler ( startObj, config, verbose )
                if verbose: print "mpuu-ftgraphs.main() - in directory:\n"+config.getFtDir()
                os.chdir ( config.getFtDir() )
                # Make the default, graphics file format (PNG)
                dbName = startObj.getDbName()
                gviFileName = dbName+'.gvi'
                if verbose: print "mpuu-ftgraphs.main() - gvi-file name:\n"+gviFileName
                fd = open ( gviFileName, 'w' )
                fd.write ( crawler.getDotFile() )
                fd.close()
                dotoptions  = ' -Tpng -o'+dbName+'.png'
                dotoptions += ' -Tcmap -o'+dbName+'.map'
                dotcmdline  = config.getDot()+dotoptions+' '+gviFileName
                if verbose: print "mpuu-ftgraphs.main() - launching Graphviz:\n"+dotcmdline
                fd = os.popen ( dotcmdline )
                while 1:
                    oline = fd.readline()
                    if not oline: break
                    if verbose: print oline.strip()
                fd.close()
                # Cleanup
                if not keepall:
                    os.remove( gviFileName )
                # Make the printable pre-file format (PostScript)
                gviFileName = dbName+'_printable.gvi'
                if verbose: print "mpuu-ftgraphs.main() - printable gvi-file name:\n"+gviFileName
                fd = open ( gviFileName, 'w' )
                printableFormat = True
                fd.write ( crawler.getDotFile( printableFormat ) )
                fd.close()
                dotoptions  = ' -Tps -o'+dbName+'.ps'
                dotcmdline  = config.getDot()+dotoptions+' '+gviFileName
                if verbose: print "mpuu-ftgraphs.main() - launching Graphviz:\n"+dotcmdline
                pipe = os.popen ( dotcmdline )
                while 1:
                    oline = pipe.readline()
                    if not oline: break
                    if verbose: print oline.strip()
                pipe.close()
                # Cleanup
                if not keepall:
                    os.remove( gviFileName )
                # Make the final printable format (PDF)
                psFileName  = dbName+'.ps'
                pdfFileName = dbName+'.pdf'
                ps2pdfargs = ''
                if config.getFtPaper().upper() != 'A4':
                    if config.getFtPaper().upper() == 'A3':
                        ps2pdfargs += ' -sPAPERSIZE=a3'
                    else:
                        ps2pdfargs += ' -sPAPERSIZE=a0'
                ps2pdfargs  += ' '+psFileName+' '+pdfFileName
                ps2pdfcmdline = config.getPs2Pdf()+ps2pdfargs
                if verbose:
                    print "mpuu-makeptpdf.main() - launching ps2pdf:\n"+ps2pdfcmdline
                pipe = os.popen ( ps2pdfcmdline )
                while 1:
                    oline = pipe.readline()
                    if not oline: break
                    if verbose: print oline.strip()
                pipe.close()
                if not keepall:
                    os.remove ( psFileName )

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

#!/home/makijarv/usr/bin/python
# -*- coding: utf-8 -*-
# -------------------------------------------------------------------
# Project     : mPuu - Makijarvi family tree database application
# Module      : mpuu-makeptpdf.py
# Description : Takes an existing name in the Personal Info XML
#               database and calculates a personal familytree,
#               converts and return it on PDF-format.
#
# Author(s)   : Petri Makijarvi (pmakijarvi@users.sourceforge.net)
#
# License     : See distribution's LICENSE file
#
# This        : $Revision: 1.3 $
#
# Original    : April 2006
# -------------------------------------------------------------------
"""
Returns a PDF application stream that presents the graph for
the Personal Information based personal family tree.
$Revision: 1.3 $
Usage: /scgi-bin/mpuu-makeptpdf.py?name=URL_name&line=father|mother[&verbose=true][&keepall=true]
       -h, --help    = show this help text if executed from command line
       name          = Person's Wiki page name
       line          = Father, Mother familyline
       verbose       = Optional, talk loud for debugging, makes
                       pdf-file in temp directory instead of returning code
       keepall       = Keep all intermediate files, good for debugging
"""

import sys
import os, os.path
import cgi
# Keep this on while debugging:
import cgitb; cgitb.enable()

# We want to use mPUU Python class libraries.
# - note that we actually running this from the (s)cgi-bin directory
# - uncomment the path printing if you encounter difficulties
# print sys.path
absPath = os.path.abspath( sys.path[0] )
# print "Content-type: text/html\n"
# print absPath
splitPath = absPath.split('/')
if len(splitPath) < 4:
    print "Cannot determine the position of mPuu directory from "+absPath
    sys.exit(2)
libPath = ''
for pathindex in range( 1, len(splitPath) - 2 ):
    libPath += '/'+splitPath[pathindex]
libPath += '/mPuu/lib'
sys.path.insert ( 1, libPath )
# print sys.path


import shutil
import getopt
import glob

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
            opts, args = getopt.getopt(argv[1:], "h", ['help'])
        except getopt.error, msg:
            raise Usage( argv[0] )
        # option processing
        verbose = False
        for option, value in opts:
            if option in ("-h", "--help"):
                print __doc__
                return 1
        # argument processing from the URL, with GET method
        try:
            method = os.environ.get('REQUEST_METHOD')
            if method.lower() != "get":
                print "Content-type: text/plain\n"
                print method+" - unsupported method"
                return 2
            args    = cgi.FieldStorage()
            # name and line being mandatory, Ok reading or exception!
            if not args.has_key( "name" ):
                raise Usage( argv[0] )
            name       = args.getvalue ( "name" )
            name = name.replace('%','\\x')
            dbName = name
            name = name.replace('_',' ')
            if not args.has_key( "line" ):
                raise Usage( argv[0] )
            parentLine = args.getvalue ( "line" )
            verbose    = False
            if args.has_key( "verbose" ):
                if args.getvalue ( "verbose" ).lower() == 'true': verbose = True
            keepall = False
            if args.has_key( "keepall" ):
                if args.getvalue ( "keepall" ).lower() == 'true': keepall = True
        except:
            raise Usage( argv[0] )
        
        # The next section is the application part
        try:
            if verbose: 
                print "Content-type: text/plain\n"
                print "mpuu-makeptpdf.main() name = "+name+" line = "+parentLine
            config = mPuuConfiguration( verbose )
            if verbose: print "mpuu-makeptpdf.main() - making Personal Tree for:\n"+name
            try:
                personalTree = mPuuPersonalTreeDot( name, parentLine, verbose )
            except mPuuException, err:
                print "Content-type: text/plain\n"
                print err.msg
                return 2
            if verbose: print "mpuu-makeptpdf.main() - in directory:\n"+config.getTempDir()
            os.chdir ( config.getTempDir() )
            gviFileName = dbName+'_'+parentLine+'.gvi'
            if verbose: print "mpuu-makeptpdf.main() - file name:\n"+gviFileName
            fd = open ( gviFileName, 'w' )
            try:
                fd.write ( personalTree.getDotFile() )
            except mPuuException, err:
                fd.close()
                print "Content-type: text/plain\n"
                print err.msg
                return 2
            fd.close()
            # make the Graphviz conversion(s)
            dotoptions  = ' -Tps -o'+dbName+'_'+parentLine+'.ps'
            dotcmdline  = config.getDot()+dotoptions+' '+gviFileName
            if verbose: print "mpuu-makeptpdf.main() - launching Graphviz:\n"+dotcmdline
            fd = os.popen ( dotcmdline )
            while 1:
                oline = fd.readline()
                if not oline: break
                if verbose: print line.strip()
            fd.close()
            # make the PostScript to Portable Document Format (PDF) conversions
            psFileName = dbName+'_'+parentLine+'.ps'
            ps2pdfargs  = ' '+psFileName
            if verbose:
                pdfFileName = dbName+'_'+parentLine+'.pdf'
                ps2pdfargs += ' '+pdfFileName
            else:
                ps2pdfargs += ' -'
            ps2pdfcmdline = config.getPs2Pdf()+ps2pdfargs
            if verbose:
                print "mpuu-makeptpdf.main() - launching ps2pdf:\n"+ps2pdfcmdline
                output = os.popen ( ps2pdfcmdline )
                while 1:
                    oline = output.readline()
                    if not oline: break
                    if verbose: print oline.strip()
                output.close()
            else:
                print "Content-type: application/pdf\n"
                pipe = os.popen ( ps2pdfcmdline )
                sys.stdout.write( pipe.read() )
                pipe.close()
            # We're done, maybe a bit cleaning?
            if not keepall:
                os.remove ( gviFileName )
                os.remove ( psFileName )
                if verbose:
                    os.remove ( pdfFileName )
                    
            if verbose: print "mpuu-makeptpdf.main() - done."

            return 1

        except mPuuException, err:
            print "Content-type: text/plain\n"
            print err.msg
            return 2

    except Usage, err:
        print "Content-type: text/plain\n"
        print err.msg
        print __doc__
        return 2

# Allow execution of main() either from the python interpreter's command line
# or as a script, python being invoked by the first line's shebang.
if __name__ == "__main__":
    sys.exit( main() )


# end of module

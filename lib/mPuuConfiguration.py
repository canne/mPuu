#!/home/makijarv/usr/bin/python
# -*- coding: utf-8 -*-
"""
# -------------------------------------------------------------------
# Project     : mPuu - Makijarvi family tree database application
# Module      : mPuuConfiguration.py
# Description : Defines location of directories, utility-programs
#               and all the configurable parameters of the mPuu
#               database off-line processing.
#
# Author(s)   : Petri Makijarvi (pmakijarvi@users.sourceforge.net)
#
# License     : See distribution's LICENSE file
#
# This        : $Revision: 1.13 $
#
# Original    : 23 April 2006
# -------------------------------------------------------------------
"""

import os.path
import sys

from mPuuException import *

class mPuuConfiguration:
    """
    ----------------------------------------------------------------
    This class defines all the configurable parameters of the mPuu
    database off-line processing. Please feel free to edit it for
    your site.
    """
    def __init__ ( self, verbose=False ):
        """
        ----------------------------------------------------------------
        Create a datastructure of constants that the mPuu family classes
        can use to determine the location of files, directories and such.
        """
        if verbose: print ( "mPuuConfiguration.__init__()\n" )
        # ----------- Public data members, edit -----------
        #
        # Site's URL to the MediaWiki main index.php file
        #
        self.siteURL = 'http://www.makijarvi.fi/wiki/index.php'
        #
        # Your site's name as it would appear on printed graphs and such.
        #
        self.siteName = 'www.makijarvi.fi'
        #
        # Absolute path to the XML database main directory
        # (accessible to the Apache/PHP for read/write access)
        #
        # self.xmlDbBase = '/var/www/html/mPuu/db'
        self.xmlDbBase = '/home/makijarv/www/mPuu/db'
        #
        # Absolute path to the graphics output directory
        # (accessible to the Apache/PHP for read access)
        #
        # self.graphsBase = '/var/www/html/mPuu/graphs'
        self.graphsBase = '/home/makijarv/www/mPuu/graphs'
        #
        # Absolute path to the temporary directory that
        # will be used essentially by the cgi-bin scripts.
        # Note that this directory will (should) be cleaned
        # with a cron-job task every night!
        #
        # self.tempDir = '/var/www/html/mPuu/temp'
        self.tempDir = '/home/makijarv/www/mPuu/temp'
        #
        # Following is a list of the persons appearing
        # in the XML Personal Info database to whom a full
        # Family Tree graph will be generated. Logically
        # this would be the oldest ancestor in the family,
        # but anything else would go, naturally. All non-ASCII
        # characters must be given in UTF-8 format, for
        # example ''Jouko_M\xc3\xa4kij\xc3\xa4rvi.'
        #
        self.fullTreeList = ['Aatami Abrahaminpoika']
        #
        # Absolute path to the directory for the XHTML
        # output for towns, houses and other similar list
        #
        # self.xhtmlOutBase = '/var/www/html/mPuu/xhtml'
        self.xhtmlOutBase = '/home/makijarv/www/mPuu/xhtml'
        #
        # Absolute path to the AT&T Graphviz's dot-application
        #
        # self.dot = '/usr/bin/dot'
        self.dot = '/home/makijarv/usr/bin/dot'
        #
        # Absolute path to the ghostscript ps2pdf application
        #
        self.ps2pdf = '/usr/bin/ps2pdf13'
        #
        # You can select between A4,A3 and A0 printable presentation
        # of the Family Tree
        #
        self.ftpaper = 'A0'

        # ----------- Private methods, do not edit -----------
        if not os.path.isdir( self.xmlDbBase ):
            raise mPuuException ("\nmPuuConfiguration.__init__()\n"+\
                                 "XML DB directory does not exists:\n"+self.xmlDbBase)
        if not os.path.isdir( self.getPiDir() ):
            raise mPuuException ("\nmPuuConfiguration.__init__()\n"+\
                                 "XML DB directory does not exists:\n"+self.getPiDir() )
        if not os.path.isdir( self.graphsBase ):
            raise mPuuException ("\nmPuuConfiguration.__init__()\n"+\
                                 "Graphs directory does not exists:\n"+self.graphsBase)
        if not os.path.isdir( self.getPtDir() ):
            raise mPuuException ("\nmPuuConfiguration.__init__()\n"+\
                                 "Graphs directory does not exists:\n"+self.getPtDir() )
        if not os.path.isdir( self.getFtDir() ):
            raise mPuuException ("\nmPuuConfiguration.__init__()\n"+\
                                 "Graphs directory does not exists:\n"+self.getFtDir() )
        if not os.path.isdir( self.getTempDir() ):
            raise mPuuException ("\nmPuuConfiguration.__init__()\n"+\
                                 "Temp directory does not exists:\n"+self.tempDir )
        if not os.path.isdir( self.xhtmlOutBase ):
            raise mPuuException ("\nmPuuConfiguration.__init__()\n"+\
                                 "XHTML output directory does not exists:\n"+\
                                 self.xhtmlOutBase)
        if not os.path.isfile ( self.dot ):
            raise mPuuException ("\nmPuuConfiguration.__init__()\n"+\
                                 "Application does not exists:\n"+self.dot )
        if not os.path.isfile ( self.ps2pdf ):
            raise mPuuException ("\nmPuuConfiguration.__init__()\n"+\
                                 "Application does not exists:\n"+self.ps2pdf )

    def getSiteName ( self ):
        """
        ----------------------------------------------------------------
        Return the site's name to be used in graph footers and such.
        """
        return self.siteName

    def getPiDir ( self ):
        """
        ----------------------------------------------------------------
        Get the absolute path to the Personal Info XML database
        directory.
        """
        return self.xmlDbBase + '/pi'

    def getPiPath ( self, utf8DbPersonName ):
        """
        ----------------------------------------------------------------
        Get the full, absolute path to the Personal Info XML database
        file using the MediaWiki database record as a key.
        """
        return self.getPiDir()+'/'+utf8DbPersonName+'.xml'
        
    def getPtDir ( self ):
        """
        ----------------------------------------------------------------
        Get the absolute path to the Personal Tree graphics directory.
        """
        return self.graphsBase + '/pt'

    def getPtPath ( self, utf8DbPersonName, line='father', fileType='GRAPH' ):
        """
        ----------------------------------------------------------------
        Get the full, absolute path to the Personal Tree graphics
        or to its supporting files:
        fileType = 'GRAPH' - the graphics output file (default)
        fileType = 'CMAP'  - client side image map
        fileType = 'PDF'   - Portable Document Format file
        fileType = 'DESC'  - description file to generate graphics
        The default parent line is 'father'. Define argument excplictly
        for 'mother' parent line.
        """
        extension = '.png'
        if fileType == 'CMAP': extension = '.map'
        if fileType == 'PDF':  extension = '.pdf'
        if fileType == 'DESC': extension = '.gvi'
        return self.getPtPath()+'/'+utf8DbPersonName+'_'+line+extension

    def getFtDir ( self ):
        """
        ----------------------------------------------------------------
        Get the absolute path to the Family Tree graphics directory.
        """
        return self.graphsBase + '/ft'

    def getTempDir ( self ):
        """
        ----------------------------------------------------------------
        Get the absolute path to the (cgi-bin) temporary directory.
        """
        return self.tempDir

    def getXhtmlOutDir ( self ):
        """
        ----------------------------------------------------------------
        Get the absolute path to the XHTML output base directory
        """
        return self.xhtmlOutBase

    def getDot ( self ):
        """
        ----------------------------------------------------------------
        Returns the path to the Graphviz's dot-application in this system
        """
        return self.dot;

    def getPs2Pdf ( self ):
        """
        ----------------------------------------------------------------
        Returns the path to the ghostscript PS to PDF conversion program
        """
        return self.ps2pdf;

    def getDbPersonName ( self, utf8PersonName ):
        """
        ----------------------------------------------------------------
        If you have person's name in UTF-8 format with spaces and such,
        convert it to XML (and MySQL) database index format with this
        method.
        """
        return utf8PersonName.replace ( ' ', '_' )

    def getPersonalInfoURL ( self, utf8DbPersonName ):
        """
        ----------------------------------------------------------------
        Get the full path to the Person's 'home' page on the MediaWiki
        site. The database key name is given as an argument, it is
        converted to a valid URL address with full path.
        """
        return self.siteURL+'?title='+self.utf8ToURL ( utf8DbPersonName )

    def utf8ToURL ( self, utf8String ):
        """
        ----------------------------------------------------------------
        On Finnish (for example) pages you get often non-ASCII (> 80h)
        page names. We need to convert the database UTF-8 presentation
        presentable in format OK for the ASCII-based URL presentation.
        From other characters that can have an escape sequence we will
        convert only the space character.
        """
        converted =  [ self.escapeNonAscii( c ) for c in list( utf8String ) ]
        return "".join ( converted )

    def escapeNonAscii ( self, character ):
        """
        ----------------------------------------------------------------
        Return character in URL Escaped format if it isn't ASCII,
        otherwise return character as it is. "character" is a single
        character string. The space character is converted as well.
        """
        if  ord( character ) < 0x80 and not ord( character ) == 0x20:
            return character
        return "%%%2X" % ord( character )

    def getFtPaper ( self ):
        """
        ----------------------------------------------------------------
        What is the requested paper size for the printable format
        family tree. Currently user can select between A4 and A3 formats.
        """
        return self.ftpaper


        
if __name__ == "__main__":
    print "Library module, cannot be used alone"
    sys.exit( 2 )

# end of module

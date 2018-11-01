#!/home/makijarv/usr/bin/python
# -*- coding: utf-8 -*-
"""
# -------------------------------------------------------------------
# Project     : mPuu - Makijarvi family tree database application
# Module      : mPuuPlaces.py
# Description : Container with XTHML output for Places and Houses
#
# Author(s)   : Petri Makijarvi (pmakijarvi@users.sourceforge.net)
#
# License     : See distribution's LICENSE file
#
# This        : $Revision: 1.5 $
#
# Original    : 02 May 2006
# -------------------------------------------------------------------
"""

import glob
import sys

from mPuuConfiguration import *
from mPuuPersonalInfo import *

class mPuuPlaces ( mPuuConfiguration ):
    """
    ----------------------------------------------------------------
    This class is a container for two dictionaries, the Towns
    Dictionary and Houses Dictionary. In a typical use, an application
    instantiates a mPuuPlaces object, which will have the dictionaries
    emtpy. The application will then give the object a name of
    a person in the mPuu Personal Information XML database.
    The Towns and Houses defined with that person will be analyzed
    and added into the dictionaries. This would be most often
    a looping process. Once no more personal information is needed
    to analyze, the application can ask the object to return
    information about a specific Town or House. Derived classes
    of this base class would define courtesy methods to return
    rather formatted output, for example in XHTML format.

    This class is not intended to be used by the client application
    but as a base to the different output engine derived classes,
    such as XHTML or XML output.
    """
    def __init__( self, verbose=False ):
        """
        ----------------------------------------------------------------
        Create the Town Dictionary and the House Dictionary. They will
        be empty, of course. You can get debug information by defining
        verbose as True.
        """
        if verbose: print "mPuuPlaces.__init__()"
        self.verbose = verbose

        # Create the dictionaries
        self.townsDict  = {}
        self.housesDict = {}

        return

    def nextPersonalInfo ( self, utf8PathToFile ):
        """
        ----------------------------------------------------------------
        This method is used to fill the Town and Houses Dictionaries.
        The given file path points to a mPuu Personal Information XML
        database file. Read it and analyze the town/house information it
        and add to the corresponding dictionaries if required.
        """
        if self.verbose: print "mPuuPlaces.nextPersonalInfo("+utf8PathToFile+")"
        newPersonalInfo = mPuuPersonalInfo ( utf8PathToFile, self.verbose )
        personName = newPersonalInfo.getName()
        placesList = newPersonalInfo.getTownsHouses ( )
        if len( placesList) == 0:
            if self.verbose: print "mPuuPlaces.nexPersonalInfo() = no places."
            return
        for houseList in placesList:
            try:
                townName = houseList[0]
            except:
                raise mPuuException ("\nmPuuPlaces.nextPersonalInfo()\n"+\
                                     "Got a house list with no contents, not even the town.")
            if not self.townsDict.has_key( townName ):
                housesList = []
                personList = []
                townsItem  = [ housesList, personList ]
                self.townsDict[ townName ] = townsItem
            for houseName in houseList[1:]:
                if not houseName in self.townsDict[ townName ][0]:
                    self.townsDict[ townName ][0].append( houseName )
                if not self.housesDict.has_key( houseName ):
                    townsList = []
                    personList = []
                    housesItem = [ townsList, personList ]
                    self.housesDict[ houseName ] = housesItem
                if not townName in self.housesDict[ houseName ][0]:
                    self.housesDict[ houseName ][0].append( townName )
                if not personName in self.housesDict[ houseName ][1]:
                    self.housesDict[ houseName ][1].append( personName ) 
            if not personName in self.townsDict[ townName ][1]:
                self.townsDict[ townName ][1].append( personName )

        if self.verbose: print "mPuuPlaces.nextPersonalInfo() - Ok return."
        return

    def stopDataCollecting ( self, sort = True ):
        """
        ----------------------------------------------------------------
        Data is collected in this container with nextPersonalInfo()
        method. When there is no more data to add into the container,
        this method should be called.
        By default, the method sorts the contents of the Town and House
        Dictionaries. The boolean parameter 'sort' can be set to False
        to prevent this.
        """
        if self.verbose: print "mPuuPlaces.stopDataCollecting(",sort,")"

        if not sort: return

        for townsDictItemName, record in self.townsDict.iteritems():
            record[0].sort()
            record[1].sort()
            
        for housesDictItemName, record in self.housesDict.iteritems():
            record[0].sort()
            record[1].sort()
            
        if self.verbose: print "mPuuPlaces.stopDataCollecting() - dictionaries sorted."
        return
            
    def getTownsDictionary ( self ):        
        """
        ----------------------------------------------------------------
        This method returns the container's dictionary for town data.
        """
        return self.townsDict

    def getHousesDictionary ( self ):        
        """
        ----------------------------------------------------------------
        This method returns the container's dictionary for houses data.
        """
        return self.housesDict

class mPuuPlacesXHTML ( mPuuPlaces ):
    """
    ----------------------------------------------------------------
    This is the XHTML output implemantation of the (rather) abstract
    class of collecting town/house/person data for formatted output.
    """
    def __init__( self, verbose=False ):
        """
        ----------------------------------------------------------------
        Create the Town Dictionary and the House Dictionary. They will
        be empty, of course. You can get debug information by defining
        verbose as True.
        """
        if verbose: print "mPuuPlacesXHTML.__init__()"

        mPuuPlaces.__init__( self, verbose )

        if self.verbose: print "mPuuPlacesXHTML.__init__() - Ok return."
        return

    def allTowns ( self, outputDir ):
        """
        ----------------------------------------------------------------
        This courtesy method avoids you to retrieve the voluminous
        dictionaries of the base class. Collect the data in normal way,
        mark the stop of the data collection, then call this method.
        It will build the include files in XHTML format for all towns
        in the dictionary.
        """
        if self.verbose: print "mPuuPlacesXHTML.allTowns("+outputDir+")"

        try:
            os.chdir ( outputDir )
        except:
            raise mPuuException ("\nmPuuPlacesXHTML.allTowns()\n"+\
                                 "Cannot change to working directory: "+outputDir)
        
        for townsDictItemName, record in self.townsDict.iteritems():
            outputFileName = townsDictItemName + '_persons.xhtml'
            outputFileName = outputFileName.replace( ' ','_' )
            try:
                fd = open ( outputFileName, 'w' )
            except:
                raise mPuuException ("\nmPuuPlacesXHTML.allTowns()\n"+\
                                     "In data directory: "+outputDir+"\n"+\
                                     "Cannot create outputfile: "+outputFileName)
            outputStr = '<div class="mpuu-town-persons">'+"\n"
            firstItem = True
            for personName in record[1]:
                if not firstItem: outputStr += "&nbsp;|&nbsp;"
                outputStr += '<a href="index.php?title='+personName+'">'+personName+"</a>"
                firstItem = False
            outputStr += '\n</div>'
            fd.write( outputStr )
            fd.close()
            outputFileName = townsDictItemName + '_houses.xhtml'
            outputFileName = outputFileName.replace( ' ','_' )
            try:
                fd = open ( outputFileName, 'w' )
            except:
                raise mPuuException ("\nmPuuPlacesXHTML.allTowns()\n"+\
                                     "In data directory: "+outputDir+"\n"+\
                                     "Cannot create outputfile: "+outputFileName)
            outputStr = '<div class="mpuu-town-houses">'+"\n"
            firstItem = True
            for houseName in record[0]:
                if not firstItem: outputStr += "&nbsp;|&nbsp;"
                outputStr += '<a href="index.php?title='+houseName+'">'+houseName+"</a>"
                firstItem = False
            outputStr += '\n</div>'
            fd.write( outputStr )
            fd.close()

        if self.verbose: print "mPuuPlacesXHTML.allTowns() - Ok return."
        return

    def allHouses ( self, outputDir ):
        """
        ----------------------------------------------------------------
        This courtesy method avoids you to retrieve the voluminous
        dictionaries of the base class. Collect the data in normal way,
        mark the stop of the data collection, then call this method.
        It will build the include files in XHTML format for all towns
        in the dictionary.
        """
        if self.verbose: print "mPuuPlacesXHTML.allHouses("+outputDir+")"

        try:
            os.chdir ( outputDir )
        except:
            raise mPuuException ("\nmPuuPlacesXHTML.allHouses()\n"+\
                                 "Cannot change to working directory: "+outputDir)
        
        for housesDictItemName, record in self.housesDict.iteritems():
            outputFileName = housesDictItemName + '_towns.xhtml'
            outputFileName = outputFileName.replace( ' ','_' )
            try:
                fd = open ( outputFileName, 'w' )
            except:
                raise mPuuException ("\nmPuuPlacesXHTML.allHouses()\n"+\
                                     "In data directory: "+outputDir+"\n"+\
                                     "Cannot create outputfile: "+outputFileName)
            outputStr = '<div class="mpuu-house-towns">'+"\n"
            firstItem = True
            for townName in record[0]:
                if not firstItem: outputStr += "&nbsp;|&nbsp;"
                outputStr += '<a href="index.php?title='+townName+'">'+townName+"</a>"
                firstItem = False
            outputStr += '\n</div>'
            fd.write( outputStr )
            fd.close()
            outputFileName = housesDictItemName + '_persons.xhtml'
            outputFileName = outputFileName.replace( ' ','_' )
            try:
                fd = open ( outputFileName, 'w' )
            except:
                raise mPuuException ("\nmPuuPlacesXHTML.allHouses()\n"+\
                                     "In data directory: "+outputDir+"\n"+\
                                     "Cannot create outputfile: "+outputFileName)
            outputStr = '<div class="mpuu-house-persons">'+"\n"
            firstItem = True
            for personName in record[1]:
                if not firstItem: outputStr += "&nbsp;|&nbsp;"
                outputStr += '<a href="index.php?title='+personName+'">'+personName+"</a>"
                firstItem = False
            outputStr += '\n</div>'
            fd.write( outputStr )
            fd.close()

        if self.verbose: print "mPuuPlacesXHTML.allHouses() - Ok return."
        return

if __name__ == "__main__":
    print "Library module, cannot be used alone"
    sys.exit( 2 )

# end of module

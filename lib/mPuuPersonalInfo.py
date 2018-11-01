#!/home/makijarv/usr/bin/python
# -*- coding: utf-8 -*-
"""
# -------------------------------------------------------------------
# Project     : mPuu - Makijarvi family tree database application
# Module      : mPuuPersonalInfo.py
# Description : Read the personal information XML database file
#               and maintain its contents accessible in an object
#               structure.
#
# Author(s)   : Petri Makijarvi (pmakijarvi@users.sourceforge.net)
#
# License     : See distribution's LICENSE file
#
# This        : $Revision: 1.7 $
#
# Original    : 2006-04-14
# -------------------------------------------------------------------
"""

import os, os.path
import sys
#
# Sax2 that we are using is from PyXML project
try:
    from xml.dom.ext.reader import Sax2
    from xml.dom.ext import StripXml
except:
    absPath = os.path.abspath( sys.path[0] )
    PyXMLPath = absPath.rstrip('/mPuu/lib')+'/usr/lib/python2.4/site-packages'
    sys.path.insert ( 1, PyXMLPath )
    print sys.path
    import xml.dom.ext.reader.Sax2
    import xml.dom.ext.StripXml

from mPuuException import *

class mPuuPersonalInfo:
    """
    ----------------------------------------------------------------
    Class to read mPuu Personal Information XML-database file and
    present it as a memory loaded object.

    All methods in this class will raise mPuuException
    class exception in case of an error.
    """
    def __init__( self, utf8PathToFile, verbose ):
        """
        ----------------------------------------------------------------
        Read and parse the personal information data from a XML database
        file.
        """
        if verbose: print ( "mPuuPersonalInfo.__init__("+utf8PathToFile+")\n" )
        self.verbose = verbose

        self.filePath = utf8PathToFile
        # By default the input file has failed..
        self.valid = False
        # create Reader object
        reader = Sax2.Reader()
        # Read the document for parsing
        if verbose: print 'opening ' + utf8PathToFile
        try:
            doc = reader.fromStream( utf8PathToFile )
        except:
            if verbose: print 'Cannot open file!'
            raise mPuuException ("\nmPuuPersonalInfo.__init__()\n"+\
                                 "Cannot open file:\n"+utf8PathToFile)
        
        if verbose: print 'Read document, search for personalinfo tag'
        personalinfo_element = doc.documentElement
        if personalinfo_element.tagName != 'personalinfo':
            raise mPuuException ("\nmPuuPersonalInfo.__init__()\n"+\
                                 "Looking for initial personalinfo tag, failed.")
        if verbose: print 'Found personalinfo tag'


        self.eIdx = 1
        self.father = self.getElementData ( personalinfo_element, self.eIdx, 'father', verbose )
        if self.father == 'ERROR':
            raise mPuuException ("\nmPuuPersonalInfo.__init__()\n"+\
                                 "Looking for mandatory father tag and data, failed.")
        
        self.eIdx += 2
        self.mother = self.getElementData ( personalinfo_element, self.eIdx, 'mother', verbose )
        if self.mother == 'ERROR':
            raise mPuuException ("\nmPuuPersonalInfo.__init__()\n"+\
                                 "Looking for mandatory mother tag and data, failed.")
        
        self.eIdx += 2
        self.gender = self.getElementData ( personalinfo_element, self.eIdx, 'gender', verbose )
        if self.gender == 'ERROR':
            raise mPuuException ("\nmPuuPersonalInfo.__init__()\n"+\
                                 "Looking for mandatory gender tag and data, failed.")
        
        self.eIdx += 2
        self.birth = self.getElementData ( personalinfo_element, self.eIdx, 'birth', verbose )
        if self.birth == 'ERROR':
            raise mPuuException ("\nmPuuPersonalInfo.__init__()\n"+\
                                 "Looking for mandatory birth tag and data, failed.")
        
        self.eIdx += 2; silentProbe = True
        self.death = self.getElementData ( personalinfo_element, self.eIdx, 'death', verbose )
        if self.death == 'ERROR':
            raise mPuuException ("\nmPuuPersonalInfo.__init__()\n"+\
                                 "Looking for mandatory death tag and data, failed.")
        
        self.eIdx += 2
        self.name = self.getElementData ( personalinfo_element, self.eIdx, 'name', verbose )
        if self.name == 'ERROR':
            raise mPuuException ("\nmPuuPersonalInfo.__init__()\n"+\
                                 "Looking for mandatory name tag and data, failed.")
        
        self.eIdx += 2
        if self.probeReadChildData ( personalinfo_element, 'spouse', 'spousename',\
                                     'childname', verbose ) == 'ERROR':
            raise mPuuException ("\nmPuuPersonalInfo.__init__()\n"+\
                                 "Looking for optional set of  spouses, children "+\
                                 "data, failed.")
        self.spouses = self.subelements

        if self.probeReadChildData ( personalinfo_element, 'town', 'townname',\
                                     'housename', verbose ) == 'ERROR':
            raise mPuuException ("\nmPuuPersonalInfo.__init__()\n"+\
                                 "Looking for optional set of  town, houses data, "+\
                                 "failed.")
        self.towns = self.subelements

        self.Valid = True
        if verbose: print 'mPuuPersonalInfo.__init__(): OK return'
        return

    def getVerbose ( self ):
        """
        ----------------------------------------------------------------
        Returns the given verbose flag boolean state
        """
        return self.verbose

    def getFather ( self ):
        """
        ----------------------------------------------------------------
        Returns father's first name and surname in UTF-8 format
        """
        if not self.Valid: raise mPuuException ("\nmPuuPersonalInfo.getFather()\n"+\
                                                "Data is not valid.")
        return self.father.encode('utf-8')
        
    def getMother ( self ):
        """
        ----------------------------------------------------------------
        Returns mother's first name and surname in UTF-8 format
        """
        if not self.Valid: raise mPuuException ("\nmPuuPersonalInfo.getMother()\n"+\
                                                "Data is not valid.")
        return self.mother.encode('utf-8')
        
    def getParent ( self, parentline='father', getother=False ):
        """
        ----------------------------------------------------------------
        Returns one of the parent's first name and surname in UTF-8 format.
        If parent line selection argument is omitted, the default 'father'
        is used. It is possible to find the opposite parent by chaning
        the default False of 'getother' argument to True.
        """
        if not self.Valid: raise mPuuException ("\nmPuuPersonalInfo.getParent()\n"+\
                                                "Data is not valid.")
        useParentLine = parentline
        if getother:
            useParentLine = 'mother'
            if parentline == 'mother':
                useParentLine = 'father'
        if useParentLine == 'mother':
            return self.mother.encode('utf-8')
        return self.father.encode('utf-8')

    def getGender ( self ):
        """
        ----------------------------------------------------------------
        Returns gender as a single letter string (language deps!), but still in UTF-8 format
        """
        if not self.Valid: raise mPuuException ("\nmPuuPersonalInfo.getGender()\n"+\
                                                "Data is not valid.")
        return self.gender.encode('utf-8')
        
    def getBirth ( self ):
        """
        ----------------------------------------------------------------
        Returns birth date in ISO-8601 format YYYY-MM-DD, string in UTF-8
        """
        if not self.Valid: raise mPuuException ("\nmPuuPersonalInfo.getBirth()\n"+\
                                                "Data is not valid.")
        return self.birth
        
    def getBirthYear ( self ):
        """
        ----------------------------------------------------------------
        Returns birth year in format YYYY, string in UTF-8
        """
        if not self.Valid: raise mPuuException ("\nmPuuPersonalInfo.getBirthYear()\n"+\
                                                "Data is not valid.")
        return self.birth.split('-')[0]
        
    def getDeath ( self ):
        """
        ----------------------------------------------------------------
        Returns birth date in ISO-8601 format YYYY-MM-DD, string in UTF-8
        """
        if not self.Valid: raise mPuuException ("\nmPuuPersonalInfo.getDeath()\n"+\
                                                "Data is not valid.")
        return self.death

    def getDeathYear ( self ):
        """
        ----------------------------------------------------------------
        Returns death year, string in UTF-8
        """
        if not self.Valid: raise mPuuException ("\nmPuuPersonalInfo.getDeathYear()\n"+\
                                                "Data is not valid.")
        return self.death.birth.split('-')[0]
        
    def getName ( self ):
        """
        ----------------------------------------------------------------
        Returns person's first name and surname in UTF-8 format
        """
        if not self.Valid: raise mPuuException ("\nmPuuPersonalInfo.getName()\n"+\
                                                "Data is not valid.")
        return self.name.encode('utf-8')

    def getSpousesChildren ( self ):
        """
        ----------------------------------------------------------------
        Returns a list of lists, containing spouses names, followed by
        CHildren.

        For example:
        [[spouse1,child1,child2]] or [[spouse1,child2,child2][spouse2]].
        The list can be empty if no spouses. If the list is not empty,
        there is at least the spouse's name but not necessarily the children.
        """
        if not self.Valid: raise mPuuException ("\nmPuuPersonalInfo.getSpousesChildren()\n"+\
                                                "Data is not valid.")
        return self.spouses

    def getTownsHouses ( self ):
        """
        ----------------------------------------------------------------
        Returns a list of lists, containing town names, followed by house
        names.

        For example:
        [[town1,house1,house2]] or [[town1,house1,house2][town2]].
        The list can be empty if no towns. If the list is not empty,
        there is at least the town's name but not necessarily the houses.
        """
        if not self.Valid: raise mPuuException ("\nmPuuPersonalInfo.getTownsHouses()\n"+\
                                                "Data is not valid.")
        return self.towns

    def getFilePath ( self ):
        """
        ----------------------------------------------------------------
        Returns the XML database file path that was used to fill the object.
        """
        if not self.Valid: raise mPuuException ("\nmPuuPersonalInfo.getFilePath()\n"+\
                                                "Data is not valid.")
        return self.filePath

    def getDbName ( self ):
        """
        ----------------------------------------------------------------
        Returns the XML database (and therefore also MediaWiki MySQL
        record) name of the object. It is actually a UTF-8 string that
        is cut off from the full path (minus .xml-extension).
        See also: getFilePath()
        """
        if not self.Valid: raise mPuuException ("\nmPuuPersonalInfo.getDbName()\n"+\
                                                "Data is not valid.")
        xmlFileName = os.path.basename(self.filePath)
        splittedFileName = xmlFileName.split('.')
        return splittedFileName[0]

    def stripWs ( self, text ):
        """
        ----------------------------------------------------------------
        Remove redundant whitespace from a string
        """
        return ' '.join(text.split())

    def getElementData ( self, personalinfo_element, nodeNo, tagName,\
                         verbose, silentProbe=False ):
        """
        ----------------------------------------------------------------
        This private method is used to read an element and its data
        """
        try:
            element = personalinfo_element.childNodes[nodeNo]
            if element.tagName != tagName:
                if verbose and not silentProbe:
                    print 'Got tagName=' + element.tagName + ', ERROR return'
                return 'ERROR'
        except:
            if verbose and not silentProbe:
                print 'element ', nodeNo, ' has no tagName, ERROR return'
            return 'ERROR'
        retval = self.stripWs( element.firstChild.data )
        if verbose: print tagName + ': ' + retval.encode('utf-8')
        return retval

    def probeReadChildData ( self, personalinfo_element, elementTag,\
                             firstChildElementTag, childElementTags, verbose ):
        """
        ----------------------------------------------------------------
        This private method will deal with the repetive case of the
        spouse and town tags and their internal lists of children and
        houses, respectively.

        If the return value is not 'ERROR', the object's
        subelements-member is set as a list that contains lists of
        spousename, child1, child2,.. or town, house1, house2,...
        The analysis starts from the Node indicated by eIdx-attribute.
        The eIdx-attribute gets updated and advanced by this method if
        child data elements are found. Good return is 'OK'.
        """
        self.subelements = []; hasMoreSubNodes = True; silentProbe = True
        while hasMoreSubNodes:
            try:
                sub_element = personalinfo_element.childNodes[self.eIdx]
            except:
                hasMoreSubNodes = False
                break
            if sub_element.tagName == elementTag:
                if sub_element.hasChildNodes():
                    firstElementData = self.getElementData ( sub_element, 1, firstChildElementTag,\
                                                       verbose, silentProbe )
                    if firstElementData == 'ERROR':
                        if verbose:
                            print 'Found '+elementTag+', was expecting '+firstChildElementTag+\
                                  ', document is not well-formed'
                        return 'ERROR'
                    firstAndDeps = [firstElementData.encode('utf-8')]
                    hasMoreDeps = True; childNode = 3
                    while hasMoreDeps:
                        depsName = self.getElementData ( sub_element, childNode,\
                                                         childElementTags, verbose, silentProbe )
                        if depsName == 'ERROR': hasMoreDeps = False; break;
                        firstAndDeps.append( depsName.encode('utf-8') )
                        childNode += 2
                    self.eIdx += 2
                    self.subelements.append ( firstAndDeps )
                else:
                    if verbose:
                        print 'Found spouse element but without child elements, not well-formed'
                    return 'ERROR'
            else:
                hasMoreSubNodes = False
                break
        return 'OK'

if __name__ == "__main__":
    print "Library module, cannot be used alone"
    sys.exit( 2 )

# end of module

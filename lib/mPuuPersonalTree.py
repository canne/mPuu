#!/home/makijarv/usr/bin/python
# -*- coding: utf-8 -*-
"""
# -------------------------------------------------------------------
# Project     : mPuu - Makijarvi family tree database application
# Module      : mPuuPersonalTree.py
# Description : Builds person's personal family tree
#
# Author(s)   : Petri Makijarvi (pmakijarvi@users.sourceforge.net)
#
# License     : See distribution's LICENSE file
#
# This        : $Revision: 1.8 $
#
# Original    : 23 April 2006
# -------------------------------------------------------------------
"""

import glob
import sys

from mPuuConfiguration import *
from mPuuPersonalInfo import *

class mPuuPersonalTree ( mPuuConfiguration ):
    """
    ----------------------------------------------------------------
    Analyze the mPuu Personal Information XML database and build
    personal family tree in format of XML database object directory
    for a person in that database.

    This class is not intended to be used by the client application
    but as a base to the different output engine derived classes,
    such as AT&T Graphviz file format, or XML output.
    """
    def __init__( self, name, line='father', verbose=False ):
        """
        ----------------------------------------------------------------
        Make the tree for the person with 'name', given in UTF-8. By
        default, the family tree line is 'father', the other alternavite
        is, of course 'mother'. You can get debug information by defining
        verbose as True.
        """
        if verbose: print ( "mPuuPersonalTree.__init__("+name+','+line+")\n" )
        mPuuConfiguration.__init__ ( self, verbose )
        self.name = name;
        self.line = line;
        self.verbose = verbose
        
        # Directory container of personal info database objects:
        # Scan and parse all XML-files in this container.
        self.xmlPiDir = {}
        xmlFiles = glob.glob(self.getPiDir()+'/*.xml')
        for file in xmlFiles:
            newObj = mPuuPersonalInfo ( file, self.verbose )
            self.xmlPiDir[newObj.getName()] = ( newObj )

        # Make a descending list according to chosen parent line
        person = self.name
        self.parentLine = []
        while True:
            if verbose: print "mPuuPersonalTree.__init__(), probing: "+person
            try:
                parent = self.xmlPiDir[person].getParent( self.line )
            except:
                if verbose: print "mPuuPersonalTree.__init__(), not found."
                break # There is no Personal Information for this parent
            if parent == '?' or parent == '':
                if verbose: print "mPuuPersonalTree.__init__(), unknown (?)"
                break # The information is not available
            if verbose: print "mPuuPersonalTree.__init__(), found."
            self.parentLine.append ( parent )
            person = parent
        if len( self.parentLine ) == 0 and verbose:
            print "mPuuPersonalTree.__init__(): no parent line avaibale for:\n"+\
                  self.name

    def getDbName ( self ):
        """
        ----------------------------------------------------------------
        Get the database compatible name for the active person.
        """
        if self.verbose: print ( "mPuuPersonalTree.getDbName()\n" )
        try:
            dbName = self.xmlPiDir[self.name].getDbName()
        except:
            if self.verbose: print ( "mPuuPersonalTree.getDbName() - xmlPiDir[] exception.\n" )
            raise mPuuException ("\nmPuuPersonalTree.getDbName():\n"+\
                                 "Cannot resolve database name for"+'"'+self.name+'"')
        if self.verbose: print ( "mPuuPersonalTree.getDbName() - returning: "+dbName)
        return dbName

class mPuuPersonalTreeDot ( mPuuPersonalTree ):
    """
    ----------------------------------------------------------------
    This class is extending the mPuuPersonalTree class by
    producing an output for the AT&T's Graphviz-program's file
    format (.dot)
    """
    def __init__( self, name, line='father', verbose=False ):
        """
        ----------------------------------------------------------------
        Make the tree for the person with 'name', given in UTF-8. By
        default, the family tree line is 'father', the other alternavite
        is, of course 'mother'. You can get debug information by defining
        verbose as True.
        """
        if verbose: print ( "mPuuPersonalTreeDot.__init__("+name+','+line+")\n" )
        mPuuPersonalTree.__init__ ( self, name, line, verbose )

        # Start building the Graphviz dot-file, see test/PersonalTreeTemplate.dot
        self.dotfile  = u''
        self.dotfile += """// Format: AT&T Graphviz 2.8 (and greater)
// Generator: mPuuPersonalTreeDot $Revision: 1.8 $
graph personal_parent_tree {
    graph [bgcolor=white, center=1]; charset=Latin1;
    ranksep=.30; nodesep=.15; margin=.25; size = \"7.5,10\"; peripheries=0;
    subgraph cluster_c0 {
        node [shape=plaintext, fontsize=12, peripheries=0];
        {
            """
        # Print the timeline in years
        gviline = '"'+self.xmlPiDir[self.name].getBirthYear()+'"';
        prevparent = self.name; yearcumul = ''; gviprot = ''
        for nextparent in self.parentLine:
            try:
                if verbose: print "mPuuPersonalTreeDot.__init__(), birth years: probing: "+nextparent
                gviprot = ' -- "'+self.xmlPiDir[nextparent].getBirthYear()+'"'
            except:
                if self.xmlPiDir[prevparent].getParent( self.line ) == '?':
                    if verbose: print "mPuuPersonalTreeDot.__init__(), not found."
                    break # There is no Personal Information for this parent
                if verbose: print "mPuuPersonalTreeDot.__init__(), record not found, but name is valid."
                gviprot = ' -- "?"'
            if verbose: print "mPuuPersonalTreeDot.__init__(), ok, adding to timeline: "+gviprot
            yearcumul += gviprot
            prevparent = nextparent
        gviline += yearcumul+';'
        self.dotfile += gviline
        self.dotfile += """        } // birth years
    } // timeline
    subgraph cluster_c1 {
        node [shape=doubleoctagon, peripheries=2, color=black, fillcolor=\"#fefc94\",
              style=bold, style=filled, fontsize=12,
              URL=\""""
        gviline  = self.getPersonalInfoURL ( self.xmlPiDir[self.name].getDbName() )
        gviline += '"];\n'
        self.dotfile += gviline

        # Print the uppermost person, the person himself
        self.dotfile +="""        {
            { rank=same; """
        gviline = '"'+self.xmlPiDir[self.name].getBirthYear()+'"; "'+\
               unicode(self.name,'utf-8')+'";}'
        self.dotfile += gviline
        self.dotfile += """
        } // the top person"""

        # Loop printing the parents, and their parents, and ...
        prevparent = self.name; depth = 0; cumuldot = ''
        for nextparent in self.parentLine:
            try:
                if verbose: print "mPuuPersonalTreeDot.__init__(), parent nodes: probing: "+nextparent
                cumuldot += """
        node [shape=Mrecord,  peripheries=2, color=blue,
              style=filled, fontsize=12, group=\"parents\",
              URL=\""""
                gviline   = self.getPersonalInfoURL ( self.xmlPiDir[nextparent].getDbName() )
                gviline  += '"];\n'
                cumuldot += gviline
                cumuldot += """        {
            parent"""
                cumuldot += "%(parentrecordno)d" % { 'parentrecordno': (depth + 1) }
                cumuldot += """ [label=\"<f0> """
                gviline   = unicode( self.xmlPiDir[nextparent].getName(), 'utf-8' )
                cumuldot += gviline
                cumuldot += """|<f1> """
                gviline   = unicode( self.xmlPiDir[prevparent].getParent( self.line, True ), 'utf-8' )
                cumuldot += gviline
                cumuldot += """\"];
        }"""
                prevparent = nextparent
                depth += 1
            except:
                if self.xmlPiDir[prevparent].getParent( self.line ) == '?':
                    if verbose: print "mPuuPersonalTreeDot.__init__(), not found."
                    break # There is no Personal Information for this parent
                if verbose: print "mPuuPersonalTreeDot.__init__(), record not found, but name is valid."
                cumuldot = ''
                cumuldot += """
        node [shape=Mrecord,  peripheries=2, color="#ffffbc",
              style=filled, fontsize=12, group=\"parents\",
              URL=\""""
                gviline   = self.getPersonalInfoURL ( nextparent )
                gviline  += '"];\n'
                cumuldot += gviline
                cumuldot += """        {
            parent"""
                cumuldot += "%(parentrecordno)d" % { 'parentrecordno': (depth + 1) }
                cumuldot += """ [label=\"<f0> """
                gviline   = unicode( self.xmlPiDir[prevparent].getParent( self.line, False), 'utf-8' )
                cumuldot += gviline
                cumuldot += """|<f1> """
                gviline   = unicode( self.xmlPiDir[prevparent].getParent( self.line, True ), 'utf-8' )
                cumuldot += gviline
                cumuldot += """\"];
        }"""
                depth += 1
            self.dotfile += cumuldot

        # Print the relationship table
        self.dotfile += '\n\n    "'+unicode(self.name,'utf-8')+'"'
        if depth > 0: self.dotfile += ' -- parent1:f0;'
        self.dotfile += '\n'
        for i in range( 2, ( depth + 1) ):
            self.dotfile += '     parent%(1st)d:f0 -- parent%(2nd)d:f0;\n' % \
                       { '1st': (i - 1), '2nd': i }
        self.dotfile += """
    } // parent line cluster

    fontsize=8; fontname=Helvetica; 
    label = \""""
        self.dotfile += self.getSiteName()
        self.dotfile += """ - made with mPuu - graphs AT&T Graphviz\";

} // personal_parent_tree
"""
        if verbose: print self.dotfile.encode('iso-8859-1')

    def getDotFile ( self, encoding='latin-1' ):
        """
        ----------------------------------------------------------------
        The initialization of this object creates a Graphviz dot-file
        contents. You can retrieve it with this method using the
        character encoding of you wish. The default encoding is
        'latin-1' which is known to work with Graphviz PostScript
        output (PostScript is required to produce PDF).
        """
        return self.dotfile.encode( encoding )

if __name__ == "__main__":
    print "Library module, cannot be used alone"
    sys.exit( 2 )

# end of module

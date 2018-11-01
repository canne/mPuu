#!/home/makijarv/usr/bin/python
# -*- coding: utf-8 -*-
"""
# -------------------------------------------------------------------
# Project     : mPuu - Makijarvi family tree database application
# Module      : mPuuCrawler.py
# Description : Crawling the mPuu family tree, branch by branch
#
# Author(s)   : Petri Makijarvi (pmakijarvi@users.sourceforge.net)
#
# License     : See distribution's LICENSE file
#
# This        : $Revision: 1.14 $
#
# Original    : May 2006
# -------------------------------------------------------------------
"""

import sys

from mPuuConfiguration import *
from mPuuException import *
from mPuuPersonalInfo import *

class mPuuCrawler:
    """
    ----------------------------------------------------------------
    This is a recursive mPuu family tree crawler. Give it a mPuu
    Personal Information card object it will start to crawl towards
    the child end of it. For each child, its mPuu Personal Information
    card is opened and a new mPuuCrawler object is created to analyze
    it in a recursive manner.

    Unlinke many other mPuu classes, this class does not inherit the
    mPuuConfiguraton class for obvious performance reasons. Therefore
    you have to instantiate a single configuration object and give
    it to the new object so that it will be used but once.
    """
    def __init__(self, personObj, confObj, verbose=False,\
                 depth=1, node=1, yourName = '', outputType='gvi', childYears=True):
        """
        ----------------------------------------------------------------
        personObj  to analyze
        confObj    configuration information object
        verbose    to get debug printing
                   (personObj has its own verbose flag)
        depth      explains how far away we are from the first node
        node       unique node number within all analyzed persons
        yourName   If this is set, then the child (yourName) does not
                   have valid personObj. The given one is the parent's one,
                   from which we found yourName.
        outputType gvi: AT&T Graphviz dot-format (others...)
        childYears By default, include child birth years in the graph
        Warning, this recursive class is a memory hog and probably not
        suitable for really big trees. But we just slam in more money to
        get bigger memory and swap area, don't we?
        """
        if verbose: print "mPuuCrawler.__init__(), depth=", depth, ", node=", node
        self.depth = depth
        self.node = node
        self.confObj = confObj
        self.verbose = verbose
        self.inpVerbose = personObj.getVerbose()
        # For the time being, only dot-format output can be produced
        if outputType != 'gvi':
            raise mPuuException ("\nmPuuCrawler.__init__(), depth=", depth,\
                                 ", node=", node, "\n"+\
                                 "Unknown output format:\n"+outputType)
        # Prepare the work with the input object and the child instances
        self.newInstances = []
        self.parentObj = True
        self.personName = yourName
        if yourName == '':
            self.personName = personObj.getName()
            self.parentObj = False
        if verbose:
            print "mPuuCrawler.__init__(), depth=", depth, ", node=", node,\
                  ", personName=",self.personName,", yourName=",yourName
        # Start building the Graphviz dot-file node for this person
        self.nodeCode      = u''
        self.relationsCode = u''
        self.nodeCode += """
    node [shape=Mrecord, peripheries=2, color="""
        if self.parentObj:
            self.nodeCode += '"#ffffbc"'
        else:
            self.nodeCode += '"#80b1d3"'
        self.nodeCode += """, style=filled, fontsize=NODEFONTSIZE, margin=NODEMARGIN, group=\"persons\",
          URL=\""""
        self.nodeCode += confObj.getPersonalInfoURL ( confObj.getDbPersonName ( self.personName ) )
        self.nodeCode += '"];'
        self.nodeCode += """
         {
            person"""
        self.nodeCode += "%(nodenumber)d" % { 'nodenumber': self.node }
        self.nodeCode += """ [label=\"<f0> """
        self.nodeCode += unicode( self.personName, 'utf-8' )
        if childYears and self.depth == 1:
            self.nodeCode += "\\n("+personObj.getBirthYear()+')'
        # Are they any spouses, children defined?
        if self.parentObj:
            nofSpouses = 0
        else:
            self.spousesChildren = personObj.getSpousesChildren()
            nofSpouses = len ( self.spousesChildren )
            if verbose:
                print "mPuuCrawler.__init__(), depth=", self.depth, ", node=", self.node,\
                      ", Nof spouses=",len ( self.spousesChildren )
        myChildNodeCnt = 0; cumulativeBranchOffset = 0; childInstanceCnt = 0;
        for spouse in range ( 0, nofSpouses ):
            # Deal with a spouse and with their possible children
            if len( self.spousesChildren[spouse] ) < 1:
                raise mPuuException ("\nmPuuCrawler.__init__(), depth=", depth,\
                                     ", node=", node, "\n"+\
                                     "No spouse name in the spouce list at index:\n"+\
                                     spouse)
            nofChildrenWithThisSpouse = len( self.spousesChildren[spouse][1:] )
            if verbose:
                print "mPuuCrawler.__init__(), depth=", depth, ", node=", node,\
                      ", Spouse=", self.spousesChildren[spouse][0]
                print "mPuuCrawler.__init__(), depth=", depth, ", node=", node,\
                      ", NofChildren=", nofChildrenWithThisSpouse
            self.nodeCode += '|<f'
            self.nodeCode += "%(spousenumber)d" % { 'spousenumber': spouse + 1 }
            self.nodeCode += '> '
            if nofChildrenWithThisSpouse == 0: self.nodeCode += '('
            self.nodeCode += unicode( self.spousesChildren[spouse][0], 'utf-8' )
            if nofChildrenWithThisSpouse == 0: self.nodeCode += ')'
            for child in self.spousesChildren[spouse][1:]:
                # For each child, try to read the Personal Information
                if verbose:
                    print "mPuuCrawler.__init__(), depth=", depth, ", node=", node,\
                          ", Child=", child
                personPath = confObj.getPiPath ( confObj.getDbPersonName ( child ) )
                hasPersonalInfo = True; yourNameArg = ''
                try:
                    givePersonObj  = mPuuPersonalInfo ( personPath, self.inpVerbose )
                except:
                    # No personal information data available for this person
                    if verbose:
                        print "mPuuCrawler.__init__(), depth=", depth, ", node=", node,\
                              ", Child=", child, " - no data."
                    hasPersonalInfo = False
                    yourNameArg = child
                myChildNodeCnt += 1
                childNodeNumber = node + myChildNodeCnt + cumulativeBranchOffset
                if hasPersonalInfo:
                    # Create new instance for the children with a DB record
                    self.newInstances.append( mPuuCrawler( givePersonObj, confObj, verbose,\
                                                           depth + 1, childNodeNumber,\
                                                           yourNameArg, outputType ) )
                else:
                    # Build a node for the children with no DB record
                    self.newInstances.append( mPuuCrawler( personObj, confObj, verbose,\
                                                           depth + 1, childNodeNumber,\
                                                           yourNameArg, outputType ) )
                childInstanceCnt += 1
                if verbose:
                    print "mPuuCrawler.__init__(), depth=", depth, ", node=", node,\
                              ", childInstanceCnt=", childInstanceCnt
                    print "mPuuCrawler.__init__(), depth=", depth, ", node=", node,\
                              ", childNodeNumber=", childNodeNumber
                cumulativeBranchOffset += self.newInstances[childInstanceCnt-1].branchNodes()
                if verbose:
                    print "mPuuCrawler.__init__(), depth=", depth, ", node=", node,\
                              ", cumulativeBranchOffset=", cumulativeBranchOffset
                self.relationsCode 
                self.relationsCode += """
    person"""
                self.relationsCode += '%(parentnode)d:f%(spousenumber)d -> ' % \
                                        { 'parentnode': self.node, 'spousenumber': spouse + 1 }
                self.relationsCode += 'person%(childnodenumber)d:f0' % \
                                        { 'childnodenumber': childNodeNumber }
                self.relationsCode += ' [fontsize=RELATIONFONTSIZE, color='
                if hasPersonalInfo:
                    self.relationsCode += 'black'
                else:
                    self.relationsCode += '"#999999"'
                if childYears and hasPersonalInfo:
                    childBirthYear = givePersonObj.getBirthYear()
                    self.relationsCode += ' label="'+childBirthYear+'"'
                self.relationsCode += '];'

        # Let's close the person - spouses node
        self.nodeCode += """\"];
         }"""

        if verbose:
            print "mPuuCrawler.__init__(), depth=", self.depth, ", node=", self.node,\
                  ": - done: branch's depth below: ", self.branchMaxDepth() - self.depth
        return 

    def branchNodes( self ):
        """
        ----------------------------------------------------------------
        Return how many nodes there are in the branch, below this node.
        We will ask from the children nodes, how many nodes they have.
        They will ask from their children, and so on. We know how many
        children nodes we do have, and will add that to the sum.
        """
        retval = 0;
        for i in range( 0, len( self.newInstances ) ):
            retval += self.newInstances[i].branchNodes()
        retval += len( self.newInstances )
        return retval

    def branchMaxDepth( self ):
        """
        ----------------------------------------------------------------
        This method will probe for the deepest node depth number value
        in this branch. Although the method can be called by the client
        it is intended to be a private method. In this case the calling
        node knows at which level it is and by a simple subtraction can
        determine how many levels there is in the branch below its own
        level
        """
        retval = self.depth;
        for i in range( 0, len( self.newInstances ) ):
            newDepth = self.newInstances[i].branchMaxDepth()
            if newDepth > retval: retval = newDepth
        return retval

    def getDotFile( self, printableFormat=False, encoding='latin-1' ):
        """
        ----------------------------------------------------------------
        While crawling the mPuu tree branches, AT&T Graphviz dot-file
        format presentation of family members and their parental relations
        is build. Get the contents of that file with this method.
        The default encoding is 'latin-1' which is known to work
        with Graphviz PostScript output (PostScript is required to
        produce PDF). If you want to produce PostScript for printable
        page, set 'printableFormat=True'.
        """
        if self.depth != 1: return
        retval = u''
        retval += """// Format: AT&T Graphviz 2.8 (and greater)
// Generator: mPuuCrawler $Revision: 1.14 $
digraph family_tree {
    graph [bgcolor=white, center=1]; charset=Latin1;"""
        if printableFormat:
            retval += ' orientation=landscape;'
            if self.confObj.getFtPaper().upper() == 'A4':
                # A4 = 8.27 x 11.69 inches
                retval += """    ranksep=.30; rankdir=LR;"""
                retval += ' size="8.1,11.5"'
                retval += """ nodesep=.15; margin=.25;
                """
            elif self.confObj.getFtPaper().upper() == 'A3':
                # A3 = 11.69 x 16.54
                retval += """    ranksep=.30; rankdir=LR;"""
                retval += ' size="11.2,16.4"'
                retval += """ nodesep=.15; margin=.25;
                """
            else:
                # A0 = 33.11 x 46.81
                retval += """    ranksep=4.0 rankdir=BT;"""
                #LR### retval += ' size="33.0,46.7"'
                retval += ' size="46.7,33.0"'
                retval += """ imagescale=true; nodesep=.02; margin=.10;
                """
        else:
            retval += """    ranksep=1.0; rankdir=LR;"""
            retval += """ nodesep=.15; margin=.25; 
            """
        retval += self.getNodeCode( encoding );
        retval += self.getRelationsCode( encoding );
        retval += """
    fontsize=BANNERFONTSIZE; fontname=Helvetica; 
    label = \""""
        retval += self.confObj.getSiteName()
        retval += """ - made with mPuu - graphs AT&T Graphviz\";

} // family_tree
"""
        if printableFormat:
            if self.confObj.getFtPaper().upper() == 'A0':
                retval = retval.replace('NODEFONTSIZE','8')
                retval = retval.replace('NODEMARGIN','0.02')
                retval = retval.replace('RELATIONFONTSIZE','7')
                retval = retval.replace('BANNERFONTSIZE','7')
            else:
                retval = retval.replace('NODEFONTSIZE','8')
                retval = retval.replace('NODEMARGIN','0.05')
                retval = retval.replace('RELATIONFONTSIZE','7')
                retval = retval.replace('BANNERFONTSIZE','7')
        else:
            retval = retval.replace('NODEFONTSIZE','10')
            retval = retval.replace('NODEMARGIN','0.05')
            retval = retval.replace('RELATIONFONTSIZE','8')
            retval = retval.replace('BANNERFONTSIZE','8')
        if self.verbose:
            print "mPuuCrawler.getDotFile(), depth=", self.depth, ", node=", self.node,\
                  ": dotFile contents:\n"+self.nodeCode.encode('iso-8859-1')
        return retval.encode( encoding )

    def getNodeCode( self, encoding='latin-1' ):
        """
        ----------------------------------------------------------------
        This private methods goes through all the nodes and retrieves
        the generated node code.
        """
        retval = u''
        retval += self.nodeCode;
        for i in range( 0, len( self.newInstances ) ):
            retval += self.newInstances[i].getNodeCode( )
        if self.verbose:
            print "mPuuCrawler.getNodeCode(), depth=", self.depth, ", node=", self.node,\
                  ":  self.nodeCode:\n"+self.nodeCode.encode('iso-8859-1')
        return retval

    def getRelationsCode( self, encoding='latin-1' ):
        """
        ----------------------------------------------------------------
        This private methods goes through all the nodes and retrieves
        the generated node code.
        """
        retval = u''
        retval += self.relationsCode;
        for i in range( 0, len( self.newInstances ) ):
            retval += self.newInstances[i].getRelationsCode( )
        if self.verbose:
            print "mPuuCrawler.getNodeCode(), depth=", self.depth, ", node=", self.node,\
                  ":  self.relationsCode:\n"+self.relationsCode.encode('iso-8859-1')
        return retval



if __name__ == "__main__":
    print "Library module, cannot be used alone"
    sys.exit( 2 )

# end of module

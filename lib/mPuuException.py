#!/home/makijarv/usr/bin/python
# -*- coding: utf-8 -*-
"""
# -------------------------------------------------------------------
# Project     : mPuu - Makijarvi family tree database application
# Module      : mPuuException.py
# Description : Definition of the exception class for mPuu-classes
#
# Author(s)   : Petri Makijarvi (pmakijarvi@users.sourceforge.net)
#
# License     : See distribution's LICENSE file
#
# This        : $Revision: 1.3 $
#
# Original    : 25 April 2006
# -------------------------------------------------------------------
"""

import sys

class mPuuException ( Exception ):
    """
    ----------------------------------------------------------------
    This type of error will arise if the methods of the objects in
    various mPuu-class modules do fail.
    """
    def __init__(self, msg):
        """
        ----------------------------------------------------------------
        Memorize the error message given by the failed method
        """
        self.msg = msg

if __name__ == "__main__":
    print "Library module, cannot be used alone"
    sys.exit( 2 )

# end of module

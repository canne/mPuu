#!/home/makijarv/usr/bin/python
# -*- coding: utf-8 -*-
"""
# -------------------------------------------------------------------
# Project     : mPuu - Makijarvi family tree database application
# Module      :
# Description :
#
# Author(s)   : Petri Makijarvi (pmakijarvi@users.sourceforge.net)
#
# License     : See distribution's LICENSE file
#
# This        : $Revision: 1.2 $
#
# Original    :
# -------------------------------------------------------------------
"""

import sys

from mPuuConfiguration import *

class mPuuXXX( mPuuConfiguration ):
    """
    ----------------------------------------------------------------
    This is an example class that derives from the configuration
    information.
    """
    def __init__(self, myParameter):
        """
        ----------------------------------------------------------------
        Description of the init-method
        """
        mPuuConfiguration.__init__ ( self )
        self.myParameter = myParameter

if __name__ == "__main__":
    print "Library module, cannot be used alone"
    sys.exit( 2 )

# end of module

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2025-03-25 at 09:57

@author: cook
"""
from pogos.core import base
from pogos.resources.demos import soss_demo
from pogos.resources.demos import miri_demo
from pogos.resources.demos import bots_g395_demo as g395_demo
from pogos.resources.demos import bots_prism_demo as prism_demo

# =============================================================================
# Define instrument short names
# =============================================================================
soss = 'JWST.NIRISS.SOSS'
prism = 'JWST.NIRSPEC.BOTS.PRISM'
g395 = 'JWST.NIRSPEC.BOTS.G395M'
miri_im = 'JWST.MIRI.IMAGING'

# =============================================================================
# Define storage
# =============================================================================
# fill this with the instrument modes
DEMOS = dict()
for instrument in base.INSTRUMENTS:
    DEMOS[instrument] = dict()

# =============================================================================
# Define usable demos
# =============================================================================
# # JWST.NIRISS.SOSS demos
DEMOS[soss]['t1b.sossisse'] = soss_demo.SossTrappist1bDemo

# # JWST.NIRSPEC.BOTS.PRISM demos
DEMOS[prism]['wasp39b.sossisse'] = prism_demo.BotsPrismDemo_WASP39b
DEMOS[g395]['wasp39b.sossisse'] = g395_demo.BotsG395Demo_WASP39b

# JWST.MIRI.IMAGING demo
DEMOS[miri_im]['miri.im.lhs1140'] = miri_demo.MiriImagingDemo_LHS1140



# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # print 'Hello World!'
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================

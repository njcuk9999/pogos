#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2025-03-25 at 09:57

@author: cook
"""
from pogos.core import base
from pogos.core import definitions
from pogos.demos import soss_demo
from pogos.demos import miri_demo
from pogos.demos import bots_g395_demo as g395_demo
from pogos.demos import bots_prism_demo as prism_demo

# =============================================================================
# Define instrument short names
# =============================================================================
soss = 'JWST.NIRISS.SOSS'
prism = 'JWST.NIRSPEC.BOTS.PRISM'
g395 = 'JWST.NIRSPEC.BOTS.G395H'
miri_im = 'JWST.MIRI.IMAGING'

# =============================================================================
# Define storage
# =============================================================================
# fill this with the instrument modes
DEMOS = dict()
for instrument_mode in definitions.ENABLED_INST_MODES:
    DEMOS[instrument_mode.name] = dict()

# =============================================================================
# Define usable demos
# =============================================================================
# # JWST.NIRISS.SOSS demos
DEMOS[soss]['t1b.sossisse'] = soss_demo.SossTrappist1bDemo
DEMOS[soss]['wasp39b.substrip256'] = soss_demo.SossWasp39bDemo
DEMOS[soss]['hatp11b.substrip96'] = soss_demo.SossHatP11bDemo

# # JWST.NIRSPEC.BOTS.PRISM demos
DEMOS[prism]['wasp39b.sossisse'] = prism_demo.BotsPrismDemo_WASP39b
DEMOS[prism]['toi2525c.sub512'] = prism_demo.BotsPrismDemo_TOI2525c
DEMOS[prism]['wasp52b.sub512s'] = prism_demo.BotsPrismDemo_WASP52b
DEMOS[prism]['wd1856b.sub2048'] = prism_demo.BotsPrismDemo_WD1856b

# JWST.NIRSPEC.BOTS.G395H demos
DEMOS[g395]['wasp39b.nrs1nrs2'] = g395_demo.BotsG395HDemo_WASP39b

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

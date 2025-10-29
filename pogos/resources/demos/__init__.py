#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2025-03-25 at 09:57

@author: cook
"""
from pogos.core import base
from pogos.resources.demos import soss_t1b_sossisse
from pogos.resources.demos import soss_t1b_sossisse_sorbet
from pogos.resources.demos import soss_t1b_sorbet
from pogos.resources.demos import prism_wasp39b_sossisse
from pogos.resources.demos import g395_wasp39b_sossisse
from pogos.resources.demos import miri_im_lhs1140_tsovore
from pogos.resources.demos import miri_im_lhs1140_miriam
from pogos.resources.demos import miri_im_lhs1140_tsovore_miriam


# =============================================================================
# Define instrument short names
# =============================================================================
soss = 'JWST.NIRISS.SOSS'
prism = 'JWST.NIRSPEC.PRISM'
g395 = 'JWST.NIRSPEC.G395'
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
# JWST.NIRISS.SOSS demos
DEMOS[soss]['t1b.sossisse'] = soss_t1b_sossisse
DEMOS[soss]['t1b.sorbet'] = soss_t1b_sorbet
DEMOS[soss]['t1b.sossisse+sorbet'] = soss_t1b_sossisse_sorbet

# JWST.NIRSPEC.PRISM demos
DEMOS[prism]['wasp39b.sossisse'] = prism_wasp39b_sossisse
DEMOS[g395]['wasp39b.sossisse'] = g395_wasp39b_sossisse

# JWST.MIRI.IMAGING demo
DEMOS[miri_im]['miri.im.lhs1140.miriam'] = miri_im_lhs1140_miriam
DEMOS[miri_im]['miri.im.lhs1140.tsovore'] = miri_im_lhs1140_tsovore
DEMOS[miri_im]['miri.im.lhs1140.tsovore+miriam'] = miri_im_lhs1140_tsovore_miriam


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

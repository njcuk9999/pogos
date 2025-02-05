#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2024-10-29 at 09:30

@author: cook
"""
from pogos.core import base
from pogos.constants import tsovore
from pogos.constants import miriam
from pogos.constants import sorbet

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'pogos.core.startup.py'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__

# set constant dictionaries
TSOVORE_SimCDict = tsovore.SimCDict
TSOVORE_ImCDict = tsovore.ImCDict
MIRIAM_CDict = miriam.CDict
SORBET_WLCTA_CDict = sorbet.WLCTA_CDict
SORBET_SLCTA_CDict = sorbet.SLCTA_CDict
SORBET_TFIT_CDict = sorbet.TFIT_CDict
SORBET_RV_CDict = sorbet.RV_CDict


# =============================================================================
# End of code
# =============================================================================

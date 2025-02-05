#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2024-10-29 at 09:30

@author: cook
"""

from aperocore.constants import constant_functions

from pogos.core import base

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'pogos.constants.constants.py'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__

# Constants definition
Const = constant_functions.Const
ConstDict = constant_functions.ConstantsDict


# =============================================================================
# Simulation module constants for TSOVORE
# =============================================================================
SimCDict = ConstDict(__NAME__)

# set the title for output yaml files
SimCDict.title = SimCDict.yaml_title('TSOVORE-Simulation',
                                     setup_program=None,
                                     version=base.TSOVORE_SIM_VERSION,
                                     date=base.TSOVORE_SIM_DATE)
# Debug parameter
SimCDict.add('DEBUG', value=False, dtype=bool, source=__NAME__,
             user=True, active=True, description='Enable debugging')

# =============================================================================
# Image calibration module constants for TSOVORE
# =============================================================================
ImCDict  = ConstDict(__NAME__)

# set the title for output yaml files
ImCDict.title = ImCDict.yaml_title('TSOVORE-ImageCalibration',
                                   setup_program=None,
                                   version=base.TSOVORE_IMCAL_VERSION,
                                   date=base.TSOVORE_IMCAL_DATE)
# Debug parameter
ImCDict.add('DEBUG', value=False, dtype=bool, source=__NAME__,
             user=True, active=True, description='Enable debugging')

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

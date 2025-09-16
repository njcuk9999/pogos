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
# General constants for TSOVORE
# =============================================================================
TSOVORE_CDict = ConstDict(__NAME__)

# set the title for output yaml files
TSOVORE_CDict.title = TSOVORE_CDict.yaml_title('TSOVORE',
                                   setup_program=None,
                                   version=base.TSOVORE_VERSION,
                                   date=base.TSOVORE_DATE)


# =============================================================================
# Simulation module constants for TSOVORE
# =============================================================================
# set the group for all simulation constants
group = 'SIM'
TSOVORE_CDict.add_group(group, description='Configs for TSOVORE.SIM',
                  source=__NAME__, user=True, active=True)

# Debug parameter
TSOVORE_CDict.add('DEBUG', value=False, dtype=bool, source=__NAME__,
            user=True, active=True, group=group,
            description='Enable debugging')

# =============================================================================
# Image calibration module constants for TSOVORE
# =============================================================================
# set the group for all image calibration constants
group = 'IMCAL'
TSOVORE_CDict.add_group(group, description='Configs for TSOVORE.IMCAL',
                  source=__NAME__, user=True, active=True)

# Debug parameter
TSOVORE_CDict.add('DEBUG', value=False, dtype=bool, source=__NAME__,
             user=True, active=True, group=group,
            description='Enable debugging')

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

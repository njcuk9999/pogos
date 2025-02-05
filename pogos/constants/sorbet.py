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
# Constants for SORBET white light curve transit analysis
# =============================================================================
WLCTA_CDict = ConstDict(__NAME__)

# set the title for output yaml files
WLCTA_CDict.title = WLCTA_CDict.yaml_title('SORBET: White light curve transit '
                                           'analysis',
                                     setup_program=None,
                                     version=base.SORBET_WLCTA_VERSION,
                                     date=base.SORBET_WLCTA_DATE)

# Debug parameter
WLCTA_CDict.add('DEBUG', value=False, dtype=bool, source=__NAME__,
                user=True, active=True, description='Enable debugging')

# =============================================================================
# Constants for SORBET spectral light curve transit analysis
# =============================================================================
SLCTA_CDict = ConstDict(__NAME__)

# set the title for output yaml files
SLCTA_CDict.title = SLCTA_CDict.yaml_title('SORBET: Spectral light curve '
                                           'transit analysis',
                                           setup_program=None,
                                           version=base.SORBET_SLCTA_VERSION,
                                           date=base.SORBET_SLCTA_DATE)
# Debug parameter
SLCTA_CDict.add('DEBUG', value=False, dtype=bool, source=__NAME__,
                user=True, active=True, description='Enable debugging')

# =============================================================================
# Constants for SORBET tfit module
# =============================================================================
TFIT_CDict = ConstDict(__NAME__)

# set the title for output yaml files
TFIT_CDict.title = TFIT_CDict.yaml_title('SORBET: TFIT',
                                         setup_program=None,
                                         version=base.SORBET_TFIT_VERSION,
                                         date=base.SORBET_TFIT_DATE)
# Debug parameter
TFIT_CDict.add('DEBUG', value=False, dtype=bool, source=__NAME__,
               user=True, active=True, description='Enable debugging')


# =============================================================================
# Constants for SORBET RV module
# =============================================================================
RV_CDict = ConstDict(__NAME__)

# set the title for output yaml files
RV_CDict.title = RV_CDict.yaml_title('SORBET: RV Module',
                                     setup_program=None,
                                     version=base.SORBET_RV_VERSION,
                                     date=base.SORBET_RV_DATE)
# Debug parameter
RV_CDict.add('DEBUG', value=False, dtype=bool, source=__NAME__,
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

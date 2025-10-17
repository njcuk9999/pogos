#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2024-10-29 at 09:35

@author: cook
"""
from pathlib import Path

import yaml
import sossisse

# =============================================================================
# Define variables
# =============================================================================
__PACKAGE__ = 'pogos'
__PATH__ = Path(__file__).parent.parent
__INSTRUMENT__ = 'None'
# load the yaml file
__YAML__ = yaml.load(open(__PATH__.joinpath('info.yaml')),
                     Loader=yaml.FullLoader)

# =============================================================================
# Get variables from info.yaml
# =============================================================================
__version__ = __YAML__['DRS.VERSION']
__authors__ = __YAML__['DRS.AUTHORS']
__date__ = __YAML__['DRS.DATE']
__release__ = __YAML__['DRS.RELEASE']

# =============================================================================
# Define core variables
# =============================================================================
# supported instruments modes
# JWST NIRISS SOSS
INSTRUMENTS = ['JWST.NIRISS.SOSS',
               'JWST.NIRISS.FGS',
               'JWST.NIRSPEC.PRISM',
               'JWST.NIRSPEC.G395',
               'JWST.NIRSPEC.G253',
               'JWST.NIRSPEC.G140',
               'JWST.MIRI.IMAGING']

# =============================================================================
# Define sub module functionality
# =============================================================================

# TSOVORE image calibration module
TSOVORE_VERSION = __YAML__['TSOVORE.VERSION']
TSOVORE_DATE = __YAML__['TSOVORE.DATE']

# MIRIAM module
MIRIAM_VERSION = __YAML__['MIRIAM.VERSION']
MIRIAM_DATE = __YAML__['MIRIAM.DATE']

# SORBET module - general
SORBET_VERSION = __YAML__['SORBET.VERSION']
SORBET_DATE = __YAML__['SORBET.DATE']

# set up external modules (still using apero-core)
EXTERNAL_CONST = dict()
EXTERNAL_CONST['SOSSISSE'] = sossisse.CDict


# =============================================================================
# Base functionality
# =============================================================================
class pogosException(Exception):
    def __init__(self, message):
        super().__init__(message)




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

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
               'JWST.NIRSPEC.G140']

# =============================================================================
# Define sub module functionality
# =============================================================================
# TSOVORE simulation module
TSOVORE_SIM_VERSION = __YAML__['TSOVORE.SIM.VERSION']
TSOVORE_SIM_DATE = __YAML__['TSOVORE.SIM.DATE']

# TSOVORE image calibration module
TSOVORE_IMCAL_VERSION = __YAML__['TSOVORE.IMCAL.VERSION']
TSOVORE_IMCAL_DATE = __YAML__['TSOVORE.IMCAL.DATE']

# MIRIAM module
MIRIAM_VERSION = __YAML__['MIRIAM.VERSION']
MIRIAM_DATE = __YAML__['MIRIAM.DATE']

# SORBET module - white light curve transit fit
SORBET_WLCTA_VERSION = __YAML__['SORBET.WLCTA.VERSION']
SORBET_WLCTA_DATE = __YAML__['SORBET.WLCTA.DATE']

# SORBET module - spectral light curve transit fit
SORBET_SLCTA_VERSION = __YAML__['SORBET.SLCTA.VERSION']
SORBET_SLCTA_DATE = __YAML__['SORBET.SLCTA.DATE']

# SORBET module - transit fit code
SORBET_TFIT_VERSION = __YAML__['SORBET.TFIT.VERSION']
SORBET_TFIT_DATE = __YAML__['SORBET.TFIT.DATE']

# SORBET module - radial velocity module
SORBET_RV_VERSION = __YAML__['SORBET.RV.VERSION']
SORBET_RV_DATE = __YAML__['SORBET.RV.DATE']

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

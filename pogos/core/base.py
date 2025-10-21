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
# Define all instruments and their sub-modes (related to our instrument names)
# =============================================================================
INSTRUMENT_MODES = dict()

# JWST NIRISS
INSTRUMENT_MODES['JWST.NIRISS'] = dict()
INSTRUMENT_MODES['JWST.NIRISS']['SOSS'] = 'JWST.NIRISS.SOSS'
INSTRUMENT_MODES['JWST.NIRISS']['FGS'] = 'JWST.NIRISS.FGS'
INSTRUMENT_MODES['JWST.NIRISS']['AMI'] = None
# JWST NIRSPEC
INSTRUMENT_MODES['JWST.NIRSPEC'] = dict()
INSTRUMENT_MODES['JWST.NIRSPEC']['BOTS.PRISM'] = 'JWST.NIRSPEC.PRISM'
INSTRUMENT_MODES['JWST.NIRSPEC']['BOTS.G395'] = 'JWST.NIRSPEC.G395'
INSTRUMENT_MODES['JWST.NIRSPEC']['BOTS.G253'] = 'JWST.NIRSPEC.G253'
INSTRUMENT_MODES['JWST.NIRSPEC']['BOTS.G140'] = 'JWST.NIRSPEC.G140'
INSTRUMENT_MODES['JWST.NIRSPEC']['FS'] = None
INSTRUMENT_MODES['JWST.NIRSPEC']['MOSS'] = None
INSTRUMENT_MODES['JWST.NIRSPEC']['IFU'] = None
# JWST NIRCam
INSTRUMENT_MODES['JWST.NIRCAM'] = dict()
INSTRUMENT_MODES['JWST.NIRCAM']['IMAGING'] = None
INSTRUMENT_MODES['JWST.NIRCAM']['WFSS'] = None
INSTRUMENT_MODES['JWST.NIRCAM']['CORON'] = None
INSTRUMENT_MODES['JWST.NIRCAM']['TSO-IMAGING'] = None
INSTRUMENT_MODES['JWST.NIRCAM']['TSO-GRISM'] = None
# JWST MIRI
INSTRUMENT_MODES['JWST.MIRI'] = dict()
INSTRUMENT_MODES['JWST.MIRI']['IMAGING'] = 'JWST.MIRI.IMAGING'
INSTRUMENT_MODES['JWST.MIRI']['LRS'] = None
INSTRUMENT_MODES['JWST.MIRI']['MRS'] = None
INSTRUMENT_MODES['JWST.MIRI']['CORON'] = None
INSTRUMENT_MODES['JWST.MIRI']['WFSS'] = None

# =============================================================================
# Define all reduction steps
# =============================================================================
RED_STEPS = dict()
RED_STEPS['Pre-extraction'] = dict()
RED_STEPS['Pre-extraction']['IDT:SOSS'] = None
RED_STEPS['Pre-extraction']['TSOVORE'] = None
RED_STEPS['Pre-extraction']['NAMELESS'] = None
RED_STEPS['Pre-extraction']['Eureka'] = None
RED_STEPS['Pre-extraction']['exoTEFRF'] = None

RED_STEPS['Extraction'] = dict()
RED_STEPS['Extraction']['SOSSISSE'] = ['JWST.NIRISS.SOSS',
                                       'JWST.NIRSPEC.PRISM',
                                       'JWST.NIRSPEC.G395',
                                       'JWST.NIRSPEC.G253',
                                       'JWST.NIRSPEC.G140']
RED_STEPS['Extraction']['MIRIAM'] = ['JWST.MIRI.IMAGING']
RED_STEPS['Extraction']['NAMELESS'] = None
RED_STEPS['Extraction']['Eureka'] = None
RED_STEPS['Extraction']['exoTEFRF'] = None
RED_STEPS['Extraction']['SimpleBox'] = None

RED_STEPS['Post-extraction'] = dict()
RED_STEPS['Post-extraction']['SORBET.WLCA'] = ['JWST.NIRISS.SOSS',
                                               'JWST.NIRSPEC.PRISM',
                                               'JWST.NIRSPEC.G395',
                                               'JWST.NIRSPEC.G253',
                                               'JWST.NIRSPEC.G140']
RED_STEPS['Post-extraction']['SORBET.SPCA'] = ['JWST.NIRISS.SOSS',
                                               'JWST.NIRSPEC.PRISM',
                                               'JWST.NIRSPEC.G395',
                                               'JWST.NIRSPEC.G253',
                                               'JWST.NIRSPEC.G140']
RED_STEPS['Post-extraction']['SORBET.TransitFit'] = None
RED_STEPS['Post-extraction']['SORBET.RVA'] = None

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

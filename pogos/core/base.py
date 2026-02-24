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

from sossisse.core.constants import CDict as SCdict

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
INSTRUMENTS = ['JWST.NIRISS.SOSS',
               # 'JWST.NIRISS.SOSS.SUPERSTRIPE',
               'JWST.NIRISS.FGS',
               'JWST.NIRSPEC.BOTS.PRISM',
               'JWST.NIRSPEC.BOTS.G395M',
               'JWST.NIRSPEC.BOTS.G235M',
               'JWST.NIRSPEC.BOTS.G140M',
               'JWST.NIRSPEC.BOTS.G395H',
               'JWST.NIRSPEC.BOTS.G235H',
               'JWST.NIRSPEC.BOTS.G140H',
               'JWST.NIRCAM.IMAGING',
               'JWST.NIRCAM.WFSS',
               # 'JWST.NIRCAM.MULTISTRIPE',
               'JWST.MIRI.IMAGING',
               'JWST.MIRI.LRS']
# define the submodules in POGOS
SUBMODULES = ['TSOVORE', 'SOSSISSE', 'MIRIAM', 'SORBET']

# =============================================================================
# Define all instruments and their sub-modes (related to our instrument
# names)
# =============================================================================
INST_MODES = dict()

# JWST NIRISS
INST_MODES['JWST.NIRISS'] = dict()
INST_MODES['JWST.NIRISS']['SOSS'] = 'JWST.NIRISS.SOSS'
INST_MODES['JWST.NIRISS']['SOSS.SUPERSTRIPE'] = None
INST_MODES['JWST.NIRISS']['FGS'] = 'JWST.NIRISS.FGS'
INST_MODES['JWST.NIRISS']['AMI'] = None
# JWST NIRSPEC
INST_MODES['JWST.NIRSPEC'] = dict()
INST_MODES['JWST.NIRSPEC']['BOTS.PRISM'] = 'JWST.NIRSPEC.BOTS.PRISM'
INST_MODES['JWST.NIRSPEC']['BOTS.G395M'] = 'JWST.NIRSPEC.BOTS.G395M'
INST_MODES['JWST.NIRSPEC']['BOTS.G235M'] = 'JWST.NIRSPEC.BOTS.G235M'
INST_MODES['JWST.NIRSPEC']['BOTS.G140M'] = 'JWST.NIRSPEC.BOTS.G140M'
INST_MODES['JWST.NIRSPEC']['BOTS.G395H'] = 'JWST.NIRSPEC.BOTS.G395H'
INST_MODES['JWST.NIRSPEC']['BOTS.G235H'] = 'JWST.NIRSPEC.BOTS.G235H'
INST_MODES['JWST.NIRSPEC']['BOTS.G140H'] = 'JWST.NIRSPEC.BOTS.G140H'
INST_MODES['JWST.NIRSPEC']['FS'] = None
INST_MODES['JWST.NIRSPEC']['MOSS'] = None
INST_MODES['JWST.NIRSPEC']['IFU'] = None
# JWST NIRCam
INST_MODES['JWST.NIRCAM'] = dict()
INST_MODES['JWST.NIRCAM']['IMAGING'] = 'JWST.NIRCAM.IMAGING'
INST_MODES['JWST.NIRCAM']['WFSS'] = 'JWST.NIRCAM.WFSS'
INST_MODES['JWST.NIRCAM']['MULTISTRIPE'] = None
INST_MODES['JWST.NIRCAM']['CORON'] = None
INST_MODES['JWST.NIRCAM']['TSO-IMAGING'] = None
INST_MODES['JWST.NIRCAM']['TSO-GRISM'] = None
# JWST MIRI
INST_MODES['JWST.MIRI'] = dict()
INST_MODES['JWST.MIRI']['IMAGING'] = 'JWST.MIRI.IMAGING'
INST_MODES['JWST.MIRI']['LRS'] = 'JWST.MIRI.LRS'
INST_MODES['JWST.MIRI']['MRS'] = None
INST_MODES['JWST.MIRI']['CORON'] = None
INST_MODES['JWST.MIRI']['WFSS'] = None

# =============================================================================
# Define all reduction steps
# =============================================================================
RED_STEPS = dict()
RED_STEPS['Pre-extraction'] = dict()
RED_STEPS['Pre-extraction']['IDT:SOSS'] = None
RED_STEPS['Pre-extraction']['TSOVORE'] = ['JWST.NIRISS.SOSS',
                                          # 'JWST.NIRISS.SOSS.SUPERSTRIPE',
                                          'JWST.NIRSPEC.BOTS.PRISM',
                                          'JWST.NIRSPEC.BOTS.G395M',
                                          'JWST.NIRSPEC.BOTS.G235M',
                                          'JWST.NIRSPEC.BOTS.G140M',
                                          'JWST.NIRSPEC.BOTS.G395H',
                                          'JWST.NIRSPEC.BOTS.G235H',
                                          'JWST.NIRSPEC.BOTS.G140H',
                                          'JWST.NIRCAM.IMAGING',
                                          'JWST.NIRCAM.WFSS',
                                          # 'JWST.NIRCAM.MULTISTRIPE',
                                          'JWST.MIRI.IMAGING']
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
                                               'JWST.NIRSPEC.G140',
                                               'JWST.MIRI.IMAGING']
RED_STEPS['Post-extraction']['SORBET.SPCA'] = ['JWST.NIRISS.SOSS',
                                               'JWST.NIRSPEC.PRISM',
                                               'JWST.NIRSPEC.G395',
                                               'JWST.NIRSPEC.G253',
                                               'JWST.NIRSPEC.G140']
RED_STEPS['Post-extraction']['SORBET.TransitFit'] = None
RED_STEPS['Post-extraction']['SORBET.RVA'] = None

# Define whether the user is allowed to run multiple flavours of these
# steps (e.g. multiple extraction methods) - if False, then only one method
# can be run for that step
RED_STEPS_MULTI = dict()
RED_STEPS_MULTI['Pre-extraction'] = False
RED_STEPS_MULTI['Extraction'] = False
RED_STEPS_MULTI['Post-extraction'] = True

# Define the shortnames for Pre/Extract/Post
RED_SHORT = dict()
RED_SHORT['Pre-extraction'] = 'Pre'
RED_SHORT['Extraction'] = 'Ext'
RED_SHORT['Post-extraction'] = 'Pst'


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
EXTERNAL_CONST['SOSSISSE'] = SCdict


# =============================================================================
# Base functionality
# =============================================================================
class PogosException(Exception):
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

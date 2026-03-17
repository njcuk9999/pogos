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
# define the submodules in POGOS
SUBMODULES = ['TSOVORE', 'PRE_NAMELESS', 'PRE_EUREKA', 'PRE_JWST',
              'SOSSISSE', 'MIRIAM', 'EXT_NAMELESS', 'EXT_EUREKA', 'EXT_JWST', 'EXT_BOX',
              'SORBET.WLCA', 'SORBET.SLCA']

# define the reduction steps (pre-extraction, extraction, post extraction)
#  then which sub module and a list of instruments supported per sub-module
RED_STEPS = dict()
RED_STEPS['Pre-extraction'] = dict()
# RED_STEPS['Pre-extraction']['IDT:SOSS'] = None
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
RED_STEPS['Pre-extraction']['PRE_NAMELESS'] = None
RED_STEPS['Pre-extraction']['PRE_EUREKA'] = None
# RED_STEPS['Pre-extraction']['exoTEFRF'] = None
RED_STEPS['Pre-extraction']['PRE_JWST'] = None

RED_STEPS['Extraction'] = dict()
RED_STEPS['Extraction']['SOSSISSE'] = ['JWST.NIRISS.SOSS',
                                       'JWST.NIRSPEC.PRISM',
                                       'JWST.NIRSPEC.G395',
                                       'JWST.NIRSPEC.G253',
                                       'JWST.NIRSPEC.G140']
RED_STEPS['Extraction']['MIRIAM'] = ['JWST.MIRI.IMAGING']
RED_STEPS['Extraction']['EXT_NAMELESS'] = None
RED_STEPS['Extraction']['EXT_EUREKA'] = None
# RED_STEPS['Extraction']['exoTEFRF'] = None
RED_STEPS['Extraction']['EXT_BOX'] = None
RED_STEPS['Extraction']['EXT_JWST'] = None

RED_STEPS['Post-extraction'] = dict()
RED_STEPS['Post-extraction']['SORBET.WLCA'] = ['JWST.NIRISS.SOSS',
                                               'JWST.NIRSPEC.PRISM',
                                               'JWST.NIRSPEC.G395',
                                               'JWST.NIRSPEC.G253',
                                               'JWST.NIRSPEC.G140',
                                               'JWST.MIRI.IMAGING']
RED_STEPS['Post-extraction']['SORBET.SLCA'] = ['JWST.NIRISS.SOSS',
                                               'JWST.NIRSPEC.PRISM',
                                               'JWST.NIRSPEC.G395',
                                               'JWST.NIRSPEC.G253',
                                               'JWST.NIRSPEC.G140']
# RED_STEPS['Post-extraction']['SORBET.TransitFit'] = None
# RED_STEPS['Post-extraction']['SORBET.RVA'] = None


# Define whether the user is allowed to run multiple flavours of these
# steps (e.g. multiple extraction methods) - if False, then only one method
# can be run for that step
RED_STEPS_MULTI = dict()
RED_STEPS_MULTI['Pre-extraction'] = False
RED_STEPS_MULTI['Extraction'] = False
RED_STEPS_MULTI['Post-extraction'] = True

# Define the prefix for constants from each module
#   in form RUN.XXXX = PREFIX    (usually prefix is TSOVORE)
RUN_KEYS = dict()
RUN_KEYS['RUN.TSOVORE'] = 'TSOVORE'
RUN_KEYS['RUN.PRE_NAMELESS'] = 'PRE_NAMELESS'
RUN_KEYS['RUN.PRE_EUREKA'] = 'PRE_EUREKA'
RUN_KEYS['RUN.PRE_JWST'] = 'PRE_JWST'
RUN_KEYS['RUN.SOSSISSE'] = 'SOSSISSE'
RUN_KEYS['RUN.MIRIAM'] = 'MIRIAM'
RUN_KEYS['RUN.EXT_NAMELESS'] = 'EXT_NAMELESS'
RUN_KEYS['RUN.EXT_EUREKA'] = 'EXT_EUREKA'
RUN_KEYS['RUN.EXT_JWST'] = 'EXT_JWST'
RUN_KEYS['RUN.EXT_BOX'] = 'EXT_BOX'
RUN_KEYS['RUN.SORBET.WLCA'] = 'SORBET.WLCA'
RUN_KEYS['RUN.SORBET.SLCA'] = 'SORBET.SLCA'

# Define the first path to create (in setup) for each module
#   when it isn't just the module name (as in RUN_KEYS)
RUN_DIRS = dict()
# RUN_DIRS['RUN.TSOVORE'] = 'TSOVORE.PATHS.INPUT_PATH'
# RUN_DIRS['RUN.PRE_NAMELESS'] = 'PRE_NAMELESS.INPUTS.PATH'
# RUN_DIRS['RUN.PRE_EUREKA'] = 'PRE_EUREKA.INPUTS.PATH'
# RUN_DIRS['RUN.PRE_JWST'] = 'PRE_JWST.INPUTS.PATH'
RUN_DIRS['RUN.SOSSISSE'] = 'SOSSISSE.INPUTS.SOSSIOPATH'
# RUN_DIRS['RUN.MIRIAM'] = 'MIRIAM.PATHS.INPUT_PATH'
# RUN_DIRS['RUN.EXT_NAMELESS'] = 'EXT_NAMELESS.INPUTS.PATH'
# RUN_DIRS['RUN.EXT_EUREKA'] = 'EXT_EUREKA.INPUTS.PATH'
# RUN_DIRS['RUN.EXT_JWST'] = 'EXT_JWST.INPUTS.PATH'
# RUN_DIRS['RUN.EXT_BOX'] = 'EXT_BOX.INPUTS.PATH'
# RUN_DIRS['RUN.SORBET.WLCA'] = 'SORBET.WLCA.INPUT_PATH'
# RUN_DIRS['RUN.SORBET.SLCA'] = 'SORBET.SLCA.INPUT_PATH'

# Define the file paths for each module that may need clearing on copying a yaml
# should be in format: FILE_PATHS[<constant name>] = <path to directory constant>
FILE_PATHS = dict()
FILE_PATHS['TSOVORE.INPUTS.FILES'] = 'TSOVORE.PATHS.INPUT_PATH'
FILE_PATHS['MIRIAM.INPUTS.FILES'] = 'MIRIAM.PATHS.INPUT_PATH'
FILE_PATHS['SOSSISSE.GENERAL.FILES'] = 'SOSSISSE.PATHS.RAWPATH'
FILE_PATHS['SOSSISSE.GENERAL.WAVE_FILE'] = 'SOSSISSE.PATHS.CALIBPATH'
FILE_PATHS['SORBET.WLCA.INPUT_FILE'] = 'SORBET.WLCA.INPUT_PATH'
FILE_PATHS['SORBET.SLCA.INPUT_FILE'] = 'SORBET.SLCA.INPUT_PATH'

# list all the required parameters for each module when copying a yaml
REQ_MODULE_PARAMS = dict()
REQ_MODULE_PARAMS['TSOVORE'] = []
REQ_MODULE_PARAMS['PRE_NAMELESS'] = []
REQ_MODULE_PARAMS['PRE_EUREKA'] = []
REQ_MODULE_PARAMS['PRE_JWST'] = []
REQ_MODULE_PARAMS['SOSSISSE'] = ['SOSSISSE.INPUTS.OBJECTNAME']
REQ_MODULE_PARAMS['MIRIAM'] = []
REQ_MODULE_PARAMS['EXT_NAMELESS'] = []
REQ_MODULE_PARAMS['EXT_EUREKA'] = []
REQ_MODULE_PARAMS['EXT_JWST'] = []
REQ_MODULE_PARAMS['EXT_BOX'] = []
REQ_MODULE_PARAMS['SORBET'] = []

# list of sorbet sub-modules
SORBET_SUB_MODS = ['SORBET.WLCA', 'SORBET.SLCA']

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

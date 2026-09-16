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

# Required primary-header values for each supported observing mode.
# Sets allow a mode to accept more than one valid header value. Although all
# current entries are JWST modes, this mapping is intentionally mission-neutral.
MODE_HEADERS = {
    'JWST.NIRISS.SOSS': {
        'INSTRUME': {'NIRISS'},
        'DETECTOR': {'NIS'},
        'EXP_TYPE': {'NIS_SOSS'},
        'PUPIL': {'GR700XD'},
    },
    'JWST.NIRISS.FGS': {
        'INSTRUME': {'FGS'},
        'EXP_TYPE': {'FGS_IMAGE', 'FGS_FOCUS'},
    },
    'JWST.NIRSPEC.BOTS.PRISM': {
        'INSTRUME': {'NIRSPEC'},
        'DETECTOR': {'NRS1', 'NRS2'},
        'EXP_TYPE': {'NRS_BRIGHTOBJ'},
        'GRATING': {'PRISM'},
    },
    'JWST.NIRSPEC.BOTS.G395M': {
        'INSTRUME': {'NIRSPEC'},
        'DETECTOR': {'NRS1', 'NRS2'},
        'EXP_TYPE': {'NRS_BRIGHTOBJ'},
        'GRATING': {'G395M'},
    },
    'JWST.NIRSPEC.BOTS.G235M': {
        'INSTRUME': {'NIRSPEC'},
        'DETECTOR': {'NRS1', 'NRS2'},
        'EXP_TYPE': {'NRS_BRIGHTOBJ'},
        'GRATING': {'G235M'},
    },
    'JWST.NIRSPEC.BOTS.G140M': {
        'INSTRUME': {'NIRSPEC'},
        'DETECTOR': {'NRS1', 'NRS2'},
        'EXP_TYPE': {'NRS_BRIGHTOBJ'},
        'GRATING': {'G140M'},
    },
    'JWST.NIRSPEC.BOTS.G395H': {
        'INSTRUME': {'NIRSPEC'},
        'DETECTOR': {'NRS1', 'NRS2'},
        'EXP_TYPE': {'NRS_BRIGHTOBJ'},
        'GRATING': {'G395H'},
    },
    'JWST.NIRSPEC.BOTS.G235H': {
        'INSTRUME': {'NIRSPEC'},
        'DETECTOR': {'NRS1', 'NRS2'},
        'EXP_TYPE': {'NRS_BRIGHTOBJ'},
        'GRATING': {'G235H'},
    },
    'JWST.NIRSPEC.BOTS.G140H': {
        'INSTRUME': {'NIRSPEC'},
        'DETECTOR': {'NRS1', 'NRS2'},
        'EXP_TYPE': {'NRS_BRIGHTOBJ'},
        'GRATING': {'G140H'},
    },
    'JWST.NIRCAM.IMAGING': {
        'INSTRUME': {'NIRCAM'},
        'EXP_TYPE': {'NRC_IMAGE', 'NRC_TSIMAGE'},
    },
    'JWST.NIRCAM.WFSS': {
        'INSTRUME': {'NIRCAM'},
        'EXP_TYPE': {'NRC_WFSS', 'NRC_TSGRISM'},
    },
    'JWST.MIRI.IMAGING': {
        'INSTRUME': {'MIRI'},
        'EXP_TYPE': {'MIR_IMAGE'},
    },
    'JWST.MIRI.LRS': {
        'INSTRUME': {'MIRI'},
        'EXP_TYPE': {'MIR_LRS-FIXEDSLIT', 'MIR_LRS-SLITLESS'},
    },
}

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
              'SORBET.WLCA', 'SORBET.SLCA', 'POST_EUREKA', 'POST_JWST']

# instrument modes supported by the JWST "standard pipeline" wrapper
#   (jwst_wrap maps every POGOS instrument mode onto a standard JWST pipeline)
JWST_MODES = list(INSTRUMENTS)

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
RED_STEPS['Pre-extraction']['PRE_NAMELESS'] = ['JWST.NIRISS.SOSS']
RED_STEPS['Pre-extraction']['PRE_EUREKA'] = ['JWST.NIRISS.SOSS',
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
                                             'JWST.MIRI.IMAGING',
                                             'JWST.MIRI.LRS']
# RED_STEPS['Pre-extraction']['exoTEFRF'] = None
RED_STEPS['Pre-extraction']['PRE_JWST'] = JWST_MODES

RED_STEPS['Extraction'] = dict()
RED_STEPS['Extraction']['SOSSISSE'] = ['JWST.NIRISS.SOSS',
                                       'JWST.NIRSPEC.BOTS.PRISM',
                                       'JWST.NIRSPEC.BOTS.G395M',
                                       'JWST.NIRSPEC.BOTS.G253M',
                                       'JWST.NIRSPEC.BOTS.G140M',
                                       'JWST.NIRSPEC.BOTS.G395H',
                                       'JWST.NIRSPEC.BOTS.G253H',
                                       'JWST.NIRSPEC.BOTS.G140H']
RED_STEPS['Extraction']['MIRIAM'] = ['JWST.MIRI.IMAGING']
RED_STEPS['Extraction']['EXT_NAMELESS'] = ['JWST.NIRISS.SOSS']
RED_STEPS['Extraction']['EXT_EUREKA'] = ['JWST.NIRISS.SOSS',
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
                                         'JWST.MIRI.IMAGING',
                                         'JWST.MIRI.LRS']
# RED_STEPS['Extraction']['exoTEFRF'] = None
RED_STEPS['Extraction']['EXT_BOX'] = None
RED_STEPS['Extraction']['EXT_JWST'] = JWST_MODES

RED_STEPS['Post-extraction'] = dict()
RED_STEPS['Post-extraction']['SORBET.WLCA'] = ['JWST.NIRISS.SOSS',
                                               'JWST.NIRSPEC.BOTS.PRISM',
                                               'JWST.NIRSPEC.BOTS.G395M',
                                               'JWST.NIRSPEC.BOTS.G253M',
                                               'JWST.NIRSPEC.BOTS.G140M',
                                               'JWST.NIRSPEC.BOTS.G395H',
                                               'JWST.NIRSPEC.BOTS.G253H',
                                               'JWST.NIRSPEC.BOTS.G140H',
                                               'JWST.MIRI.IMAGING']
RED_STEPS['Post-extraction']['SORBET.SLCA'] = ['JWST.NIRISS.SOSS',
                                               'JWST.NIRSPEC.BOTS.PRISM',
                                               'JWST.NIRSPEC.BOTS.G395M',
                                               'JWST.NIRSPEC.BOTS.G253M',
                                               'JWST.NIRSPEC.BOTS.G140M',
                                               'JWST.NIRSPEC.BOTS.G395H',
                                               'JWST.NIRSPEC.BOTS.G253H',
                                               'JWST.NIRSPEC.BOTS.G140H']
# RED_STEPS['Post-extraction']['SORBET.TransitFit'] = None
# RED_STEPS['Post-extraction']['SORBET.RVA'] = None
RED_STEPS['Post-extraction']['POST_EUREKA'] = ['JWST.NIRISS.SOSS',
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
                                               'JWST.MIRI.IMAGING',
                                               'JWST.MIRI.LRS']

# JWST standard pipeline post-extraction (reserved for additional steps)
RED_STEPS['Post-extraction']['POST_JWST'] = JWST_MODES

# Define whether the user is allowed to run multiple flavours of these
# steps (e.g. multiple extraction methods) - if False, then only one method
# can be run for that step
RED_STEPS_MULTI = dict()
RED_STEPS_MULTI['Pre-extraction'] = False
RED_STEPS_MULTI['Extraction'] = False
RED_STEPS_MULTI['Post-extraction'] = True

# Define explicit external input-file parameters for each reduction module.
# None means that the module receives products from an earlier step, discovers
# files internally, or has no raw-file list that can be checked at startup.
INPUT_FILES = dict()
for reduction_level in RED_STEPS:
    for reduction_module in RED_STEPS[reduction_level]:
        INPUT_FILES[reduction_module] = None

# TSOVORE starts from the configured raw JWST exposure list.
INPUT_FILES['TSOVORE'] = {
    'files': 'TSOVORE.INPUTS.FILES',
    'path': 'TSOVORE.PATHS.INPUT_PATH',
}
# SOSSISSE can be run directly from configured rateints files.
INPUT_FILES['SOSSISSE'] = {
    'files': 'SOSSISSE.GENERAL.FILES',
    'path': 'SOSSISSE.PATHS.RAWPATH',
}
# MIRIAM can be run directly from configured imaging files.
INPUT_FILES['MIRIAM'] = {
    'files': 'MIRIAM.INPUTS.FILES',
    'path': 'MIRIAM.PATHS.INPUT_PATH',
}

# Define the prefix for constants from each module
#   in form RUN.XXXX = PREFIX    (usually prefix is TSOVORE)
# Used in two ways:
# 1. if RUN.XXX = False --> don't put these variables in yaml
# 2. inversed if STEP.{VALUE} not setup selectiong set RUN.XXX = False
#    (used to turn off steps when demo not used)
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
RUN_KEYS['RUN.POST_EUREKA'] = 'POST_EUREKA'
RUN_KEYS['RUN.POST_JWST'] = 'POST_JWST'


# Special sub_run_keys
# Used to turn off sub keys when RUN_KEYS is not enough
# Only used when CDict is shared between RUN.XXX keys
#  e.g.  if RUN.XXX = False   don't put these variables in yaml
SUB_RUN_KEYS = dict()
SUB_RUN_KEYS['RUN.PRE_EUREKA'] = ['EUREKA.STAGE1', 'EUREKA.STAGE2']
SUB_RUN_KEYS['RUN.EXT_EUREKA'] = ['EUREKA.STAGE3']
SUB_RUN_KEYS['RUN.POST_EUREKA'] = ['EUREKA.STAGE4', 'EUREKA.STAGE5', 'EUREKA.STAGE6']
SUB_RUN_KEYS['RUN.PRE_JWST'] = ['STD_JWST.STAGE1', 'STD_JWST.STAGE2']
SUB_RUN_KEYS['RUN.EXT_JWST'] = ['STD_JWST.STAGE3']
SUB_RUN_KEYS['RUN.PRE_NAMELESS'] = ['NAMELESS.S1_SETTINGS', 'NAMELESS.S2_SETTINGS',
                                    'NAMELESS.PREP_SETTINGS', 'NAMELESS.CST_SETTINGS']
SUB_RUN_KEYS['RUN.EXT_NAMELESS'] = ['NAMELESS.EXT_SETTINGS']
# Wildcard entries are applied when all matching RUN keys are False.
SUB_RUN_KEYS['RUN.*_EUREKA'] = ['EUREKA.GENERAL']
SUB_RUN_KEYS['RUN.*_JWST'] = ['STD_JWST.GENERAL']
SUB_RUN_KEYS['RUN.*_NAMELESS'] = ['NAMELESS.GENERAL']
SUB_RUN_KEYS['RUN.SORBET.*'] = ['SORBET.GENERAL', 'SORBET.PLOTS']

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

# Run keys that should NOT create a generic {GLOBAL.DATA_PATH}/{run_value.lower()}
# directory in startup.setup(). These wrappers manage their own canonical roots
# (e.g. eureka/, nameless/, jwst/) based on module SUBDIRECTORY settings.
SKIP_GENERIC_RUN_DIRS = {
    'RUN.PRE_EUREKA', 'RUN.EXT_EUREKA', 'RUN.POST_EUREKA',
    'RUN.PRE_JWST', 'RUN.EXT_JWST', 'RUN.POST_JWST',
    'RUN.PRE_NAMELESS', 'RUN.EXT_NAMELESS'
}

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
REQ_MODULE_PARAMS['POST_JWST'] = []
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
# Filled lazily in startup.initial_setup() to avoid importing sossisse at
# module import time.


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

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

# ANSI colors used only for rendered exception messages. Traceback frames are
# generated separately by Python and remain in the terminal's normal color.
EXCEPTION_RED = '\033[1;91;1m'
COLOR_END = '\033[0;0m'

# Define the file paths for each module that may need clearing on copying a yaml
# should be in format: FILE_PATHS[<constant name>] = <path to directory constant>
FILE_PATHS = dict()
FILE_PATHS['TSOVORE.INPUTS.FILES'] = 'TSOVORE.PATHS.INPUT_PATH'
FILE_PATHS['MIRIAM.INPUTS.FILES'] = 'MIRIAM.PATHS.INPUT_PATH'
FILE_PATHS['SOSSISSE.GENERAL.FILES'] = 'SOSSISSE.PATHS.RAWPATH'
FILE_PATHS['SOSSISSE.GENERAL.WAVE_FILE'] = 'SOSSISSE.PATHS.CALIBPATH'
FILE_PATHS['SORBET.WLCA.INPUT_FILE'] = 'SORBET.WLCA.INPUT_PATH'
FILE_PATHS['SORBET.SLCA.INPUT_FILE'] = 'SORBET.SLCA.INPUT_PATH'

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
        self.message = message

    def __str__(self) -> str:
        message = 'PogosException: {0}'.format(self.message)
        return EXCEPTION_RED + message + COLOR_END




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

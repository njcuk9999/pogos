#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# sorbet.core.core.py

# Starts the SORBET sub-module inside POGOS

Created on 2025-02-19 at 13:04

@author: cook, CharlesCadieux
"""
from typing import Tuple

from aperocore.constants.param_functions import ParamDict
from aperocore.core import drs_log
from aperocore.core import drs_misc
from pogos.core import base
from pogos.core import general as pogos_general


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'pogos.sorbet.core.core'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__
# get the Drs Exceptions
AperoCodedException = drs_log.AperoCodedException
AperoCodedWarning = drs_log.AperoCodedWarning
# get display func
display_func = drs_misc.display_func
# Get Logging function
WLOG = drs_log.wlog
# Define the SORBET run constants
RUN_CONSTANTS = ['SORBET.WLCA.RUN', 'SORBET.SLCA.RUN']  # , 'SORBET.TFIT.RUN', 'SORBET.RV.RUN']


# =============================================================================
# Define functions
# =============================================================================
# TODO: Move to APERO-CORE
def sorbet_unique_id() -> str:
    """
    Assign a sossisse id based on the time now and return it and the
    time now

    :return: the process id and the human time at creation
    :rtype: Tuple[str, str]
    """
    # get unix char code
    unixtime, humantime, rval = pogos_general.unix_char_code()
    # write sid
    sid = 'SBID-{0:020d}-{1}'.format(int(unixtime), rval)
    # return sid
    return sid


def sorbet_inst_mode(params: ParamDict) -> str:
    """
    Read the instrument mode and convert to a format used by Juliet

    :param params:
    :return:
    """
    # get instrument mode
    inst_mode = params['GLOBAL.INSTRUMENTMODE'].upper()
    # make sure inst_mode has no _ for juliet compatibility
    inst_mode = inst_mode.replace('_', '.')
    # return updated instrument mode
    return inst_mode


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

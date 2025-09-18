#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# sorbet.core.core.py

# Starts the SORBET sub-module inside POGOS

Created on 2025-02-19 at 13:04

@author: cook, CharlesCadieux
"""
import random
import string
import time
from typing import Tuple

import numpy as np
from astropy.time import Time

from aperocore.constants.param_functions import ParamDict
from aperocore.core import drs_log
from aperocore.core import drs_misc
from pogos.core import base
from pogos.sorbet.recipes import run_sorbet_slcta
from pogos.sorbet.recipes import run_sorbet_wlcta

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
RUN_CONSTANTS = ['SORBET.WLCTA.RUN', 'SORBET.SLCTA.RUN']  # , 'SORBET.TFIT.RUN', 'SORBET.RV.RUN']
# get all chars
CHARS = string.ascii_uppercase + string.digits


# =============================================================================
# Define functions
# =============================================================================
def run_sorbet_module(params: ParamDict):
    """
    Run the sorbet recipes

    :param params: ParamDict, the parameter dictionary of constants

    :return: Updated params, runs sorbet recipes
    """
    # Check at least one recipe is set to run
    run_any = False
    for key in RUN_CONSTANTS:
        if params[key]:
            run_any = True
            break
    # if not running any then skip SORBET
    if not run_any:
        WLOG(params, 'warning', 'No SORBET recipes set to run - skipping.')
        return params
    
    # ----------------------------------------------------------------------
    # White Light Curve Transit Analysis
    # ----------------------------------------------------------------------
    if params['SORBET.WLCTA.RUN']:
        params = run_sorbet_wlcta(params)

    # ----------------------------------------------------------------------
    # Spectral Light Curve Transit Analysis
    # ----------------------------------------------------------------------
    if params['SORBET.SLCTA.RUN']:
        params = run_sorbet_slcta(params)

    # ----------------------------------------------------------------------
    # TFIT
    # ----------------------------------------------------------------------
    #if params['SORBET.TFIT.RUN']:
    #    params = run_sorbet_tfit(params)

    # ----------------------------------------------------------------------
    # RV Module
    # ----------------------------------------------------------------------
    #if params['SORBET.RV.RUN']:
    #    params = run_sorbet_rv(params)


    return params


# TODO: Move to APERO-CORE
def unix_char_code() -> Tuple[float, str, str]:
    """
    Get the time now (using astropy.Time) and return the unix time
    human time and a random code of 4 characters

    :return: tuple, 1. the unix time now, 2. the human time now, 3. a random
             set of 4 characters
    """
    # set function name
    # _ = display_func('unix_char_code', __NAME__)
    # we need a random seed
    np.random.seed(random.randint(1, 2 ** 30))
    # generate a random number (in case time is too similar)
    #  -- happens a lot in multiprocessing
    rint = np.random.randint(1000, 9999, 1)[0] / 1e7
    # wait a fraction of time (between 1us and 1ms)
    time.sleep(float(rint))
    # get the time now from astropy
    timenow = Time.now()
    # get unix and human time from astropy time now
    unixtime = timenow.unix * 1e7
    humantime = timenow.iso
    # generate random four characters to make sure sid is unique
    rval = ''.join(np.random.choice(list(CHARS), size=4))
    return unixtime, humantime, rval


# TODO: Move to APERO-CORE
def sorbet_unique_id() -> str:
    """
    Assign a sossisse id based on the time now and return it and the
    time now

    :return: the process id and the human time at creation
    :rtype: Tuple[str, str]
    """
    # get unix char code
    unixtime, humantime, rval = unix_char_code()
    # write sid
    sid = 'SID-{0:020d}-{1}'.format(int(unixtime), rval)
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
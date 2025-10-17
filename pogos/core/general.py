#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2024-10-29 at 10:16

@author: cook
"""
import os
import random
import string
import time
from typing import Tuple

import numpy as np
from astropy.time import Time

from aperocore.constants import param_functions
from aperocore.core import drs_log

from pogos.core import base

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'pogos.core.general.py'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__
# get parameter dictionary
ParamDict = param_functions.ParamDict
# get the logger
WLOG = drs_log.wlog
# get all chars
CHARS = string.ascii_uppercase + string.digits


# =============================================================================
# Define functions
# =============================================================================
def start_splash(name: str):
    """
    Print the start splash

    :return: None, prints to screen
    """
    WLOG(None, 'info', drs_log.MPARAMS['LOG.HEADER'], colour='magenta')
    WLOG(None, 'info', name, colour='magenta')
    vargs = [__version__, __date__]
    WLOG(None, 'info', 'v{0} [{1}]'.format(*vargs), colour='magenta')
    WLOG(None, 'info', drs_log.MPARAMS['LOG.HEADER'], colour='magenta')


def end_splash():
    """
    Print the end splash

    :return: None, prints to screen
    """
    WLOG(None, 'info', drs_log.MPARAMS['LOG.HEADER'], colour='magenta')
    WLOG(None, 'info', 'End of code', colour='magenta')
    WLOG(None, 'info', drs_log.MPARAMS['LOG.HEADER'], colour='magenta')


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


def prepare_directory(params: ParamDict, pkind: str, sid_path: str,
                      sid_null: str, file_path: str, pmode: str,
                      exception):
    """
    Prepare either an input or output directory for use in POGOS
    :param params:
    :param pkind:
    :param sid_path:
    :param file_path:
    :param mode:
    :return:
    """
    func_name = f'{__NAME__}.prepare_directory()'
    # generate SID if not given
    if params[sid_path] is None:
        params[sid_path] = sid_null
    # get the output path from the params
    path_constant = params[file_path]
    # get this to inputs by default
    if os.path.exists(os.path.realpath(path_constant)):
        my_path = os.path.realpath(path_constant)
    else:
        if path_constant is None:
            my_path = pkind
        else:
            my_path = str(path_constant)
        # if not, make it relative to the global database
        my_path = os.path.join(params['GLOBAL.DATA_PATH'], pmode,
                               params[sid_path], my_path)
    # make sure the path is in the params
    if not os.path.exists(my_path):
        os.makedirs(my_path)
    # print message on where outputs will be saved
    msg = f'All {pkind} data will be saved under: {my_path}'
    WLOG(params, 'info', msg)
    # update output path
    params.set(file_path, value=my_path, source=func_name)

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

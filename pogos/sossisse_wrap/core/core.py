#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2025-02-18 at 14:13

@author: cook
"""

import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.table import Table
from astropy import units as u
from tqdm import tqdm
import warnings

from aperocore.constants.param_functions import ParamDict
from aperocore.core import drs_misc
from aperocore.core import drs_log
from sossisse.recipes import run_sossisse as sossisse_run
import sossisse

from pogos.core import base


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'pogos.sossisse_wrap.core.core'
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


# =============================================================================
# Define functions
# =============================================================================
def run_sossisse_module(params: ParamDict):
    """
    Run the sossisse run recipe

    :param params: ParamDict, the parameter dictionary of constants

    :return: None, runs sossisse run
    """
    # if RUN.SOSSISSE is False skip
    if not params['RUN.SOSSISSE']:
        return
    # get the SOSSISSE sub-dictionary
    sossisse_params = params.get('SOSSISSE')
    # deal with SOSSISSE nested dictionary not in params
    if sossisse_params is None:
        WLOG(params, 'warning', 'SOSSISSE not in params - skipping.')
        return
    # convert to independent parameter dictionary
    sparams = sossisse_params.as_param_dict()
    # make sure yaml file is set
    sparams['INPUTS.PARAM_FILE'] = str(params['GLOBAL.YAML_FILE'])
    # run the sossisse recipe
    return sossisse_run.main(__YAML_DICT__=sparams)


def setup_sossisse_module(params: ParamDict):
    """
    Run the sossisse setup recipe

    :param params: ParamDict, the parameter dictionary of constants

    :return: None, runs sossisse setup
    """
    # set function name
    func_name = f'{__NAME__}.setup_sossisse_module()'
    # if RUN.SOSSISSE is False skip
    if not params['RUN.SOSSISSE']:
        return
    # get the SOSSISSE sub-dictionary
    sossisse_params = params.get('SOSSISSE')
    # deal with SOSSISSE nested dictionary not in params
    if sossisse_params is None:
        # we assume that if SOSSISSE is not there we don't want to run this
        return
    # convert to independent parameter dictionary
    sparams = sossisse_params.as_param_dict()
    # make sure yaml file is set
    sparams['INPUTS.PARAM_FILE'] = str(params['GLOBAL.YAML_FILE'])
    # setup for SOSSISSE just uses "get_parameters" function
    inst = sossisse.get_parameters(__NAME__=__NAME__, only_create=True,
                                      log_level='setup', __YAML_DICT__=sparams)
    # -------------------------------------------------------------------------
    # get the SOSSISSE PATH params out of instrument class
    spaths = inst.params.get('PATHS')
    # update the SOSSISSE paths
    for path in spaths.keys():
        # get the key in POGOS parameters
        pkey = f'SOSSISSE.PATHS.{path}'
        # if the key exists update it
        if pkey in params:
            params.set(pkey, spaths[path], source=func_name)
    # -------------------------------------------------------------------------
    # return the parameters
    return params


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

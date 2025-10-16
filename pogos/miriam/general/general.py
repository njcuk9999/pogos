#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2025-10-16 at 14:10

@author: cook
"""
import string
import os
import numpy as np

from aperocore.constants.param_functions import ParamDict
from aperocore.core import drs_log
from aperocore.core import drs_misc
from pogos.core import base
from pogos.sorbet.general import science
from pogos.sorbet.general import plots
from sossisse.core import misc
from pogos.miriam.core import general as mc_general

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


# =============================================================================
# Define functions
# =============================================================================
def run_miriam(params: ParamDict):
    # set the function name
    func_name = f'{__NAME__}.run_sorbet_wlcta'
    # print the white light curve splash
    print(misc.art('MIRIAM', 'yellow', 'CYAN'))
    # prepare the output directory
    prepare_output_directory(params)

    pass


def prepare_output_directory(params: ParamDict):
    """
    Prepare the output directory for SORBET results.

    :param params: ParamDict, the parameter dictionary of constants
    """
    # generate SID if not given
    if params['SORBET.GENERAL.SID'] is None:
        params['SORBET.GENERAL.SID'] = mc_general.miriam_unique_id()
    # get the output path from the params
    output_path = params[f'MIRIAM.INPUTS.OUTPUT_PATH']
    # make sure we have the full path
    output_path = os.path.realpath(output_path)
    # deal with output path being an absolute path
    if os.path.exists(output_path):
        # print message on where outputs will be saved
        msg = f'All outputs will be saved under: {output_path}'
        WLOG(params, 'info', msg)
        return
    # if not, make it relative to the global database
    output_path = os.path.join(params['GLOBAL.DATA_PATH'], 'sorbet',
                               params['SORBET.GENERAL.SID'],
                               params[f'MIRIAM.INPUTS.OUTPUT_PATH'])
    # make sure the path is in the params
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    # update output path
    params[f'MIRIAM.INPUTS.OUTPUT_PATH'] = output_path
    # print message on where outputs will be saved
    msg = f'All outputs will be saved under: {output_path}'
    WLOG(params, 'info', msg)


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

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2025-10-17 at 10:48

@author: cook
"""
import time

from aperocore.constants.param_functions import ParamDict
from aperocore.core import drs_log
from aperocore.core import drs_misc
from pogos.core import base
from pogos.core import general as pogos_general
from pogos.tsovore.instruments import select as ts_select
from pogos.tsovore.instruments import default as ts_default
from sossisse.core import misc


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'pogos.tsovore.core.general'
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
# TODO: Move to APERO-CORE
def tsovore_unique_id() -> str:
    """
    Assign a miriam id based on the time now and return it and the
    time now

    :return: the process id and the human time at creation
    :rtype: Tuple[str, str]
    """
    # get unix char code
    unixtime, humantime, rval = pogos_general.unix_char_code()
    # write sid
    sid = 'MID-{0:020d}-{1}'.format(int(unixtime), rval)
    # return sid
    return sid


def run_tsovore(params: ParamDict) -> ts_default.JWST:
    """
    Run the TSOVORE processing

    :param params: ParamDict, the parameter dictionary of constants

    :return:
    """
    # set the function name
    func_name = f'{__NAME__}.run_miriam'
    # print the white light curve splash
    print(misc.art('TSOvore', 'yellow', 'CYAN'))
    time.sleep(0.1)
    # prepare the directories
    prepare_directories(params)
    # now we load the instrument specific parameters
    inst = ts_select.load_instrument(params)
    # run the tsovore processing
    inst.process()
    # summary step
    inst.summary()
    # return parameters
    return inst


def setup_tsovore_module(params: ParamDict):
    """
    Setup the TSOVORE module within POGOS.

    :param params: ParamDict, the parameter dictionary of constants

    :return: ParamDict, the updated parameter dictionary of constants
    """
    # set the function name
    func_name = f'{__NAME__}.setup_tsovore_module'
    # deal with no requiring to run miriam
    if not params['RUN.TSOVORE']:
        return params
    # setup input and output directories
    prepare_directories(params)
    # return params
    return params


def prepare_directories(params: ParamDict):

    sid_path = 'TSOVORE.GENERAL.SUBDIRECTORY'
    sid_null = tsovore_unique_id()
    mode = 'tsovore'
    # -------------------------------------------------------------------------
    # set parameters for preparing directory
    pkind = 'input'
    file_path = f'TSOVORE.PATHS.INPUT_PATH'
    # run the prepare directory function
    pogos_general.prepare_directory(params, pkind, sid_path, sid_null,
                                    file_path, mode)
    # -------------------------------------------------------------------------
    pkind = 'temp'
    file_path = f'TSOVORE.PATHS.TEMP_PATH'
    # run the prepare directory function
    pogos_general.prepare_directory(params, pkind, sid_path, sid_null,
                                    file_path, mode)
    # -------------------------------------------------------------------------
    pkind = 'plot'
    file_path = f'TSOVORE.PATHS.PLOT_PATH'
    # runt the prepare directory function
    pogos_general.prepare_directory(params, pkind, sid_path, sid_null,
                                    file_path, mode)
    # -------------------------------------------------------------------------
    # set parameters for preparing directory
    pkind = 'output'
    file_path = f'TSOVORE.PATHS.OUTPUT_PATH'
    # runt the prepare directory function
    pogos_general.prepare_directory(params, pkind, sid_path, sid_null,
                                    file_path, mode)

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

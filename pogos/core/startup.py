#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2024-10-29 at 10:16

@author: cook
"""
import argparse
import os
import string
from typing import Optional

from aperocore.constants import param_functions
from aperocore.constants import load_functions
from aperocore.core import drs_log
from aperocore.core import drs_text

from pogos.core import base
from pogos import constants
from pogos.constants import constants as pogo_constants

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'pogos.recipes.run.py'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__
# get parameter dictionary
ParamDict = param_functions.ParamDict
# get constant dictionary
ConstDict = pogo_constants.ConstDict
# get the logger
WLOG = drs_log.wlog
# Define paths to create
PATHS = ['GLOBAL.DATA_PATH', 'GLOBAL.PLOT_PATH']
# Set the description of APERO Core
DESCRIPTIONS = dict()
DESCRIPTIONS['pogos.recipes.test_setup'] = 'Setup POGOS'
DESCRIPTIONS['pogos.recipes.test_run'] = 'Run POGOS'

INPUTARGS = dict()
INPUTARGS['pogos.recipes.test_setup'] = ['GLOBAL.YAML_FILE', 'DATA_PATH',
                                             'PLOT_PATH']
INPUTARGS['pogos.recipes.test_run'] = ['GLOBAL.YAML_FILE']


# =============================================================================
# Define functions
# =============================================================================
def setup(params: ParamDict):
    """
    Setup the general module

    :return: None
    """
    # print progress
    WLOG(params, 'info', params['LOG.HEADER'])
    WLOG(params, 'info', 'Checking arguments')
    WLOG(params, 'info', params['LOG.HEADER'])
    # ask user for any missing arguments
    params = load_functions.ask_for_missing_args(params)
    # ----------------------------------------------------------------------
    # print progress
    WLOG(params, 'info', params['LOG.HEADER'])
    WLOG(params, 'info', 'Checking paths')
    WLOG(params, 'info', params['LOG.HEADER'])
    # Create some paths
    for path in PATHS:
        # deal with path not existing in params (skip) - these really should
        #    exist though
        if path not in params:
            continue
        # convert path to a real absolute path
        params[path] = os.path.abspath(params[path])
        # find if path exists
        if os.path.exists(params[path]):
            WLOG(params, '', 'Path exists: {0}'.format(params[path]))
            continue
        # ask user to create path
        question = '\nPath does not exist: {0}\nWould you like to create it?'
        question = question.format(params[path])
        # ask user
        if drs_text.user_input(question, dtype='YN', required=True):
            os.makedirs(params[path])


    # ----------------------------------------------------------------------
    # print progress
    WLOG(params, 'info', params['LOG.HEADER'])
    WLOG(params, 'info', 'Constructing yaml file')
    WLOG(params, 'info', params['LOG.HEADER'])
    # Get the merged constants dictionary
    cdict = ConstDict.merge_configs(params['CONFIG_LIST'])
    # get the yaml file
    yaml_file = params['GLOBAL.YAML_FILE']
    # print progress
    msg = 'Saving constants to yaml file: {0}'
    WLOG(params, '', msg.format(os.path.realpath(yaml_file)))
    # save the constants dictionary to yaml file
    cdict.save_yaml(params, outpath=yaml_file, log=False)


def initial_setup():

    # define which constant lists we should be using
    const_list = dict()
    const_list['TSOVORE_SIM'] = constants.TSOVORE_SimCDict
    const_list['TSOVORE_IMCAL'] = constants.TSOVORE_ImCDict
    const_list['MIRIAM'] = constants.MIRIAM_CDict
    const_list['SORBET_WLCTA'] = constants.SORBET_WLCTA_CDict
    const_list['SORBET_SLCTA'] = constants.SORBET_SLCTA_CDict
    const_list['SORBET_TFIT'] = constants.SORBET_TFIT_CDict
    const_list['SORBET_RV'] = constants.SORBET_RV_CDict

    # add those external ones
    const_list.update(base.EXTERNAL_CONST)

    # ----------------------------------------------------------------------
    # ask user whether they want to start from a demo file or to turn on
    # individual features
    # ----------------------------------------------------------------------
    q1 = """Would you like to start from:
         - [D]emo setup (set values)
         - [S]witch features on/off (default values)
         - [A]ll features on (default values)
         """
    # # get user input
    # a1 = drs_text.user_input(q1, dtype='str', options=['D', 'S', 'A'],
    #                          required=True)
    # # ----------------------------------------------------------------------
    # if a1 == 'D':
    #     # print demos available
    #     WLOG(None, '', 'Demos available:')
    #     pass
    #
    # elif a1 == 'S':
    #     # print features available
    #     WLOG(None, '', 'Features available:')
    #     pass
    # else:
    #     pass


    # return the updated extenral constants list
    return const_list



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

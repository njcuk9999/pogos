#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

Transit fit of the SLC

Created on 2024-12-02

@author: CharlesCadieux
"""
import os

from aperocore.core import drs_log
from aperocore.constants import load_functions

from pogos.constants.constants import CDict
from pogos.core import base
from pogos.core import general
from pogos.core import startup
from pogos import sorbet


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'pogos.sorbet.recipes.run_sorbet_wlcta'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__
# set description
__description__ = 'Run the POGOS recipe'
__inputs__ = ['GLOBAL.YAML_FILE']
# get the logger
WLOG = drs_log.wlog


# =============================================================================
# Define functions
# =============================================================================
def main(**kwargs):
    # print splash
    general.start_splash('POGOS')
    # get other configs (either internal like SORBET or external like SOSSISSE)
    other_const = startup.initial_setup()
    # get parameters
    params = load_functions.get_all_params(name=__NAME__,
                                           description=__description__,
                                           inputargs=__inputs__,
                                           param_file_path='GLOBAL.YAML_FILE',
                                           config_list=[CDict],
                                           external_const=other_const,
                                           kwargs=kwargs)
    # -------------------------------------------------------------------------
    # print yaml file used
    msg = f'Using yaml file: {os.path.realpath(params["GLOBAL.YAML_FILE"])}'
    WLOG(params, 'info', msg)
    # run the spectral light curve analysis
    if params['SORBET.WLCTA.RUN']:
        sorbet.general.run_sorbet_wlcta(params)


def run():
    """
    Wrapper script for command line - no return
    :return:
    """
    _ = main()


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    _ = main()

# =============================================================================
# End of code
# =============================================================================



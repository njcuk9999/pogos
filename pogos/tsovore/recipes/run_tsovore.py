#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

Transit fit of the SLC

Created on 2025-10-16

@author: Cook
"""
import os

from aperocore.core import drs_log
from aperocore.constants import load_functions

from pogos.constants.constants import CDict
from pogos.core import base
from pogos.core import general
from pogos.core import startup
from pogos import tsovore


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'pogos.tsovore.recipes.run_sorbet_slca'
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
    yaml_file = params.rget('GLOBAL.YAML_FILE', required=True)
    run_tsovore = params.rget('TSOVORE.RUN', required=True)
    # -------------------------------------------------------------------------
    # print yaml file used
    msg = f'Using yaml file: {os.path.realpath(yaml_file)}'
    WLOG(params, 'info', msg)
    # run the spectral light curve analysis
    if run_tsovore:
        tsovore.general.run_tsovore(params)


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    _ = main()

# =============================================================================
# End of code
# =============================================================================



#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2024-10-29 at 09:32

@author: cook
"""
from aperocore.core import drs_log
from aperocore.constants import load_functions
import sossisse

from pogos.constants.constants import CDict
from pogos.core import base
from pogos.core import general
from pogos import tsovore
from pogos import sossisse_wrap
from pogos import sorbet


# =============================================================================
# Define variables
__NAME__ = 'pogos.recipes.pogos_run'
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
    # get parameters
    params = load_functions.get_all_params(name=__NAME__,
                                           description=__description__,
                                           inputargs=__inputs__,
                                           param_file_path='GLOBAL.YAML_FILE',
                                           config_list=[CDict],
                                           external_const=base.EXTERNAL_CONST,
                                           kwargs=kwargs)

    # -------------------------------------------------------------------------
    # run tsovore
    if params['RUN.TSOVORE']:
        tsovore.run_tsovore(params)
    # run sossisse_wrap
    if params['RUN.SOSSISSE']:
        sossisse_wrap.run_sossisse(params)
    # run sorbet
    if params['RUN.SORBET']:
        sorbet.run_sorbet(params)
    # -------------------------------------------------------------------------
    # print splash
    general.end_splash()


def run():
    _ = main()

# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    _ = main()

# =============================================================================
# End of code
# =============================================================================

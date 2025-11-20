#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2024-10-29 at 09:32

@author: cook
"""
import string

from aperocore.constants import load_functions
from aperocore.constants import param_functions
from aperocore.core import drs_log
from aperocore.core import drs_text
from pogos.constants import constants as pogo_constants
from pogos.constants.constants import CDict
from pogos.core import base as pogos_base
from pogos.core import general
from pogos.core import startup

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'pogos.recipes.pogos_copy'
__PACKAGE__ = pogos_base.__PACKAGE__
__version__ = pogos_base.__version__
__authors__ = pogos_base.__authors__
__date__ = pogos_base.__date__
__release__ = pogos_base.__release__
# set description
__description__ = ('Copy a POGOS demo yaml file to walk the user through '
                   'setting up a new yaml file and matching file structure.')
__inputs__ = ['GLOBAL.DEMO_FILE']
# get parameter dictionary
ParamDict = param_functions.ParamDict
# get constant dictionary
ConstDict = pogo_constants.ConstDict
# get the logger
WLOG = drs_log.wlog

# =============================================================================
# Define functions
# =============================================================================
def main(**kwargs):
    # print splash
    general.start_splash('POGOS Copy')
    # get other configs (either internal like SORBET or external like SOSSISSE)
    other_const = startup.initial_setup()
    # get parameters
    params = load_functions.get_all_params(name=__NAME__,
                                           description=__description__,
                                           inputargs=__inputs__,
                                           param_file_path='GLOBAL.DEMO_FILE',
                                           config_list=[CDict],
                                           external_const=other_const,
                                           kwargs=kwargs)
    # -------------------------------------------------------------------------
    # Print some basic properties to make sure user has correct file
    WLOG(params, 'info', 'Loaded demo file:')
    # print some info loaded from the demo file
    variables = ['GLOBAL.DEMO_FILE', 'GLOBAL.DATA_PATH',
                 'GLOBAL.INSTRUMENTMODE']
    # determine which submodules are being run
    for submodule in pogos_base.SUBMODULES:
        if 'RUN.{0}'.format(submodule) in params:
            variables.append('RUN.{0}'.format(submodule))
    # print out the variables
    for variable in variables:
        WLOG(params, '', '    - {0} = {1}'.format(variable, params[variable]),
             colour='magenta', no_timestamp=True)
    # -------------------------------------------------------------------------
    # question: new description
    # -------------------------------------------------------------------------
    # this is common to all sub-modules
    # ---------------------------------------------------------------------
    params = startup.copy_ask_description(params)

    # -------------------------------------------------------------------------
    # question: new sub-directory
    # -------------------------------------------------------------------------
    params = startup.copy_ask_subdirectories(params)


    # TODO: need to generate paths (somehow) so we can tell user where to
    #       copy files

    # -------------------------------------------------------------------------
    # clear out files (and tell user they need to copy files)
    # -------------------------------------------------------------------------
    params = startup.copy_clear_files(params)

    # TODO: Save yaml - or re-save?
    print('stop')

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

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2024-10-29 at 09:32

@author: cook
"""
import sys
# Ensure we're importing the installed packages, not a local directory
# Remove current directory from sys.path if present to avoid import confusion
if '' in sys.path:
    sys.path.remove('')
if '.' in sys.path:
    sys.path.remove('.')

from aperocore.constants import load_functions
from aperocore.constants import param_functions
from aperocore.core import drs_log
from aperocore.core import drs_text
from pogos.constants import constants as pogo_constants
from pogos.constants.constants import CDict
from pogos.core import base as pogos_base
from pogos.core import general
from pogos.core import startup
from pogos import tsovore
from pogos import sossisse_wrap
from pogos import miriam
from pogos import sorbet


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
__inputs__ = ['GLOBAL.DEMO_FILE', 'GLOBAL.LIST_YAMLS']
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
    # listing functionality
    if startup.quick_args(sys.argv): return
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

    # Ask user if this setup is okay
    prompt = ('\nPlease check the above values. '
              '\n\nIs this the correct demo file you wish to copy and modify? '
              '\n\nIf you answer "no" we will exit now.')
    # get the new description
    valid_start = drs_text.user_input(prompt, dtype='YN', required=True)
    # deal with exiting here
    if not valid_start:
        # print splash
        general.end_splash()
        return

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

    # -------------------------------------------------------------------------
    # clear out files
    # -------------------------------------------------------------------------
    filesets = startup.copy_clear_files(params)

    # -------------------------------------------------------------------------
    # Ask for required parameters in modules
    # -------------------------------------------------------------------------
    params = startup.copy_ask_req_module_params(params)

    # -------------------------------------------------------------------------
    # setup using parameters (same as pogos_setup)
    cdict = startup.setup(params, start_from_demo=False)
    # -------------------------------------------------------------------------
    # setup individual modules (same as pogos_setup)
    params = tsovore.setup_tsovore_module(params)
    sossisse_wrap.setup_sossisse_module(params, cdict)
    params = miriam.setup_miriam_module(params)
    params = sorbet.setup_sorbet_module(params)

    # -------------------------------------------------------------------------
    # Tell user where they may need to copy files
    if len(filesets) > 0:
        msg = ('You will need to copy your inputs files to one or more of '
               'the following directories. '
               '\n\nPlease note if using multiple '
               'steps, you may only need to copy files to the first step.')
        WLOG(params, 'info', msg, colour='magenta', no_timestamp=True)
        WLOG(params, 'info', '', colour='magenta', no_timestamp=True)
        for fileset in filesets:
            # get the param value
            pvalue = params[filesets[fileset]]
            msg = '    - {0}: {1}'.format(fileset, pvalue)
            WLOG(params, '', msg, colour='magenta', no_timestamp=True)

    # -------------------------------------------------------------------------
    # final remarks on reading the yaml file
    msg = ('\n\nIt is important to note that pogos_copy only copies the '
           'demo yaml file and sets up the basic directory structure. '
           '\n\nPlease open the new yaml file and check all parameters '
           'before running on your own data.'
           '\n\nThe yaml file is located here: {0}\n\n')
    margs = [params['GLOBAL.YAML_FILE']]
    WLOG(params, 'info', msg.format(*margs), colour='magenta',
         no_timestamp=True)

    # -------------------------------------------------------------------------
    # Also tell the user they will need to change values in each of the
    # sub-module sections (like Object name etc
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

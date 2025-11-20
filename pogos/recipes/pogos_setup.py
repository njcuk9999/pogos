#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2024-10-29 at 09:32

@author: cook
"""

from aperocore.constants import load_functions

from pogos.constants.constants import CDict
from pogos.core import base
from pogos.core import startup
from pogos.core import general
from pogos import tsovore
from pogos import sossisse_wrap
from pogos import miriam
from pogos import sorbet

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'pogos.recipes.pogos_setup'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__
# set description
__description__ = ('Setup the POGOS recipes starting from a demo.'
                   'Creates a configuration (yaml) file and a file structure')
__inputs__ = ['GLOBAL.YAML_FILE', 'GLOBAL.DATA_PATH']

# =============================================================================
# Define functions
# =============================================================================
def main(**kwargs):
    # print splash
    general.start_splash('POGOS Setup')
    # get other configs (either internal like SORBET or external like SOSSISSE)
    other_const = startup.initial_setup()
    # get parameters
    params = load_functions.get_all_params(name=__NAME__,
                                           description=__description__,
                                           inputargs=__inputs__,
                                           config_list=[CDict],
                                           from_file=False,
                                           external_const=other_const,
                                           kwargs=kwargs)
    # -------------------------------------------------------------------------
    # setup using parameters
    cdict = startup.setup(params)
    # -------------------------------------------------------------------------
    # setup individual modules
    params = tsovore.setup_tsovore_module(params)
    sossisse_wrap.setup_sossisse_module(params, cdict)
    params = miriam.setup_miriam_module(params)
    params = sorbet.setup_sorbet_module(params)
    # -------------------------------------------------------------------------
    # ask for data download
    load_functions.download_data(params)
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

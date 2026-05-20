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
from aperocore.core import drs_log

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
# get the logger
WLOG = drs_log.wlog
# set description
__description__ = ('Setup the POGOS recipes starting from a demo.'
                   'Creates a configuration (yaml) file and a file structure')
__inputs__ = ['GLOBAL.YAML_FILE', 'GLOBAL.DATA_PATH',
              'GLOBAL.LOCAL_DOWNLOAD_DATA','GLOBAL.DEMO_SYMLINK_DATA']

# =============================================================================
# Define functions
# =============================================================================
def main(**kwargs):
    try:
        __main__(**kwargs)
    except KeyboardInterrupt:
        msg = 'POGOS setup interrupted by user. Exiting.'
        print()
        WLOG(None, 'warning', msg, colour='red')
        WLOG(None, '', '')
        general.end_splash()

def __main__(**kwargs):
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
    # get the demo local value
    demolocal = params.get('GLOBAL.LOCAL_DOWNLOAD_DATA', None)
    demosymlink = params.get('GLOBAL.DEMO_SYMLINK_DATA', False)
    # ask for data download
    load_functions.download_data(params, demolocal=demolocal,
                                 demosymlink=demosymlink)
    # -------------------------------------------------------------------------
    # Check CRDS setup
    startup.check_crds(params)
    # -------------------------------------------------------------------------
    # Tell user to look at the yaml file created
    msg = 'Please review the yaml file created at:'
    msg += '\n  {0} \n\n You can now run POGOS with'
    msg += '\n\n\t>> pogos_run --yamlfile={0}'
    msg += '\n\n and you can use \n\n\t>> pogos_copy --demo_file={0}'
    msg += '\n\nto use this as a basis for your own setup/data'
    margs = [params['GLOBAL.YAML_FILE']]
    WLOG(None, 'info', msg.format(*margs), colour='magenta')
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

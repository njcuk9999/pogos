#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2024-10-29 at 09:32

@author: cook
"""
import sys
import time
from pathlib import Path

# Fail fast if local folders would shadow installed packages.
_shadow_dirs = ('aperocore', 'pogos', 'sossisse')
if any((Path.cwd() / name).exists() for name in _shadow_dirs):
    raise SystemExit(
        f'Error: Current directory contains one of {"/".join(_shadow_dirs)}; '
        'please run pogos_setup from another directory.'
    )

from aperocore.constants import load_functions
from aperocore.core import drs_log

from pogos.constants.constants import CDict
from pogos.core import base
from pogos.core import file_download
from pogos.core import startup
from pogos.core import general
from pogos.core import recipe_helpers

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
__inputs__ = ['GLOBAL.YAML_FILE', 'GLOBAL.DATA_PATH', 'GLOBAL.PROJECT_NAME',
              'GLOBAL.LOCAL_DOWNLOAD_DATA', 'GLOBAL.DEMO_SYMLINK_DATA',
              'GLOBAL.INSTRUMENT_SELECT', 'GLOBAL.INSTRUMENT_MODE',
              'GLOBAL.PREEXTRACT_STEP', 'GLOBAL.EXTRACT_STEP',
              'GLOBAL.POSTEXTRACT_STEP', 'GLOBAL.DEMO_SELECT',
              'GLOBAL.DOWNLOAD_MODE']

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
    WLOG(None, '', 'Initialising POGOS parameters')
    start = time.time()
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
    WLOG(params, '', f'Parameters initialised in {time.time() - start:.1f} s')
    # -------------------------------------------------------------------------
    # setup using parameters
    cdict = startup.setup(params)
    # -------------------------------------------------------------------------
    # setup enabled pre-extract, extract and post-extract modules
    params = recipe_helpers.setup_enabled_modules(params, cdict, WLOG)

    # -------------------------------------------------------------------------
    # download online input files now or at the first run (asks the user,
    #   uses GLOBAL.LOCAL_DOWNLOAD_DATA as a local mirror if set)
    file_download.setup_downloads(params)
    # -------------------------------------------------------------------------
    # Check CRDS setup
    startup.check_crds(params)
    # -------------------------------------------------------------------------
    # Tell user to look at the yaml file created
    yaml_file = params['GLOBAL.YAML_FILE']
    msg = 'Please review the yaml file created at:'
    WLOG(None, 'info', msg, colour='magenta')
    general.print_command(yaml_file)
    WLOG(None, 'info', 'You can now run POGOS with:', colour='magenta')
    general.print_command(f'pogos_run --yamlfile={yaml_file}')
    msg = 'and use this as a basis for your own setup/data with:'
    WLOG(None, 'info', msg, colour='magenta')
    general.print_command(f'pogos_edit --demo_file={yaml_file}')
    # -------------------------------------------------------------------------
    # print splash
    general.end_splash()

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

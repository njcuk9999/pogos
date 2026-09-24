#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2026-09-23 at 09:05

@author: cook
"""
import os
import sys
from pathlib import Path

# Fail fast if local folders would shadow installed packages.
_shadow_dirs = ('aperocore', 'pogos', 'sossisse')
if any((Path.cwd() / name).exists() for name in _shadow_dirs):
    raise SystemExit(
        f'Error: Current directory contains one of {"/".join(_shadow_dirs)}; '
        'please run pogos_setup from another directory.'
    )

from aperocore.core import drs_log
from aperocore.core import drs_text
from aperocore.constants import load_functions

from pogos.constants.constants import CDict
from pogos.core import base as pogos_base
from pogos.core import definitions
from pogos.core import general
from pogos.core import recipe_helpers
from pogos.core import reset
from pogos.core import startup

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'pogos.recipes.pogos_reset'
__PACKAGE__ = pogos_base.__PACKAGE__
__version__ = pogos_base.__version__
__authors__ = pogos_base.__authors__
__date__ = pogos_base.__date__
__release__ = pogos_base.__release__
# set description
__description__ = ('Reset a POGOS profile by deleting (and recreating empty) '
                   'every output/plot/temporary/other directory that POGOS '
                   'created for the enabled reduction steps in a given yaml '
                   'file. Raw input files, calibration/reference directories, '
                   'and anything not scoped to this profile\'s SUBDIRECTORY '
                   '(e.g. shared yaml backups) are never touched.')
__inputs__ = ['GLOBAL.YAML_FILE', 'GLOBAL.LIST_YAMLS']
# version error text
verr = ('The POGOS version of the {0} is not compatible with '
        'the current version of the code ({1}). '
        'Please update the config file to be compatible with the '
        'current version of the code.'
        ' You can use pogos_config to update an old config file.')
# get the logger
WLOG = drs_log.wlog

# =============================================================================
# Define functions
# =============================================================================
def main(**kwargs):
    # print splash
    general.start_splash('POGOS Reset')
    # quick_args functionality
    if startup.quick_args(sys.argv): return
    # get other configs (either internal like SORBET or external like SOSSISSE)
    other_const = startup.initial_setup()
    # get parameters
    params = load_functions.get_all_params(name=__NAME__,
                                           description=__description__,
                                           inputargs=__inputs__,
                                           param_file_path='GLOBAL.YAML_FILE',
                                           config_list=[CDict],
                                           from_file=False,
                                           external_const=other_const,
                                           kwargs=kwargs)
    # get yaml path and run interactive version check gate
    yaml_file = load_functions.get_param_file(params, 'GLOBAL.YAML_FILE',
                                              __NAME__)
    yaml_file = os.path.realpath(yaml_file)
    if not recipe_helpers.allow_stale_yaml_version(
            params, yaml_file, __version__, verr, WLOG):
        WLOG(params, 'warning', 'User declined to continue with stale yaml.')
        general.end_splash()
        return
    # load yaml after version acknowledgement
    largs = dict(files=[yaml_file], params=params,
                 version=None, version_err=None)
    params = load_functions.load_from_yaml(**largs)
    # mirror get_all_params behavior after file load
    params = WLOG.minimal_params(params)
    # print yaml file used
    WLOG(params, 'info', f'Using yaml file: {yaml_file}')
    # -------------------------------------------------------------------------
    # Make sure runs are not None - this means something is very wrong with
    # the yaml file
    for step in definitions.RED_STEPS:
        run_key = step.run_key
        if params.get(run_key) is None:
            wmsg = ('{0} is None - this means the yaml is out-of-date. '
                    'Please update the yaml file with pogos_setup')
            WLOG(params, 'warning', wmsg.format(run_key))
            params[run_key] = False
    # -------------------------------------------------------------------------
    # work out what this profile's reset would touch
    targets, protected = reset.get_reset_targets(params)
    targets, warnings = reset.filter_safe_targets(params, targets, protected)
    for warning in warnings:
        WLOG(params, 'warning', warning)
    # -------------------------------------------------------------------------
    # deal with nothing to reset
    if len(targets) == 0:
        WLOG(params, 'info', 'Nothing to reset - no POGOS-created output, '
                             'plot, temporary or other directories were '
                             'found on disk for this profile.')
        general.end_splash()
        return
    # -------------------------------------------------------------------------
    # print what will be deleted
    WLOG(params, 'info', 'The following directories will be deleted and '
                         'recreated empty:')
    ndirs = reset.print_summary(params, targets)
    # -------------------------------------------------------------------------
    # refuse to delete data non-interactively
    if recipe_helpers.is_ci_mode(kwargs):
        WLOG(params, 'warning', 'CI mode: refusing to delete data '
                                'non-interactively. Re-run interactively to '
                                'confirm this reset.')
        general.end_splash()
        return
    # -------------------------------------------------------------------------
    # ask user to confirm before deleting anything
    noun = 'directory' if ndirs == 1 else 'directories'
    prompt = ('\n{0} {1} listed above will be permanently deleted and '
              'recreated empty.'
              '\n\nRaw input files and calibration/reference directories '
              'are not touched.'
              '\n\nDo you want to continue?').format(ndirs, noun)
    proceed = drs_text.user_input(prompt, dtype='YN', required=True)
    if not proceed:
        WLOG(params, 'info', 'User cancelled. Nothing was deleted.')
        general.end_splash()
        return
    # -------------------------------------------------------------------------
    # do the reset
    reset.perform_reset(params, targets)
    WLOG(params, 'info', 'Reset complete.')
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

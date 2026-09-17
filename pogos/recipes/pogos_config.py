#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2026-09-01 at 09:05

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

from aperocore.constants import load_functions
from aperocore.core import drs_log

from pogos.constants.constants import CDict
from pogos.core import base as pogos_base
from pogos.core import general
from pogos.core import recipe_helpers
from pogos.core import startup

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'pogos.recipes.pogos_config'
__PACKAGE__ = pogos_base.__PACKAGE__
__version__ = pogos_base.__version__
__authors__ = pogos_base.__authors__
__date__ = pogos_base.__date__
__release__ = pogos_base.__release__
# set description
__description__ = ('Validate a POGOS yaml file against current constants and '
                   'optionally interactively fix invalid values.')
__inputs__ = ['GLOBAL.YAML_FILE', 'GLOBAL.LIST_YAMLS']
# version error text
verr = ('The POGOS version of the {0} is not compatible with '
        'the current version of the code ({1}). '
        'Please update the config file to be compatible with the '
        'current version of the code.')
# get the logger
WLOG = drs_log.wlog


def main(**kwargs):
    # print splash
    general.start_splash('POGOS Config')
    # quick_args functionality
    if startup.quick_args(sys.argv):
        return
    # get other configs (either internal like SORBET or external like SOSSISSE)
    other_const = startup.initial_setup()
    # get parameters (without loading yaml yet)
    params = load_functions.get_all_params(name=__NAME__,
                                           description=__description__,
                                           inputargs=__inputs__,
                                           config_list=[CDict],
                                           from_file=False,
                                           external_const=other_const,
                                           kwargs=kwargs)
    # avoid interactive prompts in CI mode
    if params['GLOBAL.YAML_FILE'] is None:
        if recipe_helpers.is_ci_mode(kwargs):
            emsg = 'CI mode requires GLOBAL.YAML_FILE (e.g. --yamlfile=...)'
            WLOG(params, 'error', emsg)
        params = load_functions.ask_for_missing_args(
            params, include_keys=['GLOBAL.YAML_FILE'])
    yaml_file = params['GLOBAL.YAML_FILE']
    if yaml_file is None:
        WLOG(params, 'warning', 'No yaml file supplied. Exiting.')
        general.end_splash()
        return

    yaml_file = os.path.realpath(str(yaml_file))
    if not os.path.exists(yaml_file):
        WLOG(params, 'error', f'Yaml file does not exist: {yaml_file}')

    ci_mode = recipe_helpers.is_ci_mode(kwargs)
    # run validation (interactive by default, non-interactive for CI)
    report = load_functions.validate_yaml_config(config_list=[CDict],
                                                 yaml_file=yaml_file,
                                                 external_const=other_const,
                                                 version=__version__,
                                                 version_err=verr,
                                                 raise_version_exception=False,
                                                 interactive=not ci_mode,
                                                 config_script='pogos_setup',
                                                 save_if_changed=not ci_mode)

    # summary report
    WLOG(params, 'info', params['LOG.HEADER'])
    WLOG(params, 'info', f'Config check complete for: {yaml_file}')
    WLOG(params, 'info', params['LOG.HEADER'])

    if not report['version_ok']:
        WLOG(params, 'warning', f'Version mismatch detected (expected {__version__}).')

    if report['aborted']:
        WLOG(params, 'warning', 'Validation stopped by user after version warning.')
        general.end_splash()
        return

    WLOG(params, 'info', f'Unknown constants: {len(report["unknown"])}')
    WLOG(params, 'info', f'Invalid values: {len(report["invalid"])}')

    for item in report['invalid']:
        msg = ('Invalid value -> {0} = {1}\n'
               'Reason: {2}')
        margs = [item['key'], item['value'], item['error']]
        WLOG(params, 'warning', msg.format(*margs))

    for suggestion in report['suggestions']:
        WLOG(params, 'warning', suggestion)

    if report['changes_made']:
        WLOG(params, 'info', 'Updated yaml file saved with interactive fixes.')

    if len(report['unknown']) == 0 and len(report['invalid']) == 0:
        WLOG(params, 'info', 'Yaml file is fully compatible with current constants.')

    if ci_mode:
        has_failures = ((not report['version_ok'])
                        or (len(report['unknown']) > 0)
                        or (len(report['invalid']) > 0)
                        or report['aborted'])
        if has_failures:
            WLOG(params, 'warning', 'CI mode: configuration validation failed.')
            general.end_splash()
            raise SystemExit(1)
        WLOG(params, 'info', 'CI mode: configuration validation passed.')

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

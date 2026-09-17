#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2024-10-29 at 09:32

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
from aperocore.constants import load_functions

from pogos.constants.constants import CDict
from pogos.core import base as pogos_base
from pogos.core import definitions
from pogos.core import general
from pogos.core import recipe_helpers
from pogos.core import startup

# =============================================================================
# Define variables
__NAME__ = 'pogos.recipes.pogos_run'
__PACKAGE__ = pogos_base.__PACKAGE__
__version__ = pogos_base.__version__
__authors__ = pogos_base.__authors__
__date__ = pogos_base.__date__
__release__ = pogos_base.__release__
# set description
__description__ = ('Run the POGOS recipe using a configuration (yaml) file.'
                   ' All input data needs to be placed according to the yaml '
                   'file given and all data and plots will be saved in the '
                   'outpaths given in the input yaml file.')
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
    general.start_splash('POGOS')
    (tsovore, sossisse_wrap, miriam, sorbet,
     jwst_wrap, nameless_wrap, eureka_wrap) = recipe_helpers.load_modules(
        ['tsovore', 'sossisse_wrap', 'miriam', 'sorbet',
         'jwst_wrap', 'nameless_wrap', 'eureka_wrap'])
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
    msg = f'Using yaml file: {yaml_file}'
    WLOG(params, 'info', msg)
    # -------------------------------------------------------------------------
    # Check CRDS setup
    startup.check_crds(params)
    # -------------------------------------------------------------------------
    # Make sure runs are not None - this means something is very wrong with
    # the yaml file
    for step in definitions.RED_STEPS:
        run_key = step.run_key
        if params.get(run_key) is None:
            # construct warning message
            wmsg = ('{0} is None - this means the yaml is out-of-date. '
                    'Please update the yaml file with pogos_setup')
            wargs = [run_key]
            # print a warning
            WLOG(params, 'warning', wmsg.format(*wargs))
            params[run_key] = False
    # -------------------------------------------------------------------------
    # Check that user is not trying to run multiple reduction steps from
    # the same level (unless this is allowed)
    startup.check_red_steps(params)
    # Check global/module instrument modes and reduction-step support.
    startup.check_instrument_modes(params)
    # =========================================================================
    # Pre-extraction steps
    # =========================================================================
    # Need to store all the pre-extraction instances in a dictionary so that
    # they can be passed to the extraction steps and used to determine inputs
    pre_inst = dict()
    # run tsovore
    if definitions.TSOVORE.is_enabled(params):
        pre_inst['tsovore'] = tsovore.run_tsovore(params)
    else:
        pre_inst['tsovore'] = None
    # -------------------------------------------------------------------------
    # run pre-eureka
    if definitions.PRE_EUREKA.is_enabled(params):
        pre_inst['pre_eureka'] = eureka_wrap.run_eureka_pre_extract(params)
    else:
        pre_inst['pre_eureka'] = None
    # -------------------------------------------------------------------------
    # run pre jwst
    if definitions.PRE_JWST.is_enabled(params):
        pre_inst['pre_jwst'] = jwst_wrap.run_jwst_pre_extract(params)
    else:
        pre_inst['pre_jwst'] = None
    # -------------------------------------------------------------------------
    # run NAMELESS
    if definitions.PRE_NAMELESS.is_enabled(params):
        pre_inst['pre_nameless'] = nameless_wrap.run_nameless_pre_extract(params)
    else:
        pre_inst['pre_nameless'] = None

    # =========================================================================
    # Extraction steps
    # =========================================================================
    # Need to store all the extraction instances in a dictionary so that
    # they can be passed to the post-extraction steps and used to
    # determine inputs
    ext_inst = dict()
    # run simple box extract
    if definitions.EXT_BOX.is_enabled(params):
        # ext_inst['EXT_BOX'] = tools.extract.run_box(params, **pre_inst)
        ext_inst['ext_box'] = None
    else:
        ext_inst['ext_box'] = None
    # -------------------------------------------------------------------------
    # run eureka
    if definitions.EXT_EUREKA.is_enabled(params):
        ext_inst['ext_eureka'] = eureka_wrap.run_eureka_extract(params,
                                                                pre_inst)
    else:
        ext_inst['ext_eureka'] = None
    # -------------------------------------------------------------------------
    # run jwst
    if definitions.EXT_JWST.is_enabled(params):
        ext_inst['ext_jwst'] = jwst_wrap.run_jwst_extract(params, pre_inst)
    else:
        ext_inst['ext_jwst']  = None
    # -------------------------------------------------------------------------
    # run nameless
    if definitions.EXT_NAMELESS.is_enabled(params):
        ext_inst['ext_nameless'] = nameless_wrap.run_nameless_extract(params,
                                                                      pre_inst)
    else:
        ext_inst['ext_nameless']  = None
    # -------------------------------------------------------------------------
    # run sossisse_wrap
    if definitions.SOSSISSE.is_enabled(params):
        ext_inst['sossisse'] = sossisse_wrap.run_sossisse(params, pre_inst)
    else:
        ext_inst['sossisse'] = None
    # -------------------------------------------------------------------------
    # run miriam
    if definitions.MIRIAM.is_enabled(params):
        ext_inst['miriam'] = miriam.run_miriam(params, pre_inst)
    else:
        ext_inst['miriam'] = None

    # =========================================================================
    # Post-extraction steps
    # =========================================================================
    # run sorbet
    if sorbet.any_sorbet_run(params):
        sorbet.run_sorbet(params, ext_inst)
    # -------------------------------------------------------------------------
    # run eureka post-extraction steps
    if definitions.POST_EUREKA.is_enabled(params):
        eureka_wrap.run_eureka_post_extract(params, ext_inst)
    # -------------------------------------------------------------------------
    # run jwst post-extraction steps
    if definitions.POST_JWST.is_enabled(params):
        jwst_wrap.run_jwst_post_extract(params, ext_inst)
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

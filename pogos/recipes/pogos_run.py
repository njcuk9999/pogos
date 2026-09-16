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
from importlib import import_module
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
from pogos.core import general
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

_LAZY_MODULES = {'tsovore', 'sossisse_wrap', 'miriam', 'sorbet',
                 'jwst_wrap', 'nameless_wrap', 'eureka_wrap'}


def __getattr__(name):
    if name in _LAZY_MODULES:
        module = import_module(f'pogos.{name}')
        globals()[name] = module
        return module
    raise AttributeError(f'module {__name__!r} has no attribute {name!r}')


def _get_module(name):
    if name in globals():
        return globals()[name]
    return __getattr__(name)


def _load_run_modules():
    names = ['tsovore', 'sossisse_wrap', 'miriam', 'sorbet',
             'jwst_wrap', 'nameless_wrap', 'eureka_wrap']
    return tuple(_get_module(name) for name in names)


# =============================================================================
# Define functions
# =============================================================================
def _allow_stale_yaml_version(params, yaml_file: str) -> bool:
    """
    Check yaml version and ask user whether to continue if it is stale.
    """
    version_ok = load_functions._check_yaml_version(yaml_file,
                                                    __version__,
                                                    verr,
                                                    raise_exception=False)
    if version_ok:
        return True

    # always show the compatibility warning
    WLOG(params, 'warning', verr.format(yaml_file, __version__))

    # allow non-interactive override for scripted runs
    override = os.environ.get('POGOS_ACCEPT_OLD_YAML', '').strip().lower()
    if override in ['1', 'true', 'yes', 'y']:
        WLOG(params, 'warning', 'Continuing with stale yaml because '
                                'POGOS_ACCEPT_OLD_YAML is set.')
        return True

    # if not interactive, require explicit env override
    if not sys.stdin.isatty():
        emsg = ('Yaml version mismatch detected in non-interactive mode. '
                'Set POGOS_ACCEPT_OLD_YAML=1 to continue anyway.')
        WLOG(params, 'error', emsg)

    question = ('\nYaml version appears to be incompatible and something '
                'could break.\nDo you want to continue anyway?')
    return drs_text.user_input(question, dtype='YN', required=True)


def main(**kwargs):
    # print splash
    general.start_splash('POGOS')
    (tsovore, sossisse_wrap, miriam, sorbet,
     jwst_wrap, nameless_wrap, eureka_wrap) = _load_run_modules()
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
    if not _allow_stale_yaml_version(params, yaml_file):
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
    for run_key in list(pogos_base.RUN_KEYS.keys()):
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
    # -------------------------------------------------------------------------
    # Check that the raw JWST headers match the selected instrument mode.
    startup.check_raw_data_headers(params)
    # =========================================================================
    # Pre-extraction steps
    # =========================================================================
    # Need to store all the pre-extraction instances in a dictionary so that
    # they can be passed to the extraction steps and used to determine inputs
    pre_inst = dict()
    # run tsovore
    if params['RUN.TSOVORE']:
        pre_inst['tsovore'] = tsovore.run_tsovore(params)
    else:
        pre_inst['tsovore'] = None
    # -------------------------------------------------------------------------
    # run pre-eureka
    if params['RUN.PRE_EUREKA']:
        pre_inst['pre_eureka'] = eureka_wrap.run_eureka_pre_extract(params)
    else:
        pre_inst['pre_eureka'] = None
    # -------------------------------------------------------------------------
    # run pre jwst
    if params['RUN.PRE_JWST']:
        pre_inst['pre_jwst'] = jwst_wrap.run_jwst_pre_extract(params)
    else:
        pre_inst['pre_jwst'] = None
    # -------------------------------------------------------------------------
    # run NAMELESS
    if params['RUN.PRE_NAMELESS']:
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
    if params['RUN.EXT_BOX']:
        # ext_inst['EXT_BOX'] = tools.extract.run_box(params, **pre_inst)
        ext_inst['ext_box'] = None
    else:
        ext_inst['ext_box'] = None
    # -------------------------------------------------------------------------
    # run eureka
    if params['RUN.EXT_EUREKA']:
        ext_inst['ext_eureka'] = eureka_wrap.run_eureka_extract(params,
                                                                pre_inst)
    else:
        ext_inst['ext_eureka'] = None
    # -------------------------------------------------------------------------
    # run jwst
    if params['RUN.EXT_JWST']:
        ext_inst['ext_jwst'] = jwst_wrap.run_jwst_extract(params, pre_inst)
    else:
        ext_inst['ext_jwst']  = None
    # -------------------------------------------------------------------------
    # run nameless
    if params['RUN.EXT_NAMELESS']:
        ext_inst['ext_nameless'] = nameless_wrap.run_nameless_extract(params,
                                                                      pre_inst)
    else:
        ext_inst['ext_nameless']  = None
    # -------------------------------------------------------------------------
    # run sossisse_wrap
    if params['RUN.SOSSISSE']:
        ext_inst['sossisse'] = sossisse_wrap.run_sossisse(params, pre_inst)
    else:
        ext_inst['sossisse'] = None
    # -------------------------------------------------------------------------
    # run miriam
    if params['RUN.MIRIAM']:
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
    if params['RUN.POST_EUREKA']:
        eureka_wrap.run_eureka_post_extract(params, ext_inst)
    # -------------------------------------------------------------------------
    # run jwst post-extraction steps
    if params['RUN.POST_JWST']:
        jwst_wrap.run_jwst_post_extract(params, ext_inst)
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

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
# Ensure we're importing the installed packages, not a local directory
# Remove current directory from sys.path if present to avoid import confusion
if '' in sys.path:
    sys.path.remove('')
if '.' in sys.path:
    sys.path.remove('.')

from aperocore.core import drs_log
from aperocore.constants import load_functions

from pogos.constants.constants import CDict
from pogos.core import base as pogos_base
from pogos.core import general
from pogos import tsovore
from pogos import sossisse_wrap
from pogos import miriam
from pogos import sorbet
from pogos import jwst_wrap
from pogos import nameless_wrap
from pogos import eureka_wrap
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
# get the logger
WLOG = drs_log.wlog


# =============================================================================
# Define functions
# =============================================================================
def main(**kwargs):
    # print splash
    general.start_splash('POGOS')
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
                                           external_const=other_const,
                                           kwargs=kwargs)
    # -------------------------------------------------------------------------
    # print yaml file used
    msg = f'Using yaml file: {os.path.realpath(params["GLOBAL.YAML_FILE"])}'
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

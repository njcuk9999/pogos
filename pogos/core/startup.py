#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2024-10-29 at 10:16

@author: cook
"""
import os
from typing import Any

from aperocore.constants import param_functions
from aperocore.constants import load_functions
from aperocore.core import drs_log
from aperocore.core import drs_text


from pogos.core import base
from pogos import constants
from pogos.constants import constants as pogo_constants
from pogos.resources import demos as demo_mod

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'pogos.recipes.run.py'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__
# get parameter dictionary
ParamDict = param_functions.ParamDict
# get constant dictionary
ConstDict = pogo_constants.ConstDict
# get the logger
WLOG = drs_log.wlog
# Define paths to create
PATHS = ['GLOBAL.DATA_PATH', 'GLOBAL.PLOT_PATH']
# Set the description of APERO Core
DESCRIPTIONS = dict()
DESCRIPTIONS['pogos.recipes.test_setup'] = 'Setup POGOS'
DESCRIPTIONS['pogos.recipes.test_run'] = 'Run POGOS'

INPUTARGS = dict()
INPUTARGS['pogos.recipes.test_setup'] = ['GLOBAL.YAML_FILE', 'DATA_PATH',
                                         'PLOT_PATH']
INPUTARGS['pogos.recipes.test_run'] = ['GLOBAL.YAML_FILE']

# deal with switching off sections (for yaml file)
RUN_KEYS = dict()
RUN_KEYS['RUN.TSOVORE'] = 'TSOVORE'
RUN_KEYS['RUN.SOSSISSE'] = 'SOSSISSE'
RUN_KEYS['RUN.MIRIAM'] = 'MIRIAM'
RUN_KEYS['RUN.SORBET'] = 'SORBET'
# deal with settings initial directories from pogos data directory
RUN_DIRS = dict()
RUN_DIRS['RUN.TSOVORE'] = 'TSOVORE.INPUTS.PATH'
RUN_DIRS['RUN.SOSSISSE'] = 'SOSSISSE.INPUTS.SOSSIOPATH'
RUN_DIRS['RUN.MIRIAM'] = 'MIRIAM.INPUTS.PATH'
RUN_DIRS['RUN.SORBET'] = 'SORBET.INPUTS.PATH'


# =============================================================================
# Define functions
# =============================================================================
def setup(params: ParamDict):
    """
    Setup the general module

    :return: None
    """
    # ------------------------------------------------------------------------
    # deal with user selecting instrument, mode and reduction steps
    params, demo_list = core_setup(params, demo_mod)

    # deal with start point (setup only) - ask user to start from demo or blank
    params = load_functions.starting_point(params, 'GLOBAL.INSTRUMENTMODE',
                                           demo_list)
    # -------------------------------------------------------------------------
    # print progress
    WLOG(params, 'info', params['LOG.HEADER'])
    WLOG(params, 'info', 'Checking arguments')
    WLOG(params, 'info', params['LOG.HEADER'])
    # -------------------------------------------------------------------------
    # ask user for run arguments
    run_keys = list(RUN_KEYS.keys())
    params = load_functions.ask_for_missing_args(params, include_keys=run_keys)
    # -------------------------------------------------------------------------
    # Deal with disabling sections we don't need in the yaml
    for run_key in run_keys:
        # if False turn off the section
        if not params[run_key]:
            for key in params.keys():
                if key.startswith(RUN_KEYS[run_key]):
                    params.instances[key].user = False
                    params.instances[key].not_none = False
    # -------------------------------------------------------------------------
    # ask user for any missing arguments
    params = load_functions.ask_for_missing_args(params,
                                                 include_keys=['GLOBAL.DATA_PATH'])
    # -------------------------------------------------------------------------
    # create paths to sub modules
    for run_key in RUN_KEYS:
        # get run value
        run_value = RUN_KEYS[run_key]
        # get path to directory
        run_path = os.path.join(params['GLOBAL.DATA_PATH'], run_value.lower())
        # make directory if it doesn't already exist
        if not os.path.exists(run_path):
            # print making directory
            WLOG(params, '', 'Creating directory: {}'.format(run_path))
            # make directory
            os.makedirs(run_path)
        # update parameters
        if run_key in RUN_DIRS:
            params[RUN_DIRS[run_key]] = run_path
    # -------------------------------------------------------------------------
    # ask user for any missing arguments
    params = load_functions.ask_for_missing_args(params)
    # ----------------------------------------------------------------------
    # print progress
    WLOG(params, 'info', params['LOG.HEADER'])
    WLOG(params, 'info', 'Checking paths')
    WLOG(params, 'info', params['LOG.HEADER'])
    # Create some paths
    for path in PATHS:
        # deal with path not existing in params (skip) - these really should
        #    exist though
        if path not in params:
            continue
        # convert path to a real absolute path
        params[path] = os.path.abspath(params[path])
        # find if path exists
        if os.path.exists(params[path]):
            WLOG(params, '', 'Path exists: {0}'.format(params[path]))
            continue
        # ask user to create path
        question = '\nPath does not exist: {0}\nWould you like to create it?'
        question = question.format(params[path])
        # ask user
        if drs_text.user_input(question, dtype='YN', required=True):
            os.makedirs(params[path])
    # ----------------------------------------------------------------------
    # print progress
    WLOG(params, 'info', params['LOG.HEADER'])
    WLOG(params, 'info', 'Constructing yaml file')
    WLOG(params, 'info', params['LOG.HEADER'])
    # Get the merged constants dictionary
    cdict = ConstDict.merge_configs(params['CONFIG_LIST'])
    # get the yaml file
    yaml_file = params['GLOBAL.YAML_FILE']
    # print progress
    msg = 'Saving constants to yaml file: {0}'
    WLOG(params, '', msg.format(os.path.realpath(yaml_file)))
    # save the constants dictionary to yaml file
    cdict.save_yaml(params, outpath=yaml_file, log=False)

    return cdict


def test_yamlfile(params: ParamDict):
    """
    Make sure yaml file is a file (and path exists)

    :param params: ParamDict, the parameters dictionary of constants
    :return:
    """
    # Make sure yaml file is a file (and path exists)
    yaml_file = params['GLOBAL.YAML_FILE']
    yaml_path = os.path.dirname(yaml_file)
    yaml_source = params.sources['GLOBAL.YAML_FILE']
    # deal with source (from command line or not)
    const_name = 'GLOBAL.YAML_FILE'
    if 'command' in yaml_source:
        const_name = f'--{params.instances["GLOBAL.YAML_FILE"].cmd_arg}'
    # -------------------------------------------------------------------------
    # don't test if yaml file is None (will be asked for later)
    if yaml_File is None:
        return
    # Make sure yaml file is not a directory
    if os.path.isdir(yaml_file):
        emsg = '{0} cannot be a directory: {1}'
        eargs = [const_name, yaml_file]
        raise base.PogosException(emsg.format(*eargs))
    # -------------------------------------------------------------------------
    try:
        if not os.path.exists(yaml_path):
            os.makedirs(yaml_path)
    except Exception as e:
        emsg = 'Cannot create path for GLOBAL.YAML_FILE: {0}\n{1}'
        eargs = [yaml_path, str(e)]
        raise base.PogosException(emsg.format(*eargs))


def core_setup(params: ParamDict, demo_mod: Any):
    """
    Deal with user selecting instrument, mode and reduction steps

    :param params: ParamDict, the parameters dictionary
    :return: ParamDict, the updated parameters dictionary
    """
    # -------------------------------------------------------------------------
    # define function name
    func_name = f'{__NAME__}.core_setup()'
    # -------------------------------------------------------------------------
    # Make sure yaml file is a file (and path exists)
    test_yamlfile(params)
    # -------------------------------------------------------------------------
    # get instrument modes
    instrument_modes = base.INSTRUMENT_MODES
    imode = None
    # -------------------------------------------------------------------------
    while imode is None:
        insts = list(instrument_modes.keys())
        ivalues = list(range(1, len(insts) + 1))
        # ask user for instrument
        question = 'Select instrument:'
        inst_choice = drs_text.user_input(question, dtype=int, options=ivalues,
                                          optiondescs=insts)
        instrument = insts[inst_choice - 1]
        # ---------------------------------------------------------------------
        # set the instrument modes
        imodes = list(instrument_modes[instrument])
        imode_values = list(range(1, len(imodes) + 1))
        # ask user for instrument mode
        question = 'Select instrument mode:'
        imode_choice = drs_text.user_input(question, dtype=int,
                                           options=imode_values,
                                           optiondescs=imodes)
        instrument_mode = imodes[imode_choice - 1]
        # ---------------------------------------------------------------------
        # deal with instrument mode not supported
        if instrument_modes[instrument][instrument_mode] is None:
            msg = ('{0}:{1} is not yet supported, please choose another')
            margs = [instrument, instrument_mode]
            WLOG(params, '', msg.format(*margs), colour='magenta')
            continue
        # ---------------------------------------------------------------------
        # set imode
        imode = instrument_modes[instrument][instrument_mode]
        # set instrument and mode in params
        params['GLOBAL.INSTRUMENTMODE'] = imode
        params.set_source('GLOBAL.INSTRUMENTMODE', func_name)
    # --------------------------------------------------------------------------
    # now ask about reduction steps
    # -------------------------------------------------------------------------
    # get the list of reduction steps
    red_steps = base.RED_STEPS
    # loop around red steps until we have all that are supported by this imode
    supported_steps = []
    # loop around reduction dictionary
    for core_step in red_steps:
        for mod_step in red_steps[core_step]:
            # deal with step not supported
            if red_steps[core_step][mod_step] is None:
                continue
            # deal with step not supported by this instrument mode
            if imode not in red_steps[core_step][mod_step]:
                continue
            # add to supported steps
            supported_steps.append(f'{core_step}:{mod_step}')
    # -------------------------------------------------------------------------
    # deal with no supported steps
    if len(supported_steps) == 0:
        emsg = 'No supported steps for instrument mode: {0}'
        eargs = [imode]
        raise base.PogosException(emsg.format(*eargs))
    # -------------------------------------------------------------------------
    # now ask user to select which steps to use
    demo_modes = []
    # set up options
    optiondescs = ['All'] + supported_steps
    # set up question
    question = ('Select all reductions steps')
    for oit, option in enumerate(optiondescs):
        question += '\n\t{0}: {1}'.format(oit, option)
    # loop around until all choices made
    drs_text.cprint(question, colour='magenta')
    # add input
    while True:
        uinput = input('Enter all numbers (comma separated):\t\t')

        if '0' in uinput:
            demo_modes = list(supported_steps)
            break
        # see it valid number were given as input
        for it in range(len(supported_steps)):
            if str(it + 1) in uinput:
                demo_modes.append(supported_steps[it])
        # if we have some modes we break
        if len(demo_modes) > 0:
            break
        # otherwise we ask again
        drs_text.cprint('No valid selection made, please try again.',
                        colour='yellow')
    # -------------------------------------------------------------------------
    # now we want to cut down demo_mod.DEMOS to only those selected
    demo_dict = dict()
    # loop around demo_mod demos to find those that match our criteria
    for inst_key in demo_mod.DEMOS:
        for demo_name in demo_mod.DEMOS[inst_key]:
            # get this specific demo
            demo = demo_mod.DEMOS[inst_key][demo_name]
            # get the INFO criteria
            info = demo.INFO
            # get the red steps
            red_steps = info.get('red_steps', [])
            # assume this demo passes our criteria below
            passed = False
            # loop around demo_modes
            for demo_mode in demo_modes:
                if demo_mode in red_steps:
                    passed = True
            # if passed we add this demo to the demo_dict
            if passed:
                # make sure instrument is in the demo_dict
                if inst_key not in demo_dict:
                    demo_dict[inst_key] = dict()
                # add mode
                demo_dict[inst_key][demo_name] = demo
    # -------------------------------------------------------------------------
    return params, demo_dict


def initial_setup():
    """
    Add all internal and external configs to const_list
    :return:
    """
    # -------------------------------------------------------------------------
    # Deal with internal first
    # -------------------------------------------------------------------------
    # define which constant lists we should be using
    const_list = dict()
    const_list['TSOVORE'] = constants.TSOVORE_CDict
    const_list['MIRIAM'] = constants.MIRIAM_CDict
    const_list['SORBET'] = constants.SORBET_CDict

    # add those external ones
    const_list.update(base.EXTERNAL_CONST)

    # return the updated extenral constants list
    return const_list



# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # print 'Hello World!'
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================

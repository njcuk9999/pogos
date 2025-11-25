#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2024-10-29 at 10:16

@author: cook
"""
import os
import string
import time
from typing import Any

from astropy.time import Time

from aperocore.constants import load_functions
from aperocore.constants import param_functions
from aperocore.core import drs_log
from aperocore.core import drs_text
from pogos import constants
from pogos.constants import constants as pogo_constants
from pogos.core import base as pogos_base
from pogos.resources import demos as demo_mod

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'pogos.core.startup.py'
__PACKAGE__ = pogos_base.__PACKAGE__
__version__ = pogos_base.__version__
__authors__ = pogos_base.__authors__
__date__ = pogos_base.__date__
__release__ = pogos_base.__release__
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


# list all file paths that may need clearing on copying a yaml
# should be in format: FILE_PATHS[<constant name>] = <path to directory constant>
FILE_PATHS = dict()
FILE_PATHS['MIRIAM.INPUTS.FILES'] = 'MIRIAM.PATHS.INPUT_PATH'
FILE_PATHS['SOSSISSE.GENERAL.FILES'] = 'SOSSISSE.PATHS.RAWPATH'
FILE_PATHS['SOSSISSE.GENERAL.WAVE_FILE'] = 'SOSSISSE.PATHS.CALIBPATH'
FILE_PATHS['TSOVORE.INPUTS.FILES'] = 'TSOVORE.PATHS.INPUT_PATH'
FILE_PATHS['SORBET.WLCTA.INPUT_FILE'] = 'SORBET.WLCTA.INPUT_PATH'
FILE_PATHS['SORBET.SLCTA.INPUT_FILE'] = 'SORBET.SLCTA.INPUT_PATH'

# list all the required parameters for each module when copying a yaml
REQ_MODULE_PARAMS = dict()
REQ_MODULE_PARAMS['TSOVORE'] = []
REQ_MODULE_PARAMS['SOSSISSE'] = ['SOSSISSE.INPUTS.OBJECTNAME']
REQ_MODULE_PARAMS['MIRIAM'] = []
REQ_MODULE_PARAMS['SORBET'] = []


# =============================================================================
# Define functions
# =============================================================================
def setup(params: ParamDict, start_from_demo: bool = True):
    """
    Setup the general module

    :return: None
    """
    # ------------------------------------------------------------------------
    # deal with user selecting instrument, mode and reduction steps
    params, demo_list = core_setup(params, demo_mod, start_from_demo)
    # if we are starting from a demo (i.e. no previous yaml)
    if start_from_demo:
        # deal with start point (setup only) - ask user to start from demo
        # or blank
        params = load_functions.starting_point(params, 'GLOBAL.INSTRUMENTMODE',
                                               demo_list)
    # -------------------------------------------------------------------------
    # print progress
    WLOG(params, 'info', params['LOG.HEADER'])
    WLOG(params, 'info', 'Checking other arguments')
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
                    # TODO: remove this if statement
                    # skip keys that are None (shouldn't be here so this is
                    # just for debugging)
                    if params.instances[key] is None:
                        print('Skipping key {0} (no instance)'.format(key))
                        continue
                    # otherwise set user and not_none to False
                    params.instances[key].user = False
                    params.instances[key].not_none = False
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
    # add to the title
    time_now = Time.now().iso
    cdict.title += '\n Yaml created on {0}'.format(time_now)
    # save the constants dictionary to yaml file
    cdict.save_yaml(params, outpath=yaml_file, log=False)
    # return the constants dictionary class
    return cdict


def test_yamlfile(params: ParamDict):
    """
    Make sure yaml file is a file (and path exists)

    :param params: ParamDict, the parameters dictionary of constants
    :return:
    """
    # Make sure yaml file is a file (and path exists)
    yaml_file = params['GLOBAL.YAML_FILE']
    # -------------------------------------------------------------------------
    # don't test if yaml file is None (will be asked for later)
    if yaml_file is None:
        return
    # don't test if the yaml file is just a file
    if os.sep not in yaml_file:
        return
    # -------------------------------------------------------------------------
    yaml_path = os.path.dirname(yaml_file)
    yaml_source = params.sources['GLOBAL.YAML_FILE']
    # deal with source (from command line or not)
    const_name = 'GLOBAL.YAML_FILE'
    if 'command' in yaml_source:
        const_name = f'--{params.instances["GLOBAL.YAML_FILE"].cmd_arg}'
    # -------------------------------------------------------------------------
    # make sure the yaml file is not blank
    if len(yaml_file) == 0:
        emsg = '{0} cannot be blank.'.format(const_name)
        raise pogos_base.PogosException(emsg)
    # Make sure yaml file is not a directory
    if os.path.isdir(yaml_file):
        emsg = '{0} cannot be a directory: {1}'
        eargs = [const_name, yaml_file]
        raise pogos_base.PogosException(emsg.format(*eargs))
    # -------------------------------------------------------------------------
    try:
        if not os.path.exists(yaml_path):
            os.makedirs(yaml_path)
    except Exception as e:
        emsg = 'Cannot create path for GLOBAL.YAML_FILE: {0}\n{1}'
        eargs = [yaml_path, str(e)]
        raise pogos_base.PogosException(emsg.format(*eargs))


def core_setup(params: ParamDict, demo_mod: Any, start_from_demo: bool = True):
    """
    Deal with user selecting instrument, mode and reduction steps

    :param params: ParamDict, the parameters dictionary
    :return: ParamDict, the updated parameters dictionary
    """
    # -------------------------------------------------------------------------
    # define function name
    func_name = f'{__NAME__}.core_setup()'

    # -------------------------------------------------------------------------
    # Ask for the global data path
    # -------------------------------------------------------------------------
    if params['GLOBAL.DATA_PATH'] is None:
        WLOG(params, 'info', params['LOG.HEADER'])
        WLOG(params, 'info', 'Checking GLOBAL.DATA_PATH')
        WLOG(params, 'info', params['LOG.HEADER'])
    # keep asking until this variable is set
    while params['GLOBAL.DATA_PATH'] is None:
        # get the desription of the data path from the constant instance
        description = params.instances['GLOBAL.DATA_PATH'].description
        # ask user for data path
        question = '\nPlease enter {0}\n'.format(description)
        data_path = drs_text.user_input(question, dtype=str, required=True)
        params['GLOBAL.DATA_PATH'] = data_path
        params.set_source('GLOBAL.DATA_PATH', func_name)

        # If directory does not exist ask the user if they want to create it
        if not os.path.exists(data_path):
            question = '\nPath does not exist: {0}\nWould you like to create it?'
            question = question.format(data_path)
            # ask user
            if drs_text.user_input(question, dtype='YN', required=True):
                os.makedirs(data_path)
            # otherwise we start again with the question
            else:
                params['GLOBAL.DATA_PATH'] = None
    # Deal with data path ending in /data/ (we will add this afterwards)
    #  so for now we remote it
    if os.path.basename(params['GLOBAL.DATA_PATH']) == 'data':
        data_path = os.path.dirname(params['GLOBAL.DATA_PATH'])
        params['GLOBAL.DATA_PATH'] = data_path
    # -------------------------------------------------------------------------
    # we want to make sure the yaml file is set
    # -------------------------------------------------------------------------
    if params['GLOBAL.YAML_FILE'] is None:
        WLOG(params, 'info', params['LOG.HEADER'])
        WLOG(params, 'info', 'Checking GLOBAL.YAML_FILE')
        WLOG(params, 'info', params['LOG.HEADER'])
    # Make sure yaml file is a file (and path exists)
    test_yamlfile(params)
    # keep asking until this variable is set
    while params['GLOBAL.YAML_FILE'] is None:
        # get the desription of the yaml file from the constant instance
        description = params.instances['GLOBAL.YAML_FILE'].description
        yamldir = os.path.join(params['GLOBAL.DATA_PATH'], 'yamls')
        # ask user for yaml file
        question = '\nPlease enter {0}'
        question += ('\n\nNote if no path is given the yaml file will '
                     'be put in the {1} directory.')
        question = question.format(description, yamldir)
        yaml_file = drs_text.user_input(question, dtype=str, required=True)
        params['GLOBAL.YAML_FILE'] = yaml_file
        params.set_source('GLOBAL.YAML_FILE', func_name)
        # test yaml file
        test_yamlfile(params)
        if params['GLOBAL.YAML_FILE'] is None:
            continue
        # test if we have no path
        if os.sep not in yaml_file:
            yaml_file = os.path.join(params['GLOBAL.DATA_PATH'], 'yamls',
                                     yaml_file)
            params['GLOBAL.YAML_FILE'] = yaml_file
            params.set_source('GLOBAL.YAML_FILE', func_name)
        # If directory does not exist ask the user if they want to create it
        yaml_path = os.path.dirname(yaml_file)
        if not os.path.exists(yaml_path):
            question = '\nPath does not exist: {0}\nWould you like to create it?'
            question = question.format(yaml_path)
            # ask user
            if drs_text.user_input(question, dtype='YN', required=True):
                os.makedirs(yaml_path)
            # otherwise we start again with the question
            else:
                params['GLOBAL.YAML_FILE'] = None
    # -------------------------------------------------------------------------
    # finally make sure the yaml file has .yaml on the end
    if not params['GLOBAL.YAML_FILE'].endswith('.yaml'):
        params['GLOBAL.YAML_FILE'] += '.yaml'
    # and finally make sure the data path has /data on the end
    if not os.path.basename(params['GLOBAL.DATA_PATH']) == 'data':
        # add data path
        params['GLOBAL.DATA_PATH'] = os.path.join(params['GLOBAL.DATA_PATH'],
                                                  'data')
        # make sure this data path exists
        if not os.path.exists(params['GLOBAL.DATA_PATH']):
            os.makedirs(params['GLOBAL.DATA_PATH'])
    # -------------------------------------------------------------------------
    # get instrument modes
    # -------------------------------------------------------------------------
    instrument_modes = pogos_base.INSTRUMENT_MODES
    # -------------------------------------------------------------------------
    if params['GLOBAL.INSTRUMENTMODE'] is None:
        WLOG(params, 'info', params['LOG.HEADER'])
        WLOG(params, 'info', 'Checking GLOBAL.INSTRUMENTMODE')
        WLOG(params, 'info', params['LOG.HEADER'])
        imode = None
    else:
        imode = params['GLOBAL.INSTRUMENTMODE']
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
    # -------------------------------------------------------------------------
    # if we are not in start_from_demo return here
    if not start_from_demo:
        return params, dict()
    # --------------------------------------------------------------------------
    # now ask about reduction steps
    # -------------------------------------------------------------------------
    # get the list of reduction steps
    red_steps = pogos_base.RED_STEPS
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
        raise pogos_base.PogosException(emsg.format(*eargs))
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
    const_list.update(pogos_base.EXTERNAL_CONST)

    # return the updated extenral constants list
    return const_list



def copy_ask_description(params: ParamDict):
    # print process
    WLOG(params, 'info', '*'*50)
    WLOG(params, 'info',  'Setting up new description')
    WLOG(params, 'info', '*'*50)
    # ---------------------------------------------------------------------
    descriptions = dict()
    # find a previous description if it exists
    for submodule in pogos_base.SUBMODULES:
        # skip if we don't have this sub-module
        if 'RUN.{0}'.format(submodule) not in params:
            continue
        # skip if not running
        if not params['RUN.{0}'.format(submodule)]:
            continue
        # get sub-params
        subparams = params.get(submodule)
        # define sub-directory path
        desc_key = None
        if 'GENERAL.DESCRIPTION' in subparams:
            desc_key = 'GENERAL.DESCRIPTION'
        elif 'INPUTS.DESCRIPTION' in subparams:
            desc_key = 'INPUTS.DESCRIPTION'
        # skip if no description
        if desc_key is None:
            continue
        # skip if no value set
        if subparams[desc_key] is None:
            continue
        # add a sub-dictionary
        descriptions[submodule] = dict()
        # save the key for params
        descriptions[submodule]['key'] = f'{submodule}.{desc_key}'
        # save the value from params
        descriptions[submodule]['value'] = subparams[desc_key]
        # save the description from the params instance
        desc_inst = params.instances[f'{submodule}.{desc_key}']
        descriptions[submodule]['desc'] = desc_inst.description
    # ---------------------------------------------------------------------
    # ask question
    question = ('Please enter a description for this POGOS yaml file.')
    question += '\n\nThis description will be applied to all sub-modules.'
    # just add the first one of these descriptions
    if len(descriptions) > 0:
        # get the submodules that have descriptions
        submodules = list(descriptions.keys())
        # get the first description and desc (assume they are all the same)
        #   this is not exactly true but via POGOS we will make them all
        #   the same
        value = descriptions[submodules[0]]['value']
        desc =  descriptions[submodules[0]]['desc']
        # if we have a description use it
        if desc is not None:
            question += '\n\n' + desc
        # if we have a previous value use it
        if value is not None:
            question += '\n\nPrevious description:\n"""\n{0}\n"""'.format(value)
    # -------------------------------------------------------------------------
    # get the new description
    new_description = drs_text.user_input(question, dtype=str, required=True)
    # -------------------------------------------------------------------------
    # update all descriptions
    for submodule in descriptions:
        params.set(key=descriptions[submodule]['key'],
                   value=new_description, source='user input')
    # -------------------------------------------------------------------------
    # return the updated params
    return params


def copy_ask_subdirectories(params: ParamDict):
    for submodule in pogos_base.SUBMODULES:
        # skip if we don't have this sub-module
        if 'RUN.{0}'.format(submodule) not in params:
            continue
        # skip if not running
        if not params['RUN.{0}'.format(submodule)]:
            continue
        # get sub-params
        subparams = params.get(submodule)
        # define sub-directory path
        subdir, subdir_key, desc_key = None, None, None
        if 'GENERAL.SUBDIRECTORY' in subparams:
            subdir_key = 'GENERAL.SUBDIRECTORY'
            desc_key = 'GENERAL.DESCRIPTION'
        elif 'INPUTS.SUBDIRECTORY' in subparams:
            subdir_key = 'INPUTS.SUBDIRECTORY'
            desc_key = 'INPUTS.DESCRIPTION'
        # skip if no sub-directory
        if subdir_key is None:
            continue
        # set the sub-directory value
        subdir = subparams[subdir_key]
        # get the description from the params instance
        subdir_inst = params.instances[f'{submodule}.{subdir_key}']
        if subdir_inst is not None:
            subdir_desc = subdir_inst.description
        else:
            subdir_desc = None
        # ---------------------------------------------------------------------
        # print process
        WLOG(params, 'info', '*'*50)
        subtitle = ('Setting up new sub-directory for '
                    '{0} module').format(submodule)
        WLOG(params, 'info', subtitle)
        WLOG(params, 'info', '*'*50)
        time.sleep(0.1)
        # ---------------------------------------------------------------------
        # ask question
        question = ('For the {0} module, Please enter a new value for {1}  '
                    '\n\nPrevious value = {2}'
                    ).format(submodule, subdir_key, subdir)
        if subdir_desc is not None:
            question += '\n\n' + subdir_desc
        # ---------------------------------------------------------------------
        # loop and ask the question
        while True:
            value = drs_text.user_input(question, dtype=str, required=True)
            # -----------------------------------------------------------------
            # make sure there are no white spaces
            if any([c.isspace() for c in value]):
                WLOG(params, '',
                     'The value cannot contain any white spaces. Please '
                     'try again.', no_timestamp=True, colour='yellow')
                continue

            if len(value) == 0:
                WLOG(params, '',
                     'The value cannot be empty. Please try again.',
                     no_timestamp=True, colour='yellow')
                continue
            # -----------------------------------------------------------------
            # make sure there are no special characters other than underscores
            char_passed = True
            for char in string.punctuation:
                if char != '_' and char in value:
                    WLOG(params, '',
                         'The value cannot contain special characters '
                         'other than underscores. Please try again.',
                         no_timestamp=True, colour='yellow')
                    char_passed = False
                    break
            # re-check and ask the question again
            if not char_passed:
                continue
            # -----------------------------------------------------------------
            # break the loop
            break
        # set the new value
        params.set(key=f'{submodule}.{subdir_key}', value=value,
                   source='user input')

    return params


def copy_clear_files(params: ParamDict):
    # set function name
    func_name = f'{__NAME__}.copy_clear_files()'
    # storage for found sets (used later to inform user)
    found_sets = dict()
    # list of files
    for fileset in list(FILE_PATHS.keys()):
        # skip if we don't have this fileset
        if fileset not in params:
            continue
        # get the value from params
        file_value = params[fileset]
        # skip if None or empty
        if file_value is None:
            continue
        if drs_text.null_text(file_value, ['None', '', 'Null']):
            continue
        # deal with empty string
        if isinstance(file_value, str):
            # skip if empty string
            if len(file_value) == 0:
                continue
        # deal with empty list (skip if empty)
        elif isinstance(file_value, list):
            if len(file_value) == 0:
                continue

        # save path for later
        found_sets[fileset] = FILE_PATHS[fileset]
        # update params
        params.set(key=fileset, value=[], source=func_name)
    # return the found sets (used to inform user later on where to
    # copy input files)
    return found_sets


def copy_ask_req_module_params(params: ParamDict):

    # set function name
    func_name = f'{__NAME__}.copy_ask_req_module_params()'
    # -------------------------------------------------------------------------
    # loop around sub-modules
    for submodule in REQ_MODULE_PARAMS:
        # skip question if we don't have this sub-module
        if 'RUN.{0}'.format(submodule) not in params:
            continue
        # skip if not running
        if not params['RUN.{0}'.format(submodule)]:
            continue
        # loop around required parameters
        for req_param in REQ_MODULE_PARAMS[submodule]:
            # skip if we don't have this required parameter
            if req_param not in params:
                continue
            # -----------------------------------------------------------------
            # print process
            WLOG(params, 'info', '*'*50)
            subtitle = ('Setting up required parameter '
                        '{0} for {1} module').format(req_param, submodule)
            WLOG(params, 'info', subtitle)
            WLOG(params, 'info', '*'*50)
            time.sleep(0.1)
            # -----------------------------------------------------------------
            ikeys = [req_param]
            # set value to None (so we ask for it)
            params.set(key=req_param, value=None, source=func_name,
                       instance=params.instances[req_param])
            # ask for missing args for this required parameter
            params = load_functions.ask_for_missing_args(params,
                                                         include_keys=ikeys)
    # -------------------------------------------------------------------------
    # return the updated parameters
    return params


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

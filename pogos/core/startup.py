#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2024-10-29 at 10:16

@author: cook
"""
import glob
import os
import string
import sys
import time
from typing import Any, List, Optional, Tuple

from pogos.constants import constants as pogo_constants
from pogos.core import base as pogos_base
from pogos.core import definitions

from aperocore.base import base as aperocore_base
from aperocore.constants import load_functions
from aperocore.constants import param_functions
from aperocore.core import drs_log
from aperocore.core import drs_text
from pogos import constants

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

# Define allowed punctuation for sub-directory names
VALID_PUNC = ['-', '+', '.', '_']

def _load_demo_module():
    from pogos.resources import demos as demo_module
    return demo_module


def _load_time_class():
    from astropy.time import Time
    return Time


def _load_crds_runtime():
    from crds.client import api as crds_api
    from crds.core import utils as crds_utils
    return crds_api, crds_utils


def _load_initial_setup_modules():
    from pogos import eureka_wrap
    from pogos import jwst_wrap
    from pogos import nameless_wrap
    from sossisse.core.constants import CDict as sossisse_cdict
    return eureka_wrap, jwst_wrap, nameless_wrap, sossisse_cdict


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
    demo_module = _load_demo_module() if start_from_demo else None
    params, demo_list = core_setup(params, demo_module, start_from_demo)
    # if we are starting from a demo (i.e. no previous yaml)
    if start_from_demo:
        # deal with start point (setup only) - ask user to start from demo
        # or blank
        params = load_functions.starting_point(params, 'GLOBAL.INSTRUMENTMODE',
                                               demo_list,
                                               ask_for_missing_on_no_demo=False)

    # now set up yaml file name
    params = core_yaml_setup(params)
    # -------------------------------------------------------------------------
    # print progress
    WLOG(params, 'info', params['LOG.HEADER'])
    WLOG(params, 'info', 'Checking other arguments')
    WLOG(params, 'info', params['LOG.HEADER'])
    # -------------------------------------------------------------------------
    # ask user for run arguments
    run_keys = [step.run_key for step in definitions.RED_STEPS]
    params = load_functions.ask_for_missing_args(params, include_keys=run_keys)
    # -------------------------------------------------------------------------
    # Deal with disabling sections we don't need in the yaml
    disable_prefixes = set()
    for step in definitions.RED_STEPS:
        if not step.is_enabled(params):
            disable_prefixes.add(step.parameter_prefix)
            disable_prefixes.update(step.sub_prefixes)

    # Disable shared configuration only when every owning step is disabled.
    shared_prefixes = {prefix for step in definitions.RED_STEPS
                       for prefix in step.shared_prefixes}
    for prefix in shared_prefixes:
        owners = [step for step in definitions.RED_STEPS
                  if prefix in step.shared_prefixes]
        if all(not step.is_enabled(params) for step in owners):
            disable_prefixes.add(prefix)

    for key in params.keys():
        if not any(key.startswith(prefix) for prefix in disable_prefixes):
            continue
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
    data_path = None
    for step in definitions.RED_STEPS:
        # don't create if we don't have the run key in params
        if step.run_key not in params:
            continue
        # don't create if RUN = False
        if not step.is_enabled(params):
            continue
        # wrappers with shared roots (eureka/nameless/jwst) manage their own
        # directory trees, so avoid creating empty generic stage folders.
        if not step.generic_run_dir:
            continue
        if data_path is None:
            data_path = params.rget('GLOBAL.DATA_PATH', required=True)
        # get run value
        run_value = step.name
        # get path to directory
        run_path = os.path.join(data_path, run_value.lower())
        # make directory if it doesn't already exist
        if not os.path.exists(run_path):
            # print making directory
            WLOG(params, '', 'Creating directory: {}'.format(run_path))
            # make directory
            os.makedirs(run_path)
        # update parameters
        if step.run_dir_key is not None:
            params[step.run_dir_key] = run_path
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
        absolute_path = os.path.abspath(params.rget(path, required=True))
        params[path] = absolute_path
        # find if path exists
        if os.path.exists(absolute_path):
            WLOG(params, '', 'Path exists: {0}'.format(absolute_path))
            continue
        # ask user to create path
        question = '\nPath does not exist: {0}\nWould you like to create it?'
        question = question.format(absolute_path)
        # ask user
        if drs_text.user_input(question, dtype='YN', required=True):
            os.makedirs(absolute_path)
    # ----------------------------------------------------------------------
    # print progress
    WLOG(params, 'info', params['LOG.HEADER'])
    WLOG(params, 'info', 'Constructing yaml file')
    WLOG(params, 'info', params['LOG.HEADER'])
    config_list = params.rget('CONFIG_LIST', required=True)
    yaml_file = params.rget('GLOBAL.YAML_FILE', required=True)
    # Get the merged constants dictionary
    cdict = ConstDict.merge_configs(config_list)
    # print progress
    msg = 'Saving constants to yaml file: {0}'
    WLOG(params, '', msg.format(os.path.realpath(yaml_file)))
    # add to the title
    time_now = _load_time_class().now().iso
    cdict.title += '\n Yaml created on {0}'.format(time_now)
    # deal with adding from demo (if required)
    # Form demos we do not need to ask the user
    if 'DEMO_PARAMS' in params:
        if 'ID' in params['DEMO_PARAMS']:
            # set yaml file from the DEMO ID
            demo_id = params['DEMO_PARAMS']['ID']
            cdict.title += '\n\n Based on demo ID: {0}'.format(demo_id)
    # save the constants dictionary to yaml file
    cdict.save_yaml(params, outpath=yaml_file, log=False,
                    mode=params['GLOBAL.INSTRUMENTMODE'])
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


def core_setup(params: ParamDict, demo_mod: Optional[Any],
               start_from_demo: bool = True) -> Tuple[ParamDict, dict]:
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
    # -------------------------------------------------------------------------
    # get instrument modes
    # -------------------------------------------------------------------------
    instrument_modes = definitions.mode_choices()
    # -------------------------------------------------------------------------
    imode: Optional[str]
    if params['GLOBAL.INSTRUMENTMODE'] is None:
        WLOG(params, 'info', params['LOG.HEADER'])
        WLOG(params, 'info', 'Checking GLOBAL.INSTRUMENTMODE')
        WLOG(params, 'info', params['LOG.HEADER'])
        imode = None
    else:
        imode = params['GLOBAL.INSTRUMENTMODE']
    # -------------------------------------------------------------------------
    # pre-answers from the command line (skip the interactive prompts)
    preset_inst = params['GLOBAL.INSTRUMENT_SELECT']
    preset_imode = params['GLOBAL.INSTRUMENT_MODE']
    # -------------------------------------------------------------------------
    while imode is None:
        insts = list(instrument_modes.keys())
        ivalues = list(range(1, len(insts) + 1))
        # ask user for instrument (or use the command line pre-answer)
        if preset_inst is not None:
            inst_choice = preset_inst
        else:
            question = 'Select instrument:'
            inst_choice = drs_text.user_input(question, dtype=int,
                                              options=ivalues,
                                              optiondescs=insts)
        instrument = insts[inst_choice - 1]
        # ---------------------------------------------------------------------
        # set the instrument modes
        imodes = list(instrument_modes[instrument])
        imode_values = list(range(1, len(imodes) + 1))
        # ask user for instrument mode (or use the command line pre-answer)
        if preset_imode is not None:
            imode_choice = preset_imode
        else:
            question = 'Select instrument mode:'
            imode_choice = drs_text.user_input(question, dtype=int,
                                               options=imode_values,
                                               optiondescs=[mode.label
                                                            for mode in imodes])
        instrument_mode = imodes[imode_choice - 1]
        # ---------------------------------------------------------------------
        # deal with instrument mode not supported
        if not instrument_mode.enabled:
            msg = ('{0}:{1} is not yet supported, please choose another')
            margs = [instrument, instrument_mode.label]
            WLOG(params, '', msg.format(*margs), colour='magenta')
            # a command line pre-answer cannot be re-asked - stop here
            if preset_inst is not None or preset_imode is not None:
                emsg = ('Command line instrument selection {0}:{1} is not '
                        'supported. Please correct --instrument_select / '
                        '--instrument_mode.')
                WLOG(params, 'error', emsg.format(*margs))
            continue
        # ---------------------------------------------------------------------
        # set imode
        imode = instrument_mode.name
        # set instrument and mode in params
        params['GLOBAL.INSTRUMENTMODE'] = imode
        params.set_source('GLOBAL.INSTRUMENTMODE', func_name)
    # -------------------------------------------------------------------------
    # if we are not in start_from_demo return here
    if not start_from_demo:
        return params, dict()
    if imode is None:
        raise pogos_base.PogosException('GLOBAL.INSTRUMENTMODE could not be resolved.')
    # --------------------------------------------------------------------------
    # now ask about reduction steps
    # -------------------------------------------------------------------------
    # now ask user to select which steps to use
    resolved_imode = str(imode)
    demo_modes = ask_reduction_steps(params, resolved_imode)
    # deal with no demo modes selected
    if len(demo_modes) == 0:
        return params, dict()
    # -------------------------------------------------------------------------
    # Push True into the run keys for demo_modes (this will decide what we
    #  ask the user about later)
    params = update_run_after_demo_modes(params, demo_modes)
    # -------------------------------------------------------------------------
    # now we want to cut down demo_mod.DEMOS to only those selected
    demo_dict = dict()
    # loop around demo_mod demos to find those that match our criteria
    for inst_key in demo_mod.DEMOS:
        for demo_name in demo_mod.DEMOS[inst_key]:
            # get this specific demo and construct
            demo_inst = demo_mod.DEMOS[inst_key][demo_name]()
            # get the reduction steps for this demo
            red_steps = demo_inst.redsteps
            # assume this demo passes our criteria below
            passed = False
            # loop around demo_modes
            for demo_mode in demo_modes:
                if demo_mode in red_steps:
                    passed = True
                # add demo mode to tmodes
                if demo_mode not in demo_inst.flavours:
                    # add to flavours
                    demo_inst.flavours.append(demo_mode)
                    # add to tflavours
                    # we use a shortname for these as they get a bit long
                    dsplit = demo_mode.split(':')
                    demo_inst.tflavours.append(f'{dsplit[1]}')
            # if passed we add this demo to the demo_dict
            if passed:
                # deal with first time we hit this instrument mode
                if inst_key not in demo_dict:
                    demo_dict[inst_key] = dict()
                # add the demo
                demo_dict[inst_key][demo_name] = demo_inst
    # -------------------------------------------------------------------------
    return params, demo_dict


def ask_reduction_steps(params: ParamDict, imode: str) -> List[str]:
    # Resolve the serialized mode name to its authoritative definition.
    instrument_mode = definitions.MODE_BY_NAME[imode]
    # Group supported steps under their ordered reduction levels.
    supported_steps = dict()
    for level in definitions.REDUCTION_LEVELS:
        level_steps = [step for step in definitions.steps_for_level(level)
                       if step.supports(instrument_mode)]
        if len(level_steps) > 0:
            supported_steps[level] = level_steps
    # -------------------------------------------------------------------------
    # deal with no supported steps
    if len(supported_steps) == 0:
        msg = 'No supported steps for instrument mode: {0}.'
        margs = [imode]
        WLOG(params, 'warning', msg.format(*margs))

        # ask user whether they wish to continue or exit
        question = 'Would you like to continue setting up POGOS? [Y]es or [N]o'
        if not drs_text.user_input(question, dtype='YN', required=True):
            # exit program (without traceback)
            WLOG(params, 'error', 'Exiting POGOS setup as per user request.',
                 raise_exception=False)
            raise SystemExit(0)
        # otherwise return
        return []
    # -------------------------------------------------------------------------
    # storage for output
    demo_modes = []
    run_values = []
    # command line pre-answers for each core step (skip interactive prompts)
    step_presets = {'Pre-extraction': params['GLOBAL.PREEXTRACT_STEP'],
                    'Extraction': params['GLOBAL.EXTRACT_STEP'],
                    'Post-extraction': params['GLOBAL.POSTEXTRACT_STEP']}
    # loop around supported steps and ask user which they want to use
    for level in supported_steps:
        # get the command line pre-answer for this step (None = ask the user)
        preset = step_presets.get(level.name, None)
        # deal with no supported steps for this step
        if len(supported_steps[level]) == 0:
            msg = 'No supported steps for {0} for instrument mode: {1}.'
            margs = [level.name, imode]
            drs_text.cprint(msg.format(*margs), colour='yellow')
        # ---------------------------------------------------------------------
        # Deal with allowing multiple options for this step
        # (e.g. for SORBET WLCA and SLCA)
        if level.allow_multiple:
            # set the question for this step
            question = 'Please choose flavour(s) of {0} for {1} or skip it.'
            question = question.format(level.name, imode)

            # set up options
            optiondescs = ['Skip'] + [step.name
                                      for step in supported_steps[level]]

            for oit, option in enumerate(optiondescs):
                question += '\n\t{0}: {1}'.format(oit, option)
            # add input
            while True:
                # use the command line pre-answer if given, else ask the user
                if preset is not None:
                    uinput = str(preset)
                else:
                    uinput = input(question + '\n\nEnter all numbers (comma '
                                              'separated):\t\t')
                # zero means skip
                if '0' in uinput:
                    break
                # otherwise we test what the user has given us
                valid = True
                _demo_modes = []
                # see it valid number were given as input
                uinputs = uinput.split(',')
                for _uinput in uinputs:
                    # anything that is not a digit is bad
                    try:
                        unum = int(_uinput.strip())
                    except ValueError:
                        emsg = 'Invalid input: {0}, please try again.'
                        drs_text.cprint(emsg.format(_uinput), colour='yellow')
                        valid = False
                        break
                    # at this point anything less than 1 or greater than
                    # the number of options is a bad input
                    if unum < 1 or unum >= len(optiondescs):
                        emsg = 'Option {0} not valid, please try again.'
                        drs_text.cprint(emsg.format(_uinput), colour='yellow')
                        valid = False
                        break
                    # add demo mode if it isn't already present
                    demo_mode = '{0}:{1}'.format(level.name,
                                                 optiondescs[unum])
                    if demo_mode not in _demo_modes:
                        _demo_modes.append(demo_mode)
                # ask the question again
                if not valid:
                    # a command line pre-answer cannot be re-asked
                    if preset is not None:
                        emsg = ('Command line --postextract_step={0} is not '
                                'valid for {1}.')
                        WLOG(params, 'error', emsg.format(preset, level.name))
                    continue
                else:
                    demo_modes += _demo_modes
                # if we have some modes we break
                if len(demo_modes) > 0:
                    break
                # a command line pre-answer cannot be re-asked
                if preset is not None:
                    break
                # otherwise we ask again
                drs_text.cprint('No valid selection made, please try again.',
                                colour='yellow')
        # ---------------------------------------------------------------------
        # Otherwise we only allow one option for this step
        else:
            # set the question for this step
            question = 'Please choose a flavour of {0} for {1} or skip it.'
            question = question.format(level.name, imode)
            # set up options and option descriptions (add skip as first option)
            optiondescs = ['Skip'] + [step.name
                                      for step in supported_steps[level]]
            options = list(range(len(optiondescs)))
            # use the command line pre-answer if given, else ask the user
            if preset is not None:
                uinput = str(preset)
            else:
                uinput = drs_text.user_input(question, dtype='options',
                                             options=options,
                                             optiondescs=optiondescs)
            # deal with skipping and adding to available demo modes
            if uinput.strip() == '0':
                continue
            else:
                # add demo mode if it isn't already present
                demo_mode = '{0}:{1}'.format(level.name,
                                             optiondescs[int(uinput)])
                if demo_mode not in demo_modes:
                    demo_modes.append(demo_mode)
    # return the demo modes
    return demo_modes


def update_run_after_demo_modes(params: ParamDict,
                                demo_modes: List[str]) -> ParamDict:
    """
    Update

    :param params:
    :param demo_modes:
    :return:
    """
    # set the function name
    func_name = f'{__NAME__}.update_run_after_demo_modes()'
    for demo_mode in demo_modes:
        # get the flavour our
        step, flavour = demo_mode.split(':')
        # only update RUN.{run_key} if its present in our RUN_KEYS
        if flavour in definitions.STEP_BY_NAME:
            # get the run key
            run_key = definitions.STEP_BY_NAME[flavour].run_key
            # set the run value to True
            params.set(run_key, value=True, source=func_name)
    # return the updated params
    return params


def core_yaml_setup(params: ParamDict):
    # -------------------------------------------------------------------------
    # define function name
    func_name = f'{__NAME__}.core_setup()'

    # Make sure yaml file is a file (and path exists)
    test_yamlfile(params)
    data_path = params.rget('GLOBAL.DATA_PATH', required=True)
    # keep asking until this variable is set
    while params['GLOBAL.YAML_FILE'] is None:
        # get the yaml directory
        yamldir = os.path.join(data_path, 'yamls')
        # create this directory
        if not os.path.exists(yamldir):
            os.makedirs(yamldir)
        # Form demos we do not need to ask the user
        if 'DEMO_PARAMS' in params:
            if 'ID' in params['DEMO_PARAMS']:
                if params['DEMO_PARAMS']['ID'] is not None:
                    # set yaml file from the DEMO ID
                    yamlfile = params['DEMO_PARAMS']['ID'] + '.yaml'
                    # get the full path
                    yaml_path = os.path.join(yamldir, yamlfile)
                    # push into params
                    params['GLOBAL.YAML_FILE'] = yaml_path
                    # tell the user what we have done
                    msg = 'Using demo ID to set yaml file to: {0}'
                    WLOG(params, '', msg.format(yaml_path))
                    # break the loop
                    break
        # ---------------------------------------------------------------------
        # get the description of the yaml file from the constant instance
        description = params.instances['GLOBAL.YAML_FILE'].description
        # ask user for yaml file
        question = '\nPlease enter {0}'
        question += ('\n\nNote if no path is given the yaml file will '
                     'be put in the {1} directory.')
        yaml_file = ''
        while len(yaml_file) < 3:
            question = question.format(description, yamldir)
            yaml_file = drs_text.user_input(question, dtype=str, required=True)
            # deal with no yaml file given
            if len(yaml_file) >= 3:
                # deal with no .yaml
                if not yaml_file.endswith('.yaml'):
                    yaml_file += '.yaml'

                break
            else:
                WLOG(params, 'warning', 'You need to at least name the '
                                        'yaml file with 3 characters,'
                                        ' please try again.')
                continue
        # ---------------------------------------------------------------------
        # set yaml file
        params['GLOBAL.YAML_FILE'] = yaml_file
        params.set_source('GLOBAL.YAML_FILE', func_name)
        # test yaml file
        test_yamlfile(params)
        if params['GLOBAL.YAML_FILE'] is None:
            continue
        # test if we have no path
        if os.sep not in yaml_file:
            yaml_file = os.path.join(yamldir, yaml_file)
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
    # and finally make sure the data exists
    if not os.path.exists(data_path):
        os.makedirs(data_path)
    # -------------------------------------------------------------------------
    return params


def initial_setup():
    """
    Add all internal and external configs to const_list
    :return:
    """
    # -------------------------------------------------------------------------
    # Deal with internal first
    # -------------------------------------------------------------------------
    eureka_wrap, jwst_wrap, nameless_wrap, sossisse_cdict = (
        _load_initial_setup_modules())
    # define which constant lists we should be using
    const_list = dict()
    const_list['TSOVORE'] = constants.TSOVORE_CDict
    const_list['EUREKA'] = eureka_wrap.Eureka_CDict
    const_list['STD_JWST'] = jwst_wrap.JWST_CDict
    const_list['NAMELESS'] = nameless_wrap.NAMELESS_CDict
    const_list['MIRIAM'] = constants.MIRIAM_CDict
    const_list['SORBET'] = constants.SORBET_CDict

    # add lazy-loaded external constants
    const_list['SOSSISSE'] = sossisse_cdict

    # add any additional external ones
    const_list.update(pogos_base.EXTERNAL_CONST)

    # return the updated extenral constants list
    return const_list


def check_red_steps(params: ParamDict):
    """
    Check that only one reduction step is being run for each step (if we have
    more than one step for this step we raise an error)

    :param params: ParamDict, the parameters dictionary of constants

    :return: None, raises an error if more than one reduction step
             is being run for any
    """
    # loop around all reduction steps and check that only one is being run f
    # or each step (if we have more than one step for this step we
    # raise an error)
    for level in definitions.REDUCTION_LEVELS:
        # start a counter
        counter = 0
        # do not check steps that are not in our multi flag list
        if level.allow_multiple:
            continue
        # get the red steps
        red_steps = definitions.steps_for_level(level)
        # otherwise we check which steps are being run for this step
        for red_step in red_steps:
            # first check for standard RUN.XXX = False (or True)
            run_step_str = red_step.run_key
            # we should check that the run step is defined
            if run_step_str in params:
                if params[run_step_str]:
                    counter += 1
                    continue
            # if it isn't raise an error
            else:
                emsg = (f'{run_step_str} [{level.name}] not defined in params. '
                        f'This is a developer error and a mismatch '
                        f'between parameters and the RedStep definitions.')
                raise pogos_base.PogosException(emsg)
        # if we have more than one step for this step we raise an error
        if counter > 1:
            emsg = ('Multiple reduction steps selected for {0}, but only one '
                    'is allowed. Please set only one of the following to True'
                    ' in the yaml file')
            for red_step in red_steps:
                emsg += f'\n - {red_step.run_key}'

            margs = [level.name]
            raise pogos_base.PogosException(emsg.format(*margs))


def check_instrument_modes(params: ParamDict):
    """
    Validate the global mode and synchronize active module mode parameters.

    :param params: ParamDict, POGOS parameters
    :return: None, raises PogosException for unknown or inconsistent modes
    """
    mode_name = params['GLOBAL.INSTRUMENTMODE']
    mode = definitions.MODE_BY_NAME.get(mode_name)
    if mode is None or not mode.enabled:
        raise pogos_base.PogosException(
            f'Unsupported GLOBAL.INSTRUMENTMODE: {mode_name}')
    for step in definitions.RED_STEPS:
        if not step.is_enabled(params):
            continue
        if not step.supports(mode):
            emsg = f'{step.name} does not support {mode.name}.'
            raise pogos_base.PogosException(emsg)
        if step.mode_key is None:
            continue
        module_mode = params.get(step.mode_key)
        if module_mode is None:
            params[step.mode_key] = mode.name
        elif module_mode != mode.name:
            emsg = (f'{step.mode_key}={module_mode} does not match '
                    f'GLOBAL.INSTRUMENTMODE={mode.name}.')
            raise pogos_base.PogosException(emsg)


def _propagate_crds_setup(crds_path: str, server_url: str):
    """
    Push CRDS configuration into the environment and refresh CRDS runtime
    state so already-imported CRDS/JWST modules see the updated settings.

    :param crds_path: str, CRDS cache root path
    :param server_url: str, CRDS server URL
    :return: tuple[str, str], normalized path and server URL
    """
    crds_api, crds_utils = _load_crds_runtime()
    # normalize inputs
    crds_path = os.path.realpath(crds_path)
    server_url = server_url.rstrip('/')

    # clear any derived CRDS path variables so CRDS_PATH is the single source
    # of truth for this runtime session
    for env_name in list(os.environ.keys()):
        if env_name.startswith('CRDS_') and 'PATH' in env_name:
            os.environ.pop(env_name, None)

    # push into environment
    os.environ['CRDS_PATH'] = crds_path
    os.environ['CRDS_SERVER_URL'] = server_url

    # CRDS keeps an in-memory server proxy once configured, so update it
    # explicitly for already-imported modules.
    crds_api.set_crds_server(server_url)

    # CRDS also memoizes a number of environment-dependent lookups (used by
    # stpipe/JWST as well), so clear those caches after updating the runtime
    # configuration.
    for cached_function in list(crds_utils.CachedFunction.cache_set):
        cached_function.cache.clear()

    return crds_path, server_url


def check_crds(params: ParamDict):
    data_path = params.rget('GLOBAL.DATA_PATH', required=True)
    # use any pre-existing CRDS setup if available, otherwise fall back to the
    # POGOS-managed cache inside the data directory
    check1 = 'CRDS_PATH' in os.environ
    check2 = 'CRDS_SERVER_URL' in os.environ
    crds_path = os.environ.get('CRDS_PATH',
                               os.path.join(data_path, 'crds'))
    server_url = os.environ.get('CRDS_SERVER_URL',
                                'https://jwst-crds.stsci.edu')

    # make sure directory exists
    if not os.path.exists(crds_path):
        os.makedirs(crds_path)

    if check1 and check2:
        WLOG(params, 'info', 'Previous CRDS setup detected')
    else:
        WLOG(params, 'info', 'Configuring CRDS runtime')

    crds_path, server_url = _propagate_crds_setup(crds_path, server_url)
    msg = 'Using CRDS cache: {0}\nUsing CRDS server: {1}'
    WLOG(params, 'info', msg.format(crds_path, server_url))



# =============================================================================
# Quick argument functionality
# =============================================================================
def quick_args(cmd_args: List[str], listing: bool = True):
    """
    Check for quick arguments
    :param cmd_args: list of args from sys.argv
    :return: bool, True if we want to exit, False if not
    """
    # set quick arg flags
    do_return = False
    do_listing = False
    # deal with no - or -- at start of first argument
    set_yaml_file(cmd_args)
    # loop around all arguments and look for --list
    for cmd_arg in cmd_args[1:]:
        if listing and '--list' in cmd_arg:
            do_listing = True
            break
    # deal with listing
    if do_listing:
        do_return = list_yamls()
    # print the modules
    return do_return


def set_yaml_file(cmd_args):
    # if we have no arguments skip this
    if len(cmd_args) <= 1:
        return
    # if we have only options skip this
    if cmd_args[1].startswith('-'):
        return
    # if we have only options skip this
    if cmd_args[1].startswith('--'):
        return
    # if the argument is a file that exists set sys.argv[1]
    if os.path.exists(cmd_args[1]):
        # make sure we are not overwriting an existing --yamlfile
        for cmd_arg in cmd_args:
            if '--yamlfile' in cmd_arg:
                return
        # update sys.argv[1]
        sys.argv[1] = '--yamlfile={0}'.format(cmd_args[1])


def _find_subdirs(obj, key: str='SUBDIRECTORY'):
    """
    Recursively search for any "key" keys
    anywhere inside the module dictionary. This will
    :param obj:
    :return:
    """
    found = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == key:
                found.append(v)
            else:
                found.extend(_find_subdirs(v))
    elif isinstance(obj, list):
        for item in obj:
            found.extend(_find_subdirs(item))
    return found


def list_yamls():

    """
    List all available POGOS demo yamls
    :return: bool, True if we want to exit, False if not
    """
    # get all yamls in the current working directory
    all_yaml_files = glob.glob('*.yaml')
    # -------------------------------------------------------------------------
    # try to read each yaml file and see if it is a POGOS yaml
    pogos_summaries = []
    pogos_yamls = []
    for yaml_file in all_yaml_files:
        try:

            # -----------------------------------------------------------------
            # load as text file
            idict = dict(red=aperocore_base.COLOURS['RED1'],
                         blue=aperocore_base.COLOURS['BLUE1'],
                         green=aperocore_base.COLOURS['GREEN1'],
                         end=aperocore_base.COLOURS['ENDC'],
                         POGOS=False)
            with open(yaml_file, 'r') as f:
                yaml_text = f.readlines()
            # loop around first 10 lines looking for version info
            for line in yaml_text[:10]:
                if 'POGOS' in line:
                    idict['POGOS'] = True
                elif 'Version = ' in line:
                    idict['Version'] = line.split('=')[-1].strip()
                elif 'Version Date' in line:
                    idict['Version Date'] = line.split('=')[-1].strip()
            # skip if no POGOS found this is not a valid yaml
            if not idict['POGOS']:
                continue
            # construct version string
            vstr = ('POGOS {red}v{Version}{green} '
                    '({blue}{Version Date}{green})').format(**idict)
            # -----------------------------------------------------------------
            # load the yaml file
            ydict = load_functions.base.load_yaml(yaml_file)
            # check if it is a POGOS yaml
            if 'GLOBAL' in ydict:
                # get instrument mode
                instmode = ydict['GLOBAL'].get('INSTRUMENTMODE', None)
                if instmode is None:
                    continue
                # make sure run is in the yaml
                if 'RUN' not in ydict:
                    continue
                # make sure data dict exists
                datadict = ydict['GLOBAL'].get('DATA_PATH', None)
                if datadict is None:
                    continue
                # start summary
                summary = f'{os.path.basename(yaml_file)}'
                summary += '\n' + '='*70
                summary += f'\n - {vstr}'
                summary += f'\n - Inst Mode: {instmode}'
                # loop around modules a
                for step in definitions.RED_STEPS:
                    module = step.name
                    run_mod = ydict['RUN'].get(module, False)
                    if not run_mod:
                        continue

                    if module in ydict and run_mod:
                        # Recursively search for any 'SUBDIRECTORY' keys
                        # anywhere inside the module dictionary. This will
                        # handle dicts or lists nested to any depth.
                        subdirs = _find_subdirs(ydict[module])
                        if len(subdirs) > 0:
                            dpath = os.path.join(datadict, module.lower(),
                                                 subdirs[0])
                            summary += '\n - {0}: {1}'.format(module, dpath)
                pogos_summaries.append(summary)
                pogos_yamls.append(yaml_file)
        except Exception:
            continue
    # -------------------------------------------------------------------------
    # deal with no yaml files found
    if len(pogos_yamls) == 0:
        drs_text.cprint('*'*70, colour='yellow')
        drs_text.cprint('No valid POGOS yaml files found in current directory.',
                        colour='yellow')
        drs_text.cprint('*'*70, colour='yellow')
        # return True to exit program
        return True
    # -------------------------------------------------------------------------
    # print splash
    drs_text.cprint('*'*70, colour='blue')
    drs_text.cprint('Available, valid POGOS yaml files:', colour='blue')
    drs_text.cprint('*'*70, colour='blue')
    # get all demo yamls
    # loop around and print
    for p_it, pogo_yaml in enumerate(pogos_summaries):
        # add header and number
        pogo_printout = '='*70 + '\n'
        pogo_printout += '{0}: {1}\n'.format(p_it + 1, pogo_yaml)
        # print this yaml summary
        drs_text.cprint(pogo_printout, colour='green')
    drs_text.cprint('*'*70, colour='blue')

    # --------------------------------------------------------------------------
    # ask user if they want to use one of these yamls
    question = 'Select a demo yaml to use (enter number) or blank to exit:\t'
    # loop around until we have a valid selection or blank to exit
    while True:
        uinput = input(question)
        if uinput == '':
            # return True to exit program
            return True
        try:
            uinput = int(uinput)
            if 1 <= uinput <= len(pogos_yamls):
                break
            else:
                drs_text.cprint('Invalid selection, please try again.',
                                colour='yellow')
        except ValueError:
            drs_text.cprint('Invalid input, please enter a number.',
                            colour='yellow')
    # update the sys.argv to use the selected yaml file
    sys.argv = [sys.argv[0]]
    sys.argv += ['--yamlfile', pogos_yamls[uinput - 1]]
    # return True to exit program
    return False


# =============================================================================
# Copy functionality
# =============================================================================
def copy_ask_description(params: ParamDict):
    # print process
    WLOG(params, 'info', '*'*50)
    WLOG(params, 'info',  'Setting up new description')
    WLOG(params, 'info', '*'*50)
    # ---------------------------------------------------------------------
    descriptions = dict()
    # find a previous description if it exists
    for step in definitions.RED_STEPS:
        submodule = step.name
        # skip if we don't have this sub-module
        if step.run_key not in params:
            continue
        # skip if not running
        if not step.is_enabled(params):
            continue
        # need to figure out if we are dealing with a submodule with multiple
        # parts
        if len(step.sub_prefixes) > 0:
            subkeys = step.sub_prefixes
        else:
            subkeys = [submodule]
        # need to loop around submodules (subkeys may have multiple submodules)
        for subkey in subkeys:
            # get sub-params
            subparams = params.get(subkey)
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

    prev = None

    for step in definitions.RED_STEPS:
        submodule = step.name
        # skip if we don't have this sub-module
        if step.run_key not in params:
            continue
        # skip if not running
        if not step.is_enabled(params):
            continue
        # need to figure out if we are dealing with a submodule with multiple
        # parts
        if len(step.sub_prefixes) > 0:
            subkeys = step.sub_prefixes
        else:
            subkeys = [submodule]
        # need to loop around submodules (subkeys may have multiple submodules)
        for subkey in subkeys:
            # get sub-params
            subparams = params.get(subkey)
            # define sub-directory path
            subdir, subdir_key, desc_key = None, None, None
            if 'GENERAL.SUBDIRECTORY' in subparams:
                subdir_key = 'GENERAL.SUBDIRECTORY'
            elif 'INPUTS.SUBDIRECTORY' in subparams:
                subdir_key = 'INPUTS.SUBDIRECTORY'
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
            # -----------------------------------------------------------------
            # print process
            WLOG(params, 'info', '*'*50)
            subtitle = ('Setting up new sub-directory for '
                        '{0} module').format(submodule)
            WLOG(params, 'info', subtitle)
            WLOG(params, 'info', '*'*50)
            time.sleep(0.1)
            # -----------------------------------------------------------------
            # ask question
            question = ('For the {0} module, Please enter a new value for {1}  '
                        '\n\nPrevious value = {2}'
                        ).format(submodule, subdir_key, subdir)
            if subdir_desc is not None:
                question += '\n\n' + subdir_desc
            # -----------------------------------------------------------------
            # loop and ask the question
            while True:
                if prev is None:
                    required = True
                else:
                    required = False

                value = drs_text.user_input(question, dtype=str,
                                            required=required, default=prev)
                # -------------------------------------------------------------
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
                # -------------------------------------------------------------
                # make sure there are no special characters other
                # than underscores
                char_passed = True
                for char in string.punctuation:
                    if char not in VALID_PUNC and char in value:
                        msg = ('The value cannot contain special characters '
                               'other than {0}. Please try again.')
                        margs = [', '.join(VALID_PUNC)]
                        WLOG(params, '', msg.format(*margs),
                             no_timestamp=True, colour='yellow')
                        char_passed = False
                        break
                # re-check and ask the question again
                if not char_passed:
                    continue
                # -------------------------------------------------------------
                # break the loop
                break
            # set the new value
            params.set(key=f'{submodule}.{subdir_key}', value=value,
                       source='user input')
            # update prev
            prev = str(value)

    return params


def copy_clear_files(params: ParamDict):
    # set function name
    func_name = f'{__NAME__}.copy_clear_files()'
    # storage for found sets (used later to inform user)
    found_sets = dict()
    # list of files
    for fileset in list(pogos_base.FILE_PATHS.keys()):
        # skip if we don't have this fileset
        if fileset not in params:
            continue
        # get sub-module from fileset
        submodule = fileset.split('.')[0]
        # skip if we are not running this sub-module
        if 'RUN.{0}'.format(submodule) in params:
            if not params['RUN.{0}'.format(submodule)]:
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
        found_sets[fileset] = pogos_base.FILE_PATHS[fileset]
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
    for step in definitions.RED_STEPS:
        submodule = step.name
        # skip question if we don't have this sub-module
        if step.run_key not in params:
            continue
        # skip if not running
        if not step.is_enabled(params):
            continue
        # loop around required parameters
        for req_param in step.required_params:
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

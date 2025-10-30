#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2025-02-18 at 14:13

@author: cook
"""
import os
import shutil
from typing import Optional

import sossisse
from aperocore.constants.param_functions import ParamDict
from aperocore.core import drs_log
from aperocore.core import drs_misc
from pogos.core import base
from pogos.tsovore.instruments import default
from sossisse.core import const_funcs
from sossisse.core.exceptions import SossisseFileException
from sossisse.recipes import run_sossisse as sossisse_run

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'pogos.sossisse_wrap.core.core'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__
# get the Drs Exceptions
AperoCodedException = drs_log.AperoCodedException
AperoCodedWarning = drs_log.AperoCodedWarning
# get display func
display_func = drs_misc.display_func
# Get Logging function
WLOG = drs_log.wlog


# =============================================================================
# Define functions
# =============================================================================
def run_sossisse_module(params: ParamDict,
                        tsovore_inst: default.Instrument = None):
    """
    Run the sossisse run recipe

    :param params: ParamDict, the parameter dictionary of constants

    :return: None, runs sossisse run
    """
    # if RUN.SOSSISSE is False skip
    if not params['RUN.SOSSISSE']:
        return
    # get the SOSSISSE sub-dictionary
    sossisse_params = params.get('SOSSISSE')
    # deal with SOSSISSE nested dictionary not in params
    if sossisse_params is None:
        WLOG(params, 'warning', 'SOSSISSE not in params - skipping.')
        return
    # convert to independent parameter dictionary
    sparams = sossisse_params.as_param_dict()
    # make sure yaml file is set
    sparams['INPUTS.PARAM_FILE'] = str(params['GLOBAL.YAML_FILE'])

    # ----------------------------------------------------------------------
    # Deal with input from SOSSISSE if available
    # ----------------------------------------------------------------------
    if tsovore_inst is not None:
        params = tsovore_input(params, tsovore_inst)

    # SOSSISSE requires raw data to be copied to a specific location
    # check here if that exists and if not prompt the user
    spath = os.path.join(sparams['INPUTS.SOSSIOPATH'],
                         params['GLOBAL.INSTRUMENTMODE'],
                         sparams['INPUTS.OBJECTNAME'], 'rawdata')
    # deal with SOSSISSE raw data path not existing
    if not os.path.exists(spath):
        msg = ('\n\nSOSSISSE requires raw data to be in a specific location:\n'
               '  {0}\n'
               'Please copy the raw data to this location and re-run.\n'
               'Skipping SOSSISSE run.')
        # create path if not there
        os.makedirs(spath, exist_ok=True)
        # return an error
        raise SossisseFileException(msg.format(spath))
    # -------------------------------------------------------------------------
    # run the sossisse recipe
    inst = sossisse_run.main(__YAML_DICT__=sparams)
    # get the output SOSSISSE directory
    return inst


def setup_sossisse_module(params: ParamDict, cdict):
    """
    Run the sossisse setup recipe

    :param params: ParamDict, the parameter dictionary of constants

    :return: None, runs sossisse setup
    """
    # set function name
    func_name = f'{__NAME__}.setup_sossisse_module()'
    # if RUN.SOSSISSE is False skip
    if not params['RUN.SOSSISSE']:
        return
    # get the SOSSISSE sub-dictionary
    sossisse_params = params.get('SOSSISSE')
    # deal with SOSSISSE nested dictionary not in params
    if sossisse_params is None:
        # we assume that if SOSSISSE is not there we don't want to run this
        return
    # convert to independent parameter dictionary
    sparams = sossisse_params.as_param_dict()
    # make sure yaml file is set
    sparams['INPUTS.PARAM_FILE'] = str(params['GLOBAL.YAML_FILE'])
    # setup for SOSSISSE just uses "get_parameters" function
    inst = sossisse.get_parameters(__NAME__=__NAME__, only_create=True,
                                   log_level='setup', __YAML_DICT__=sparams)
    # -------------------------------------------------------------------------
    # get the SOSSISSE PATH params out of instrument class
    spaths = inst.params.get('PATHS')
    # update the SOSSISSE paths
    for path in spaths.keys():
        # get the key in POGOS parameters
        pkey = f'SOSSISSE.PATHS.{path}'
        # if the key exists update it
        if pkey in params:
            params.set(pkey, spaths[path], source=func_name)
    # update the SID if changed
    if sparams['INPUTS.SID'] is not None:
        params.set('SOSSISSE.INPUTS.SID', sparams['INPUTS.SID'],
                   source=sparams.sources['INPUTS.SID'])
    # -------------------------------------------------------------------------
    # re-save the yaml file after sossisse updates
    # get the yaml file
    yaml_file = params['GLOBAL.YAML_FILE']
    # print progress
    msg = 'Re-saving constants to yaml file after SOSSISSE setup: {0}'
    WLOG(params, '', msg.format(os.path.realpath(yaml_file)))
    # save the constants dictionary to yaml file
    cdict.save_yaml(params, outpath=yaml_file, log=False)
    # -------------------------------------------------------------------------
    # return the parameters
    return params


def tsovore_input(params: ParamDict,
                  tsovore_inst: Optional[default.Instrument] = None):
    # set function name
    func_name = f'{__NAME__}.tsovore_input'
    # -------------------------------------------------------------------------
    # get the SOSSISSE sub-dictionary
    sossisse_params = params.get('SOSSISSE')
    # deal with SOSSISSE nested dictionary not in params
    if sossisse_params is None:
        # we assume that if SOSSISSE is not there we don't want to run this
        return
    # convert to independent parameter dictionary
    sparams = sossisse_params.as_param_dict()
    # -------------------------------------------------------------------------
    # get tsovore files to copy
    tsovore_outputs = tsovore_inst.variables['LAST']
    # ---------------------------------------------------------------------
    # prepare input directory
    sparams = const_funcs.run_time_params(sparams, only_create=True)
    # Get the SOSSISSE input directory
    sossisse_input_dir = sparams['PATHS.RAWPATH']
    # ---------------------------------------------------------------------
    # copy files to SOSSISSE input location
    for tsovore_output in tsovore_outputs:
        # get the filename
        filename = os.path.basename(tsovore_output)
        # define source and destination
        source = str(os.path.join(tsovore_outputs, filename))
        dest = str(os.path.join(sossisse_input_dir, filename))
        # log the copy
        msg = f'Copying TSOVORE output file to SOSSISSE input: {filename}'
        WLOG(params, '', msg)
        # copy file
        shutil.copy(source, dest)

    # return params
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

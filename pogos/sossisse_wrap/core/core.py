#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2025-02-18 at 14:13

@author: cook
"""
import os

from aperocore.constants.param_functions import ParamDict
from aperocore.core import drs_misc
from aperocore.core import drs_log
from sossisse.recipes import run_sossisse as sossisse_run
from sossisse.core.exceptions import SossisseFileException
import sossisse

from pogos.core import base
from pogos.core import io as pogo_io


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
def run_sossisse_module(params: ParamDict):
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
    _ = sossisse_run.main(__YAML_DICT__=sparams)
    # -------------------------------------------------------------------------
    # after sossisse run we may need to copy files to SORBET input location
    if params['RUN.SORBET']:
        # get sorbet parameters
        sb_params = params.get('SORBET')
        # get the output SOSSISSE directory
        sossisse_output_dir = params['SOSSISSE.PATHS.OUT_PATH']

        # deal with sossisse output directory not existing
        if not os.path.exists(sossisse_output_dir):
            msg = ('\n\nSOSSISSE output directory does not exist:\n'
                   '  {0}\n'
                   'Cannot copy files to SORBET input locations.\n'
                   'Skipping SORBET file copy - SORBET may fail!')
            WLOG(params, 'warning', msg.format(sossisse_output_dir))
            return

        # deal with WLCTA files
        if sb_params['WLCTA.RUN']:
            # get the sorbet input directory for WLCTA
            sorbet_wlcta_input_dir = sb_params['WLCTA.INPUT_PATH']
            # copy all files from SOSSISSE output to SORBET WLCTA input
            pogo_io.copy_file_directory(params, sossisse_output_dir,
                                        sorbet_wlcta_input_dir)
        # deal with SLCTA files
        if sb_params['SLCTA.RUN']:
            # get the sorbet input directory for SLCTA
            sorbet_slcta_input_dir = sb_params['SLCTA.INPUT_PATH']
            # copy all files from SOSSISSE output to SORBET SLCTA input
            pogo_io.copy_file_directory(params, sossisse_output_dir,
                                        sorbet_slcta_input_dir)





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

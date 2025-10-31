#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2025-10-16 at 14:10

@author: cook
"""
import os
import shutil
import time
from typing import Optional

import numpy as np

from aperocore.constants.param_functions import ParamDict
from aperocore.core import drs_log
from pogos.core import base
from pogos.core import general as pogos_general
from pogos.core import io as pogos_io
from pogos.miriam.core import general as mc_general
from pogos.miriam.general import plots as mc_plots
from pogos.miriam.general import science as mc_science
from pogos.miriam.general import io as mc_io
from pogos.tsovore.instruments import default as ts_default
from sossisse.core import misc

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'pogos.miriam.general.general'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__
# Get Logging function
WLOG = drs_log.wlog


# =============================================================================
# Define functions
# =============================================================================
def run_miriam(params: ParamDict, tsovore_inst: Optional = None) -> ParamDict:
    """
    Run the MIRIAM processing

    :param params: ParamDict, the parameter dictionary of constants

    :return:
    """
    # set the function name
    func_name = f'{__NAME__}.run_miriam'
    # print the white light curve splash
    print(misc.art('MIRIAM', 'yellow', 'CYAN'))
    time.sleep(0.1)
    # prepare the directories
    prepare_directories(params)

    # ----------------------------------------------------------------------
    # Deal with input from TSOVORE if available
    # ----------------------------------------------------------------------
    if tsovore_inst is not None:
        params = tsovore_input(params, tsovore_inst)
    # ----------------------------------------------------------------------

    # get miriam specific parameters
    mparams = params.get('MIRIAM')
    # -------------------------------------------------------------------------
    # Step 1: merge all input files into a single (cropped) data structure
    # -------------------------------------------------------------------------
    mi_out = mc_science.merge_inputs(params)
    cube, cube_err, mtbl, weights, xstart, ystart = mi_out

    # -------------------------------------------------------------------------
    # Step 2: perform systematics correction on the data
    # -------------------------------------------------------------------------
    cube2, mtbl = mc_science.remove_background_cube(params, cube, mtbl)
    # -------------------------------------------------------------------------
    # Step 3: Calculate errors in the cube
    # -------------------------------------------------------------------------
    # TODO decide if we want to compute errors or keep errors from
    #     the original cube files
    cube2, cube2_err = mc_science.calculate_cube_errors(params, cube2)
    if mparams['INPUTS.USE_ORIGINAL_ERRORS']:
        cube2_err = np.array(cube_err)

    # -------------------------------------------------------------------------
    # Step 4: Change the cube to photometry
    # -------------------------------------------------------------------------
    ptbl0 = mc_science.cube2phot(params, cube2, cube2_err, mtbl, weights,
                                 xstart, ystart, d2flag=True)
    ptbl1 = mc_science.cube2phot(params, cube2, cube2_err, mtbl, weights,
                                 xstart, ystart, d2flag=False)
    # -------------------------------------------------------------------------
    # Step 5: plot results
    # -------------------------------------------------------------------------
    mc_plots.plot_correlations(params, ptbl0, d2flag=True)
    mc_plots.plot_correlations(params, ptbl1, d2flag=False)
    mc_plots.plot_photometry(params, ptbl0, ptbl1)

    # -------------------------------------------------------------------------
    # Step 6: save results
    # -------------------------------------------------------------------------
    oparams = mc_io.write_photometry_results(params, ptbl0, ptbl1)
    # -------------------------------------------------------------------------
    # produce summary html
    stitle = params.get('MIRIAM.GENERAL.DESCRIPTION', '')
    pogos_io.summary_html(params, 'MIRIAM', 'MIRIAM.PATHS.PLOT_PATH',
                          'MIRIAM.GENERAL.SID', 'MIRIAM.PATHS.OUTPUT_PATH',
                          stitle)
    # return output params
    return oparams


def setup_miriam_module(params: ParamDict) -> ParamDict:
    """
    Setup the MIRIAM module within POGOS.

    :param params: ParamDict, the parameter dictionary of constants

    :return: ParamDict, the updated parameter dictionary of constants
    """
    # set the function name
    func_name = f'{__NAME__}.setup_miriam_module'
    # deal with no requiring to run miriam
    if not params['RUN.MIRIAM']:
        return params
    # setup input and output directories
    prepare_directories(params)
    # return params
    return params


def prepare_directories(params: ParamDict):

    sid_path = 'MIRIAM.GENERAL.SID'
    sid_null = mc_general.miriam_unique_id()
    mode = 'miriam'
    # -------------------------------------------------------------------------
    # set parameters for preparing directory
    pkind = 'input'
    file_path = f'MIRIAM.PATHS.INPUT_PATH'
    # run the prepare directory function
    pogos_general.prepare_directory(params, pkind, sid_path, sid_null,
                                    file_path, mode)
    # -------------------------------------------------------------------------
    pkind = 'temp'
    file_path = f'MIRIAM.PATHS.TEMP_PATH'
    # run the prepare directory function
    pogos_general.prepare_directory(params, pkind, sid_path, sid_null,
                                    file_path, mode)
    # -------------------------------------------------------------------------
    pkind = 'plot'
    file_path = f'MIRIAM.PATHS.PLOT_PATH'
    # runt the prepare directory function
    pogos_general.prepare_directory(params, pkind, sid_path, sid_null,
                                    file_path, mode)
    # -------------------------------------------------------------------------
    # set parameters for preparing directory
    pkind = 'output'
    file_path = f'MIRIAM.PATHS.OUTPUT_PATH'
    # runt the prepare directory function
    pogos_general.prepare_directory(params, pkind, sid_path, sid_null,
                                    file_path, mode)


def tsovore_input(params: ParamDict,
                  tsovore_inst: Optional[ts_default.Instrument] = None):
    # set function name
    func_name = f'{__NAME__}.tsovore_input'
    # -------------------------------------------------------------------------
    # get the MIRIAM sub-dictionary
    miriam_params = params.get('MIRIAM')
    # deal with MIRIAM nested dictionary not in params
    if miriam_params is None:
        # we assume that if MIRIAM is not there we don't want to run this
        return
    # convert to independent parameter dictionary
    miriam_params = miriam_params.as_param_dict()
    # -------------------------------------------------------------------------
    # get tsovore files to copy
    tsovore_outputs = tsovore_inst.variables['OUT']
    # ---------------------------------------------------------------------
    # Get the MIRIAM input directory
    miriam_input_dir = miriam_params['PATHS.INPUT_PATH']
    # ---------------------------------------------------------------------
    basenames = []
    # copy files to MIRIAM input location
    for tsovore_output in tsovore_outputs:
        # get the filename
        basename = os.path.basename(tsovore_output)
        # define source and destination
        dest = str(os.path.join(miriam_input_dir, basename))
        # log the copy
        msg = f'Copying TSOVORE output file to MIRIAM input: {basename}'
        WLOG(params, '', msg)
        # copy file
        shutil.copy(tsovore_output, dest)
        # store basename
        basenames.append(basename)
    # update MIRIAM inputs
    params['MIRIAM.INPUTS.FILES'] = basenames
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

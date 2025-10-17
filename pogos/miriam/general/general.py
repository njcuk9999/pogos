#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2025-10-16 at 14:10

@author: cook
"""
from aperocore.constants.param_functions import ParamDict
from aperocore.core import drs_log
from aperocore.core import drs_misc
from pogos.core import base
from pogos.core import general as pogos_general
from pogos.miriam.core import base as miriam_base
from sossisse.core import misc
from pogos.miriam.core import general as mc_general
from pogos.miriam.general import science as mc_science
from pogos.miriam.general import plots as mc_plots

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'pogos.miriam.general.general'
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
def run_miriam(params: ParamDict):
    # set the function name
    func_name = f'{__NAME__}.run_sorbet_wlcta'
    # print the white light curve splash
    print(misc.art('MIRIAM', 'yellow', 'CYAN'))
    # prepare the input directory
    prepare_input_directory(params)
    # prepare the output directory
    prepare_output_directory(params)

    # -------------------------------------------------------------------------
    # Step 1: merge all input files into a single (cropped) data structure
    # -------------------------------------------------------------------------
    cube, cube_err, mtbl, weights = mc_science.merge_inputs(params)

    # -------------------------------------------------------------------------
    # Step 2: perform systematics correction on the data
    # -------------------------------------------------------------------------
    cube2, cube2_err = mc_science.correct_systematics(params, cube, cube_err)

    # -------------------------------------------------------------------------
    # Step 3: Change the cube to photometry
    # -------------------------------------------------------------------------
    ptbl0 = mc_science.cube2phot(params, cube2, cube2_err, mtbl, weights,
                                d2flag=True)
    ptbl1 = mc_science.cube2phot(params, cube2, cube2_err, mtbl, weights,
                                d2flag=False)

    # -------------------------------------------------------------------------
    # Step 4: plot results
    # -------------------------------------------------------------------------
    mc_plots.plot_correlations(params, ptbl0, d2flag=True)
    mc_plots.plot_correlations(params, ptbl1, d2flag=False)
    mc_plots.plot_photometry(params, ptbl0, ptbl1)

    # -------------------------------------------------------------------------
    # Step 5: save results
    # -------------------------------------------------------------------------
    mc_science.write_photometry_results(params, ptbl0, ptbl1)


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
    prepare_input_directory(params)
    prepare_output_directory(params)
    # return params
    return params


def prepare_input_directory(params: ParamDict):
    # set parameters for preparing directory
    pkind = 'input'
    sid_path = 'MIRIAM.GENERAL.SID'
    sid_null = mc_general.miriam_unique_id()
    file_path = f'MIRIAM.PATHS.INPUT_PATH'
    mode = 'miriam'
    # runt the prepare directory function
    pogos_general.prepare_directory(params, pkind, sid_path, sid_null,
                                    file_path, mode,
                                    miriam_base.MiriamException)


def prepare_output_directory(params: ParamDict):
    """
    Prepare the output directory for SORBET results.

    :param params: ParamDict, the parameter dictionary of constants
    """
    # set parameters for preparing directory
    pkind = 'output'
    sid_path = 'MIRIAM.PATHS.SID'
    sid_null = mc_general.miriam_unique_id()
    file_path = f'MIRIAM.INPUTS.OUTPUT_PATH'
    mode = 'miriam'
    # runt the prepare directory function
    pogos_general.prepare_directory(params, pkind, sid_path, sid_null,
                                    file_path, mode,
                                    miriam_base.MiriamException)


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

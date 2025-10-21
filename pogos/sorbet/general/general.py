#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2025-10-16 at 13:39

@author: cook
"""
import shutil
import string
import os
from typing import Optional

import numpy as np

from aperocore.constants.param_functions import ParamDict
from aperocore.core import drs_log
from aperocore.core import drs_misc
from pogos.core import base
from pogos.core import general as pogos_general
from pogos.core import io as pogos_io
from pogos.sorbet.core import base as sorbet_base
from pogos.sorbet.core import core as sorbet_core
from pogos.sorbet.general import science as sorbet_science
from pogos.sorbet.general import plots as sorbet_plots
from sossisse.core import misc
from sossisse.instruments import default

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'pogos.sorbet.core.core'
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
# Define the SORBET run constants
RUN_CONSTANTS = ['SORBET.WLCTA.RUN', 'SORBET.SLCTA.RUN']  # , 'SORBET.TFIT.RUN', 'SORBET.RV.RUN']
# get all chars
CHARS = string.ascii_uppercase + string.digits


# =============================================================================
# Define functions
# =============================================================================
def setup_sorbet_module(params: ParamDict):
    """
    Setup the SORBET module

    :param params: ParamDict, the parameter dictionary of constants

    :return: Updated params, sets up sorbet module
    """
    # deal with no requiring to run sorbet
    if not params['RUN.SORBET']:
        return params
    # ----------------------------------------------------------------------
    # setup the wlcta  input and output directories
    if params['SORBET.WLCTA.RUN']:
        # prepare input directory
        prepare_input_directory(params, method='WLCTA')
        # prepare output directory
        prepare_output_directory(params, method='WLCTA')
    # ----------------------------------------------------------------------
    # setup the slcta  input and output directories
    if params['SORBET.SLCTA.RUN']:
        # prepare input directory
        prepare_input_directory(params, method='SLCTA')
        # prepare output directory
        prepare_output_directory(params, method='SLCTA')

    return params


def run_sorbet_module(params: ParamDict,
                      sossisse_inst: Optional[default.Instrument] = None):
    """
    Run the sorbet recipes

    :param params: ParamDict, the parameter dictionary of constants

    :return: Updated params, runs sorbet recipes
    """
    # Check at least one recipe is set to run
    run_any = False
    for key in RUN_CONSTANTS:
        if params[key]:
            run_any = True
            break
    # if not running any then skip SORBET
    if not run_any:
        WLOG(params, 'warning', 'No SORBET recipes set to run - skipping.')
        return params

    # ----------------------------------------------------------------------
    # Deal with input from SOSSISSE if available
    # ----------------------------------------------------------------------
    if sossisse_inst is not None:
        params = sossisse_input(params, sossisse_inst)

    # ----------------------------------------------------------------------
    # White Light Curve Transit Analysis
    # ----------------------------------------------------------------------
    if params['SORBET.WLCTA.RUN']:
        params = run_sorbet_wlcta(params)

    # ----------------------------------------------------------------------
    # Spectral Light Curve Transit Analysis
    # ----------------------------------------------------------------------
    if params['SORBET.SLCTA.RUN']:
        params = run_sorbet_slcta(params)

    # ----------------------------------------------------------------------
    # TFIT
    # ----------------------------------------------------------------------
    # if params['SORBET.TFIT.RUN']:
    #    params = run_sorbet_tfit(params)

    # ----------------------------------------------------------------------
    # RV Module
    # ----------------------------------------------------------------------
    # if params['SORBET.RV.RUN']:
    #    params = run_sorbet_rv(params)

    return params


def sossisse_input(params: ParamDict,
                   sossisse_inst: Optional[default.Instrument] = None):
    # set function name
    func_name = f'{__NAME__}.sossisse_input'
    # -------------------------------------------------------------------------
    # after sossisse run we may need to copy files to SORBET input location
    sossisse_output_dir = sossisse_inst.params['PATHS.OUT_PATH']
    # get sorbet parameters
    sb_params = params.get('SORBET')
    # get sossisse
    # get sossisse files to copy
    sossisse_wlc_file = sossisse_inst.get_variable('OUT_WLC_FILE',
                                                   func_name)
    sossisse_spec_lc_file = sossisse_inst.get_variable('OUT_SPEC_LC_FILE',
                                                       func_name)
    # ---------------------------------------------------------------------
    # deal with WLCTA files
    if sb_params['WLCTA.RUN']:
        # prepare input directory
        prepare_input_directory(params, method='WLCTA',
                                           verbose=False)
        # get the sorbet input directory for WLCTA
        sorbet_wlcta_input_dir = sb_params['WLCTA.INPUT_PATH']
        # get absolute path to
        sorbet_file = str(os.path.join(sorbet_wlcta_input_dir,
                                       os.path.basename(sossisse_wlc_file)))
        # copy linear recon coeffs csv file
        shutil.copy(sossisse_wlc_file, sorbet_file)
        # update params
        params['SORBET.WLCTA.INPUT_FILE'] = os.path.basename(sorbet_file)
    # ---------------------------------------------------------------------
    # deal with SLCTA files
    if sb_params['SLCTA.RUN']:
        # prepare input directory
        prepare_input_directory(params, method='SLCTA',
                                           verbose=False)
        # get the sorbet input directory for SLCTA
        sorbet_slcta_input_dir = sb_params['SLCTA.INPUT_PATH']
        # get absolute path to
        sorbet_file = str(os.path.join(sorbet_slcta_input_dir,
                                       os.path.basename(sossisse_spec_lc_file)))
        # copy linear recon coeffs csv file
        shutil.copy(sossisse_spec_lc_file, sorbet_file)
        # update params
        params['SORBET.SLCTA.INPUT_FILE'] = os.path.basename(sorbet_file)
    # return params
    return params


def run_sorbet_wlcta(params: ParamDict):
    """
    Run the SORBET White Light Curve Transit Analysis recipe

    :param params: ParamDict, the parameter dictionary of constants

    :return: Updated params, runs sorbet recipes
    """
    # set the function name
    func_name = f'{__NAME__}.run_sorbet_wlcta'
    # print the white light curve splash
    print(misc.art('SORBET WLC Transit Analysis', 'yellow', 'CYAN'))
    # --------------------------------------------------------------------------
    # prepare input directory
    prepare_input_directory(params, method='WLCTA')
    # -------------------------------------------------------------------------
    # prepare output directory
    prepare_output_directory(params, method='WLCTA')
    # load the dataset
    dataset = sorbet_science.load_wlc(params)
    # find outliers
    medfilt_model, outlier_mask = sorbet_science.find_outliers(params,
                                                               dataset,
                                                               method='WLCTA')
    # diagnostic plot for outlier removal
    sorbet_plots.plot_outlier(params, dataset, medfilt_model, outlier_mask,
                              method='WLCTA')
    # -------------------------------------------------------------------------
    # prepare the dataset for juliet
    dataset = sorbet_science.prepare_dataset(params, dataset, method='WLCTA',
                                      outlier_mask=outlier_mask)
    # -------------------------------------------------------------------------
    # fit the dataset with juliet/batman
    results = sorbet_science.fit_transit(params, dataset, method='WLCTA')
    # -------------------------------------------------------------------------
    # save the model components to disk
    sorbet_science.save_transit_model(params, results, method='WLCTA')
    # -------------------------------------------------------------------------
    # plot the results (corner plot)
    sorbet_plots.plot_corner(params, dataset, results, method='WLCTA')
    # -------------------------------------------------------------------------
    # plot the best-fit model
    sorbet_plots.plot_transit(params, dataset, results, method='WLCTA')
    # -------------------------------------------------------------------------
    # produce summary html
    stitle = params.get('SORBET.GENERAL.DESCRIPTION', '')
    pogos_io.summary_html(params, 'SORBET:WLCTA', 'SORBET.WLCTA.PLOT_PATH',
                          'SORBET.GENERAL.SID', 'SORBET.WLCTA.OUTPUT_PATH',
                          stitle)
    # return params
    return params


def run_sorbet_slcta(params: ParamDict):
    """
    Run the SORBET Spectral Light Curves Transit Analysis recipe

    :param params: ParamDict, the parameter dictionary of constants

    :return: Updated params, runs sorbet recipes
    """
    # set the function name
    func_name = f'{__NAME__}.run_sorbet_slcta'
    # print the spectral light curve splash
    print(misc.art('SORBET SLC Transit Analysis', 'blue', 'CYAN'))
    # get the sorbet parameters
    slcta_params = params.get('SORBET.SLCTA')
    # --------------------------------------------------------------------------
    # prepare input directory
    prepare_input_directory(params, method='SLCTA')
    # --------------------------------------------------------------------------
    # prepare output directory
    prepare_output_directory(params, method='SLCTA')
    # check the dataset (multiple channels/orders?)
    input_file = slcta_params['INPUT_FILE']
    if isinstance(input_file, str):
        raise ValueError("Input file of SORBET.SLCTA must be a list.")
    else:
        len_channel = len(input_file)
    for chl in range(len_channel):
        # select dataset
        slcta_params['INPUT_FILE'] = input_file[chl]
        # load the dataset
        bjd, wave_tuple, flux_bin, eflux_bin, channel = sorbet_science.load_slc(params)
        # TODO
        # eflux_bin = np.ones_like(flux_bin) * 10e-6
        # initiate transmission spectrum table
        spec_tbl, nbin = sorbet_science.initiate_transmission_spectrum(wave_tuple)
        # set the instrumental channel
        slcta_params['CHANNEL'] = channel
        # looping through spectral bins
        for wb in range(nbin):
            # print the wavelength bin
            msg = f'Spectral bin {wb + 1}/{nbin}'
            # print the message
            misc.printc(msg, msg_type='info')
            # set the wavelength bin number
            slcta_params['BINNUMBER'] = wb
            # set the wavelength bin limits
            slcta_params['WAVE_BIN_LOW'] = wave_tuple[1][0, wb]
            slcta_params['WAVE_BIN_HIGH'] = wave_tuple[2][0, wb]
            # ----------------------------------------------------------------------
            # prepare the dataset
            dataset = sorbet_science.create_dataset_table(bjd, flux_bin[:, wb],
                                                   eflux_bin[:, wb])
            # TODO some bins are nan everywhere
            if np.isnan(dataset['amplitude']).all():
                msg = f'Wavelength bin {wb + 1}/{nbin} is empty, skipping...'
                misc.printc(msg, msg_type='warning')
                continue
            # find outliers
            medfilt_model, outlier_mask = sorbet_science.find_outliers(params,
                                                                dataset,
                                                                method='SLCTA')
            # diagnostic plot for outlier removal
            sorbet_plots.plot_outlier(params, dataset, medfilt_model, outlier_mask,
                               method='SLCTA', )
            # prepare the dataset for juliet
            dataset = sorbet_science.prepare_dataset(params, dataset, method='SLCTA',
                                              outlier_mask=outlier_mask)
            # -----------------------------------------------------------------
            # fit the dataset with juliet/batman
            results = sorbet_science.fit_transit(params, dataset, method='SLCTA')
            # -----------------------------------------------------------------
            # save the model components to disk
            sorbet_science.save_transit_model(params, results, method='SLCTA')
            # -----------------------------------------------------------------
            # plot the results (corner plot)
            sorbet_plots.plot_corner(params, dataset, results, method='SLCTA')
            # -----------------------------------------------------------------
            # plot the best-fit model
            sorbet_plots.plot_transit(params, dataset, results, method='SLCTA')
            # -----------------------------------------------------------------
            # append to transmission spectrum table
            spec_tbl = sorbet_science.append_transmission_spectrum(params, results,
                                                            spec_tbl, wb)

        # save the transmission spectrum table
        sorbet_science.save_transmission_spectrum(params, spec_tbl)
        # plot the transmission spectrum
        sorbet_plots.plot_transmission_spectrum(params, method='SLCTA')
    # -------------------------------------------------------------------------
    # produce summary html
    stitle = params.get('SORBET.GENERAL.DESCRIPTION', '')
    pogos_io.summary_html(params, 'SORBET:SLCTA', 'SORBET.SLCTA.PLOT_PATH',
                          'SORBET.GENERAL.SID', 'SORBET.SLCTA.OUTPUT_PATH',
                          stitle)

    # return params
    return params


def prepare_input_directory(params: ParamDict, method: str,
                            verbose: bool = True):
    # set parameters for preparing directory
    pkind = 'input'
    sid_path = 'SORBET.GENERAL.SID'
    sid_null = sorbet_core.sorbet_unique_id()
    file_path = f'SORBET.{method}.INPUT_PATH'
    mode = 'sorbet'
    # runt the prepare directory function
    pogos_general.prepare_directory(params, pkind, sid_path, sid_null,
                                    file_path, mode, verbose=verbose)


def prepare_output_directory(params: ParamDict, method: str,
                             verbose: bool = True):
    """
    Prepare the output directory for SORBET results.

    :param params: ParamDict, the parameter dictionary of constants
    """
    # set parameters for preparing directory
    pkind = 'output'
    sid_path = 'SORBET.GENERAL.SID'
    sid_null = sorbet_core.sorbet_unique_id()
    file_path = f'SORBET.{method}.OUTPUT_PATH'
    mode = 'sorbet'
    # runt the prepare directory function
    pogos_general.prepare_directory(params, pkind, sid_path, sid_null,
                                    file_path, mode, verbose)


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

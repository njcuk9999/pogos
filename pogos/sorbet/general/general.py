#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2025-10-16 at 13:39

@author: cook
"""
import string

import numpy as np

from aperocore.constants.param_functions import ParamDict
from aperocore.core import drs_log
from aperocore.core import drs_misc
from pogos.core import base
from pogos.sorbet.general import science
from pogos.sorbet.general import plots
from sossisse.core import misc

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
def run_sorbet_module(params: ParamDict):
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
    # -------------------------------------------------------------------------
    # prepare output directory
    science.prepare_output_directory(params, method='WLCTA')
    # load the dataset
    dataset = science.load_wlc(params)
    # find outliers
    medfilt_model, outlier_mask = science.find_outliers(params,
                                                        dataset,
                                                        method='WLCTA')
    # diagnostic plot for outlier removal
    plots.plot_outlier(params, dataset, medfilt_model, outlier_mask,
                       method='WLCTA')
    # -------------------------------------------------------------------------
    # prepare the dataset for juliet
    dataset = science.prepare_dataset(params, dataset, method='WLCTA',
                                      outlier_mask=outlier_mask)
    # -------------------------------------------------------------------------
    # fit the dataset with juliet/batman
    results = science.fit_transit(params, dataset, method='WLCTA')
    # -------------------------------------------------------------------------
    # save the model components to disk
    science.save_transit_model(params, results, method='WLCTA')
    # -------------------------------------------------------------------------
    # plot the results (corner plot)
    plots.plot_corner(params, dataset, results, method='WLCTA')
    # -------------------------------------------------------------------------
    # plot the best-fit model
    plots.plot_transit(params, dataset, results, method='WLCTA')

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
    # prepare output directory
    science.prepare_output_directory(params, method='SLCTA')
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
        bjd, wave_tuple, flux_bin, eflux_bin, channel = science.load_slc(params)
        # TODO
        # eflux_bin = np.ones_like(flux_bin) * 10e-6
        # initiate transmission spectrum table
        spec_tbl, nbin = science.initiate_transmission_spectrum(wave_tuple)
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
            dataset = science.create_dataset_table(bjd, flux_bin[:, wb],
                                                   eflux_bin[:, wb])
            # TODO some bins are nan everywhere
            if np.isnan(dataset['amplitude']).all():
                msg = f'Wavelength bin {wb + 1}/{nbin} is empty, skipping...'
                misc.printc(msg, msg_type='warning')
                continue
            # find outliers
            medfilt_model, outlier_mask = science.find_outliers(params,
                                                                dataset,
                                                                method='SLCTA')
            # diagnostic plot for outlier removal
            plots.plot_outlier(params, dataset, medfilt_model, outlier_mask,
                               method='SLCTA', )
            # prepare the dataset for juliet
            dataset = science.prepare_dataset(params, dataset, method='SLCTA',
                                              outlier_mask=outlier_mask)
            # -----------------------------------------------------------------
            # fit the dataset with juliet/batman
            results = science.fit_transit(params, dataset, method='SLCTA')
            # -----------------------------------------------------------------
            # save the model components to disk
            science.save_transit_model(params, results, method='SLCTA')
            # -----------------------------------------------------------------
            # plot the results (corner plot)
            plots.plot_corner(params, dataset, results, method='SLCTA')
            # -----------------------------------------------------------------
            # plot the best-fit model
            plots.plot_transit(params, dataset, results, method='SLCTA')
            # -----------------------------------------------------------------
            # append to transmission spectrum table
            spec_tbl = science.append_transmission_spectrum(params, results,
                                                            spec_tbl, wb)

        # save the transmission spectrum table
        science.save_transmission_spectrum(params, spec_tbl)
        # plot the transmission spectrum
        plots.plot_transmission_spectrum(params)

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

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

Transit fit of the SLC

Created on 2024-12-02

@author: CharlesCadieux
"""
import numpy as np
from astropy.table import Table

from aperocore.constants.param_functions import ParamDict
from sossisse.core import misc
from sossisse.core import io
from pogos import sorbet
from pogos.core import base
from pogos.sorbet.general import plots

import juliet

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'pogos.sorbet.recipes.run_sorbet_slcta'
__version__ = base.__version__
__date__ = base.__date__
__authors__ = base.__authors__


# =============================================================================
# Define functions
# =============================================================================
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
    sorbet.prepare_output_directory(params, method='SLCTA')
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
        bjd, wave_tuple, flux_bin, eflux_bin, channel = sorbet.load_slc(params)
        # TODO
        #eflux_bin = np.ones_like(flux_bin) * 10e-6
        # initiate transmission spectrum table
        spec_tbl, nbin = initiate_transmission_spectrum(wave_tuple)
        # set the instrumental channel
        slcta_params['CHANNEL'] = channel
        # looping through spectral bins
        for wb in range(nbin):
            # print the wavelength bin
            msg = f'Spectral bin {wb+1}/{nbin}'
            # print the message
            misc.printc(msg, msg_type='info')
            # set the wavelength bin number
            slcta_params['BINNUMBER'] = wb
            # set the wavelength bin limits
            slcta_params['WAVE_BIN_LOW'] = wave_tuple[1][0, wb]
            slcta_params['WAVE_BIN_HIGH'] = wave_tuple[2][0, wb]
            # ----------------------------------------------------------------------
            # prepare the dataset
            dataset = create_dataset_table(bjd, flux_bin[:, wb], eflux_bin[:, wb])
            # TODO some bins are nan everywhere
            if np.isnan(dataset['amplitude']).all():
                msg = f'Wavelength bin {wb+1}/{nbin} is empty, skipping...'
                misc.printc(msg, msg_type='warning')
                continue
            # find outliers
            medfilt_model, outlier_mask = sorbet.find_outliers(params,
                                                               dataset,
                                                               method='SLCTA')
            # diagnostic plot for outlier removal
            plots.plot_outlier(params, dataset, medfilt_model, outlier_mask,
                               method='SLCTA', )
            # prepare the dataset for juliet
            dataset = sorbet.prepare_dataset(params, dataset, method='SLCTA',
                                             outlier_mask=outlier_mask)
            # -----------------------------------------------------------------
            # fit the dataset with juliet/batman
            results = sorbet.fit_transit(params, dataset, method='SLCTA')
            # -----------------------------------------------------------------
            # save the model components to disk
            sorbet.save_transit_model(params, results, method='SLCTA')
            # -----------------------------------------------------------------
            # plot the results (corner plot)
            plots.plot_corner(params, dataset, results, method='SLCTA')
            # -----------------------------------------------------------------
            # plot the best-fit model
            plots.plot_transit(params, dataset, results, method='SLCTA')
            # -----------------------------------------------------------------
            # append to transmission spectrum table
            spec_tbl = append_transmission_spectrum(params, results, spec_tbl, wb)
        
        # save the transmission spectrum table
        sorbet.save_transmission_spectrum(params, spec_tbl)
        # plot the transmission spectrum
        plots.plot_transmission_spectrum(params)
    
    # return params
    return params


def create_dataset_table(bjd, flux, eflux):
    """
    Create and prepare the dataset table.

    :param bjd: Array of time values (BJD)
    :param flux: 2D array of flux values
    :param eflux: 2D array of flux error values

    :return: Prepared dataset table
    """
    # create the dataset table
    dataset = Table()
    dataset['bjd'] = bjd
    dataset['amplitude'] = flux
    dataset['amplitude_error'] = eflux

    return dataset


def initiate_transmission_spectrum(wave_tuple):
    """
    Create the transmission spectrum table.

    :param wave_tuple: Tuple containing wavelength bin, lower and upper limits

    :return: Transmission spectrum table, number of wavelength bins
    """
    # unpack the wave tuple
    wave_bin, wave_low, wave_high = wave_tuple
    # number of wavelength bins
    nbin = wave_bin.shape[1]
    # create the transmission spectrum table
    spec_tbl = Table()
    spec_tbl['wave'] = wave_bin[0, :]
    wave_bin_size = (wave_high[0, :] - wave_low[0, :]) / 2
    spec_tbl['wave_err'] = wave_bin_size
    spec_tbl['transit_depth'] = np.zeros(nbin)
    spec_tbl['transit_depth_err'] = np.zeros(nbin)
    
    return spec_tbl, nbin


def append_transmission_spectrum(params: ParamDict, results: juliet.fit,
                                 spec_tbl: Table, wb: int):
    """
    Append the transit depth to the transmission spectrum table.
    :param params: ParamDict, the parameter dictionary of constants
    :param results: juliet.results, the juliet results
    :param spec_tbl: astropy.table.Table, the transmission spectrum table
    :param wb: int, the wavelength bin number
    :return: spec_tbl: astropy.table.Table, the updated transmission spectrum table
    """
    # append transit depth to the transmission spectrum table
    p = results.posteriors['posterior_samples']['p_p1']
    delta = np.median(p**2)
    delta_ci = np.percentile(p**2, [16, 84])
    delta_err = (delta_ci[1] - delta_ci[0]) / 2
    spec_tbl['transit_depth'][wb] = delta
    spec_tbl['transit_depth_err'][wb] = delta_err

    return spec_tbl
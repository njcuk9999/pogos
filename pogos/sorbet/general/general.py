#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# sorbet.general.general.py
# General functions for SORBET

Created on 2025-02-19 at 13:43

@author: CharlesCadieux
"""

import os
import pickle as pkl
import warnings
from typing import Literal

import numpy as np
import astropy.table
from scipy.signal import medfilt

from aperocore.core import drs_log
from aperocore.constants.param_functions import ParamDict
from aperocore import math as mp
from sossisse.core import io

from pogos.core import base
from pogos.sorbet.core.io import convert_to_number
from pogos.sorbet.core import base as sorbet_base
from pogos.sorbet.core import core

import juliet
from exotic_ld import StellarLimbDarkening


# =============================================================================
# Define variables
__NAME__ = 'pogos.sorbet.general.general'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__
# set description
__description__ = 'General functions for SORBET'
__inputs__ = ['GLOBAL.YAML_FILE']
# get the logger
WLOG = drs_log.wlog


# =============================================================================
# Define functions
# =============================================================================
def prepare_output_directory(params: ParamDict,
                             method: Literal['WLCTA', 'SLCTA']):
    """
    Prepare the output directory for SORBET results.

    :param params: ParamDict, the parameter dictionary of constants
    """
    # generate SID if not given
    if params['SORBET.GENERAL.SID'] is None:
        params['SORBET.GENERAL.SID'] = core.sorbet_unique_id()
    # get the output path from the params
    output_path = params[f'SORBET.{method}.OUTPUT_PATH']
    # make sure we have the full path
    output_path = os.path.realpath(output_path)
    # deal with output path being an absolute path
    if os.path.exists(output_path):
        # print message on where outputs will be saved
        msg = f'All outputs will be saved under: {output_path}'
        WLOG(params, 'info', msg)
        return
    # if not, make it relative to the global database
    output_path = os.path.join(params['GLOBAL.DATA_PATH'], 'sorbet',
                               params['SORBET.GENERAL.SID'],
                               params[f'SORBET.{method}.OUTPUT_PATH'])
    # make sure the path is in the params
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    # update output path
    params[f'SORBET.{method}.OUTPUT_PATH'] = output_path
    # print message on where outputs will be saved
    msg = f'All outputs will be saved under: {output_path}'
    WLOG(params, 'info', msg)

def load_wlc(params: ParamDict):
    """
    Load the WLC dataset using configs from the yaml file

    :param params: ParamDict, the parameter dictionary of constants

    :return: dataset table, astropy.table
    """
    # get function name
    func_name = __NAME__ + '.load_wlc()'
    # check that this function is only being used for SORBET.WLCTA
    if params['SORBET.WLCTA.RUN'] is None:
        msg = f'Cannot use "{func_name}" without SORBET.WLCTA.RUN = True'
        raise sorbet_base.SorbetException(msg)
    # input file with the white light curve data
    input_file = params['SORBET.WLCTA.INPUT_FILE']
    # check if the file exists
    if os.path.isfile(input_file):
        filename = input_file
    else:
        filename = os.path.join(params['GLOBAL.DATA_PATH'], input_file)
    # load the light curve table
    try:
        dataset = io.load_table(filename)
    except Exception as e:
        msg = (f'Failed to load data from file "{filename}": {e}'
               f'\n\tFunction = {func_name}')
        raise sorbet_base.SorbetException(msg)
    
    return dataset


def load_slc(params: ParamDict):
    """
    Load the wavelength grid and spectral light curves for the
    transmission spectrum

    :param params: ParamDict, the parameter dictionary of constants

    :return: bjd, wave_tuple, flux_bin, eflux_bin, channel
    """
    # get function name
    func_name = __NAME__ + '.load_slc()'
    # check that this function is only being used for SORBET.SLCTA
    if params['SORBET.SLCTA.RUN'] is None:
        msg = f'Cannot use "{func_name}" without SORBEt.SLCTA.RUN = True'
        raise sorbet_base.SorbetException(msg)
    # get the sorbet parameters
    slcta_params = params.get('SORBET.SLCTA')
    # load data
    input_file = slcta_params['INPUT_FILE']
    # check if the file exists
    if os.path.isfile(input_file):
        filename = input_file
    else:
        filename = os.path.join(params['GLOBAL.DATA_PATH'], input_file)
    # load the light curve data
    # TODO why are the data >f8 dtype?
    try:
        wave = io.load_fits(filename,
                            extname='WAVELENGTH').astype(np.float64)
        flux = io.load_fits(filename,
                            extname='RELFLUX').astype(np.float64)
        eflux = io.load_fits(filename,
                             extname='RELFLUX_ERROR').astype(np.float64)
        bjd = io.load_fits(filename,
                           extname='BJD').astype(np.float64)
    except Exception as e:
        msg = (f'Failed to load data from file "{filename}": {e}'
               f'\n\tFunction = {func_name}')
        raise sorbet_base.SorbetException(msg)

    # determine order (NIRISS SOSS)
    if params['GLOBAL.INSTRUMENTMODE'] == 'JWST.NIRISS.SOSS':
        valid = np.isfinite(flux)
        w = 1 / eflux[valid]**2
        weighted_wave = np.nansum(wave[valid] * w) / np.nansum(w)
        if weighted_wave < 1.:
            channel = 2
        else:
            channel = 1
        if channel == 2:
            good = (wave[0, :] > 0.6) & (wave[0, :] < 0.85)
            wave = wave[:, good]
            flux = flux[:, good]
            eflux = eflux[:, good]
    else:
        channel = None

    # -------------------------------------------------------------------------
    # bin data to right resolution
    res = slcta_params['RESOLUTION_BIN']
    if res > 1:
        wave_tuple, flux_bin, eflux_bin = bin_spectrum(wave, flux, eflux,
                                                       res=res,
                                                       return_range=True)
    # else native resolution
    else: 
        wave_bin = wave.copy()
        # force ascending order
        s = np.argsort(wave_bin[0, :])
        wave_bin = wave_bin[:, s]
        flux_bin = flux[:, s]
        eflux_bin = eflux[:, s]
        # define bandwidth
        wave_low = wave_bin.copy()
        wave_high = wave_bin.copy()
        wave_low[:, 1:] = (wave_low[:, 1:] + wave_low[:, :-1]) / 2
        wave_high[:, :-1] = (wave_high[:, 1:] + wave_high[:, :-1]) / 2
        wave_tuple = (wave_bin, wave_low, wave_high)

    # -------------------------------------------------------------------------

    return bjd, wave_tuple, flux_bin, eflux_bin, channel


# TODO function from sossisse.instruments.defaults
# TODO merge with the above function, but bug during saving table in spectral extraction
# TODO: preferable to report mean wavelength of the bin and not the min value 
def bin_spectrum(wavegrid: np.ndarray, spec_in: np.ndarray,
                 spec_err_in: np.ndarray, res: int = 100,
                 return_range=False):
    """
    Bin the spectrum
    Can take 1D or 2D arrays with shape (epochs, wavelength)
    
    :param wavegrid: np.ndarray, the wavelength grid
    :param spec_in: np.ndarray, the in-transit
    :param spec_err_in: np.ndarray, the in-transit error
    :param return_range: bool, returns the wavelength bin ranges (low, high)
        along with the binned spectrum.
    
    """
    # get the wavelength bins
    with warnings.catch_warnings(record=True) as _:
        # log the wavelength
        logwave = np.log(wavegrid / np.nanmin(wavegrid))
        # get the wavelength binning
        wbin = np.floor(logwave * res)
    # create a wavebin, fluxbin and corresponding error vectors for output
    if wbin.shape[0] == 1:
        wave_bin = np.unique(wbin[~np.isnan(wbin)])
    else:    
        wave_bin = np.tile(np.unique(wbin[~np.isnan(wbin)]), 
                            (wbin.shape[0], 1))
    wave_low = np.zeros_like(wave_bin)
    wave_high = np.zeros_like(wave_bin)
    flux_bin = np.zeros_like(wave_bin)
    err_bin = np.zeros_like(wave_bin)
    # nframes and nbins
    nframes, nbins = wave_bin.shape

    # loop around frames
    for iframe in range(nframes):
        # loop around bins in wavelength
        for ibin in range(nbins):
            # find all wavelengths in this bin
            valid = wbin[iframe] == wave_bin[iframe, ibin]
            # get the flux and error using odd_ratio_mean
            flux, error = mp.odd_ratio_mean(spec_in[iframe, valid], 
                                            spec_err_in[iframe, valid])
            # push into array
            wave_low[iframe, ibin] = np.nanmin(wavegrid[iframe, valid])
            wave_high[iframe, ibin] = np.nanmax(wavegrid[iframe, valid])
            # wave_bin the mean of the bin
            wave_bin[iframe, ibin] = np.nanmean(wavegrid[iframe, valid])
            flux_bin[iframe, ibin] = flux
            err_bin[iframe, ibin] = error
    # return the binned data
    # TODO: best way to return the range of the bins not a Tuple?
    if return_range:
        return (wave_bin, wave_low, wave_high), flux_bin, err_bin
    else:
        return wave_bin, flux_bin, err_bin


def find_outliers(params: ParamDict, dataset: astropy.table.Table,
                  method: Literal['WLCTA', 'SLCTA']):
    """
    Find outliers in the dataset using a median filter

    :param params: ParamDict, the parameter dictionary of constants
    :param dataset: astropy.table.Table, the dataset to find outliers in
    :return: None
    """
    # load the dataset
    bjd = dataset['bjd'].data
    flux = dataset['amplitude'].data

    # apply median filter to remove outliers
    # transits are roughly the same duration so number of integration may be a 
    # good proxy of exposure time (inverserly proportional)
    kernel_size = int(0.05 * len(bjd))
    if kernel_size % 2 == 0:
        kernel_size += 1 # make sure it's odd
    medfilt_model = medfilt(flux, kernel_size) # model including the transit
    
    # remove outliers
    mad = np.median(np.abs(flux - medfilt_model))
    bad = np.abs(flux - medfilt_model) > 5 * mad

    # save medfilt model
    params[f'SORBET.{method}.MEDFILT_MODEL'] = medfilt_model
    # save the outlier mask
    params[f'SORBET.{method}.OUTLIER_MASK'] = bad.astype(bool)

    return medfilt_model, bad.astype(bool)


def prepare_dataset(params: ParamDict, dataset: astropy.table.Table,
                    method: Literal['WLCTA', 'SLCTA'],
                    outlier_mask: np.ndarray):
    """
    Prepare the dataset for juliet

    :param params: ParamDict, the parameter dictionary of constants
    :param dataset: astropy.table.Table, the dataset to prepare

    :return: dataset, the juliet dataset
    """
    # get function name
    func_name = __NAME__ + '.prepare_dataset()'
    # get the sorbet params (based on method)
    sparams = params.get(f'SORBET.{method}')
    slcta_params = params.get('SORBET.SLCTA')
    # select instrumental mode
    inst_mode = params['GLOBAL.INSTRUMENTMODE']
    # make sure inst_mode has no _ for juliet compatibility
    inst_mode = inst_mode.replace('_', '.')
    # -------------------------------------------------------------------------
    # convert the data into juliet format
    times, fluxes, fluxes_error = {},{},{}
    # -------------------------------------------------------------------------
    # put data arrays into dictionaries so we can fit it with juliet
    times[inst_mode] = dataset['bjd'].data[~outlier_mask]
    fluxes[inst_mode] = dataset['amplitude'].data[~outlier_mask]
    fluxes_error[inst_mode] = dataset['amplitude_error'].data[~outlier_mask]
    # -------------------------------------------------------------------------
    # load the juliet parameters, prior distributions, and prior parameters
    # list of juliet parameters
    juliet_params = sparams['JULIET_PARAMETERS']
    # replace INSTRUMENT with the instrument mode
    juliet_params = [param.replace('{INST_MODE}', inst_mode) for param in juliet_params]
    # list of prior distributions
    prior_dists = sparams['JULIET_PRIOR_DISTS']
    # list of prior hyperparameters
    prior_vals = sparams['JULIET_PRIOR_VALS']
    # make sure values from yaml are numbers
    prior_vals = [convert_to_number(val) for val in prior_vals]
    # -------------------------------------------------------------------------
    # add parameter for GP
    do_gp = False
    for param in juliet_params:
        if 'GP_' in param:
            do_gp = True
            break
    if do_gp:
        GP_regressors_lc = times
    else:
        GP_regressors_lc = None
    # -------------------------------------------------------------------------
    # add parameter for linear detrending
    # temporal slope# check if the file exists
    if sparams['LINEAR_DETRENDING'] == 'time':
        # make sure to not fit baseline twice
        idx = juliet_params.index(f'mflux_{inst_mode}')
        prior_dists[idx] = 'fixed'
        prior_vals[idx] = 0.0

        # add linear regressors
        lm_quantities = np.zeros((len(times[inst_mode]), 2))
        # first column is the constant term
        lm_quantities[:, 0] = np.ones_like(times[inst_mode])
        # second column is the temporal slope (error normalized)
        part1 = times[inst_mode] - np.nanmean(times[inst_mode])
        part2 = np.nanstd(times[inst_mode])
        lm_quantities[:, 1] = part1 / part2
        # add to the dictionary
        linear_regressors = {inst_mode: lm_quantities}

        # check if juliet parameters are already defined
        if f'theta0_{inst_mode}' not in juliet_params:
            # add the parameters to the juliet parameters
            juliet_params.append(f'theta0_{inst_mode}') 
            prior_dists.append('uniform')
            prior_vals.append([-5, 5])
        if f'theta1_{inst_mode}' not in juliet_params:
            juliet_params.append(f'theta1_{inst_mode}')
            prior_dists.append('uniform')
            prior_vals.append([-5, 5])

    elif sparams['LINEAR_DETRENDING'] not in [None, 'None', 'none']:
        # check if file exists
        input_file = sparams['LINEAR_DETRENDING']
        if os.path.isfile(input_file):
            filename = input_file
        else:
            filename = os.path.join(params['GLOBAL.DATA_PATH'], input_file)
        # load the linear detrending data
        try:
            lm_tbl = io.load_table(filename)
            bad = sparams['OUTLIER_MASK']
            lm_tbl = lm_tbl[~bad]
        except Exception as e:
            msg = (f'Failed to load data from file "{filename}": {e}'
                   f'\n\tFunction = {func_name}')
            raise sorbet_base.SorbetException(msg)
        
        # fetch columns names
        lm_cols = lm_tbl.colnames
        # convert table to array
        lm_quantities = np.ones((len(lm_tbl[lm_cols[0]]), len(lm_cols)))
        # fetch columns names
        lm_cols = lm_tbl.colnames
        # convert table to array
        lm_quantities = np.zeros((len(lm_tbl[lm_cols[0]]), len(lm_cols)))
        # loop around the columns (including the constant term)
        for i in range(len(lm_cols)):
            # columns to linear detrend
            col = lm_cols[i]
            detrender = lm_tbl[col].data
            # check if juliet parameters are already defined
            if f'theta{i}_{inst_mode}' not in juliet_params:
                # only consider non zero values
                not_zero = np.isfinite(detrender) & (detrender != 0)
                part1 = detrender[not_zero] - np.nanmean(detrender[not_zero])
                part2 = np.nanstd(detrender[not_zero])
                # do not normalize if a constant term
                if part2 == 0:
                    lm_quantities[:, i] = detrender
                else:
                    lm_quantities[:, i][not_zero] = part1 / part2
                juliet_params.append(f'theta{i}_{inst_mode}')
                prior_dists.append('uniform')
                prior_vals.append([-5, 5])
            else:
                lm_quantities[:, i] = detrender
            # add to the dictionary
            linear_regressors = {inst_mode: lm_quantities}
    else:
        linear_regressors = None
        
    # use model limb-darkening if ExoTiC-LD is enabled
    if method == 'SLCTA':
        # check if ExoTiC-LD is enabled
        if slcta_params['EXOTIC-LD.ENABLE']:
            # check if LD law are defined
            ld_law = slcta_params['EXOTIC-LD.LD_LAW']
            if ld_law is None:
                raise ValueError("ExoTiC-LD law is not defined")
            # check if ExoTiC-LD path exists
            exotic_ld_path = slcta_params['EXOTIC-LD.MODEL_PATH']
            if not os.path.isdir(exotic_ld_path):
                raise ValueError(f"ExoTiC-LD path '{exotic_ld_path}' does not exist")
            # check if ExoTiC-LD model grid is defined
            exotic_ld_model = slcta_params['EXOTIC-LD.MODEL_GRID']
            if exotic_ld_model is None:
                msg = ('ExoTiC-LD model grid is not defined. '
                       '\n\tFunction = {func_name}')
                raise sorbet_base.SorbetException(msg)
            
            # compute the q1 and q2 quadratic coefficients
            try:
                if ld_law == 'quadratic':
                    u1, u2 = get_model_ld_coeffs(params)
                    # overwrite the priors
                    idx = juliet_params.index(f'u1_{inst_mode}')
                    prior_dists[idx] = 'fixed'
                    prior_vals[idx] = u1
                    idx = juliet_params.index(f'u2_{inst_mode}')
                    prior_dists[idx] = 'fixed'
                    prior_vals[idx] = u2
                elif ld_law == 'kipping':
                    q1, q2 = get_model_ld_coeffs(params)
                    # overwrite the priors
                    idx = juliet_params.index(f'q1_{inst_mode}')
                    prior_dists[idx] = 'fixed'
                    prior_vals[idx] = q1
                    idx = juliet_params.index(f'q2_{inst_mode}')
                    prior_dists[idx] = 'fixed'
                    prior_vals[idx] = q2
                elif ld_law == 'nonlinear':
                    c1, c2, c3, c4 = get_model_ld_coeffs(params)
                    # overwrite the priors
                    idx = juliet_params.index(f'c1_{inst_mode}')
                    prior_dists[idx] = 'fixed'
                    prior_vals[idx] = c1
                    idx = juliet_params.index(f'c2_{inst_mode}')
                    prior_dists[idx] = 'fixed'
                    prior_vals[idx] = c2
                    idx = juliet_params.index(f'c3_{inst_mode}')
                    prior_dists[idx] = 'fixed'
                    prior_vals[idx] = c3
                    idx = juliet_params.index(f'c4_{inst_mode}')
                    prior_dists[idx] = 'fixed'
                    prior_vals[idx] = c4
            except Exception as e:
                msg = (f'Failed to compute limb darkening coefficients: {e}'
                       f'\n\tFunction = {func_name}')
                raise sorbet_base.SorbetException(msg)

    # populate the priors dictionary:
    priors = juliet.generate_priors(juliet_params, prior_dists, prior_vals)

    # add output path to the params
    out_folder = sparams['OUTPUT_PATH']
    # if spectral bins
    if method == 'SLCTA':
        wb = slcta_params['BINNUMBER']
        channel = slcta_params['CHANNEL']
        # check if the folder exists
        if os.path.isdir(out_folder):
            out_folder = os.path.join(out_folder, f'ord{channel}bin{wb}')
        else:
            os.mkdir(out_folder)
            out_folder = os.path.join(out_folder, f'ord{channel}bin{wb}')
        # update the output path
        sparams['OUTPUT_SUBPATH'] = out_folder

    # Load and fit dataset with juliet:
    dataset = juliet.load(priors=priors,
                          t_lc=times, y_lc=fluxes, yerr_lc=fluxes_error,
                          GP_regressors_lc=GP_regressors_lc,
                          linear_regressors_lc=linear_regressors,
                          out_folder=out_folder)

    return dataset


def fit_transit(params: ParamDict, dataset: juliet.load,
                method: Literal['WLCTA', 'SLCTA']):
    """
    Fit the transit using juliet/batman

    :param params: ParamDict, the parameter dictionary of constants
    :param dataset: juliet.load, the juliet dataset

    :return: results, the juliet results
    """
    # TODO allow more sampling options
    sampling_options = params[f'SORBET.{method}.SAMPLING_OPTIONS']
    # Fit the dataset
    results = dataset.fit(sampler=sampling_options, nthreads=4)

    return results


def save_transit_model(params: ParamDict, results: juliet.fit,
                       method: Literal['WLCTA', 'SLCTA']):
    """
    Save the best-fit model (transit + systematics)

    :param params: ParamDict, the parameter dictionary of constants
    :param results: juliet.results, the juliet results

    :return: None
    """
    # select instrumental mode
    inst_mode = params['GLOBAL.INSTRUMENTMODE']
    # from juliet tutorial
    # extract the components of the model (transit, systematics, etc.)
    full_model, components = results.lc.evaluate(inst_mode, 
                                        return_components=True)
    # add full_model to components
    components['full_model'] = full_model
    # add gp to components
    if 'GP' in results.lc.model[inst_mode].keys():
        components['gp'] = results.lc.model[inst_mode]['GP']

    # file path
    if method == 'SLCTA':
        filepath = os.path.join(params[f'SORBET.{method}.OUTPUT_SUBPATH'],
                             'model_components.pkl')
    else:
        filepath = os.path.join(params[f'SORBET.{method}.OUTPUT_PATH'],
                             'model_components.pkl')
    # save the best-fit model
    with open(filepath, "wb") as pfile:
        pkl.dump(components, pfile)


def load_transit_model(params: ParamDict, method: Literal['WLCTA', 'SLCTA']):
    """
    Load the best-fit model (transit + systematics)

    :param params: ParamDict, the parameter dictionary of constants

    :return: components, the best-fit model components
    """
    # file path
    if method == 'SLCTA':
        filepath = os.path.join(params[f'SORBET.{method}.OUTPUT_SUBPATH'],
                             'model_components.pkl')
    else:
        filepath = os.path.join(params[f'SORBET.{method}.OUTPUT_PATH'],
                             'model_components.pkl')
    # load the best-fit model
    with open(filepath, "rb") as f:
        components = pkl.load(f)

    return components


def save_transmission_spectrum(params: ParamDict, spec_tbl: astropy.table.Table):
    """
    Save the transmission spectrum

    :param params: ParamDict, the parameter dictionary of constants
    :param spec_tbl: astropy.table.Table, the transmission spectrum table

    :return: None
    """
    # select instrumental mode
    inst_mode = params['GLOBAL.INSTRUMENTMODE']
    # select channel
    channel = params['SORBET.SLCTA.CHANNEL']
    # output path
    output_path = params['SORBET.SLCTA.OUTPUT_PATH']
    filename = os.path.join(output_path,
        'transmission_spectrum_{0}_ord{1}.csv'.format(inst_mode.replace('.', '_'),
                                                      channel))
    # save new path
    params['SORBET.SLCTA.TRANSMISSION_SPECTRUM_FILE'] = filename

    # save the transmission spectrum table
    io.save_table(filename, spec_tbl, fmt='csv')


def get_model_ld_coeffs(params: ParamDict):
    """
    Get the quadratic limb darkening parameters (Kipping 2013) for a
    given wavelength range using the ExoTiC-LD package.

    :param params: ParamDict, the parameter dictionary of constants

    :return: tuple, the quadratic limb darkening parameters q1, q2
    """
    
    # Following the example in the ExoTiC-LD tutorial

    # set SLCTA.EXOTIC params
    ex_params = params.get('SORBET.SLCTA.EXOTIC-LD')

    # Path to the downloaded data
    ld_data_path = ex_params['MODEL_PATH']
    # Select limb-darkening law
    ld_law = ex_params['LD_LAW']
    # Stellar models grid
    # Supported grids: https://exotic-ld.readthedocs.io/en/latest/views/supported_stellar_grids.html
    ld_model = ex_params['MODEL_GRID']
    # Metallicty [dex]
    M_H = ex_params['STELLAR_MET']
    # Effective temperature [K]
    Teff = ex_params['STELLAR_TEFF']
    # Surface gravity [dex]
    logg = ex_params['STELLAR_LOGG']

    # load ExoTiC-LD 
    sld = StellarLimbDarkening(M_H, Teff, logg, ld_model, ld_data_path)

    # select instrumental mode
    inst_mode = params['GLOBAL.INSTRUMENTMODE']
    # convert to instrumental profile supported in ExoTiC-LD
    # https://exotic-ld.readthedocs.io/en/latest/views/supported_instruments.html
    if inst_mode == 'JWST.NIRISS.SOSS':
        if params['SORBET.SLCTA.CHANNEL'] == 1:
            inst_profile = 'JWST_NIRISS_SOSSo1'
        elif params['SORBET.SLCTA.CHANNEL'] == 2:
            inst_profile = 'JWST_NIRISS_SOSSo2'
        else:
            raise ValueError('Provide a valid order for the NIRISS SOSS')
    elif inst_mode == 'JWST.NIRISS.PRISM':
        inst_profile = 'JWST_NIRSpec_Prism'
    else:
        raise ValueError('Provide a valid instrument mode')

    # convert wavelength range in microns to Angstrom (ExoTiC-LD)
    wave_low = params['SORBET.SLCTA.WAVE_BIN_LOW']
    wave_high = params['SORBET.SLCTA.WAVE_BIN_HIGH']
    wave_range = np.array([wave_low, wave_high]) * 1e4

    # compute the limb-darkening coefficients
    if ld_law == 'quadratic':
        u1, u2 = sld.compute_quadratic_ld_coeffs(wave_range, inst_profile)
        return u1, u2
    elif ld_law == 'kipping': 
        q1, q2 = sld.compute_kipping_ld_coeffs(wave_range, inst_profile)
        return q1, q2
    elif ld_law == 'nonlinear':
        c1, c2, c3, c4 = sld.compute_4_parameter_non_linear_ld_coeffs(wave_range, inst_profile)
        return c1, c2, c3, c4
    else:
        msg = 'Provide a valid limb-darkening law (quadratic, kipping, or nonlinear)'
        raise sorbet_base.SorbetException(msg)

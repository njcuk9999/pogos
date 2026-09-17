#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# sorbet.general.general.py
# Science functions for SORBET

Created on 2025-02-19 at 13:43

@author: CharlesCadieux

No imports from sorbet.general.general
"""
from pogos.core.external_imports import juliet, StellarLimbDarkening
from pogos.core.external_imports import JULIET_IMPORT_MESSAGES
from pogos.core.external_imports import EXOTIC_LD_IMPORT_MESSAGES

import os
import pickle as pkl
import warnings
from typing import Any, Dict, Literal, List, Optional
import numpy as np
from astropy.table import Table
from astropy.io import fits

from scipy.signal import medfilt

from aperocore import math as mp
from aperocore.constants.param_functions import ParamDict
from aperocore.core import drs_log
from pogos.core import base
from pogos.core import input_validation
from pogos.sorbet.core import base as sorbet_base
from pogos.sorbet.core import core
from sossisse.core import io


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
def load_wlc(params: ParamDict):
    """
    Load the WLC dataset using configs from the yaml file

    :param params: ParamDict, the parameter dictionary of constants

    :return: dataset table, astropy.table
    """
    # get function name
    func_name = __NAME__ + '.load_wlc()'
    # check that this function is only being used for SORBET.WLCA
    if params['RUN.SORBET.WLCA'] is None:
        msg = f'Cannot use "{func_name}" without RUN.SORBET.WLCA = True'
        raise sorbet_base.SorbetException(msg)

    # input file with the white light curve data
    input_file = params['SORBET.WLCA.INPUT_FILE']
    # check if the file exists
    if os.path.isfile(input_file):
        filename = input_file
    else:
        # get input path
        inpath = params[f'SORBET.WLCA.INPUT_PATH']
        # construct full filename
        filename = os.path.join(inpath, input_file)
    # Resolve and check the FITS product before reading its table extension.
    filename = os.path.abspath(filename)
    if not os.path.isfile(filename):
        msg = f'SORBET.WLCA.INPUT_FILE="{filename}" does not exist.'
        raise sorbet_base.SorbetException(msg)
    input_validation.check_input_data_headers(params, [filename])
    # load the light curve table
    try:
        dataset = io.load_table(filename)
    except Exception as e:
        msg = (f'Failed to load data from file "{filename}": {e}'
               f'\n\tFunction = {func_name}')
        raise sorbet_base.SorbetException(msg)
    
    return dataset


def load_slc(params: ParamDict, input_file: str,
             trace_order: int = 1):
    """
    Load the wavelength grid and spectral light curves for the
    transmission spectrum

    :param params: ParamDict, the parameter dictionary of constants

    :return: bjd, wave_tuple, flux_bin, eflux_bin, channel
    """
    # get function name
    func_name = __NAME__ + '.load_slc()'
    # check that this function is only being used for SORBET.SLCA
    if params['RUN.SORBET.SLCA'] is None:
        msg = f'Cannot use "{func_name}" without RUN.SORBET.SLCA = True'
        raise sorbet_base.SorbetException(msg)
    # get the sorbet parameters
    slcta_params = params.get('SORBET.SLCA')
    # check if the file exists
    if os.path.exists(input_file):
        filename = input_file
    else:
        # get input path
        inpath = slcta_params['INPUT_PATH']
        # construct full filename
        filename = os.path.join(inpath, input_file)
        # ---------------------------------------------------------------------
        # deal with file not existing
        if not os.path.exists(filename):
            msg = f'SORBET.SLCA.INPUT_FILE="{filename}" does not exist.'
            raise sorbet_base.SorbetException(msg)
    # Resolve and validate the FITS product before reading its extensions.
    filename = os.path.abspath(filename)
    input_validation.check_input_data_headers(params, [filename])
    # -------------------------------------------------------------------------
    # load the light curve data
    try:
        with fits.open(filename) as hdulist:
            wave = np.array(hdulist[f'WAVELENGTH_{trace_order}'].data)
            flux = np.array(hdulist[f'RELFLUX_{trace_order}'].data)
            eflux = np.array(hdulist[f'RELFLUX_ERROR_{trace_order}'].data)
            bjd = np.array(hdulist[f'BJD_{trace_order}'].data)
            # cast as np.float64
            wave = wave.astype(np.float64)
            flux = flux.astype(np.float64)
            eflux = eflux.astype(np.float64)
            bjd = bjd.astype(np.float64)
    except Exception as e:
        msg = (f'Failed to load data from file "{filename}": {e}'
               f'\n\tFunction = {func_name}')
        raise sorbet_base.SorbetException(msg)

    # deal with wave being 1D or 2D (we just take the first row)
    # TODO: is this the right thing to do?
    if wave.shape != flux.shape:
        # we take the first wave solution and apply it to all integrations
        wave = np.tile(wave[0], flux.shape[0]).reshape(flux.shape)

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


def find_outliers(params: ParamDict, data_table: Table,
                  method: Literal['WLCA', 'SLCA']):
    """
    Find outliers in the dataset using a median filter

    :param params: ParamDict, the parameter dictionary of constants
    :param dataset: astropy.table.Table, the dataset to find outliers in
    :return: None
    """
    # load the dataset
    bjd = np.array(data_table['Time']).astype(np.float64)
    flux = np.array(data_table['RelFlux']).astype(np.float64)
    # get the outlier kernel size
    outlier_kernel_size = params[f'SORBET.{method}.OUTLIER_KERNEL_SIZE']

    # apply median filter to remove outliers
    # transits are roughly the same duration so number of integration may be a 
    # good proxy of exposure time (inverserly proportional)
    if outlier_kernel_size is not None:
        kernel_size = int(outlier_kernel_size)
    else:
        kernel_size = int(0.05 * len(bjd))
    # it must be odd for medfilt
    if kernel_size % 2 == 0:
        kernel_size += 1 # make sure it's odd
    medfilt_model = medfilt(flux, kernel_size) # model including the transit
    
    # remove outliers
    mad = np.median(np.abs(flux - medfilt_model))
    outlier_mask = np.abs(flux - medfilt_model) > 5 * mad

    return medfilt_model, outlier_mask.astype(bool)


def test_juliet_distributions(params: ParamDict,
                              method: Literal['WLCA', 'SLCA']) -> List[str]:
    """
    Test the user inputted all the Juliet distributions correctly

    :param params: ParamDict, the parameter dictionary of constants
    :param method: str, the method to use (WLCA or SLCA)

    :return: list of strings, the prior distributions for each juliet parameter
    """
    # select instrumental mode
    inst_mode = core.sorbet_inst_mode(params)
    # get the juliet parameters and prior distributions from sparams
    jparams = params[f'SORBET.{method}.JULIET_PARAMETERS']
    jdists = params[f'SORBET.{method}.JULIET_PRIOR_DISTS']

    # deal with jvals being empty
    if jdists is None or len(jdists) == 0:
        msg = (f'No juliet prior values defined in '
               f'"SORBET.{method}.JULIET_PRIOR_DISTS". '
               f' Cannot proceed with the fit.')
        raise sorbet_base.SorbetException(msg)

    # get valid distribution types
    valid_dists = params['SORBET.GENERAL.JULIET_VALID_DISTS']

    # deal with valid dists being empty
    if valid_dists is None or len(valid_dists) == 0:
        msg = (f'No juliet valid disributions defined in '
               f'"SORBET.GENERAL.JULIET_VALID_DISTS". '
               f' Cannot proceed with the fit.')
        raise sorbet_base.SorbetException(msg)

    # test that all juliet parameters have a prior distribution
    prior_dists: List[str] = []
    found = []
    for param in jparams:
        if param in jdists and jdists[param] in valid_dists:
            prior_dists.append(jdists[param])
            found.append(param)
        elif param in jdists and jdists[param] not in valid_dists:
            msg = (f'Parameter "{param}" has an invalid prior distribution '
                   f'"{jdists[param]}". Valid distributions are: '
                   f'{valid_dists}. Please define it under '
                   f' "SORBET.{method}.JULIET_PRIOR_DISTS". '
                   f' If we have missed one you can override '
                   f' SORBET.GENERAL.JULIET_VALID_DISTS')
            raise sorbet_base.SorbetException(msg)
        else:
            msg = (f'Parameter "{param}" does not have a prior distribution '
                   f'defined in the yaml file. Please define it under '
                   f' "SORBET.{method}.JULIET_PRIOR_DISTS"')
            raise sorbet_base.SorbetException(msg)

    # deal with param in piror dists but not in parameters
    for param in jdists:
        if param not in found:
            msg = (f'Parameter "{param}" is in JULIET_PRIOR_DISTS but not in '
                   f'JULIET_PARAMETERS. Please remove it from '
                   f'JULIET_PRIOR_DISTS or add it to JULIET_PARAMETERS.')
            raise sorbet_base.SorbetException(msg)

    # update juliet params with instrument mode
    prior_dists = [p.replace('{INST_MODE}', inst_mode) for p in prior_dists]
    # return the prior distributions
    return prior_dists


def test_juliet_values(params: ParamDict,
                       method: Literal['WLCA', 'SLCA']
                       ) -> List[float | List[float]]:
    """
    Test the user inputted all the Juliet prior values correctly

    :param params: ParamDict, the parameter dictionary of constants
    :param method: str, the method to use (WLCA or SLCA)

    :return: list of float or list of float, the prior values for each
             juliet parameter
    """
    # get the juliet parameters and prior distributions from sparams
    jparams = params[f'SORBET.{method}.JULIET_PARAMETERS']
    jvals = params[f'SORBET.{method}.JULIET_PRIOR_VALS']

    # deal with jvals being empty
    if jvals is None or len(jvals) == 0:
        msg = (f'No juliet prior values defined in '
               f'"SORBET.{method}.JULIET_PRIOR_VALS". '
               f' Cannot proceed with the fit.')
        raise sorbet_base.SorbetException(msg)

    # function to force float conversion#
    def force_float(value: Any) -> float:
        """
        Force conversion to float, raise exception if not possible
        :param value: Any, the value to convert

        :raises SorbetException: if value is not a float
        :return: float, the converted value
        """
        try:
            return float(value)
        except ValueError:
            msg = (f'Value "{value}" cannot be converted to a float. '
                   f'Please define it under "SORBET.{method}.JULIET_PRIOR_VALS"')
            raise sorbet_base.SorbetException(msg)

    # test that all juliet parameters have a prior distribution
    prior_vals: List[float | List[float]] = []
    found = []
    for param in jparams:
        if param in jvals:
            # get yaml value
            raw_val = jvals[param]
            # deal with raw value being a float
            if isinstance(raw_val, (int, float, str)):
                prior_vals.append(force_float(raw_val))
                found.append(param)
            # deal with raw value being a string (i.e 4e5 is read as a string)
            elif isinstance(raw_val, list):
                # make sure all values are numbers
                list_val = [force_float(v) for v in raw_val]
                prior_vals.append(list_val)
                found.append(param)
            # deal with anything else (bad)
            else:
                msg = (f'Value "{raw_val}" is not a valid type. '
                       f'Please define it under "SORBET.{method}.JULIET_PRIOR_VALS"')
                raise sorbet_base.SorbetException(msg)
        else:
            msg = (f'Parameter "{param}" does not have a prior distribution '
                   f'defined in the yaml file. Please define it under '
                   f' "SORBET.{method}.JULIET_PRIOR_VALS"')
            raise sorbet_base.SorbetException(msg)

    # deal with param in piror dists but not in parameters
    for param in jvals:
        if param not in found:
            msg = (f'Parameter "{param}" is in JULIET_PRIOR_VALS but not in '
                   f'JULIET_PARAMETERS. Please remove it from '
                   f'JULIET_PRIOR_VALS or add it to JULIET_PARAMETERS.')
            raise sorbet_base.SorbetException(msg)
    # return the prior values
    return prior_vals


def prepare_dataset(params: ParamDict, data_table: Table,
                    method: Literal['WLCA', 'SLCA'],
                    outlier_mask: np.ndarray,
                    bin_params: Optional[Dict[str, Any]] = None) -> juliet.load:
    """
    Prepare the dataset for juliet

    :param params: ParamDict, the parameter dictionary of constants
    :param data_table: astropy.table.Table, the dataset to prepare

    :return: dataset, the juliet dataset
    """
    # get function name
    func_name = __NAME__ + '.prepare_dataset()'
    # -------------------------------------------------------------------------
    # Juliet is about to be used - print any warnings
    if len(JULIET_IMPORT_MESSAGES) > 0:
        for msg in JULIET_IMPORT_MESSAGES:
            WLOG(params, 'warning', msg)
    # -------------------------------------------------------------------------
    # deal with no bin params
    if bin_params is None:
        bin_params = dict(CHANNEL=None, BINNUMBER=None,
                          WAVE_BIN_LOW=None, WAVE_BIN_HIGH=None,
                          suffix=None)
    # get the sorbet params (based on method)
    sparams = params.get(f'SORBET.{method}')
    slcta_params = params.get('SORBET.SLCA')
    # select instrumental mode
    inst_mode = core.sorbet_inst_mode(params)
    # -------------------------------------------------------------------------
    # convert the data into juliet format
    times, fluxes, fluxes_error = {},{},{}
    # -------------------------------------------------------------------------
    # put data arrays into dictionaries so we can fit it with juliet
    times[inst_mode] = np.array(data_table['Time'])[~outlier_mask]
    fluxes[inst_mode] = np.array(data_table['RelFlux'])[~outlier_mask]
    fluxes_error[inst_mode] = np.array(data_table['RelFlux_Err'])[~outlier_mask]
    # -------------------------------------------------------------------------
    # load the juliet parameters, prior distributions, and prior parameters
    #  in SORBET these are a list, a two dictionaries but we need to do some
    #  checks and data type conversion before passing them into juliet
    # -------------------------------------------------------------------------
    # list of juliet parameters
    juliet_params = sparams['JULIET_PARAMETERS']
    # select instrumental mode
    inst_mode = core.sorbet_inst_mode(params)
    # update juliet params with instrument mode
    juliet_params = [p.replace('{INST_MODE}', inst_mode) for p in juliet_params]
    # deal with no parameters
    if juliet_params is None or len(juliet_params) == 0:
        msg = (f'No juliet parameters defined in '
               f'"SORBET.{method}.JULIET_PARAMETERS". '
               f' Cannot proceed with the fit.'
               f'\n\tFunction = {func_name}')
        raise sorbet_base.SorbetException(msg)
    # list of prior distributions
    prior_dists = test_juliet_distributions(params, method=method)
    # list of prior hyperparameters
    prior_vals = test_juliet_values(params, method=method)
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
    linear_regressors = None
    # temporal slope# check if the file exists
    if sparams['LINEAR_DETRENDING'] == 'time':
        # make sure to not fit baseline twice
        idx = juliet_params.index(f'mflux_{str(inst_mode)}')
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
        input_type = sparams['LINEAR_DETRENDING_TYPE']
        if os.path.isfile(input_file):
            filename = input_file
        else:
            filename = os.path.join(params['GLOBAL.DATA_PATH'], input_file)
        # load the linear detrending data
        try:
            lm_tbl = io.load_table(filename, fmt=input_type)
            lm_tbl = lm_tbl[~outlier_mask]
        except Exception as e:
            msg = (f'Failed to load data from file "{filename}": {e}'
                   f'\n\tFunction = {func_name}')
            raise sorbet_base.SorbetException(msg)

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
    if method == 'SLCA':
        # check if ExoTiC-LD is enabled
        if slcta_params['EXOTIC-LD.ENABLE']:
            # log exotic ld import warnings
            if len(EXOTIC_LD_IMPORT_MESSAGES) > 0:
                for msg in EXOTIC_LD_IMPORT_MESSAGES:
                    WLOG(params, 'warning', msg, func_name=func_name)
            # check if LD law are defined
            ld_law = slcta_params['EXOTIC-LD.LD_LAW']
            if ld_law is None:
                emsg = ('ExoTiC-LD law is not defined. '
                        'Please define in SORBET.SLCA.EXOTIC-LD.LD_LAW')
                raise sorbet_base.SorbetException(emsg)
            # check if ExoTiC-LD path exists
            exotic_ld_path = slcta_params['EXOTIC-LD.MODEL_PATH']
            if not os.path.isdir(exotic_ld_path):
                emsg = (f'ExoTiC-LD path "{exotic_ld_path}" does not exist. '
                        f'Please define in SORBET.SLCA.EXOTIC-LD.MODEL_PATH')
                raise sorbet_base.SorbetException(emsg)
            # check if ExoTiC-LD model grid is defined
            exotic_ld_model = slcta_params['EXOTIC-LD.MODEL_GRID']
            if exotic_ld_model is None:
                msg = ('ExoTiC-LD model grid is not defined.'
                       ' Please define in SORBET.SLCA.EXOTIC-LD.MODEL_GRID')
                raise sorbet_base.SorbetException(msg)
            
            # compute the q1 and q2 quadratic coefficients
            try:
                if ld_law == 'quadratic':
                    u1, u2 = get_model_ld_coeffs(params, bin_params)
                    # overwrite the priors
                    idx = juliet_params.index(f'u1_{inst_mode}')
                    prior_dists[idx] = 'fixed'
                    prior_vals[idx] = u1
                    idx = juliet_params.index(f'u2_{inst_mode}')
                    prior_dists[idx] = 'fixed'
                    prior_vals[idx] = u2
                elif ld_law == 'kipping':
                    q1, q2 = get_model_ld_coeffs(params, bin_params)
                    # overwrite the priors
                    idx = juliet_params.index(f'q1_{inst_mode}')
                    prior_dists[idx] = 'fixed'
                    prior_vals[idx] = q1
                    idx = juliet_params.index(f'q2_{inst_mode}')
                    prior_dists[idx] = 'fixed'
                    prior_vals[idx] = q2
                elif ld_law == 'nonlinear':
                    c1, c2, c3, c4 = get_model_ld_coeffs(params, bin_params)
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
    if method == 'SLCA':
        suffix = str(bin_params['SUFFIX'])
        # check if the folder exists
        if os.path.isdir(out_folder):
            out_folder = os.path.join(out_folder, suffix)
        else:
            out_folder = os.path.join(out_folder, suffix)
        # update the output path
        sparams['OUTPUT_SUBPATH'] = out_folder

    # make directories if they do not exists
    if not os.path.exists(out_folder):
        os.makedirs(out_folder, exist_ok=True)

    # Deal with having temporary files
    deal_with_previous_juilet_files(params, sparams, out_folder)

    # Load and fit dataset with juliet:
    dataset = juliet.load(priors=priors,
                          t_lc=times, y_lc=fluxes, yerr_lc=fluxes_error,
                          GP_regressors_lc=GP_regressors_lc,
                          linear_regressors_lc=linear_regressors,
                          out_folder=out_folder)

    return dataset


def deal_with_previous_juilet_files(params: ParamDict, sparams: ParamDict,
                                    out_folder: str):

    # if user has flagged they want to use previous juliet files, do not delete
    if sparams['USE_PREV_JULIET']:
        # print progress
        msg = (f'User has flagged to use previous Juliet files '
               f'in "{out_folder}". '
               f'\nProceeding without deleting previous Juliet files.')
        WLOG(params, 'warning', msg, sublevel=2)
        return
    # -------------------------------------------------------------------------
    # get the yaml file
    yaml_file = params['GLOBAL.YAML_FILE']
    # -------------------------------------------------------------------------
    # list files in the output folder
    prev_files = os.listdir(out_folder)
    # remove the yaml file from this list
    if os.path.basename(yaml_file) in prev_files:
        prev_files.remove(os.path.basename(yaml_file))
    # -------------------------------------------------------------------------
    # if directory is empty we save a copy of the yaml file and move on
    if len(prev_files) == 0:
        # copy the yaml file to the output folder
        dest_yaml_file = os.path.join(out_folder, os.path.basename(yaml_file))
        io.copy_file(yaml_file, dest_yaml_file)
        # print progress
        msg = (f'No previous juliet files found in "{out_folder}". '
               f'Copying yaml file to output folder.')
        WLOG(params, '', msg)
        return
    # -------------------------------------------------------------------------
    # otherwise we have to compare previous yaml file with current one
    dest_yaml_file = os.path.join(out_folder, os.path.basename(yaml_file))
    # if the file does not exist we remove everything in the output folder
    if not os.path.isfile(dest_yaml_file):
        pass
    else:
        # compare the two yaml files
        files_match = io.compare_yaml_files(yaml_file, dest_yaml_file)
        # if they match we do not remove the previous juliet files
        if files_match:
            # print progress
            msg = (f'Previous juliet files found in "{out_folder}" but '
                   f'yaml files match. '
                   f'\nProceeding with fit without deleting previous '
                   f'Juliet files.')
            WLOG(params, '', msg)
            return
    # -------------------------------------------------------------------------
    # print progress
    msg = (f'Previous juliet files found in "{out_folder}" but yaml '
           f'files do not match. '
           f'\nRemoving previous Juliet files.')
    WLOG(params, '', msg)
    # remove everything in the output folder
    for filename in prev_files:
        file_path = os.path.join(out_folder, filename)
        try:
            if os.path.isfile(file_path):
                # print removal progress
                msg = f'Removing file "{file_path}"'
                WLOG(params, '', msg)
                # remove file
                os.remove(file_path)
            elif os.path.isdir(file_path):
                # print removal progress
                msg = f'Removing directory "{file_path}"'
                WLOG(params, '', msg)
                # remove directory
                os.rmdir(file_path)
        except Exception as e:
            msg = (f'Failed to delete file "{file_path}": {e}')
            raise sorbet_base.SorbetException(msg)


def fit_transit(params: ParamDict, dataset: juliet.load,
                method: Literal['WLCA', 'SLCA']):
    """
    Fit the transit using juliet/batman

    :param params: ParamDict, the parameter dictionary of constants
    :param dataset: juliet.load, the juliet dataset

    :return: results, the juliet results
    """
    # TODO: this breaks if pkl file already exists, do we want to remove
    #       File is: dataset.out_folder + dataset.sampler_prefix +
    #                                'posteriors.pkl'
    #       Content is: dict_keys(['dynesty_output', 'lnZ', 'lnZerr', 'posterior_samples'])
    #       Breaks when prior name is changed in posterior_samples
    #       pkl files from previous runs?
    # TODO allow more sampling options
    sampling_options = params[f'SORBET.{method}.SAMPLING_OPTIONS']
    # Fit the dataset
    results = dataset.fit(sampler=sampling_options, nthreads=4)

    return results


def save_transit_model(params: ParamDict, dataset, results: juliet.fit,
                       method: Literal['WLCA', 'SLCA']):
    """
    Save the best-fit model (transit + systematics)

    :param params: ParamDict, the parameter dictionary of constants
    :param results: juliet.results, the juliet results

    :return: None
    """
    # select instrumental mode
    inst_mode = core.sorbet_inst_mode(params)
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
    if method == 'SLCA':
        filepath = os.path.join(params[f'SORBET.{method}.OUTPUT_SUBPATH'],
                                'model_components.pkl')
    else:
        filepath = os.path.join(params[f'SORBET.{method}.OUTPUT_PATH'],
                                'model_components.pkl')
    # save the best-fit model
    with open(filepath, "wb") as pfile:
        pkl.dump(components, pfile)
    # -------------------------------------------------------------------------
    # construct table filename
    model_tbl_filename = filepath.replace('.pkl', '.fits')
    # save as a Table
    model_tbl = Table()
    model_tbl['Time'] = dataset.t_lc
    for key in components.keys():
        model_tbl[key] = components[key]
    # print progress
    msg = f'Saving best-fit model components to "{model_tbl_filename}"'
    WLOG(params, '', msg)
    # save table file as fits file
    model_tbl.write(model_tbl_filename, overwrite=True)


def load_transit_model(params: ParamDict, method: Literal['WLCA', 'SLCA']):
    """
    Load the best-fit model (transit + systematics)

    :param params: ParamDict, the parameter dictionary of constants

    :return: components, the best-fit model components
    """
    # file path
    if method == 'SLCA':
        filepath = os.path.join(params[f'SORBET.{method}.OUTPUT_SUBPATH'],
                             'model_components.pkl')
    else:
        filepath = os.path.join(params[f'SORBET.{method}.OUTPUT_PATH'],
                             'model_components.pkl')
    # load the best-fit model
    with open(filepath, "rb") as f:
        components = pkl.load(f)

    return components


def save_transmission_spectrum(params: ParamDict, spec_tbl: Table,
                               channel: int):
    """
    Save the transmission spectrum

    :param params: ParamDict, the parameter dictionary of constants
    :param spec_tbl: astropy.table.Table, the transmission spectrum table

    :return: None
    """
    # select instrumental mode
    inst_mode = params['GLOBAL.INSTRUMENTMODE'].upper()
    # output path
    bargs = [inst_mode, channel]
    basename = 'transmission_spectrum_{0}_ord{1}.csv'.format(*bargs)
    output_path = params['SORBET.SLCA.OUTPUT_PATH']
    filename = os.path.join(output_path, basename)
    # save new path
    params['SORBET.SLCA.TRANSMISSION_SPECTRUM_FILE'] = filename
    # save the transmission spectrum table
    io.save_table(filename, spec_tbl, fmt='csv')


def get_model_ld_coeffs(params: ParamDict, bin_params: Dict[str, Any]):
    """
    Get the quadratic limb darkening parameters (Kipping 2013) for a
    given wavelength range using the ExoTiC-LD package.

    :param params: ParamDict, the parameter dictionary of constants

    :return: tuple, the quadratic limb darkening parameters q1, q2
    """
    
    # Following the example in the ExoTiC-LD tutorial

    # set SLCA.EXOTIC params
    ex_params = params.get('SORBET.SLCA.EXOTIC-LD')

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
    inst_mode = core.sorbet_inst_mode(params)
    # convert to instrumental profile supported in ExoTiC-LD
    # https://exotic-ld.readthedocs.io/en/latest/views/supported_instruments.html
    if inst_mode == 'JWST.NIRISS.SOSS':
        if params['SORBET.SLCA.CHANNEL'] == 1:
            inst_profile = 'JWST_NIRISS_SOSSo1'
        elif params['SORBET.SLCA.CHANNEL'] == 2:
            inst_profile = 'JWST_NIRISS_SOSSo2'
        else:
            raise ValueError('Provide a valid order for the NIRISS SOSS')
    elif inst_mode == 'JWST.NIRISS.PRISM':
        inst_profile = 'JWST_NIRSpec_Prism'
    else:
        raise ValueError('Provide a valid instrument mode')

    # convert wavelength range in microns to Angstrom (ExoTiC-LD)
    wave_low = bin_params['WAVE_BIN_LOW']
    wave_high = bin_params['WAVE_BIN_HIGH']
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
    dataset['Time'] = bjd
    dataset['RelFlux'] = flux
    dataset['RelFlux_Err'] = eflux

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


def append_transmission_spec(params: ParamDict, results: juliet.fit,
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
    delta = np.median(p ** 2)
    delta_ci = np.percentile(p ** 2, [16, 84])
    delta_err = (delta_ci[1] - delta_ci[0]) / 2
    spec_tbl['transit_depth'][wb] = delta
    spec_tbl['transit_depth_err'][wb] = delta_err

    return spec_tbl

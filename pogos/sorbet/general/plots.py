# -*- coding: utf-8 -*-
"""
# sorbet plots.py

# General plotting functions for SORBET

Created on 2024-08-13 at 11:23

@author: cook
"""
import os
from typing import Any, Dict, Literal

import corner
import juliet
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from astropy.table import Table

from aperocore.constants.param_functions import ParamDict
from pogos.core import base
from pogos.core import plots as pogos_plots
from pogos.sorbet.general import science
from sossisse.core import io
from sossisse.core import misc

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'pogos.sorbet.general.plots'
__version__ = base.__version__
__date__ = base.__date__
__authors__ = base.__authors__

# =============================================================================
# Define functions used by plots
# =============================================================================
def save_show_plot(params: ParamDict, outname: str, method: str,
                   title: str, description: str = 'No description',
                   func_name = 'Unknown'):
    """
    Save and show the plot
    :param params: ParamDict, the parameter dictionary of constants
    :param outname: str, the output name for the plot

    :return:
    """
    figure_types = f'SORBET.PLOTS.FIGURE_TYPES'
    plot_path = f'SORBET.{method}.PLOT_PATH'
    plot_show = f'SORBET.PLOTS.SHOW'

    pogos_plots.save_show_plot(params, outname, figure_types, plot_path,
                               plot_show, title, description, func_name)


def plot_corner(params: ParamDict, dataset: juliet.load, results: juliet.fit,
                method: Literal['WLCA', 'SLCA'],
                bin_params: Dict[str, Any] = None):
    """
    Plot the posterior distributions of the fitted parameters (corner plot)

    :param params: ParamDict, the parameter dictionary of constants
    :param dataset: juliet.load, the juliet dataset
    :param results: juliet.fit, the juliet fit results

    return: None
    """
    # set function name
    func_name = f'{__NAME__}.plot_corner()'
    # -------------------------------------------------------------------------
    # set title
    title = 'Posterior distributions of fitted parameters'
    description = ('Corner plot of the posterior distributions of the '
                   'fitted parameters')
    if bin_params is not None:
        title += ' ({SUFFIX})'.format(**bin_params)
        description += ('\n channel={CHANNEL} bin={BIN} '
                        'wave={WAVE_BIN_LOW}-{WAVE_BIN_HIGH}um'
                        ).format(**bin_params)
    # -------------------------------------------------------------------------
    # labels and list of fitted parameters
    juliet_params = []
    for key in dataset.priors.keys():
        if dataset.priors[key]['distribution'] != 'fixed':
            juliet_params.append(key)
    # get the samples
    # loop from the juliet tutorial
    first_time = True
    for i in range(len(juliet_params)):
        if first_time:
            posterior_data = results.posteriors['posterior_samples'][juliet_params[i]]
            first_time = False
        else:
            posterior_data  = np.vstack((posterior_data, 
                            results.posteriors['posterior_samples'][juliet_params[i]]))
    posterior_data = posterior_data.T
    # produce the corner plot
    corner.corner(posterior_data, labels=juliet_params, bins=40, 
                  show_titles=True, title_fmt='.3f', quantiles=[0.16, 0.5, 0.84],
                  title_kwargs={'fontsize':14}, hist_kwargs={"linewidth":3},
                  plot_datapoints=False, smooth=1., levels=(0.393,0.865,0.989))
    # -------------------------------------------------------------------------
    # get tag
    tag = 'corner_plot'
    if bin_params is not None:
        tag += '_{SUFFIX}'.format(**bin_params)
    # save and show the plot
    save_show_plot(params, tag, method, title, description, func_name)


def plot_transit(params: ParamDict, dataset: juliet.load, results: juliet.fit,
                 method: Literal['WLCA', 'SLCA'],
                 bin_params: Dict[str, Any] = None):
    """
    Plot the transit photometry and best-fit transit model

    :param params: ParamDict, the parameter dictionary of constants
    :param dataset: juliet.load, the juliet dataset
    :param results: juliet.fit, the juliet fit results

    return: None
    """
    # set function name
    func_name = f'{__NAME__}.plot_transit()'
    # -------------------------------------------------------------------------
    # set title
    title = 'Transit fit to the light curve'
    description = ('Plot showing the transit fit to the light curve, '
                   'including the data, best-fit model, and residuals')

    if bin_params is not None:
        title += ' ({SUFFIX})'.format(**bin_params)
        description += ('\n channel={CHANNEL} bin={BIN} '
                        'wave={WAVE_BIN_LOW}-{WAVE_BIN_HIGH}um'
                        ).format(**bin_params)
    # -------------------------------------------------------------------------
    # select instrumental mode
    inst_mode = params['GLOBAL.INSTRUMENTMODE']
    # load best-fit model components
    components = science.load_transit_model(params, method=method)
    # check if lm was indeed fitted (by default juliet reports a lm of zeros)
    if np.array_equal(components['lm'], 
                      np.zeros(len(dataset.times_lc[inst_mode]))):
        del components['lm']
    # components to show
    comps = ['transit', 'lm', 'gp', 'full_model']
    comps_offset = [0, 1, 1, 0]
    comps_colors = ['r', 'b', 'darkorange', 'k']
    # extract period and time of mid-transit
    if dataset.priors['P_p1']['distribution'] == 'fixed':
        per = dataset.priors['P_p1']['hyperparameters']
    else:
        per = np.median(results.posteriors['posterior_samples']['P_p1'])
    if dataset.priors['t0_p1']['distribution'] == 'fixed':
        t0 = dataset.priors['t0_p1']['hyperparameters']
    else:
        t0 = np.median(results.posteriors['posterior_samples']['t0_p1'])
    # if secondary eclipse
    if 't_secondary_p1' in dataset.priors:
        if dataset.priors['t_secondary_p1']['distribution'] == 'fixed':
            t0 = dataset.priors['t_secondary_p1']['hyperparameters']
        else:
            t0 = np.median(results.posteriors['posterior_samples']['t_secondary_p1'])
    # extract extra white noise
    if results.posteriors['posterior_samples'][f'sigma_w_{inst_mode}'] is not None:
        jitter = np.median(results.posteriors['posterior_samples'][f'sigma_w_{inst_mode}'])
    else:
        jitter = 0
    # get phases
    phases = juliet.get_phases(dataset.times_lc[inst_mode], per, t0)
    idx = np.argsort(phases)

    # plot the phase-folded transit
    fig, frames = plt.subplots(2, 1, 
                    figsize=(8,8), gridspec_kw={'height_ratios': [3, 1]})
    # plot the light curve and transit model
    frames[0].errorbar(phases * 24 * per, 
                       dataset.data_lc[inst_mode], 
                       yerr=np.sqrt(dataset.errors_lc[inst_mode]**2 + (jitter/1e6)**2), 
                       linestyle='none', 
                       marker='o', 
                       ms=2.5, 
                       mfc='silver', 
                       mec='cadetblue', 
                       ecolor='silver', 
                       zorder=1)
    # plot the components
    for i in range(len(comps)):
        if comps[i] in components.keys():
            if comps_offset[i] == 0:
                frames[0].plot(phases[idx] * 24 * per, 
                               components[comps[i]][idx],
                               color=comps_colors[i],
                               zorder=3, 
                               label=comps[i])
            else:
                frames[0].plot(phases[idx] * 24 * per, 
                               components[comps[i]][idx] + comps_offset[i],
                               color=comps_colors[i],
                               zorder=3, 
                               label=comps[i])
    frames[0].set_ylabel('Relative flux', fontsize = 14)
    frames[0].set_xlim([np.amin(phases * 24 * per), np.amax(phases * 24 * per)])
    frames[0].minorticks_on()
    frames[0].tick_params(axis="both", labelsize=14, direction = 'in', length = 5)
    frames[0].tick_params(axis="both", which = 'minor', direction = 'in', length = 3)
    frames[0].yaxis.set_ticks_position('both')
    frames[0].xaxis.set_ticks_position('both')
    frames[0].set_xticklabels([])
    frames[0].legend(loc='best', fontsize = 12)
    # plot the residuals
    res = (dataset.data_lc[inst_mode] - components['full_model']) * 1e6
    res_err = np.sqrt(dataset.errors_lc[inst_mode]**2 + (jitter/1e6)**2) * 1e6
    frames[1].errorbar(phases * 24 * per, 
                      res, 
                      yerr=res_err,
                      linestyle='none', 
                      marker='o', 
                      ms=2.5, 
                      mfc='silver', 
                      mec='cadetblue', 
                      ecolor='silver', 
                      zorder=1)
    p16_84 = np.nanpercentile(res, [16, 84])
    rms_res = (p16_84[1] - p16_84[0]) / 2.0
    frames[1].text(0.97, 0.85, f'RMS = {rms_res:.0f} ppm', fontsize=12, ha='right',
                   fontweight='bold', transform=frames[1].transAxes)
    frames[1].axhline(y=0, linestyle='--', color='k', zorder=3)
    frames[1].set_xlabel('Time from mid-transit (hours)', fontsize = 14)
    frames[1].set_ylabel(r'$O - C$ (ppm)', fontsize = 14)
    frames[1].set_xlim([np.amin(phases * 24 * per), np.amax(phases * 24 * per)])
    frames[1].minorticks_on()
    frames[1].tick_params(axis="both", labelsize=14, direction = 'in', length = 5)
    frames[1].tick_params(axis="both", which = 'minor', direction = 'in', length = 3)
    frames[1].yaxis.set_ticks_position('both')
    frames[1].xaxis.set_ticks_position('both')
    

    # -------------------------------------------------------------------------
    # force a tight layout
    plt.tight_layout()
    # -------------------------------------------------------------------------
    # get tag
    tag = 'transit_fit'
    if bin_params is not None:
        tag += '_{SUFFIX}'.format(**bin_params)
    # save and show the plot
    save_show_plot(params, tag, method, title, description, func_name)


def plot_outlier(params: ParamDict, data_table: Table,
                 medfilt_model: np.ndarray, outlier_mask: np.ndarray,
                 method: Literal['WLCA', 'SLCA'],
                 bin_params: Dict[str, Any] = None):
    """
    Plot the outlier removal diagnostic plot
    :param params: ParamDict, the parameter dictionary of constants
    """
    # set function name
    func_name = f'{__NAME__}.plot_outlier()'
    # set title
    title = 'Outlier removal diagnostic plot'
    description = ('Diagnostic plot showing the outlier removal '
                   'from the light curve.')
    if bin_params is not None:
        title += ' ({SUFFIX})'.format(**bin_params)
        description += ('\n channel={CHANNEL} bin={BIN} '
                        'wave={WAVE_BIN_LOW}-{WAVE_BIN_HIGH}um'
                        ).format(**bin_params)
    # get bjd and flux
    bjd = np.array(data_table['Time'])
    flux = np.array(data_table['RelFlux'])
    # -------------------------------------------------------------------------
    # plot the outlier removal
    fig, frame = plt.subplots(figsize=(8, 6))
    # plot the light curve
    frame.scatter(bjd[~outlier_mask], flux[~outlier_mask],
                  marker='o', s=5, c='k', label='Data')
    frame.scatter(bjd[outlier_mask], flux[outlier_mask],
                  marker='o', s=15, c='r', label='Outliers')
    frame.plot(bjd, medfilt_model,
               color='r', alpha=0.5, label='Medfilt model')
    # set the labels
    frame.set_xlabel('Time (BJD)', fontsize=16)
    frame.set_ylabel('Relative flux', fontsize=16)
    # set the ticks
    frame.minorticks_on()
    frame.tick_params(axis="both", labelsize=12, direction='in', length=5)
    frame.tick_params(axis="both", which='minor', direction='in', length=3)
    frame.yaxis.set_ticks_position('both')
    frame.xaxis.set_ticks_position('both')
    # set the legend
    frame.legend(loc='best', fontsize=12)
    # -------------------------------------------------------------------------
    # force a tight layout
    plt.tight_layout()
    # -------------------------------------------------------------------------
    # get tag
    tag = 'outlier_removal'
    if bin_params is not None:
        tag += '_{SUFFIX}'.format(**bin_params)
    # save and show the plot
    save_show_plot(params, tag, method, title, description, func_name)


def plot_transmission_spectrum(params: ParamDict,
                               method: Literal['WLCA', 'SLCA'],
                               suffix: str = None):
    """
    Plot the transmission spectrum from the SLCA
    :param params: ParamDict, the parameter dictionary of constants
    :return: None
    """
    # set function name
    func_name = f'{__NAME__}.plot_transmission_spectrum()'
    # set title
    title = 'Transmission Spectrum'
    description = 'Plot showing the transmission spectrum from the SLCA'
    # -------------------------------------------------------------------------
    # get slca parameters
    slcta_params = params.get('SORBET.SLCA')
    # load the transmission spectrum
    filename = slcta_params['TRANSMISSION_SPECTRUM_FILE']
    # check if the file exists
    if not os.path.isfile(filename):
        msg = f'Transmission spectrum file does not exist: {filename}'
        misc.printc(msg, msg_type='error')
        return
    spec_tbl = io.load_table(filename)

    # plot the transmission spectrum
    fig, frame = plt.subplots(figsize = (12,5))

    # construct label
    label = '($R \sim$ {0})'.format(slcta_params['RESOLUTION_BIN'])
    # remove bins that did not compute
    good = spec_tbl['transit_depth'] > 0
    frame.errorbar(spec_tbl['wave'][good],
                    spec_tbl['transit_depth'][good]*1e6, 
                    xerr=spec_tbl['wave_err'][good], 
                    yerr=spec_tbl['transit_depth_err'][good]*1e6, 
                    marker='o', linestyle='none', ms=5, 
                    mec='k', ecolor='k', capsize=2, zorder = 4, 
                    label=label)

    frame.set_xscale('log')
    frame.set_xlabel(r'Wavelength ($\mu$m)', fontsize = 16)
    frame.set_ylabel(r'Transit Depth (ppm)', fontsize = 16)
    frame.minorticks_on()
    frame.tick_params(axis="both", labelsize=12, direction = 'in', length = 5)
    frame.tick_params(axis="both", which = 'minor', direction = 'in', length = 3)
    frame.yaxis.set_ticks_position('both')
    frame.xaxis.set_ticks_position('both')
    frame.get_xaxis().set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
    frame.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
    frame.get_xaxis().set_minor_formatter(matplotlib.ticker.NullFormatter())

    plt.legend(loc='best', fontsize = 12)
    plt.tight_layout()
    # -------------------------------------------------------------------------
    # get tag
    tag = 'transmission_spectrum'
    if suffix is not None:
        tag += f'_{suffix}'
    # save and show the plot
    save_show_plot(params, tag, method, title, description, func_name)

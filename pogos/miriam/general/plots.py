# -*- coding: utf-8 -*-
"""
# sorbet plots.py

# General plotting functions for SORBET

Created on 2024-08-13 at 11:23

@author: cook
"""
import os
from typing import Literal
from astropy.table import Table

import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import astropy.table
from pogos.core import base
from aperocore.constants.param_functions import ParamDict
from sossisse.core import misc
from sossisse.core import io
from pogos.sorbet.general import science
from pogos.core import plots as pogos_plots


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
# TODO same function in sossisse.general.plots using different paths
def save_show_plot(params: ParamDict, outname: str, title: str,
                   description: str = 'No description',
                   func_name='Unknown'):
    """
    Save and show the plot
    :param params: ParamDict, the parameter dictionary of constants
    :param outname: str, the output name for the plot

    :return:
    """
    figure_types = f'MIRIAM.PLOTS.FIGURE_TYPES'
    plot_path = f'MIRIAM.PATHS.PLOT_PATH'
    plot_show = f'MIRIAM.PLOTS.SHOW'

    pogos_plots.save_show_plot(params, outname, figure_types, plot_path,
                               plot_show, title, description, func_name)


def plot_fit_params(params: ParamDict, psf: np.ndarray,
                    gradx: np.ndarray, grady: np.ndarray,
                    psf2ortho: np.ndarray):
    # set function name
    func_name = f'{__NAME__}.plot_fit_params'
    # -------------------------------------------------------------------------
    # set title and description
    title = 'MIRIAM Fit Parameters'
    description = ('Plot of the MIRIAM fit parameters used in the PSF fitting. '
                   'M is the PSF model, D is the orthogonalized PSF, '
                   'and the gradients are the derivatives of M with respect to '
                   'x and y.')
    # -------------------------------------------------------------------------
    # list the images
    images = [psf, psf2ortho, gradx, grady]
    ftitles = [r'$M_{i,j}$',
               r'$D_{i,j}$',
               r'$\frac{\partial M_{i,j}}{\partial x}$',
               r'$\frac{\partial M_{i,j}}{\partial y}$']
    # -------------------------------------------------------------------------
    fig, frames = plt.subplots(2, 2, figsize=(16, 16))
    # loop around frames
    for frame, image, ftitle in zip(frames.flat, images, ftitles):
        # get the max value for the image
        maxval = np.nanmax(np.abs(image))
        # plot the image for this frame
        frame.imshow(image / maxval, origin='lower', cmap='viridis',
                     vmin=-1, vmax=1)
        # turn off x and y ticks
        frame.set_xticks([])
        frame.set_yticks([])
        # add title to the figure
        frame.text(0.04, 0.96, ftitle,
                   transform=frame.transAxes,
                   fontsize=24,
                   va='top', ha='left',
                   bbox=dict(facecolor='wheat', edgecolor='none',
                             boxstyle='round,pad=0.3'))
    # Make spacing much tighter
    plt.subplots_adjust(wspace=0.02, hspace=0.02)
    plt.tight_layout()
    # -------------------------------------------------------------------------
    # save and show the plot
    save_show_plot(params, 'fit_params', title, description, func_name)

def plot_correlations(params: ParamDict, ptbl: Table, d2flag: bool):
    # set function name
    func_name = f'{__NAME__}.plot_correlations'
    plot_pedestal = params.rget('MIRIAM.PLOTS.CORR_PLOT_PEDESTAL',
                                required=True, func=func_name)
    # set title and description
    title = 'MIRIAM Fit Parameter Correlations'
    description = ('Plot of the MIRIAM fit parameter correlations used in the '
                   'PSF fitting. Showing the time series of the fit parameters '
                   'used to correct the photometry for instrumental '
                   'systematics.')
    # -------------------------------------------------------------------------
    # work out the segments
    gaps = []
    for iframe in range(1, len(ptbl)):
        prev_frame = ptbl['SEGMENT'][iframe - 1]
        this_frame = ptbl['SEGMENT'][iframe]
        if this_frame != prev_frame:
            gaps.append(iframe)
    # -------------------------------------------------------------------------
    if plot_pedestal:
        fig, frames = plt.subplots(4, 1, figsize=(16, 16), sharex='all')
    else:
        fig, frames = plt.subplots(3, 1, figsize=(16, 12))

    # -------------------------------------------------------------------------
    # plot the amps
    frames[0].errorbar(ptbl['int_mid_BJD_TDB'], ptbl['amps'],
                       yerr=ptbl['amps_err'], alpha=0.3, marker='.',
                       ls='None')
    frames[0].set(xlabel='Time [BJD]', ylabel='Normalized flux')
    frames[0].grid(color='gray', ls='--', lw=0.5)
    # plot the segments
    for gap in gaps:
        frames[0].axvline(ptbl['int_mid_BJD_TDB'][gap], color='pink',
                          ls='-', lw=1, ymin=0.0, ymax=1.0)
    # --------------------------------------------------------------------------
    # plot dx and dy
    frames[1].errorbar(ptbl['int_mid_BJD_TDB'], ptbl['dxs'],
                       yerr=ptbl['dxs_err'], alpha=0.3, marker='.',
                       label=r'$b_x$', ls='None')
    frames[1].errorbar(ptbl['int_mid_BJD_TDB'], ptbl['dys'],
                       yerr=ptbl['dys_err'], alpha=0.3, marker='.',
                       label=r'$b_y$', ls='None')
    frames[1].legend(loc=0)
    frames[1].set(xlabel='Time [BJD]', ylabel='Position offset [pixels]')
    frames[1].grid(color='gray', ls='--', lw=0.5)
    # --------------------------------------------------------------------------
    # plot d2s
    frames[2].errorbar(ptbl['int_mid_BJD_TDB'], ptbl['d2s'],
                       yerr=ptbl['d2s_err'], alpha=0.3, marker='.',
                       ls='None')
    frames[2].set(xlabel='Time [BJD]', ylabel=r'Shape parameter ($c_\perp$)')
    frames[2].grid(color='gray', ls='--', lw=0.5)
    # --------------------------------------------------------------------------
    # plot pedestal if required
    if plot_pedestal:
        frames[3].plot(ptbl['int_mid_BJD_TDB'], ptbl['pedestal_mean'],
                       alpha=0.3, marker='.', ls='None', label='Pedestal Mean')
        frames[3].plot(ptbl['int_mid_BJD_TDB'], ptbl['pedestal_psf'],
                       alpha=0.3, marker='.', ls='None', label='Pedestal PSF')
        frames[3].set(xlabel='Time [BJD]', ylabel='Pedestal level [ADU]')
        frames[3].grid(color='gray', ls='--', lw=0.5)
        frames[3].legend(loc=0)
        frames[3].set(xlabel='Time [BJD]', ylabel='Pedestal')
    # --------------------------------------------------------------------------
    plt.suptitle(title)
    plt.tight_layout()
    # -------------------------------------------------------------------------
    # set filename
    tag = f'correlations_d2flag_{d2flag}'
    # -------------------------------------------------------------------------
    # save and show the plot
    save_show_plot(params, tag, title, description, func_name)


def plot_photometry(params: ParamDict, ptbl0: Table, ptbl1: Table):
    # set function name
    func_name = f'{__NAME__}.plot_photometry'
    # set title and description
    title = 'MIRIAM Photometric Comparison'
    description = ('Plot comparing the photometric measurements obtained '
                   'using D2 Flag True and D2 Flag False during the '
                   'photometric extraction process.')
    # -------------------------------------------------------------------------
    fig, frames = plt.subplots(nrows=2, ncols=1, figsize=(10, 8))
    # -------------------------------------------------------------------------
    # plot amps
    frames[0].plot(ptbl0['int_mid_BJD_TDB'], ptbl0['amps'], marker='.',
                   ls='None', label='D2 Flag True')
    frames[0].plot(ptbl1['int_mid_BJD_TDB'], ptbl1['amps'], marker='.',
                   ls='None', label='D2 Flag False')
    frames[0].set(xlabel='Time [BJD]', ylabel='Flux Amplitude',
                  title='Photometric measurements')
    frames[0].legend(loc=0)
    # -------------------------------------------------------------------------
    # plot residuals
    residuals = ptbl0['amps'] = ptbl1['amps']
    frames[1].plot(ptbl0['int_mid_BJD_TDB'], residuals, marker='.',
                   color='k', ls='None')
    frames[1].set(xlabel='Time [BJD]', ylabel='Flux Amplitude Residuals',
                  title='Residuals between D2 Flag True and False')
    # -------------------------------------------------------------------------
    # set title
    plt.suptitle(title)
    # filename
    tag = f'photometry'
    # -------------------------------------------------------------------------
    # save and show the plot
    save_show_plot(params, tag, title, description, func_name)


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

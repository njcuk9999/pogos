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
    figure_types = params[f'MIRIAM.PLOTS.FIGURE_TYPES']
    plot_path = params[f'MIRIAM.PATHS.PLOT_PATH']
    plot_show = params[f'MIRIAM.PLOTS.SHOW']

    pogos_plots.save_show_plot(params, outname, figure_types, plot_path,
                               plot_show, title, description, func_name)


def plot_fit_params(params, psf, psf2ortho, gradx, grady):
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
        # plot the image for this frame
        frame.imshow(image, origin='lower', cmap='viridis', vmin=-1, vmax=1)
        # turn off x and y ticks
        frame.set_xticks([])
        frame.set_yticks([])
        # add title to the figure
        frame.text(0.04, 0.96, ftitle,
                   transform=a.transAxes,
                   fontsize=24,
                   va='top', ha='left',
                   bbox=dict(facecolor='wheat', edgecolor='none',
                             boxstyle='round,pad=0.3'))
    # Make spacing much tighter
    plt.subplots_adjust(wspace=0.02, hspace=0.02)
    # -------------------------------------------------------------------------
    # save and show the plot
    save_show_plot(params, 'fit_params', title, description, func_name)

def plot_correlations(params: ParamDict, ptbl: Table, d2flag: bool):
    # set function name
    func_name = f'{__NAME__}.plot_correlations'
    # set title and description

    # -------------------------------------------------------------------------
    # work out the segments
    # TODO: Got to here 2025-10-23 15:10


    # -------------------------------------------------------------------------
    # save and show the plot
    save_show_plot(params, 'fit_params', title, description, func_name)


def plot_photometry(params: ParamDict, ptbl0: Table, ptbl1: Table):
    # set function name
    func_name = f'{__NAME__}.plot_photometry'
    # set title and description

    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # save and show the plot
    save_show_plot(params, 'fit_params', title, description, func_name)

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

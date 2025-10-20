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


def plot_correlations(params: ParamDict, ptbl: Table, d2flag: bool):
    pass


def plot_photometry(params: ParamDict, ptbl0: Table, ptbl1: Table):
    pass

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

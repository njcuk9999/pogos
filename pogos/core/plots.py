# -*- coding: utf-8 -*-
"""
# sorbet plots.py

# General plotting functions for SORBET

Created on 2024-08-13 at 11:23

@author: cook
"""
import os
import time

import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import astropy.table
from pogos.core import base
from aperocore.constants.param_functions import ParamDict
from sossisse.core import misc
from sossisse.core import io
from pogos.sorbet.general import science
from aperocore.base import base as aperobase



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
# TODO: same function in sossisse.general.plots -> move to aperocore
def plot_file(params: ParamDict, outname: str, plot_path, title,
              description: str = 'No description',
              func_name = 'Unknown'):
    # get plot file
    plotfile = os.path.join(params[plot_path], 'plots.yaml')
    # read yaml file
    if os.path.exists(plotfile):
        blocks = aperobase.load_yaml(plotfile)
    else:
        blocks = dict()
    # ------------------------------------------------------------------------
    # empty this block
    blocks[outname] = dict()
    # prepare yaml block
    blocks[outname]['title'] = title
    blocks[outname]['description'] = description
    blocks[outname]['time'] = float(time.time())
    blocks[outname]['func'] = func_name
    # ------------------------------------------------------------------------
    # save the yaml file
    aperobase.write_yaml(blocks, plotfile)


# TODO: same function in sossisse.general.plots -> move to aperocore
def save_show_plot(params: ParamDict, outname: str, figure_types: str,
                   plot_path: str, plot_show: str,
                   title: str = '', description: str = 'No description',
                   func_name = 'Unknown'):
    """
    Save and show the plot
    :param params: dict, the parameters for the instrument
    :param outname: str, the output name for the plot

    :return:
    """
    # save to yaml file (for html writing)
    plot_file(params, outname, plot_path, title, description, func_name)
    # loop around figure types
    for figtype in params[figure_types]:
        # construct the basename with extension
        basename = f'{outname}.{figtype}'
        # contstruct the full path
        abspath = os.path.join(params[plot_path], basename)
        # say that we are plotting graph
        msg = f'Plotting graph: {basename}'
        misc.printc(msg, msg_type='info')
        # save the figure
        plt.savefig(abspath)
    # if we want to show the plot do it now
    if params[plot_show]:
        # deal with description
        if len(description) > 0:
            misc.printc(f'PLOT: {title} \n\n{description}', 'plot')
        # show the plot
        plt.show(block=True)
    # finally close the plot
    plt.close()


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

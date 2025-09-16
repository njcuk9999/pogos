#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

Transit fit of the WLC

Created on 2024-12-02

@author: CharlesCadieux
"""

import numpy as np
from aperocore.constants.param_functions import ParamDict
from sossisse.core import misc
from pogos import sorbet
from pogos.core import base
from pogos.sorbet.general import plots

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'pogos.sorbet.recipes.run_sorbet_wlcta'
__version__ = base.__version__
__date__ = base.__date__
__authors__ = base.__authors__


# =============================================================================
# Define functions
# =============================================================================
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
    sorbet.prepare_output_directory(params, method='WLCTA')
    # load the dataset
    dataset = sorbet.load_wlc(params)
    # find outliers
    medfilt_model, outlier_mask = sorbet.find_outliers(params,
                                                       dataset,
                                                       method='WLCTA')
    # diagnostic plot for outlier removal
    plots.plot_outlier(params, dataset, medfilt_model, outlier_mask,
                       method='WLCTA')
    # -------------------------------------------------------------------------
    # prepare the dataset for juliet
    dataset = sorbet.prepare_dataset(params, dataset, method='WLCTA',
                                     outlier_mask=outlier_mask)
    # -------------------------------------------------------------------------
    # fit the dataset with juliet/batman
    results = sorbet.fit_transit(params, dataset, method='WLCTA')
    # -------------------------------------------------------------------------
    # save the model components to disk
    sorbet.save_transit_model(params, results, method='WLCTA')
    # -------------------------------------------------------------------------
    # plot the results (corner plot)
    plots.plot_corner(params, dataset, results, method='WLCTA')
    # -------------------------------------------------------------------------
    # plot the best-fit model
    plots.plot_transit(params, dataset, results, method='WLCTA')
    
    # return params
    return params
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2025-01-31 at 15:04

@author: cook
"""
from pogos.sorbet.core import core
from pogos.sorbet.general import general

# =============================================================================
# Define variables
# =============================================================================

# import to a sub module function
run_sorbet = core.run_sorbet_module

# SORBET.WLCTA
prepare_output_directory = general.prepare_output_directory
load_wlc = general.load_wlc
find_outliers = general.find_outliers
prepare_dataset = general.prepare_dataset
fit_transit = general.fit_transit
save_transit_model = general.save_transit_model
load_transit_model = general.load_transit_model

# SORBET.SLCTA
prepare_output_directory = general.prepare_output_directory
load_slc = general.load_slc
bin_spectrum = general.bin_spectrum
save_transmission_spectrum = general.save_transmission_spectrum
get_model_ld_coeffs = general.get_model_ld_coeffs

# SORBET.TFIT

# SORBET.RV


# =============================================================================
# End of code
# =============================================================================

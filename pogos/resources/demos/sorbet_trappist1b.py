#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2025-03-25 at 09:57

@author: cook
"""
from pogos.constants import constants as pconst
from pogos.constants import sorbet as sconst

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'sorbet_trappist1b.py'

# copy of CDict
Cdict = pconst.CDict.copy(source=__NAME__)
SORBET_Cdict = sconst.SORBET_CDict.copy(source=__NAME__)
# copy sorbet constants into Cdict
Cdict.add_sub_cdict('SORBET', SORBET_Cdict, source=__NAME__)

# =============================================================================
# Define info (must contain "title")
# =============================================================================
INFO = dict()
INFO['title'] = 'JWST.NIRISS.SOSS Trappist 1b transit fit with SORBET'
INFO['object'] = 'Trappist 1b'
INFO['instrument'] = 'JWST.NIRISS.SOSS'
INFO['description'] = 'Extract the transit spectrum of Trappist 1b observed on 2022-07-18'
INFO['date'] = '2025-08-28'
# TODO: Check RUN_TSOVORE, RUN_SOSSISSE, RUN_SORBET
INFO['author'] = 'Charles Cadieux'
INFO['sid'] = 'Trappist1b-SOSS-20250828'
# url for data download
URL = 'https://www.astro.umontreal.ca/~cook/pogo-data/'
# download: key = file, value = local path
DOWNLOAD = dict()
DOWNLOAD['SORBET.WLCTA.INPUT_FILE'] = 'GLOBAL.DATA_PATH'
DOWNLOAD['SORBET.SLCTA.INPUT_FILE'] = 'GLOBAL.DATA_PATH'


# =============================================================================
# global settings (generally don't touch these)
# =============================================================================
cgroup = 'GLOBAL'

# Instrument mode i.e. JWST.NIRISS.SOSS or JWST.NIRISS.PRISM
Cdict.set('INSTRUMENTMODE', group=cgroup, source=__NAME__,
          value=INFO['instrument'])

# =============================================================================
# Switches to turn of major features
# =============================================================================
cgroup = 'RUN'

# Run TSOVORE
Cdict.set('TSOVORE', group=cgroup, source=__NAME__,
          value=False)

# Run SOSSISSE
Cdict.set('SOSSISSE', group=cgroup, source=__NAME__,
          value=False)

# Run MIRIAM
Cdict.set('MIRIAM', group=cgroup, source=__NAME__,
          value=False)

# Run SORBET
Cdict.set('SORBET', group=cgroup, source=__NAME__,
          value=True)

# =============================================================================
# General SORBET settings
# =============================================================================
cgroup = 'SORBET.GENERAL'
# The SID to use
Cdict.set('SID', group=cgroup, source=__NAME__, value=INFO['sid'])

# =============================================================================
# Switches to turn large parts of the code on/off
# =============================================================================
cgroup = 'SORBET.WLCTA'

# Switch for turning on/off the white light curve transit fit
Cdict.set('RUN', group=cgroup, source=__NAME__,
          value=True)

# =============================================================================
# Definition of inputs related to the data
# =============================================================================
# Path to input file relative to GLOBAL data path defined by the user
Cdict.set('INPUT_FILE', group=cgroup, source=__NAME__,
          value='stability.csv')

# Path to the result folder relative to GLOBAL data path defined by the user
Cdict.set('OUTPUT_PATH', group=cgroup, source=__NAME__,
          value='sorbet_wlcta_fit')

# =============================================================================
# Definition of general inputs SORBET_WLCTA
# =============================================================================
# Prior distributions for the default juliet parameterization
Cdict.set('JULIET_PRIOR_DISTS', group=cgroup, source=__NAME__,
          value=['fixed', 'uniform', 'uniform', 'truncatednormal', 'uniform',
                 'fixed', 'fixed',
                 'uniform', 'uniform',
                 'fixed', 'fixed',
                 'loguniform'])
# Priors for the default juliet parameterization
# Following Lim et al. 2023
Cdict.set('JULIET_PRIOR_VALS', group=cgroup, source=__NAME__,
          value=[1.51087081, [2459779.1, 2459779.3], [0.01, 0.22], [0.095, 0.65, 0.0, 1.0], [10, 30],
                 0.0, 90.0,
                 [0.0, 1.0], [0.0, 1.0],
                 1.0, 0.0,
                 [1, 1000]])
# Fit temporal slope by default
Cdict.set('LINEAR_DETRENDING', group=cgroup, source=__NAME__,
          value='time')

# =============================================================================
# Switches to turn large parts of the code on/off
# =============================================================================
cgroup = 'SORBET.SLCTA'

# Switch for turning on/off the white light curve transit fit
Cdict.set('RUN', group=cgroup, source=__NAME__,
          value=True)

# =============================================================================
# Definition of inputs related to the data
# =============================================================================
# Path to input file relative to GLOBAL data path defined by the user
Cdict.set('INPUT_FILE', group=cgroup, source=__NAME__,
          value=['spectra_ord1.fits'])

# Path to the result folder relative to GLOBAL data path defined by the user
Cdict.set('OUTPUT_PATH', group=cgroup, source=__NAME__,
          value='sorbet_slcta_fit')
# Degrading spectral resolution before fitting
Cdict.set('RESOLUTION_BIN', group=cgroup, source=__NAME__,
          value=20)

# =============================================================================
# Definition of general inputs SORBET_SLCTA
# =============================================================================
# Prior distributions for the default juliet parameterization
Cdict.set('JULIET_PRIOR_DISTS', group=cgroup, source=__NAME__,
          value=['fixed', 'fixed', 'uniform', 'fixed', 'fixed',
                 'fixed', 'fixed',
                 'uniform', 'uniform',
                 'fixed', 'fixed',
                 'loguniform'])
# Priors for the default juliet parameterization
# Following Lim et al. 2023
Cdict.set('JULIET_PRIOR_VALS', group=cgroup, source=__NAME__,
          value=[1.51087081, 2459779.210475, [0.01, 0.22], 0.098, 20.66,
                 0.0, 90.0,
                 [0.0, 1.0], [0.0, 1.0],
                 1.0, 0.0,
                 [1, 1000]])
# Fit temporal slope by default
Cdict.set('LINEAR_DETRENDING', group=cgroup, source=__NAME__,
          value='time')


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

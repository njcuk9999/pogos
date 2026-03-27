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
INFO['title'] = 'JWST.NIRISS.SOSS Trappist 1b transit fit [SORBET]'
INFO['object'] = 'Trappist 1b'
INFO['instrument'] = 'JWST.NIRISS.SOSS'
INFO['description'] = 'Transit spectrum of Trappist 1b observed on 2022-07-18'
INFO['date'] = '2025-08-28'
INFO['author'] = 'Charles Cadieux'
INFO['id'] = 'DEMO_T1b_JWST.NIRISS.SOSS_SORBET_20220718'
INFO['red_steps'] = ['Post-extraction:SORBET.WLCA',
                     'Post-extraction:SORBET.SLCA']
INFO['keywords'] = ['transit']
# url for data download
URL = 'http://206.12.93.77/ari/data/pogos/demos/soss/'
# download: key = file, value = local path
DOWNLOAD = dict()
DOWNLOAD['SORBET.WLCA.INPUT_FILE'] = 'SORBET.WLCA.INPUT_PATH'
DOWNLOAD['SORBET.SLCA.INPUT_FILE'] = 'SORBET.SLCA.INPUT_PATH'


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
# The sub-directory to use for this SORBET run.
# This should be descriptive and unique.
# It should contain no whitespaces or special
# characters other than underscoes
# All sorbet data will be stored in {GLOBAL.DATA_PATH}/sorbet/{SUBDIRECTORY}/
Cdict.set('SUBDIRECTORY', group=cgroup, source=__NAME__, value=INFO['id'])
# Description of the SORBET run e.g. object name, date of observation,
# is it a transit or an eclipse etc.
Cdict.set('DESCRIPTION', group=cgroup, source=__NAME__,
          value=INFO['description'])

# =============================================================================
# Switches to turn large parts of the code on/off
# =============================================================================
cgroup = 'SORBET.WLCA'

# Switch for turning on/off the white light curve transit fit
Cdict.set('RUN', group=cgroup, source=__NAME__,
          value=True)

# =============================================================================
# Definition of inputs related to the data
# =============================================================================
# Path to input file relative to GLOBAL data path defined by the user
Cdict.set('INPUT_FILE', group=cgroup, source=__NAME__,
          value='white_light_curve.fits')

# =============================================================================
# Definition of general inputs SORBET_WLCA
# =============================================================================
# Prior distributions for the default juliet parameterization
jps_values = ['P_p1', 't0_p1', 'p_p1', 'b_p1', 'a_p1',
              'ecc_p1', 'omega_p1',
              'q1_{INST_MODE}', 'q2_{INST_MODE}',
              'mdilution_{INST_MODE}', 'mflux_{INST_MODE}',
              'sigma_w_{INST_MODE}']
Cdict.set('JULIET_PARAMETERS', group=cgroup, source=__NAME__,
          value=jps_values)

# Prior distributions for the default juliet parameterization
jpd_values = dict()
jpd_values['P_p1'] = 'fixed'
jpd_values['t0_p1'] = 'uniform'
jpd_values['p_p1'] = 'uniform'
jpd_values['b_p1'] = 'truncatednormal'
jpd_values['a_p1'] = 'uniform'
jpd_values['ecc_p1'] = 'fixed'
jpd_values['omega_p1'] = 'fixed'
jpd_values['q1_{INST_MODE}'] = 'uniform'
jpd_values['q2_{INST_MODE}'] = 'uniform'
jpd_values['mdilution_{INST_MODE}'] = 'fixed'
jpd_values['mflux_{INST_MODE}'] = 'fixed'
jpd_values['sigma_w_{INST_MODE}'] = 'loguniform'
Cdict.set('JULIET_PRIOR_DISTS', group=cgroup, source=__NAME__,
          value=jpd_values)
# Priors for the default juliet parameterization
# Following Lim et al. 2023
jpv_values = dict()
jpv_values['P_p1'] = 1.51087081
jpv_values['t0_p1'] = [2459779.1, 2459779.3]
jpv_values['p_p1'] = [0.01, 0.22]
jpv_values['b_p1'] = [0.095, 0.65, 0.0, 1.0]
jpv_values['a_p1'] = [10, 30]
jpv_values['ecc_p1'] = 0.0
jpv_values['omega_p1'] = 90.0
jpv_values['q1_{INST_MODE}'] = [0.0, 1.0]
jpv_values['q2_{INST_MODE}'] = [0.0, 1.0]
jpv_values['mdilution_{INST_MODE}'] = 1.0
jpv_values['mflux_{INST_MODE}'] = 0.0
jpv_values['sigma_w_{INST_MODE}'] = [1, 1000]
Cdict.set('JULIET_PRIOR_VALS', group=cgroup, source=__NAME__,
          value=jpv_values)

# Fit temporal slope by default
Cdict.set('LINEAR_DETRENDING', group=cgroup, source=__NAME__,
          value='time')

# =============================================================================
# Switches to turn large parts of the code on/off
# =============================================================================
cgroup = 'SORBET.SLCA'

# Switch for turning on/off the white light curve transit fit
Cdict.set('RUN', group=cgroup, source=__NAME__,
          value=True)

# =============================================================================
# Definition of inputs related to the data
# =============================================================================
# Path to input file relative to GLOBAL data path defined by the user
Cdict.set('INPUT_FILE', group=cgroup, source=__NAME__,
          value=['spectroscopy_light_curves.fits'])

# Trace orders, must be a list the same length as INPUT_FILES
#     (Set each item to 1 if there is only one order) otherwise set each item
#     to the order number
Cdict.set('TRACE_ORDERS', group=cgroup, source=__NAME__,
          value=[1])

# Degrading spectral resolution before fitting
Cdict.set('RESOLUTION_BIN', group=cgroup, source=__NAME__,
          value=20)

# =============================================================================
# Definition of general inputs SORBET_SLCA
# =============================================================================
# Prior distributions for the default juliet parameterization
jps_values = ['P_p1', 't0_p1', 'p_p1', 'b_p1', 'a_p1',
              'ecc_p1', 'omega_p1',
              'q1_{INST_MODE}', 'q2_{INST_MODE}',
              'mdilution_{INST_MODE}', 'mflux_{INST_MODE}',
              'sigma_w_{INST_MODE}']
Cdict.set('JULIET_PARAMETERS', group=cgroup, source=__NAME__,
          value=jps_values)

# Prior distributions for the default juliet parameterization
jpd_values = dict()
jpd_values['P_p1'] = 'fixed'
jpd_values['t0_p1'] = 'fixed'
jpd_values['p_p1'] = 'uniform'
jpd_values['b_p1'] = 'fixed'
jpd_values['a_p1'] = 'fixed'
jpd_values['ecc_p1'] = 'fixed'
jpd_values['omega_p1'] = 'fixed'
jpd_values['q1_{INST_MODE}'] = 'uniform'
jpd_values['q2_{INST_MODE}'] = 'uniform'
jpd_values['mdilution_{INST_MODE}'] = 'fixed'
jpd_values['mflux_{INST_MODE}'] = 'fixed'
jpd_values['sigma_w_{INST_MODE}'] = 'loguniform'
Cdict.set('JULIET_PRIOR_DISTS', group=cgroup, source=__NAME__,
          value=jpd_values)
# Priors for the default juliet parameterization
# Following Lim et al. 2023
jpv_values = dict()
jpv_values['P_p1'] = 1.51087081
jpv_values['t0_p1'] = 2459779.210475
jpv_values['p_p1'] = [0.01, 0.22]
jpv_values['b_p1'] = 0.098
jpv_values['a_p1'] = 20.66
jpv_values['ecc_p1'] = 0.0
jpv_values['omega_p1'] = 90.0
jpv_values['q1_{INST_MODE}'] = [0.0, 1.0]
jpv_values['q2_{INST_MODE}'] = [0.0, 1.0]
jpv_values['mdilution_{INST_MODE}'] = 1.0
jpv_values['mflux_{INST_MODE}'] = 0.0
jpv_values['sigma_w_{INST_MODE}'] = [1, 1000]
Cdict.set('JULIET_PRIOR_VALS', group=cgroup, source=__NAME__,
          value=jpv_values)

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

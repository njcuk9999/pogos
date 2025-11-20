#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2025-03-25 at 09:57

@author: cook
"""
from sossisse.core import constants as sconst
from pogos.constants import constants as pconst
from pogos.constants import sorbet as sbconst

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'soss_trappist1b.py'

# copy of CDict
Cdict = pconst.CDict.copy(source=__NAME__)
SOSSSISE_Cdict = sconst.CDict.copy(source=__NAME__)
SORBET_Cdict = sbconst.SORBET_CDict.copy(source=__NAME__)
# copy sossisse constants into Cdict
Cdict.add_sub_cdict('SOSSISSE', SOSSSISE_Cdict, source=__NAME__)
Cdict.add_sub_cdict('SORBET', SORBET_Cdict, source=__NAME__)

# =============================================================================
# Define info (must contain "title")
# =============================================================================
INFO = dict()
INFO['title'] = 'JWST.NIRISS.SOSS Trappist 1b transit [SOSSISSE + SORBET]'
INFO['object'] = 'Trappist 1b'
INFO['instrument'] = 'JWST.NIRISS.SOSS'
INFO['description'] = 'Trappist 1b transit observed on 2022-07-18'
INFO['date'] = '2025-03-25'
INFO['author'] = 'Etienne Artigau + Charles Cadieux'
INFO['red_steps'] = ['Extraction:SOSSISSE', 'Post-extraction:SORBET.WLCA',
                     'Post-extraction:SORBET.SLCTA']
INFO['sid'] = 'DEMO-Trappist1b-SOSS-20250718'
INFO['sbid'] = 'DEMO-Trappist1b-SOSS-20250718'
# url for data download
URL = 'http://206.12.93.77/ari/data/pogos/demos/soss/'
# download: key = file, value = local path
DOWNLOAD = dict()
DOWNLOAD['SOSSISSE.GENERAL.FILES'] = 'SOSSISSE.PATHS.RAWPATH'
DOWNLOAD['SOSSISSE.GENERAL.BKGFILE'] = 'SOSSISSE.PATHS.CALIBPATH'
DOWNLOAD['SOSSISSE.GENERAL.FLATFILE'] = 'SOSSISSE.PATHS.CALIBPATH'
DOWNLOAD['SOSSISSE.GENERAL.POS_FILE'] = 'SOSSISSE.PATHS.CALIBPATH'

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
          value=True)

# Run MIRIAM
Cdict.set('MIRIAM', group=cgroup, source=__NAME__,
          value=False)

# Run SORBET
Cdict.set('SORBET', group=cgroup, source=__NAME__,
          value=True)

# =============================================================================
# Switches to turn large parts of the code on/off
# =============================================================================
cgroup = 'SOSSISSE.RUN'

# Switch for turning on/off the linear reconstruction step
Cdict.set('LINEAR_RECON', group=cgroup, source=__NAME__,
          value=True)

# Switch for turning on/off the spectral extraction
Cdict.set('SPECTRAL_EXTRACTION', group=cgroup, source=__NAME__,
          value=True)

# =============================================================================
# Definition of inputs related to the data
# =============================================================================
cgroup = 'SOSSISSE.INPUTS'

# The sub-directory to use for this SOSSISSE run.
# This should be descriptive and unique.
# It should contain no whitespaces or special
# characters other than underscoes
# All sossisse data will be stored in {GLOBAL.DATA_PATH}/sossisse/{SUBDIRECTORY}/
Cdict.set('SUBDIRECTORY', group=cgroup, source=__NAME__, value=INFO['sid'])

# Description of the SOSSISSE run e.g. object name, date of observation,
# is it a transit or an eclipse etc.
Cdict.set('DESCRIPTION', group=cgroup, source=__NAME__,
          value=INFO['description'])

# Instrument mode
Cdict.set('INSTRUMENTMODE', group=cgroup, source=__NAME__,
          value=INFO['instrument'])

# Name of the object (must match the object directory name)
Cdict.set('OBJECTNAME', group=cgroup, source=__NAME__,
          value='Trappist1b')


# =============================================================================
# Definition of general inputs
# =============================================================================
cgroup = 'SOSSISSE.GENERAL'

# List of files to be processed in form:
# FILES:
#  - file1
#  - file2
#  - file3
Cdict.set('FILES', group=cgroup, source=__NAME__,
          value=['jw02589001001_04101_00001-seg001_nis_rateints.fits',
                 'jw02589001001_04101_00001-seg002_nis_rateints.fits'])

# background file --> leave as None if the is no background available for
#    the mode - if empty DO_BACKGROUND is set to False regardless of the value
Cdict.set('BKGFILE', group=cgroup, source=__NAME__,
          value='model_background256.fits')

# do background correction - must have BKGFILE defined to do this
Cdict.set('DO_BACKGROUND', value=True, group=cgroup, source=__NAME__)

# flat field file --> leave as '' if there is no flat field available
#     for the mode
Cdict.set('FLATFILE', group=cgroup, source=__NAME__,
          value='jwst_niriss_flat_0275.fits')

# trace position file
Cdict.set('POS_FILE', group=cgroup, source=__NAME__,
          value='SOSS_ref_trace_table_SUBSTRIP256.fits')

# Wavelength calibration file
Cdict.set('WAVE_FILE', group=cgroup, source=__NAME__,
          value=None)

# Wavelength calibration file type
Cdict.set('WAVE_FILE_TYPE', group=cgroup, source=__NAME__,
          value=None)

# Define which orders to use e.g.
# - 1
# - 2
Cdict.set('TRACE_ORDERS', group=cgroup, source=__NAME__,
          value=[1,2])

# =============================================================================
# Definition of inputs related to the position within data cube timeseries
# =============================================================================
cgroup = 'SOSSISSE.WLC.INPUTS'

# Integrations used to construct a model PSF.
#     This should be a list of [start, end] lists
#     These should be out-of-transit (if any) and without flares.
#     If you observed constantly a variable object (brown dwarf, phase curve),
#     you should enter the first to last as frame IDs, except significant
#     flares.
#     Note that on a first pass of data reduction, you may not know the
#     optimal parameters. You can enter a guess and fine-tune in a second step.
#     As a starting point, BASELINE_INTS can be [0, NINTS-1] where NINTS can
#     be found in your fits header.
#     Note the 1st frame is zero (pythonic numbering)
#     Note that leaving this blank sets the baseline from 0 to NINTS-1
#     E.g.
#         BASELINE_INTS:
#               - [0, 89]
#               - [111, 153]
Cdict.set('BASELINE_INTS', group=cgroup, source=__NAME__,
          value=[[0, 89], [111, 153]])

# define the area around which we will optimize the background
#   this should be a length 4 list (x start, x end, y start, y end)
Cdict.set('BACKGROUND_GLITCH_BOX', group=cgroup, source=__NAME__,
          value=[650, 750, 200, 240])

# define the area around which the background will be optimized
#    should be a list (start, end, step)
Cdict.set('BACKGROUND_SHIFTS', group=cgroup, source=__NAME__,
          value=[-5.0, 5.2, 0.2])

# =============================================================================
# Definition of inputs related to handling of the data within each frame
# =============================================================================
cgroup = 'SOSSISSE.WLC.GENERAL'

# Trace extraction width. Set to 0 to use the full image
Cdict.set('LINRECON_TRACE_WIDTH', group=cgroup, source=__NAME__,
          value=40)

# define the width for masking the white light curve trace
#         Default
Cdict.set('TRACE_WIDTH_MASKING', group=cgroup, source=__NAME__,
          value=40)
# Set the range of dys to scan over number of -nbypix/trace_y_scale to
#     +nbyix/trace_y_scale
Cdict.set('TRACE_Y_SCALE', group=cgroup, source=__NAME__,
          value=10)
# Set the range of dys to scan over number of -nbxpix/trace_x_scale to
#     +nbxpix/trace_x_scale
Cdict.set('TRACE_X_SCALE', group=cgroup, source=__NAME__,
          value=10)

# =============================================================================
# Definition for white light curve
# =============================================================================
cgroup = 'SOSSISSE.SPEC_EXT'

# =============================================================================
# General SORBET settings
# =============================================================================
cgroup = 'SORBET.GENERAL'
# The sub-directory to use for this SORBET run.
# This should be descriptive and unique.
# It should contain no whitespaces or special
# characters other than underscoes
# All sorbet data will be stored in {GLOBAL.DATA_PATH}/sorbet/{SUBDIRECTORY}/
Cdict.set('SUBDIRECTORY', group=cgroup, source=__NAME__, value=INFO['sbid'])
# Description of the SORBET run e.g. object name, date of observation,
# is it a transit or an eclipse etc.
Cdict.set('DESCRIPTION', group=cgroup, source=__NAME__,
          value=INFO['description'])

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
          value='white_light_curve.fits')

# =============================================================================
# Definition of general inputs SORBET_WLCTA
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
cgroup = 'SORBET.SLCTA'

# Switch for turning on/off the white light curve transit fit
Cdict.set('RUN', group=cgroup, source=__NAME__,
          value=True)

# =============================================================================
# Definition of inputs related to the data
# =============================================================================
# Path to input file relative to GLOBAL data path defined by the user
Cdict.set('INPUT_FILES', group=cgroup, source=__NAME__,
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
# Definition of general inputs SORBET_SLCTA
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

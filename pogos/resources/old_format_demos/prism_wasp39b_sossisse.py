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

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'soss_trappist1b.py'

# copy of CDict
Cdict = pconst.CDict.copy(source=__NAME__)
S_Cdict = sconst.CDict.copy(source=__NAME__)
# copy sossisse constants into Cdict
Cdict.add_sub_cdict('SOSSISSE', S_Cdict, source=__NAME__)


# =============================================================================
# Define info (must contain "title")
# =============================================================================
INFO = dict()
INFO['title'] = 'JWST.NIRSPEC.PRISM WASP 39b transit [SOSSISSE]'
INFO['object'] = 'WASP 39b'
INFO['instrument'] = 'JWST.NIRSPEC.BOTS.PRISM'
INFO['description'] = 'WASP 39b transit observed on 2022-07-10'
INFO['date'] = '2025-12-08'
INFO['author'] = 'Neil Cook'
INFO['red_steps'] = ['Extraction:SOSSISSE']
INFO['id'] = 'DEMO_WASP39b_JWST.NIRSPEC.PRISM_SOSSISSE_20220710'
INFO['keywords'] = ['transit']
# url for data download
URL = 'http://206.12.93.77/ari/data/pogos/demos/nirspec/'
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

# Instrument mode i.e. JWST.NIRISS.SOSS or JWST.NIRSPEC.PRISM
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
          value=False)

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
Cdict.set('SUBDIRECTORY', group=cgroup, source=__NAME__, value=INFO['id'])
# Description of the SOSSISSE run e.g. object name, date of observation,
# is it a transit or an eclipse etc.
Cdict.set('DESCRIPTION', group=cgroup, source=__NAME__,
          value=INFO['description'])

# Instrument mode
Cdict.set('INSTRUMENTMODE', group=cgroup, source=__NAME__,
          value=INFO['instrument'])

# Name of the object (must match the object directory name)
Cdict.set('OBJECTNAME', group=cgroup, source=__NAME__,
          value='WASP39b')

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
          value=['jw01366004001_04101_00001-seg001_nrs1_rateints.fits',
                 'jw01366004001_04101_00001-seg002_nrs1_rateints.fits',
                 'jw01366004001_04101_00001-seg003_nrs1_rateints.fits',
                 'jw01366004001_04101_00001-seg004_nrs1_rateints.fits'])

# do background correction - must have BKGFILE defined to do this
Cdict.set('DO_BACKGROUND', value=False, group=cgroup, source=__NAME__)

# flat field file --> leave as '' if there is no flat field available
#     for the mode
Cdict.set('FLATFILE', group=cgroup, source=__NAME__,
          value=None)

# trace position file
Cdict.set('POS_FILE', group=cgroup, source=__NAME__,
          value=None)

# Wavelength calibration file
Cdict.set('WAVE_FILE', group=cgroup, source=__NAME__,
          value='jw01366004001_04101_00001-seg004_nrs1_x1dints.fits')

# Wavelength calibration file type
Cdict.set('WAVE_FILE_TYPE', group=cgroup, source=__NAME__,
          value='ext1d')

# Define which orders to use e.g.
# - 1
# - 2
Cdict.set('TRACE_ORDERS', group=cgroup, source=__NAME__,
          value=None)

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
          value=[[0, 8199], [15700, 21500]])


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

# Trace extraction width. Set to 0 to use the full image
Cdict.set('LINRECON_TRACE_WIDTH', group=cgroup, source=__NAME__,
          value=7)

# define the width for masking the white light curve trace
Cdict.set('TRACE_WIDTH_MASKING', group=cgroup, source=__NAME__,
          value=5)


# =============================================================================
# Definition for white light curve
# =============================================================================
cgroup = 'SOSSISSE.SPEC_EXT'


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

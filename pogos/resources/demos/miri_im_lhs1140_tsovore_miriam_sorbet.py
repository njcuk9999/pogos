#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2025-03-25 at 09:57

@author: cook
"""
from pogos.constants import constants as pconst
from pogos.constants import miriam as mconst
from pogos.constants import tsovore as tconst
from pogos.constants import sorbet as sbconst

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'miri_lhs_1140_imaging.py'

# copy of CDict
Cdict = pconst.CDict.copy(source=__NAME__)
TSOvore_CDict = tconst.TSOVORE_CDict.copy(source=__NAME__)
MIRIAM_CDict = mconst.MIRIAM_CDict.copy(source=__NAME__)
SORBET_CDict = sbconst.SORBET_CDict.copy(source=__NAME__)
# copy sorbet constants into Cdict
Cdict.add_sub_cdict('MIRIAM', MIRIAM_CDict, source=__NAME__)
Cdict.add_sub_cdict('TSOVORE', TSOvore_CDict, source=__NAME__)
Cdict.add_sub_cdict('SORBET', SORBET_CDict, source=__NAME__)

# =============================================================================
# Define info (must contain "title")
# =============================================================================
INFO = dict()
INFO['title'] = 'JWST.MIRI.IMAGE LHS-1140 eclipse [TSOVORE + MIRIAM + SORBET]'
INFO['object'] = 'LHS-1140'
INFO['instrument'] = 'JWST.MIRI.IMAGING'
INFO['description'] = 'LHS-1140 eclipse observed on 2024-07-07'
INFO['date'] = '2025-10-16'
INFO['author'] = 'Etienne Artigau'
INFO['mbid'] = 'DEMO-LHS-1140-MIRIAM-20240707'
INFO['tsid'] = 'DEMO-LHS-1140-TSOVORE-20240707'
INFO['sbid'] = 'DEMO-LHS-1140-SORBET-20240707'
INFO['red_steps'] = ['Pre-extraction:TSOVORE', 'Extraction:MIRIAM',
                     'Post-extraction:SORBET']
# url for data download
URL = 'http://206.12.93.77/ari/data/pogos/demos/miri/'
# download: key = file, value = local path
DOWNLOAD = dict()
DOWNLOAD['TSOVORE.INPUTS.FILES'] = 'TSOVORE.PATHS.INPUT_PATH'



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
          value=True)

# Run SOSSISSE
Cdict.set('SOSSISSE', group=cgroup, source=__NAME__,
          value=False)

# Run MIRIAM
Cdict.set('MIRIAM', group=cgroup, source=__NAME__,
          value=True)

# Run SORBET
Cdict.set('SORBET', group=cgroup, source=__NAME__,
          value=True)

# =============================================================================
# General settings
# =============================================================================
cgroup = 'TSOVORE.GENERAL'

# The SID to use
Cdict.set('SID', group=cgroup, source=__NAME__, value=INFO['tsid'])

# Set the description for the MIRIAM run
Cdict.set('DESCRIPTION', group=cgroup, source=__NAME__,
          value=INFO['description'])

# =============================================================================
# Input settings
# =============================================================================
cgroup = 'TSOVORE.INPUTS'

# Instrument mode i.e. JWST.NIRISS.SOSS or JWST.NIRISS.PRISM
Cdict.set('INSTRUMENTMODE', group=cgroup, source=__NAME__,
          value='JWST.MIRI.IMAGING')

# List of files to be processed in form:
# FILES:
#  - file1
#  - file2
#  - file3
Cdict.set('FILES', group=cgroup, source=__NAME__,
          value=['jw03730009001_03101_00001-seg001_mirimage_uncal.fits',
                 'jw03730009001_03101_00001-seg002_mirimage_uncal.fits',
                 'jw03730009001_03101_00001-seg003_mirimage_uncal.fits',
                 'jw03730009001_03101_00001-seg004_mirimage_uncal.fits',
                 'jw03730009001_03101_00001-seg005_mirimage_uncal.fits'])

# Whether to remove intermediate files
Cdict.set('REMOVE_INTERMEDIATES', group=cgroup, source=__NAME__,
          value=True)

# =============================================================================
# General settings
# =============================================================================
cgroup = 'MIRIAM.GENERAL'

# The SID to use
Cdict.set('SID', group=cgroup, source=__NAME__, value=INFO['mbid'])

# Set the description for the MIRIAM run
Cdict.set('DESCRIPTION', group=cgroup, source=__NAME__,
          value=INFO['description'])

# =============================================================================
# Input settings
# =============================================================================
cgroup = 'MIRIAM.INPUTS'

# List of files to be processed in form:
# FILES:
#  - file1
#  - file2
#  - file3
Cdict.set('FILES', group=cgroup, source=__NAME__,
          value=['jw03730009001_03101_00001-seg001_mirimage_rateints.fits',
                 'jw03730009001_03101_00001-seg002_mirimage_rateints.fits',
                 'jw03730009001_03101_00001-seg003_mirimage_rateints.fits',
                 'jw03730009001_03101_00001-seg004_mirimage_rateints.fits',
                 'jw03730009001_03101_00001-seg005_mirimage_rateints.fits'])

# =============================================================================
# Constants for SORBET: Suite Of Reduction tools for Both Eclipse and Transit
# =============================================================================
cgroup = 'SORBET.GENERAL'

# The SID to use
Cdict.set('SID', group=cgroup, source=__NAME__, value=INFO['sbid'])

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
jpv_values = dict()
jpv_values['P_p1'] = 3.777940
jpv_values['t0_p1'] = [2460498.5, 2460498.8]
jpv_values['p_p1'] = [0., 1.]
jpv_values['b_p1'] = [0.090, 0.65, 0.0, 1.0]
jpv_values['a_p1'] = [10, 30] # 26.57
jpv_values['ecc_p1'] = 0.0
jpv_values['omega_p1'] = 90.0
jpv_values['q1_{INST_MODE}'] = [0.0, 1.0]
jpv_values['q2_{INST_MODE}'] = [0.0, 1.0]
jpv_values['mdilution_{INST_MODE}'] = 1.0
jpv_values['mflux_{INST_MODE}'] = 0.0
jpv_values['sigma_w_{INST_MODE}'] = [1, 1000]
Cdict.set('JULIET_PRIOR_VALS', group=cgroup, source=__NAME__,
          value=jpv_values)


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

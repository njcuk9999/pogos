#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2025-03-25 at 09:57

@author: cook
"""
from pogos.constants import constants as pconst
from pogos.constants import tsovore as tconst

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'miri_lhs_1140_imaging.py'

# copy of CDict
Cdict = pconst.CDict.copy(source=__NAME__)
TSOvore_CDict = tconst.TSOVORE_CDict.copy(source=__NAME__)
# copy sorbet constants into Cdict
Cdict.add_sub_cdict('TSOVORE', TSOvore_CDict, source=__NAME__)

# =============================================================================
# Define info (must contain "title")
# =============================================================================
INFO = dict()
INFO['title'] = 'JWST.MIRI.IMAGE LHS-1140 eclipse [TSOVORE]'
INFO['object'] = 'LHS-1140'
INFO['instrument'] = 'JWST.MIRI.IMAGING'
INFO['description'] = 'LHS-1140 eclipse observed on 2024-07-07'
INFO['date'] = '2025-10-28'
INFO['author'] = 'Loic Albert'
INFO['tsid'] = 'DEMO-LHS-1140-TSOVORE-20240707'
INFO['red_steps'] = ['Pre-extraction:TSOVORE']
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
          value=False)

# Run SORBET
Cdict.set('SORBET', group=cgroup, source=__NAME__,
          value=False)


# =============================================================================
# General settings
# =============================================================================
cgroup = 'TSOVORE.GENERAL'

# The sub-directory to use for this TSOVORE run.
# This should be descriptive and unique.
# It should contain no whitespaces or special
# characters other than underscoes
# All tsovore data will be stored in {GLOBAL.DATA_PATH}/tsovore/{SUBDIRECTORY}/
Cdict.set('SUBDIRECTORY', group=cgroup, source=__NAME__, value=INFO['tsid'])

# Description of the MIRIAM run e.g. object name, date of observation,
# is it a transit or an eclipse etc.
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

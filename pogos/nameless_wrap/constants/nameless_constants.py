#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

Constants for the POGOS NAMELESS wrapper (nameless_wrap).

NAMELESS is a JWST NIRISS/SOSS-only time-series reduction code. This mirrors
the eureka_wrap constants (Eureka_CDict) but exposes the NAMELESS settings.
The NAMELESS reduction maps onto the POGOS reduction steps as follows:

    Pre-extraction  [RUN.PRE_NAMELESS]  -> run_s1, run_s2, run_prep, run_cst
    Extraction      [RUN.EXT_NAMELESS]  -> run_ext
    (there is no post-extraction step for NAMELESS)

Created on 2026-06-26

@author: cook
"""
from aperocore.constants import constant_functions

from pogos.core import base

try:
    import NAMELESS
    nversion = getattr(NAMELESS, '__version__', 'Unknown')
    ndate = getattr(NAMELESS, '__date__', 'Unknown')
except ImportError:
    nversion = 'Unknown'
    ndate = 'Unknown'

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'nameless_wrap.constants.nameless_constants.py'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__

# Constants definition
Const = constant_functions.Const
ConstDict = constant_functions.ConstantsDict

# =============================================================================
# constants for the NAMELESS wrapper
# =============================================================================
NAMELESS_CDict = ConstDict(__NAME__)

# set the title for output yaml files
NAMELESS_CDict.title = NAMELESS_CDict.yaml_title('NAMELESS Module',
                                                 setup_program=None,
                                                 version=nversion,
                                                 date=ndate)

# =============================================================================
# General settings (generally don't touch these)
# =============================================================================
cgroup = 'GENERAL'
NAMELESS_CDict.add_group(cgroup, description='General configs for NAMELESS '
                                             '(JWST NIRISS/SOSS only)',
                         source=__NAME__, user=True, active=True)

# add the sub-directory (used when a default path is required)
#   the NAMELESS red_dir (reduction directory) is set to
#   {GLOBAL.DATA_PATH}/nameless/{SUBDIRECTORY}
NAMELESS_CDict.add('SUBDIRECTORY', value=None, dtype=str, source=__NAME__,
                   user=True, active=True, group=cgroup, not_none=True,
                   description='The sub-directory to use for this NAMELESS run. '
                               'This should be descriptive and unique. '
                               '\nIt should contain no whitespaces or special '
                               'characters other than underscores.'
                               '\nAll NAMELESS data will be stored in '
                               '{GLOBAL.DATA_PATH}/nameless/{SUBDIRECTORY}/ '
                               '(this is the NAMELESS red_dir)'
                               '\n\nWe suggest {OBJNAME}-SOSS-{STEP}-{YYYYMMDD}')

# describe what we are running through NAMELESS
NAMELESS_CDict.add('DESCRIPTION', value='', dtype=str, source=__NAME__,
                   user=True, active=True, group=cgroup,
                   description='Description of the POGOS run e.g. object name, '
                               'date of observation, is it a transit or '
                               'an eclipse etc.')

# Define whether we are in test mode (sets up directories but does not run)
NAMELESS_CDict.add('TESTMODE', value=False, dtype=bool, source=__NAME__,
                   user=True, active=True, group=cgroup,
                   description='Define whether we are in test mode (sets up '
                               'directories but does not run NAMELESS)')

# The folder (relative to the run sub-directory) that holds the *uncal.fits
NAMELESS_CDict.add('INPUTDIR', value='Uncalibrated', dtype=str, source=__NAME__,
                   user=True, active=True, group=cgroup, not_none=True,
                   description='Folder (relative to the NAMELESS run '
                               'sub-directory) containing the raw *_uncal.fits '
                               'input files')

# Optional explicit file handle (auto-detected from the uncal files if None)
NAMELESS_CDict.add('HANDLE', value=None, dtype=str, source=__NAME__,
                   user=True, active=True, group=cgroup,
                   description='The JWST file handle (e.g. '
                               '"jwXXXXYYY001_04101_00001"). Leave as None to '
                               'auto-detect from the uncal files.')

# Optional number of segments (auto-detected if None)
NAMELESS_CDict.add('NSEG', value=None, dtype=int, source=__NAME__,
                   user=True, active=True, group=cgroup,
                   description='Number of data segments. Leave as None to '
                               'auto-detect (reduce all segments).')

# Optional explicit segment list (auto-detected if None)
NAMELESS_CDict.add('SEGS', value=None, dtype=list, source=__NAME__,
                   user=True, active=True, group=cgroup,
                   description="List of segments to analyse e.g. "
                               "['001', '002', '003']. Leave as None to "
                               "auto-detect all segments.")


# =============================================================================
# Define the paths
# =============================================================================
cgroup = 'PATHS'
NAMELESS_CDict.add_group(cgroup, description='POGOS paths for NAMELESS',
                         source=__NAME__, user=True, active=True)

# absolute input path (uncal files) - filled in by POGOS, not the user
NAMELESS_CDict.add('IN_PATH', value=None, dtype=str, source=__NAME__,
                   user=False, active=False, group=cgroup,
                   description='POGOS full path to the uncal input files')

# absolute reduction directory (NAMELESS red_dir / topdir) - filled by POGOS
NAMELESS_CDict.add('TOPDIR', value=None, dtype=str, source=__NAME__,
                   user=False, active=False, group=cgroup,
                   description='POGOS full path used as the NAMELESS red_dir '
                               '(reduction directory)')

# path to the NAMELESS Auxiliary (ancillary) files
NAMELESS_CDict.add('ANCIL_PATH', value=None, dtype='path', source=__NAME__,
                   user=True, active=True, group=cgroup,
                   description='Absolute path to the NAMELESS Auxiliary '
                               'directory containing the reference files '
                               '(e.g. jwst_niriss_specprofile, spectrace, '
                               'model_background256.npy). '
                               'E.g. /home/User/NAMELESS/Auxiliary')


# =============================================================================
# Stage 1 settings (jwst calwebb_detector1 steps)
# =============================================================================
cgroup = 'S1_SETTINGS'
NAMELESS_CDict.add_group(cgroup, description='NAMELESS Stage 1 settings (jwst '
                                             'calwebb_detector1 steps) '
                                             '[RUN.PRE_NAMELESS=True]',
                         source=__NAME__, user=True, active=True)

# which intermediate step outputs to save to disk
_s1_saves = [('save_gs', 'group scale'), ('save_dq', 'data quality'),
             ('save_sat', 'saturation'), ('save_sb', 'superbias'),
             ('save_rp', 'reference pixel'), ('save_lin', 'linearity'),
             ('save_dc', 'dark current'), ('save_jd', 'jump detection'),
             ('save_rf', 'ramp fitting'), ('save_gain', 'gain scaling')]
for _key, _desc in _s1_saves:
    # by default only the ramp fit output is saved (needed for Stage 2)
    _default = _key == 'save_rf'
    NAMELESS_CDict.add(_key, value=_default, dtype=bool, source=__NAME__,
                       user=True, active=True, group=cgroup,
                       description='Save output after the {0} step'.format(_desc))

# which steps to skip
NAMELESS_CDict.add('skip_dc', value=True, dtype=bool, source=__NAME__,
                   user=True, active=True, group=cgroup,
                   description='Skip the dark current step')
NAMELESS_CDict.add('skip_jd', value=False, dtype=bool, source=__NAME__,
                   user=True, active=True, group=cgroup,
                   description='Skip the jump detection step')
NAMELESS_CDict.add('skip_gain', value=True, dtype=bool, source=__NAME__,
                   user=True, active=True, group=cgroup,
                   description='Skip the gain scaling step')


# =============================================================================
# Stage 2 settings (jwst calwebb_spec2 steps)
# =============================================================================
cgroup = 'S2_SETTINGS'
NAMELESS_CDict.add_group(cgroup, description='NAMELESS Stage 2 settings (jwst '
                                             'calwebb_spec2 steps) '
                                             '[RUN.PRE_NAMELESS=True]',
                         source=__NAME__, user=True, active=True)

NAMELESS_CDict.add('save_wcs', value=False, dtype=bool, source=__NAME__,
                   user=True, active=True, group=cgroup,
                   description='Save output after the assign WCS step')
NAMELESS_CDict.add('save_ff', value=False, dtype=bool, source=__NAME__,
                   user=True, active=True, group=cgroup,
                   description='Save output after the flat field step')
NAMELESS_CDict.add('save_st', value=True, dtype=bool, source=__NAME__,
                   user=True, active=True, group=cgroup,
                   description='Save output after the source type step '
                               '(needed for the prep/custom steps)')


# =============================================================================
# Prep settings (preparatory steps before the custom corrections)
# =============================================================================
cgroup = 'PREP_SETTINGS'
NAMELESS_CDict.add_group(cgroup, description='NAMELESS preparatory step '
                                             'settings [RUN.PRE_NAMELESS=True]',
                         source=__NAME__, user=True, active=True)

NAMELESS_CDict.add('wlc_pixs', value=[[1250, 1750], [40, 70]], dtype=list,
                   source=__NAME__, user=True, active=True, group=cgroup,
                   description='Pixels used to compute the rough white light '
                               'curve [[xmin, xmax], [ymin, ymax]]')
NAMELESS_CDict.add('trace_method', value='CCF', dtype=str,
                   options=['CCF', 'pastasoss'], source=__NAME__, user=True,
                   active=True, group=cgroup,
                   description='Method used to get the centre positions of '
                               "orders 1 and 2, either 'CCF' or 'pastasoss'")
NAMELESS_CDict.add('sampfac', value=100, dtype=int, source=__NAME__, user=True,
                   active=True, group=cgroup,
                   description='Factor used to supersample the detector when '
                               'doing the CCF method')
NAMELESS_CDict.add('nknots_o1', value=11, dtype=int, source=__NAME__, user=True,
                   active=True, group=cgroup,
                   description='Number of knots used to smooth the Order 1 '
                               'trace')
NAMELESS_CDict.add('nknots_o2', value=7, dtype=int, source=__NAME__, user=True,
                   active=True, group=cgroup,
                   description='Number of knots used to smooth the Order 2 '
                               'trace')
NAMELESS_CDict.add('xmin_o2', value=750, dtype=int, source=__NAME__, user=True,
                   active=True, group=cgroup,
                   description='Lower column cutoff considered for order 2')
NAMELESS_CDict.add('xmax_o2', value=1800, dtype=int, source=__NAME__, user=True,
                   active=True, group=cgroup,
                   description='Upper column cutoff considered for order 2')
NAMELESS_CDict.add('plotting', value=True, dtype=bool, source=__NAME__,
                   user=True, active=True, group=cgroup,
                   description='Produce and save the diagnostic plots')
NAMELESS_CDict.add('dpi', value=300, dtype=int, source=__NAME__, user=True,
                   active=True, group=cgroup,
                   description='dpi of the figures')


# =============================================================================
# Custom step settings (bad pixel, background, cosmic ray, 1/f corrections)
# =============================================================================
cgroup = 'CST_SETTINGS'
NAMELESS_CDict.add_group(cgroup, description='NAMELESS custom-correction step '
                                             'settings [RUN.PRE_NAMELESS=True]',
                         source=__NAME__, user=True, active=True)

# Bad pixel correction
NAMELESS_CDict.add('frac_int', value=0.5, dtype=float, source=__NAME__,
                   user=True, active=True, group=cgroup,
                   description='Fraction of flagged integrations needed for a '
                               'pixel to be considered bad')
NAMELESS_CDict.add('interp_bp', value='linear', dtype=str,
                   options=['nearest', 'linear', 'cubic'], source=__NAME__,
                   user=True, active=True, group=cgroup,
                   description='Interpolation method to correct bad pixels')
# Background subtraction (shape [[xmin, xmax], [ymin, ymax]])
NAMELESS_CDict.add('inds1_bg', value=[[500, 675], [210, -5]], dtype=list,
                   source=__NAME__, user=True, active=True, group=cgroup,
                   description='Pixels used to compute the background scaling '
                               'for the left portion of the detector')
NAMELESS_CDict.add('inds2_bg', value=[[725, 900], [230, -5]], dtype=list,
                   source=__NAME__, user=True, active=True, group=cgroup,
                   description='Pixels used to compute the background scaling '
                               'for the right portion of the detector')
NAMELESS_CDict.add('bg_quant', value=0.05, dtype=float, source=__NAME__,
                   user=True, active=True, group=cgroup,
                   description='Quantile of the data vs model ratio '
                               'distribution used to compute the scaling value')
# Cosmic ray correction
NAMELESS_CDict.add('wlc_pixs', value=[[1250, 1750], [40, 70]], dtype=list,
                   source=__NAME__, user=True, active=True, group=cgroup,
                   description='Pixels used to compute the rough white light '
                               'curve [[xmin, xmax], [ymin, ymax]]')
NAMELESS_CDict.add('nsig_CR', value=4, dtype=int, source=__NAME__, user=True,
                   active=True, group=cgroup,
                   description='Any count that is >X sigma away from the '
                               'running median is flagged as a cosmic ray')
NAMELESS_CDict.add('wlc_window', value=11, dtype=int, source=__NAME__,
                   user=True, active=True, group=cgroup,
                   description='Window size used to "smooth" the white light '
                               'curve')
NAMELESS_CDict.add('CR_window', value=10, dtype=int, source=__NAME__,
                   user=True, active=True, group=cgroup,
                   description='Window size of the running median used to flag '
                               'the cosmic rays')
# 1/f correction
NAMELESS_CDict.add('ap_1f', value=20, dtype=int, source=__NAME__, user=True,
                   active=True, group=cgroup,
                   description='Size of the aperture RADIUS used to compute the '
                               '1/f values')
NAMELESS_CDict.add('median_ints', value=[0, 200], dtype=list, source=__NAME__,
                   user=True, active=True, group=cgroup,
                   description='Range of integrations used to compute the '
                               'median columns [int_min, int_max]')
NAMELESS_CDict.add('plotting', value=True, dtype=bool, source=__NAME__,
                   user=True, active=True, group=cgroup,
                   description='Produce and save the diagnostic plots')
NAMELESS_CDict.add('dpi', value=300, dtype=int, source=__NAME__, user=True,
                   active=True, group=cgroup,
                   description='dpi of the figures')


# =============================================================================
# Extraction settings (2D light curve extraction)
# =============================================================================
cgroup = 'EXT_SETTINGS'
NAMELESS_CDict.add_group(cgroup, description='NAMELESS extraction step '
                                             'settings [RUN.EXT_NAMELESS=True]',
                         source=__NAME__, user=True, active=True)

NAMELESS_CDict.add('ap_radius', value=18.0, dtype=float, source=__NAME__,
                   user=True, active=True, group=cgroup,
                   description='Aperture radius used for the box extraction')
NAMELESS_CDict.add('plotting', value=True, dtype=bool, source=__NAME__,
                   user=True, active=True, group=cgroup,
                   description='Produce and save the diagnostic plots')
NAMELESS_CDict.add('dpi', value=300, dtype=int, source=__NAME__, user=True,
                   active=True, group=cgroup,
                   description='dpi of the figures')


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================


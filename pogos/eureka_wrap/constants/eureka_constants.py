#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2024-10-29 at 09:30

@author: cook
"""

from aperocore.constants import constant_functions

from pogos.core import base


try:
    import eureka
    eversion = eureka.__version__
    edate = eureka.__date__

except ImportError:
    eversion  = 'Unknown'
    edate = 'Unknown'

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'eureka_wrap.constants.eureka_constants.py'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__

# Constants definition
Const = constant_functions.Const
ConstDict = constant_functions.ConstantsDict

# =============================================================================
# constants from MIRIAM
# =============================================================================
Eureka_CDict = ConstDict(__NAME__)

# set the title for output yaml files
Eureka_CDict.title = Eureka_CDict.yaml_title('EUREKA! Module',
                                             setup_program=None,
                                             version=eversion,
                                             date=edate)

# =============================================================================
# General settings (generally don't touch these)
# =============================================================================
# set the group for general constants
cgroup = 'GENERAL'
Eureka_CDict.add_group(cgroup, description='General configs for Eureka',
                       source=__NAME__, user=True, active=True)
# add the sid (to be used when default path required)
Eureka_CDict.add('SUBDIRECTORY', value=None, dtype=str, source=__NAME__,
                 user=True, active=True, group=cgroup, not_none=True,
                 description='The sub-directory to use for this Eureka run. '
                             'This should be descriptive and unique. '
                             '\nIt should contain no whitespaces or special '
                             'characters other than underscoes.'
                             '\nAll miriam data will be stored in '
                             '{GLOBAL.DATA_PATH}/eureka/{SUBDIRECTORY}/'
                             '\n\nWe suggest {OBJNAME}-{INST.MODE}-{STEP}-{YYYYMMDD}')

# define what we are running through MIRIAM
Eureka_CDict.add('DESCRIPTION', value='', dtype=str, source=__NAME__,
                 user=True, active=True, group=cgroup,
                 description='Description of the POGOS run e.g. object name, '
                             'date of observation, is it a transit or '
                             'an eclipse etc.')

# define what the event label, should be very similar to description but no
#     white spaces
Eureka_CDict.add('EVENTLABEL', value=None, dtype=str, source=__NAME__,
                 user=True, active=True, group=cgroup, not_none=True,
                 description='Eureka eventlabel, description of the POGOS run'
                             ' e.g. object name, date of observation, '
                             'is it a transit or an eclipse etc. '
                             'No white spaces allowed, '
                             'use underscores instead. ')

# Define whether we are in test mode
Eureka_CDict.add('TESTMODE', value=False, dtype=bool, source=__NAME__,
                 user=True, active=True, group=cgroup,
                 description='Define whether we are in test mode')


# =============================================================================
# Define the paths
# =============================================================================
# set the group for general constants
cgroup = 'PATHS'
Eureka_CDict.add_group(cgroup, description='POGO Paths for Eureka',
                       source=__NAME__, user=True, active=True)

# Set the input paths for the stages (so pogos can work with them)
Eureka_CDict.add('IN_S1_PATH', value=None, dtype=str, source=__NAME__,
                 user=False, active=False, group=cgroup,
                 description='POGOS full path to Stage 1 input')
Eureka_CDict.add('IN_S2_PATH', value=None, dtype=str, source=__NAME__,
                 user=False, active=False, group=cgroup,
                 description='POGOS full path to Stage 2 input')
Eureka_CDict.add('IN_S3_PATH', value=None, dtype=str, source=__NAME__,
                 user=False, active=False, group=cgroup,
                 description='POGOS full path to Stage 3 input')
# Set the input paths for the stages (so pogos can work with them)
Eureka_CDict.add('OUT_S1_PATH', value=None, dtype=str, source=__NAME__,
                 user=False, active=False, group=cgroup,
                 description='POGOS full path to Stage 1 output')
Eureka_CDict.add('OUT_S2_PATH', value=None, dtype=str, source=__NAME__,
                 user=False, active=False, group=cgroup,
                 description='POGOS full path to Stage 2 output')
Eureka_CDict.add('OUT_S3_PATH', value=None, dtype=str, source=__NAME__,
                 user=False, active=False, group=cgroup,
                 description='POGOS full path to Stage 3 output')

# Path to pogos-created ECF
Eureka_CDict.add('ECF_PATH', value=None, dtype=str, source=__NAME__,
                 user=False, active=False, group=cgroup,
                 description='Path to pogos-created ECF file')


# =============================================================================
# Setting up Eureka groups (Do not touch)
# =============================================================================
group_desc = ['Eureka! Stage 1 metadata (required for Pre-extraction Step '
              '[RUN.PRE_EUREKA=True])',
              'Eureka! Stage 2 metadata (required for Pre-extraction Step '
              '[RUN.PRE_EUREKA=True])',
              'Eureka! Stage 3 metadata (required for Extraction Step '
              '[RUN.EXT_EUREKA=True])',
              'Eureka! Stage 4 metadata (required for Post-extraction Step '
              '[RUN.POST_EUREKA=True])',
              'Eureka! Stage 5 metadata (required for Post-extraction Step '
              '[RUN.POST_EUREKA=True])',
              'Eureka! Stage 6 metadata (required for Post-extraction Step) '
              '[RUN.POST_EUREKA=True])',]

for _stage in range(6):
    # stage 1 parameters
    cgroup = f'STAGE{_stage+1}'
    Eureka_CDict.add_group(cgroup, description=group_desc[_stage],
                           source=__NAME__, user=True, active=True)

# =============================================================================
# Settings imported directly from Eureka (Do not touch)
# =============================================================================
# >>> BEGIN AUTO-GENERATED ECF CONSTANTS (do not edit) >>>
# Regenerated by eureka_ecf.update_constants_from_ecfs() - do not hand-edit.
# Override values AFTER this block with Eureka_CDict.set(...).

cgroup = 'STAGE1'
Eureka_CDict.add('suffix', value='uncal', dtype=str, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=None)
Eureka_CDict.add('maximum_cores', value='half', dtype=str,
                 options=[None, 'quarter', 'half', 'all'], source=__NAME__,
                 user=True, active=True, group=cgroup,
                 description="Options are 'none', quarter', 'half', 'all'")
Eureka_CDict.add('skip_saturation', value=False, dtype=bool, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=None)
Eureka_CDict.add('skip_refpix', value=False, dtype=bool, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=None)
Eureka_CDict.add('skip_linearity', value=False, dtype=bool, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=None)
Eureka_CDict.add('skip_dark_current', value=False, dtype=bool, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=None)
Eureka_CDict.add('skip_jump', value=False, dtype=bool, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=None)
Eureka_CDict.add('skip_ramp_fitting', value=False, dtype=bool, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=None)
Eureka_CDict.add('jump_rejection_threshold', value=4.0, dtype=float,
                 options=None, source=__NAME__, user=True, active=True,
                 group=cgroup,
                 description=('float, default is 4.0, CR sigma rejection '
                              'threshold. Usually recommend a larger value '
                              'for TSO data.'))
Eureka_CDict.add('custom_linearity', value=False, dtype=bool, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=None)
Eureka_CDict.add('linearity_file', value=None, dtype='path', options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description='E.g. /path/to/custom/linearity/fits/file')
Eureka_CDict.add('update_sat_flags', value=False, dtype=bool, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('Wheter to update the saturation flags more '
                              'aggressively'))
Eureka_CDict.add('expand_prev_group', value=False, dtype=bool, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description='Expand saturation flags to previous group')
Eureka_CDict.add('dq_sat_mode', value='percentile', dtype=str,
                 options=['percentile', 'min', 'defined'], source=__NAME__,
                 user=True, active=True, group=cgroup,
                 description='Options: [percentile, min, defined]')
Eureka_CDict.add('dq_sat_percentile', value=50, dtype=int, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('Percentile of the entire time series to use to '
                              'define the saturation mask (50=median)'))
Eureka_CDict.add('dq_sat_columns',
                 value=[[0, 0], [0, 0], [0, 0], [0, 0], [0, 0]], dtype=list,
                 options=None, source=__NAME__, user=True, active=True,
                 group=cgroup,
                 description=('for dq_sat_mode = defined, user defined '
                              'saturated columns'))
Eureka_CDict.add('grouplevel_bg', value=None, dtype=bool, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=None)
Eureka_CDict.add('ncpu', value=None, dtype=int, options=None, source=__NAME__,
                 user=True, active=True, group=cgroup, description=None)
Eureka_CDict.add('bg_y1', value=6, dtype=int, options=None, source=__NAME__,
                 user=True, active=True, group=cgroup, description=None)
Eureka_CDict.add('bg_y2', value=26, dtype=int, options=None, source=__NAME__,
                 user=True, active=True, group=cgroup, description=None)
Eureka_CDict.add('bg_deg', value=0, dtype=int, options=None, source=__NAME__,
                 user=True, active=True, group=cgroup, description=None)
Eureka_CDict.add('bg_method', value='median', dtype=str,
                 options=['std', 'median', 'mean'], source=__NAME__, user=True,
                 active=True, group=cgroup,
                 description=('Options: std (Standard Deviation), median '
                              '(Median Absolute Deviation), mean (Mean '
                              'Absolute Deviation)'))
Eureka_CDict.add('p3thresh', value=5, dtype=int, options=None, source=__NAME__,
                 user=True, active=True, group=cgroup, description=None)
Eureka_CDict.add('isplots_S1', value=None, dtype=int, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=None)
Eureka_CDict.add('nplots', value=5, dtype=int, options=None, source=__NAME__,
                 user=True, active=True, group=cgroup, description=None)
Eureka_CDict.add('hide_plots', value=True, dtype=bool, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=None)
Eureka_CDict.add('verbose', value=True, dtype=bool, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=None)
Eureka_CDict.add('topdir', value=None, dtype='path', options=None,
                 source=__NAME__, user=True, active=False, group=cgroup,
                 description='E.g. /home/User/Data/JWST-Sim/NIRSpec/')
Eureka_CDict.add('inputdir', value='Uncalibrated', dtype=str, options=None,
                 source=__NAME__, user=True, active=True, not_none=True,
                 group=cgroup, description=None)
Eureka_CDict.add('outputdir', value='Stage1', dtype=str, options=None,
                 source=__NAME__, user=True, active=True, not_none=True,
                 group=cgroup, description=None)

cgroup = 'STAGE2'
Eureka_CDict.add('suffix', value='rateints', dtype=str, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description='Data file suffix')
Eureka_CDict.add('skip_flat_field', value=None, dtype=bool, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('Set this to False if you want to compute '
                              'calibrated stellar spectra.'))
Eureka_CDict.add('skip_photom', value=True, dtype=bool, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('Recommended to skip to get better '
                              'uncertainties out of Stage 3. Set this to '
                              'False if you want to compute calibrated '
                              'stellar spectra.'))
Eureka_CDict.add('hide_plots', value=True, dtype=bool, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('If True, plots will automatically be closed '
                              'rather than popping up'))
Eureka_CDict.add('topdir', value=None, dtype='path', options=None,
                 source=__NAME__, user=True, active=False, group=cgroup,
                 description='E.g. /home/User/Data/JWST-Sim/NIRISS/')
Eureka_CDict.add('inputdir', value='Stage1', dtype=str, options=None,
                 source=__NAME__, user=True, active=True, not_none=True,
                 group=cgroup, description=None)
Eureka_CDict.add('outputdir', value='Stage2', dtype=str, options=None,
                 source=__NAME__, user=True, active=True, not_none=True,
                 group=cgroup, description=None)

cgroup = 'STAGE3'
Eureka_CDict.add('ncpu', value=4, dtype=int, options=None, source=__NAME__,
                 user=True, active=True, group=cgroup,
                 description='Number of CPUs')
Eureka_CDict.add('nfiles', value=None, dtype=int, options=None, source=__NAME__,
                 user=True, active=True, group=cgroup,
                 description=('The number of data files to analyze '
                              'simultaneously'))
Eureka_CDict.add('max_memory', value=0.5, dtype=float, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('The maximum fraction of memory you want '
                              'utilized by read-in frames (this will reduce '
                              'nfiles if need be)'))
Eureka_CDict.add('indep_batches', value=False, dtype=bool, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('Independently treat each batch of files? '
                              'Strongly recommended to leave this as False '
                              'unless you have a clear reason to set it to '
                              'True.'))
Eureka_CDict.add('suffix', value='calints', dtype=str, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description='Data file suffix')
Eureka_CDict.add('calibrated_spectra', value=False, dtype=bool, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('Set True to generate flux-calibrated '
                              'spectra/photometry in mJy Set False to convert '
                              'to electrons'))
Eureka_CDict.add('ywindow', value=None, dtype=list, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description='Vertical axis as seen in DS9')
Eureka_CDict.add('xwindow', value=None, dtype=list, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description='Horizontal axis as seen in DS9')
Eureka_CDict.add('dqmask', value=True, dtype=bool, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description='Mask pixels with an odd entry in the DQ array')
Eureka_CDict.add('ff_outlier', value=False, dtype=bool, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('Set False to use only background region '
                              '(recommended for deep transits) Set True to '
                              'use full frame (works well for shallow '
                              'transits/eclipses)'))
Eureka_CDict.add('bg_thresh', value=None, dtype=list, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('Double-iteration X-sigma threshold for outlier '
                              'rejection along time axis'))
Eureka_CDict.add('isplots_S3', value=3, dtype=int, options=[1, 2, 3, 4, 5],
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('Generate few (1), some (3), or many (5) '
                              'figures (Options: 1 - 5)'))
Eureka_CDict.add('nplots', value=5, dtype=int, options=None, source=__NAME__,
                 user=True, active=True, group=cgroup,
                 description=('How many of each type of figure do you want to '
                              'make per file?'))
Eureka_CDict.add('hide_plots', value=True, dtype=bool, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('If True, plots will automatically be closed '
                              'rather than popping up'))
Eureka_CDict.add('save_output', value=True, dtype=bool, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description='Save outputs for use in S4')
Eureka_CDict.add('save_fluxdata', value=False, dtype=bool, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('Save the much larger FluxData.h5 outputs which '
                              'can be useful for debugging or comparisons '
                              'between different pipelines'))
Eureka_CDict.add('verbose', value=True, dtype=bool, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('If True, more details will be printed about '
                              'steps'))
Eureka_CDict.add('topdir', value=None, dtype='path', options=None,
                 source=__NAME__, user=True, active=False, group=cgroup,
                 description='E.g. /home/User/Data/JWST-Sim/NIRISS/')
Eureka_CDict.add('inputdir', value='Stage2', dtype=str, options=None,
                 source=__NAME__, user=True, active=True, not_none=True,
                 group=cgroup,
                 description=('The folder containing the outputs from '
                              "Eureka!'s S2 or JWST's S2 pipeline (will be "
                              'overwritten if calling S2 and S3 sequentially)'))
Eureka_CDict.add('outputdir', value='Stage3', dtype=str, options=None,
                 source=__NAME__, user=True, active=True, not_none=True,
                 group=cgroup, description=None)

cgroup = 'STAGE4'
Eureka_CDict.add('nspecchan', value=2, dtype=int, options=None, source=__NAME__,
                 user=True, active=True, group=cgroup,
                 description=('Number of spectroscopic channels spread evenly '
                              'over given wavelength range. Set to None to '
                              'leave the spectrum unbinned.'))
Eureka_CDict.add('compute_white', value=True, dtype=bool, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description='Also compute the white-light lightcurve')
Eureka_CDict.add('s4_order', value=None, dtype=None, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description='For NIRISS, specify spectral order')
Eureka_CDict.add('wave_min', value=1.5, dtype=float, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('Minimum wavelength. Set to None to use the '
                              'shortest extracted wavelength from Stage 3.'))
Eureka_CDict.add('wave_max', value=4.5, dtype=float, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('Maximum wavelength. Set to None to use the '
                              'longest extracted wavelength from Stage 3.'))
Eureka_CDict.add('wave_input', value=None, dtype=None, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('Full path to a txt file with pre-defined '
                              'wavelength bins in two columns separated by '
                              'whitespace.'))
Eureka_CDict.add('allapers', value=False, dtype=bool, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('Run S4 on all of the apertures considered in '
                              'S3? Otherwise will use newest output in the '
                              'inputdir'))
Eureka_CDict.add('mad_sigma', value=7, dtype=int, options=None, source=__NAME__,
                 user=True, active=True, group=cgroup,
                 description=('The number of sigmas an unbinned MAD value '
                              'must be from the rolling median (using '
                              'mad_box_width) to be considered an outlier. '
                              'Outlier columns are masked.'))
Eureka_CDict.add('mad_box_width', value=21, dtype=int, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('The rolling median box width to use when '
                              "computing whether a wavelength element's MAD "
                              'is an outlier'))
Eureka_CDict.add('recordDrift', value=False, dtype=bool, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('Set True to record drift/jitter in 1D spectra '
                              '(always recorded if correctDrift is True)'))
Eureka_CDict.add('correctDrift', value=False, dtype=bool, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('Set True to correct drift/jitter in 1D spectra '
                              '(not recommended)'))
Eureka_CDict.add('clip_unbinned', value=False, dtype=bool, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('Whether or not sigma clipping should be '
                              'performed on the unbinned 1D time series'))
Eureka_CDict.add('clip_binned', value=True, dtype=bool, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('Whether or not sigma clipping should be '
                              'performed on the binned 1D time series'))
Eureka_CDict.add('sigma', value=10, dtype=int, options=None, source=__NAME__,
                 user=True, active=True, group=cgroup,
                 description=('The number of sigmas a point must be from the '
                              'rolling median to be considered an outlier'))
Eureka_CDict.add('box_width', value=31, dtype=int, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('The width of the box-car filter (used to '
                              'calculated the rolling median) in units of '
                              'number of data points'))
Eureka_CDict.add('maxiters', value=5, dtype=int, options=None, source=__NAME__,
                 user=True, active=True, group=cgroup,
                 description=('The number of iterations of sigma clipping '
                              'that should be performed.'))
Eureka_CDict.add('boundary', value='fill', dtype=str, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=("Use 'fill' to extend the boundary values by "
                              'the median of all data points (recommended), '
                              "'wrap' to use a periodic boundary, or 'extend' "
                              'to use the first/last data points'))
Eureka_CDict.add('fill_value', value='mask', dtype=str, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=("Either the string 'mask' to mask the outlier "
                              "values (recommended), 'boxcar' to replace data "
                              'with the mean from the box-car filter, or a '
                              'constant float-type fill value.'))
Eureka_CDict.add('compute_ld', value=False, dtype=bool,
                 options=['exotic-ld', 'spam', False], source=__NAME__,
                 user=True, active=True, group=cgroup,
                 description='Options: exotic-ld, spam, False')
Eureka_CDict.add('metallicity', value=0.1, dtype=float, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description='Metallicity of the star')
Eureka_CDict.add('teff', value=6000, dtype=int, options=None, source=__NAME__,
                 user=True, active=True, group=cgroup,
                 description='Effective temperature of the star in K')
Eureka_CDict.add('logg', value=4.0, dtype=float, options=None, source=__NAME__,
                 user=True, active=True, group=cgroup,
                 description='Surface gravity in log g')
Eureka_CDict.add('minmu', value=0.2, dtype=float, options=None, source=__NAME__,
                 user=True, active=True, group=cgroup,
                 description=('minimum mu to use when calculating LD in '
                              'ExoTiC-LD'))
Eureka_CDict.add('exotic_ld_direc', value=None, dtype='path', options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('Directory for ancillary files for exotic-ld, '
                              'download from: '
                              'https://zenodo.org/doi/10.5281/zenodo.6047317 '
                              'E.g /home/User/exotic-ld_data/'))
Eureka_CDict.add('exotic_ld_grid', value='stagger', dtype=str, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('You can choose from kurucz (or 1D), stagger '
                              '(or 3D), mps1, or mps2 model grids, or custom '
                              '(to use custom_si_grid below)'))
Eureka_CDict.add('spam_file', value=None, dtype='path', options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('Pre-generated file of SPAM limb-darkening '
                              'values at high resolution E.g '
                              '/home/User/spam-ldcoeff-u1-u2.txt'))
Eureka_CDict.add('isplots_S4', value=3, dtype=int, options=[1, 2, 3, 4, 5],
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('Generate few (1), some (3), or many (5) '
                              'figures (Options: 1 - 5)'))
Eureka_CDict.add('vmin', value=0.97, dtype=float, options=None, source=__NAME__,
                 user=True, active=True, group=cgroup,
                 description='Sets the vmin of the color bar for Figure 4101.')
Eureka_CDict.add('vmax', value=1.03, dtype=float, options=None, source=__NAME__,
                 user=True, active=True, group=cgroup,
                 description='Sets the vmax of the color bar for Figure 4101.')
Eureka_CDict.add('time_axis', value='y', dtype=str, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('Determines whether the time axis in Figure '
                              "4101 is along the y-axis ('y') or the x-axis "
                              "('x')"))
Eureka_CDict.add('hide_plots', value=True, dtype=bool, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('If True, plots will automatically be closed '
                              'rather than popping up'))
Eureka_CDict.add('verbose', value=True, dtype=bool, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('If True, more details will be printed about '
                              'steps'))
Eureka_CDict.add('topdir', value=None, dtype='path', options=None,
                 source=__NAME__, user=True, active=False, group=cgroup,
                 description='E.g. /home/User/Data/JWST-Sim/NIRSpec/')
Eureka_CDict.add('inputdir', value='Stage3', dtype=str, options=None,
                 source=__NAME__, user=True, active=True, not_none=True,
                 group=cgroup,
                 description=('The folder containing the outputs from '
                              "Eureka!'s S3 or JWST's S3 pipeline (will be "
                              'overwritten if calling S3 and S4 sequentially)'))
Eureka_CDict.add('outputdir', value='Stage4', dtype=str, options=None,
                 source=__NAME__, user=True, active=True, not_none=True,
                 group=cgroup, description=None)

cgroup = 'STAGE5'
Eureka_CDict.add('ncpu', value=4, dtype=int, options=None, source=__NAME__,
                 user=True, active=True, group=cgroup,
                 description=('The number of CPU threads to use when running '
                              'emcee or dynesty in parallel'))
Eureka_CDict.add('multwhite', value=False, dtype=bool, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('Are you simultaneously fitting multiple white '
                              'lightcurves? (if so, use inputdirlist and see '
                              'docs)'))
Eureka_CDict.add('allapers', value=False, dtype=bool, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('Run S5 on all of the apertures considered in '
                              'S4? Otherwise will use newest output in the '
                              'inputdir'))
Eureka_CDict.add('manual_clip', value=None, dtype=None, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('A list of lists specifying the start and end '
                              'integration numbers for manual removal.'))
Eureka_CDict.add('fit_par', value='./S5_fit_par_template.epf', dtype=str,
                 options=None, source=__NAME__, user=True, active=True,
                 group=cgroup,
                 description='What fitting epf do you want to use?')
Eureka_CDict.add('fit_method', value='dynesty', dtype=str,
                 options=['lsq', 'emcee', 'dynesty', 'exoplanet', 'nuts'],
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('options are: lsq, emcee, dynesty, exoplanet, '
                              'nuts (can list multiple types separated by '
                              'commas)'))
Eureka_CDict.add('run_myfuncs', value='batman_tr,polynomial', dtype=str,
                 options=None, source=__NAME__, user=True, active=True,
                 group=cgroup,
                 description=('options are: batman_tr, batman_ecl, '
                              'catwoman_tr, sinusoid_pc, quasilambert_pc, '
                              'poet_tr, poet_ecl, poet_pc, fleck_tr, starry, '
                              'expramp, polynomial, step, xpos, ypos, xwidth, '
                              'ywidth, lorentzian, damped_osc, common_mode, '
                              'and GP (can list multiple types separated by '
                              'commas)'))
Eureka_CDict.add('compute_ltt', value=False, dtype=bool, options=[True, False],
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('options are: True (correct model for the light '
                              'travel time effect), or False (ignore the '
                              'light travel time effect)'))
Eureka_CDict.add('force_positivity', value=False, dtype=bool, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('Optional boolean for sinusoid_pc and poet_pc '
                              'models.  Set True to force positive phase '
                              'variations.'))
Eureka_CDict.add('use_generate_ld', value=None, dtype=None,
                 options=['exotic-ld', 'spam', 'None.', 'the', 'quadratic', '3-parameter'],
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('use the generated limb-darkening coefficients '
                              'from Stage 4? Options: exotic-ld, spam, None. '
                              'For exotic-ld and spam, the limb-darkening '
                              'laws available are linear, quadratic, '
                              '3-parameter and 4-parameter non-linear.'))
Eureka_CDict.add('ld_file', value=None, dtype=None, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('Fully qualified path to the location of a limb '
                              'darkening file that you want to use'))
Eureka_CDict.add('ld_file_white', value=None, dtype=None, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('Fully qualified path to the location of a limb '
                              'darkening file that you want to use for the '
                              'white-light light curve (required if ld_file '
                              'is not None and any EPF parameters are set to '
                              'white_free or white_fixed).'))
Eureka_CDict.add('recenter_ld_prior', value=True, dtype=bool, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('Set to True if you want your Gaussian prior on '
                              "the 'free' limb-darkening coefficients to be "
                              'centered around the model coefficients for '
                              'each wavelength.'))
Eureka_CDict.add('spotcon_file', value=None, dtype=None, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('Fully qualified path to the location of a spot '
                              'contrast model file that you want to use'))
Eureka_CDict.add('spotcon_file_white', value=None, dtype=None, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('Fully qualified path to the location of a spot '
                              'contrast model file that you want to use for '
                              'the white-light light curve (required if '
                              'spotcon_file is not None and any EPF '
                              'parameters are set to white_free or '
                              'white_fixed).'))
Eureka_CDict.add('recenter_spotcon_prior', value=True, dtype=bool, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('Set to True if you want your Gaussian prior on '
                              "the 'free' spot-contrast coefficients to be "
                              'centered around the model coefficients for '
                              'each wavelength.'))
Eureka_CDict.add('old_fitparams', value=None, dtype=None, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('filename relative to topdir that points to a '
                              'fitparams csv to resume where you left off '
                              '(set to None to start from scratch)'))
Eureka_CDict.add('lsq_method', value='Powell', dtype=str, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('The scipy.optimize.minimize optimization '
                              'method to use'))
Eureka_CDict.add('lsq_tol', value=1e-07, dtype=float, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('The tolerance for the scipy.optimize.minimize '
                              'optimization method'))
Eureka_CDict.add('lsq_maxiter', value=None, dtype=None, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('Maximum number of iterations to perform. '
                              'Depending on the method each iteration may use '
                              'several function evaluations. Set to None to '
                              'use the default value'))
Eureka_CDict.add('old_chain', value=None, dtype=None, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('Output folder relative to topdir that contains '
                              'an old emcee chain to resume where you left '
                              'off (set to None to start from scratch)'))
Eureka_CDict.add('lsq_first', value=True, dtype=bool, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('Initialize with an initial lsq call (can help '
                              'shorten burn-in, but turn off if lsq fails). '
                              'Only used if old_chain is None'))
Eureka_CDict.add('run_nsteps', value=1000, dtype=int, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=None)
Eureka_CDict.add('run_nwalkers', value=200, dtype=int, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=None)
Eureka_CDict.add('run_nburn', value=500, dtype=int, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('How many of run_nsteps should be discarded as '
                              'burn-in steps'))
Eureka_CDict.add('run_nlive', value='min', dtype=str, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description='Must be > ndim * (ndim + 1) // 2')
Eureka_CDict.add('run_bound', value='multi', dtype=str, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=None)
Eureka_CDict.add('run_sample', value='auto', dtype=str, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=None)
Eureka_CDict.add('run_tol', value=0.01, dtype=float, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=None)
Eureka_CDict.add('dynesty_checkpoint', value=False, dtype=bool, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('Enables periodic dynesty checkpoint files for '
                              'long runs'))
Eureka_CDict.add('dynesty_resume', value=False, dtype=bool, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description='Resumes dynesty from an existing checkpoint file')
Eureka_CDict.add('dynesty_checkpoint_every', value=600, dtype=int, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description='Seconds between dynesty checkpoint writes')
Eureka_CDict.add('old_dynesty_checkpoint', value=None, dtype=None, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('Previous dynesty checkpoint file or parent '
                              'folder relative to topdir; used when '
                              'dynesty_resume is True'))
Eureka_CDict.add('dynesty_maxiter', value=None, dtype=None, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description='Optional maximum number of dynesty iterations')
Eureka_CDict.add('dynesty_maxcall', value=None, dtype=None, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('Optional maximum number of dynesty likelihood '
                              'calls'))
Eureka_CDict.add('run_dynamic', value=False, dtype=bool, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('If False, use only dynesty static fitter; if '
                              'True, use dynamic dynesty fitter'))
Eureka_CDict.add('run_nlive_batch', value='auto', dtype=str, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('Number of live points per batch for dynamic '
                              "nested sampling; use int or 'auto' for minimum "
                              'safe default (max(25, run_nlive // 2)).'))
Eureka_CDict.add('run_pfrac', value=0.5, dtype=float, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('Fraction of samples from posterior vs prior '
                              'during refinement; 0.5 is balanced, higher '
                              'favors posterior precision, lower improves '
                              'evidence precision.'))
Eureka_CDict.add('exoplanet_first', value=False, dtype=bool, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('Initialize with an initial exoplanet optimizer '
                              'call (generally not recommended, but can '
                              'sometimes be helpful if your initial manual '
                              'guess is quite poor)'))
Eureka_CDict.add('tune', value=3000, dtype=int, options=None, source=__NAME__,
                 user=True, active=True, group=cgroup, description=None)
Eureka_CDict.add('draws', value=1500, dtype=int, options=None, source=__NAME__,
                 user=True, active=True, group=cgroup, description=None)
Eureka_CDict.add('chains', value=3, dtype=int, options=None, source=__NAME__,
                 user=True, active=True, group=cgroup, description=None)
Eureka_CDict.add('target_accept', value=0.85, dtype=float, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=None)
Eureka_CDict.add('kernel_inputs', value=['time'], dtype=list, options=['time'],
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description='options: time')
Eureka_CDict.add('kernel_class', value=['Matern32'], dtype=list,
                 options=['ExpSquared', 'Matern32', 'Exp', 'RationalQuadratic'],
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('options: ExpSquared, Matern32, Exp, '
                              'RationalQuadratic for george, Matern32 for '
                              'celerite (sums of kernels possible for george '
                              'separated by commas)'))
Eureka_CDict.add('GP_package', value='celerite', dtype=str,
                 options=['george', 'celerite'], source=__NAME__, user=True,
                 active=True, group=cgroup,
                 description='options: george, celerite')
Eureka_CDict.add('interp', value=False, dtype=bool, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('Should astrophysical model be interpolated '
                              '(useful for uneven sampling like that from '
                              'HST)'))
Eureka_CDict.add('isplots_S5', value=5, dtype=int, options=[1, 2, 3, 4, 5],
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('Generate few (1), some (3), or many (5) '
                              'figures (Options: 1 - 5)'))
Eureka_CDict.add('nbin_plot', value=None, dtype=None, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('The number of bins that should be used for '
                              'figures 5104 and 5304'))
Eureka_CDict.add('hide_plots', value=True, dtype=bool, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('If True, plots will automatically be closed '
                              'rather than popping up'))
Eureka_CDict.add('verbose', value=True, dtype=bool, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('If True, more details will be printed about '
                              'steps'))
Eureka_CDict.add('topdir', value=None, dtype='path', options=None,
                 source=__NAME__, user=True, active=False, group=cgroup,
                 description='E.g. /home/User/Data/JWST-Sim/NIRSpec/')
Eureka_CDict.add('inputdir', value='Stage4', dtype=str, options=None,
                 source=__NAME__, user=True, active=True, not_none=True,
                 group=cgroup,
                 description=('The folder containing the outputs from '
                              "Eureka!'s S4 pipeline (will be overwritten if "
                              'calling S4 and S5 sequentially)'))
Eureka_CDict.add('outputdir', value='Stage5', dtype=str, options=None,
                 source=__NAME__, user=True, active=True, not_none=True,
                 group=cgroup, description=None)

cgroup = 'STAGE6'
Eureka_CDict.add('allapers', value=False, dtype=bool, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('Run S6 on all of the apertures considered in '
                              'S5? Otherwise will use newest output in the '
                              'inputdir'))
Eureka_CDict.add('y_params',
                 value=['rp^2', 'u1', 'u2', 'c0', 'c1', 'scatter_mult'],
                 dtype=list, options=None, source=__NAME__, user=True,
                 active=True, group=cgroup,
                 description=('The parameter name as entered in your EPF file '
                              'in Stage 5. rp^2, 1/r1, 1/r4, fn (nightside '
                              'flux), pc_amp (phase curve amplitude), and '
                              'pc_offset (phase curve offset), '
                              'amp_order1/amp_order2 (first/second order '
                              'phase curve amplitude), and '
                              'offset_order1/offset_order2 (first/second '
                              'order phase curve offset) are also permitted. '
                              "Use 'morning_limb' or 'evening_limb' to plot "
                              'the corresponding limb when using Harmonica.'))
Eureka_CDict.add('y_labels', value=None, dtype=None, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('The formatted string you want on the y-label. '
                              'Set to None to use the default formatting.'))
Eureka_CDict.add('y_label_units', value=None, dtype=None, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('The formatted string for the units you want on '
                              'the y-label - e.g., (ppm), (seconds), '
                              "'(days$^{-1})$', etc.. Set to None to "
                              'automatically add any implied units from '
                              "y_scalars (e.g. ppm), or set to '' to force no "
                              'units.'))
Eureka_CDict.add('y_scalars', value=[100, 1, 1, 1, 1, 1], dtype=list,
                 options=None, source=__NAME__, user=True, active=True,
                 group=cgroup,
                 description=('Can be used to convert to percent (100), ppm '
                              '(1e6), etc.'))
Eureka_CDict.add('x_unit', value='um', dtype=str, options=None, source=__NAME__,
                 user=True, active=True, group=cgroup,
                 description=('Options include any measurement of light '
                              'included in astropy.units.spectral (e.g. um, '
                              'nm, Hz, etc.)'))
Eureka_CDict.add('ncol', value=4, dtype=int, options=None, source=__NAME__,
                 user=True, active=True, group=cgroup,
                 description=('The number of columns you want in your LaTeX '
                              'formatted tables'))
Eureka_CDict.add('star_Rad', value=0.6506, dtype=float, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description='The radius of the star in units of solar radii')
Eureka_CDict.add('planet_Teq', value=1400, dtype=int, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('The equilibrium temperature of the planet in '
                              'units of Kelvin'))
Eureka_CDict.add('planet_Mass', value=2, dtype=int, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=("The planet's mass in units of Jupiter masses "
                              '(used to calculate surface gravity)'))
Eureka_CDict.add('planet_Rad', value=None, dtype=None, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=("The planet's radius in units of Jupiter radii "
                              '(used to calculate surface gravity); Set to '
                              'None to use the average fitted radius'))
Eureka_CDict.add('planet_mu', value=2.3, dtype=float, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('The mean molecular mass of the atmosphere (in '
                              'atomic mass units)'))
Eureka_CDict.add('planet_R0', value=None, dtype=None, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('The reference radius (in Jupiter radii) for '
                              'the scale height measurement; Set to None to '
                              'use the mean fitted radius'))
Eureka_CDict.add('isplots_S6', value=5, dtype=int, options=[1, 2, 3, 4, 5],
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('Generate few (1), some (3), or many (5) '
                              'figures (Options: 1 - 5)'))
Eureka_CDict.add('hide_plots', value=True, dtype=bool, options=None,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=('If True, plots will automatically be closed '
                              'rather than popping up'))
Eureka_CDict.add('topdir', value=None, dtype='path', options=None,
                 source=__NAME__, user=True, active=False, group=cgroup,
                 description='E.g. /home/User/Data/JWST-Sim/NIRSpec/')
Eureka_CDict.add('inputdir', value='Stage5', dtype=str, options=None,
                 source=__NAME__, user=True, active=True, not_none=True,
                 group=cgroup,
                 description=('The folder containing the outputs from '
                              "Eureka!'s S5 pipeline (will be overwritten if "
                              'calling S5 and S6 sequentially)'))
Eureka_CDict.add('outputdir', value='Stage6', dtype=str, options=None,
                 source=__NAME__, user=True, active=True, not_none=True,
                 group=cgroup, description=None)
# <<< END AUTO-GENERATED ECF CONSTANTS <<<


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

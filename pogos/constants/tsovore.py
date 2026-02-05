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

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'pogos.constants.constants.py'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__

# Constants definition
Const = constant_functions.Const
ConstDict = constant_functions.ConstantsDict


# =============================================================================
# General constants for TSOVORE
# =============================================================================
TSOVORE_CDict = ConstDict(__NAME__)

# set the title for output yaml files
TSOVORE_CDict.title = TSOVORE_CDict.yaml_title('TSOVORE',
                                   setup_program=None,
                                   version=base.TSOVORE_VERSION,
                                   date=base.TSOVORE_DATE)


# =============================================================================
# General settings (generally don't touch these)
# =============================================================================
# set the group for all WLCTA constants
cgroup = 'GENERAL'
TSOVORE_CDict.add_group(cgroup, description='General configs for TSOVORE',
                        source=__NAME__, user=True, active=True)
# add the subdirectory (to be used when default path required)
TSOVORE_CDict.add('SUBDIRECTORY', value=None, dtype=str, source=__NAME__,
                  user=True, active=True, group=cgroup,
                  description='The sub-directory to use for this TSOVORE run. '
                              'This should be descriptive and unique. '
                              '\nIt should contain no whitespaces or special '
                              'characters other than underscoes.'
                              '\nAll miriam data will be stored in '
                              '{GLOBAL.DATA_PATH}/tsovore/{SUBDIRECTORY}/'
                             '\n\nWe suggest {OBJNAME}-{INST.MODE}-{STEP}-{YYYYMMDD}')

# define what we are running through SORBET
TSOVORE_CDict.add('DESCRIPTION', value='', dtype=str, source=__NAME__,
                  user=True, active=True, group=cgroup,
                  description='Description of the POGOS run e.g. '
                              'object name, date of observation, is it a '
                              'transit or an eclipse etc.')

# =============================================================================
# Path settings
# =============================================================================
cgroup = 'PATHS'
TSOVORE_CDict.add_group(cgroup, description='Definition of paths (normally '
                                           'created at run time but can be '
                                           'overridden)',
                        source=__NAME__, user=False, active=False)
TSOVORE_CDict.add_group(cgroup, description='Definition of paths (normally '
                                           'created at run time but can be '
                                           'overridden)',
                       source=__NAME__, user=False, active=False)
# Input data folder or path to the input folderinput path
TSOVORE_CDict.add('INPUT_PATH', value='inputs', dtype=str, source=__NAME__,
                 user=False, active=False, group=cgroup,
                 description='Input data folder or path to the input folder.')

# Temporary results folder
TSOVORE_CDict.add('TEMP_PATH', value='temporary', dtype=str,
                 source=__NAME__,
                 user=False, active=False,
                 group=cgroup,
                 description='Temporary result folder or path to the '
                             'output folder.'
                             '\nIf this is an aboslute path it will be '
                             'used as is'
                             '\n otherwise it will be relative to '
                             'GLOBAL.DATA_PATH/tsovore/')

# Output results folder
TSOVORE_CDict.add('OUTPUT_PATH', value='outputs', dtype=str,
                 source=__NAME__,
                 user=False, active=False,
                 group=cgroup,
                 description='Output result folder or path to the '
                             'output folder.'
                             '\nIf this is an aboslute path it will '
                             'be used as is'
                             '\n otherwise it will be relative to '
                             'GLOBAL.DATA_PATH/tsovore/')
# the plot path
TSOVORE_CDict.add('PLOT_PATH', value='plots', dtype=str,
                 source=__NAME__, active=False, user=False, group=cgroup,
                 description='The plot path')


# =============================================================================
# Definition of inputs related to plots
# =============================================================================
cgroup = 'PLOTS'
TSOVORE_CDict.add_group(cgroup,
                       description='Definition of inputs related to plots',
                       source=__NAME__, user=True, active=True)
# -----------------------------------------------------------------------------
# Or you can use the following to always show plots regardless of the username
TSOVORE_CDict.add('SHOW', value=False, dtype=bool,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description='Or you can use the following to always show '
                             'plots regardless of the username')
# -----------------------------------------------------------------------------
# output(s) type of figure
TSOVORE_CDict.add('FIGURE_TYPES', value=['png', 'pdf'], dtype=list, dtypei=str,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description='output(s) type of figure')
# -----------------------------------------------------------------------------
# Whether to plot the pedestal in the correction plots
TSOVORE_CDict.add('CORR_PLOT_PEDESTAL', value=True, dtype=bool,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description='Whether to plot the pedestal in the correction ')


# =============================================================================
# Input settings
# =============================================================================
cgroup = 'INPUTS'
TSOVORE_CDict.add_group(cgroup, source=__NAME__, user=True, active=True,
                       description='Definition of inputs related to the data')
# -----------------------------------------------------------------------------
# Instrument mode i.e. JWST.NIRISS.SOSS or JWST.NIRISS.PRISM
TSOVORE_CDict.add('INSTRUMENTMODE', value=None, dtype=str, not_none=True,
                  source=__NAME__, user=True, active=True,
                  options=base.INSTRUMENTS,
                  cmd_arg='instmode', group=cgroup,
                  description='Instrument mode e.g. one of the following: {0}'
                              ''.format('\n\t'.join(base.INSTRUMENTS)))
# -----------------------------------------------------------------------------
# Raw files
fdesc = ('List of files to be processed in form: '
         '\nFILES:\n - file1\n - file2\n - file3'
         '\n\nBy default these should be placed in '
         '{GLOBAL.DATA_PATH}/{MIRIAM.PATHS.INTPUT_PATH}/'
         '\n or whatever is set in {TSOVORE.PATHS.INTPUT_PATH} (if absolute)')
TSOVORE_CDict.add('FILES', value=None, dtype=list, dtypei=str, not_none=False,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=fdesc)
# -----------------------------------------------------------------------------
# Whether to remove intermediate files
TSOVORE_CDict.add('REMOVE_INTERMEDIATES', value=True, dtype=bool,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description='Whether to remove intermediate files')
# -----------------------------------------------------------------------------
# Whether to skip files that have already been processed
TSOVORE_CDict.add('SKIP_PROCESSED_FILES', value=True, dtype=bool,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description='Whether to skip files that have already been '
                             'processed')

# =============================================================================
# Science step settings
# =============================================================================
cgroup = 'STEP'
TSOVORE_CDict.add_group(cgroup, source=__NAME__, user=True, active=True,
                       description='Settings for the science steps')
# -----------------------------------------------------------------------------
STEPS = ['INITIALIZE_DETECTOR_DATA',
         'APPLY_INTERPIXEL_CAPACITANCE',
         'SUBTRACT_SUPERBIAS',
         'APPLY_REFERENCE_PIXEL_CORRECTION',
         'REMOVE_FIRST_FRAME_SIGNAL',
         'REMOVE_LAST_FRAME_SIGNAL',
         'CORRECT_RESET_ANOMALY',
         'APPLY_LINEARITY_CORRECTION',
         'APPLY_RSCD_CORRECTION',
         'SUBTRACT_DARK_CURRENT',
         'CORRECT_PERSISTENCE',
         'CORRECT_CHARGE_MIGRATION',
         'DETECT_AND_FLAG_JUMPS',
         'PICTURE_FRAME_STEP',
         'REMOVE_FLICKER_NOISE',
         'FIT_SIGNAL_RAMPS',
         'APPLY_GAIN_SCALING',
         'SUBTRACT_BACKGROUND',
         'ASSIGN_WCS_SOLUTION',
         'EXTRACT_2D_SPECTRUM',
         'SRCTYPE_DETERMINATION',
         'CORRECT_STRAY_LIGHT',
         'APPLY_FLAT_FIELD',
         'CORRECT_FRINGE',
         'CORRECT_PATH_LOSS',
         'CORRECT_BAR_SHADOW',
         'CORRECT_WFSS_CONTAMINATION',
         'CORRECT_WAVELENGTH',
         'SUBTRACT_MASTER_BACKGROUND',
         'MEASURE_TARGET_CENTROID',
         'CORRECT_RESIDUAL_FRINGE',
         'EXTRACT_1D_SPECTRUM',
         'APPLY_PHOTOMETRIC_CALIBRATION',
         'RESAMPLE_IMAGES']

# default flavour for each step
DEFAULT_FLAVOURS = dict()
DEFAULT_FLAVOURS['INITIALIZE_DETECTOR_DATA'] = 'jwst'
DEFAULT_FLAVOURS['APPLY_INTERPIXEL_CAPACITANCE'] = 'jwst'
DEFAULT_FLAVOURS['SUBTRACT_SUPERBIAS'] = 'jwst'
DEFAULT_FLAVOURS['APPLY_REFERENCE_PIXEL_CORRECTION'] = 'jwst'
DEFAULT_FLAVOURS['REMOVE_FIRST_FRAME_SIGNAL'] = 'jwst'
DEFAULT_FLAVOURS['REMOVE_LAST_FRAME_SIGNAL'] = 'jwst'
DEFAULT_FLAVOURS['CORRECT_RESET_ANOMALY'] = 'jwst'
DEFAULT_FLAVOURS['APPLY_LINEARITY_CORRECTION'] = 'jwst'
DEFAULT_FLAVOURS['APPLY_RSCD_CORRECTION'] = 'jwst'
DEFAULT_FLAVOURS['SUBTRACT_DARK_CURRENT'] = 'jwst'
DEFAULT_FLAVOURS['CORRECT_PERSISTENCE'] = 'jwst'
DEFAULT_FLAVOURS['CORRECT_CHARGE_MIGRATION'] = 'jwst'
DEFAULT_FLAVOURS['DETECT_AND_FLAG_JUMPS'] = 'jwst'
DEFAULT_FLAVOURS['PICTURE_FRAME_STEP'] = 'jwst'
DEFAULT_FLAVOURS['REMOVE_FLICKER_NOISE'] = 'jwst'
DEFAULT_FLAVOURS['FIT_SIGNAL_RAMPS'] = 'jwst'
DEFAULT_FLAVOURS['APPLY_GAIN_SCALING'] = 'jwst'
DEFAULT_FLAVOURS['SUBTRACT_BACKGROUND'] = 'jwst'
DEFAULT_FLAVOURS['ASSIGN_WCS_SOLUTION'] = 'jwst'
DEFAULT_FLAVOURS['EXTRACT_2D_SPECTRUM'] = 'jwst'
DEFAULT_FLAVOURS['SRCTYPE_DETERMINATION'] = 'jwst'
DEFAULT_FLAVOURS['CORRECT_STRAY_LIGHT'] = 'jwst'
DEFAULT_FLAVOURS['APPLY_FLAT_FIELD'] = 'jwst'
DEFAULT_FLAVOURS['CORRECT_FRINGE'] = 'jwst'
DEFAULT_FLAVOURS['CORRECT_PATH_LOSS'] = 'jwst'
DEFAULT_FLAVOURS['CORRECT_BAR_SHADOW'] = 'jwst'
DEFAULT_FLAVOURS['CORRECT_WFSS_CONTAMINATION'] = 'jwst'
DEFAULT_FLAVOURS['CORRECT_WAVELENGTH'] = 'jwst'
DEFAULT_FLAVOURS['SUBTRACT_MASTER_BACKGROUND'] = 'jwst'
DEFAULT_FLAVOURS['MEASURE_TARGET_CENTROID'] = 'jwst'
DEFAULT_FLAVOURS['CORRECT_RESIDUAL_FRINGE'] = 'jwst'
DEFAULT_FLAVOURS['EXTRACT_1D_SPECTRUM'] = 'jwst'
DEFAULT_FLAVOURS['APPLY_PHOTOMETRIC_CALIBRATION'] = 'jwst'
DEFAULT_FLAVOURS['RESAMPLE_IMAGES'] = 'jwst'

# Default run state for each step (based on JWST pipeline defaults)
DEFAULT_RUN = dict()
DEFAULT_RUN['INITIALIZE_DETECTOR_DATA'] = True
DEFAULT_RUN['APPLY_INTERPIXEL_CAPACITANCE'] = True
DEFAULT_RUN['SUBTRACT_SUPERBIAS'] = True
DEFAULT_RUN['APPLY_REFERENCE_PIXEL_CORRECTION'] = True
DEFAULT_RUN['REMOVE_FIRST_FRAME_SIGNAL'] = True
DEFAULT_RUN['REMOVE_LAST_FRAME_SIGNAL'] = True
DEFAULT_RUN['CORRECT_RESET_ANOMALY'] = True
DEFAULT_RUN['APPLY_LINEARITY_CORRECTION'] = True
DEFAULT_RUN['APPLY_RSCD_CORRECTION'] = True
DEFAULT_RUN['SUBTRACT_DARK_CURRENT'] = True
DEFAULT_RUN['CORRECT_PERSISTENCE'] = False  # Always commented out
DEFAULT_RUN['CORRECT_CHARGE_MIGRATION'] = True
DEFAULT_RUN['DETECT_AND_FLAG_JUMPS'] = True
DEFAULT_RUN['PICTURE_FRAME_STEP'] = True
DEFAULT_RUN['REMOVE_FLICKER_NOISE'] = True
DEFAULT_RUN['FIT_SIGNAL_RAMPS'] = True
DEFAULT_RUN['APPLY_GAIN_SCALING'] = True
DEFAULT_RUN['SUBTRACT_BACKGROUND'] = True
DEFAULT_RUN['ASSIGN_WCS_SOLUTION'] = True
DEFAULT_RUN['EXTRACT_2D_SPECTRUM'] = True
DEFAULT_RUN['SRCTYPE_DETERMINATION'] = True
DEFAULT_RUN['CORRECT_STRAY_LIGHT'] = True
DEFAULT_RUN['APPLY_FLAT_FIELD'] = True
DEFAULT_RUN['CORRECT_FRINGE'] = True
DEFAULT_RUN['CORRECT_PATH_LOSS'] = True
DEFAULT_RUN['CORRECT_BAR_SHADOW'] = True
DEFAULT_RUN['CORRECT_WFSS_CONTAMINATION'] = True
DEFAULT_RUN['CORRECT_WAVELENGTH'] = True
DEFAULT_RUN['SUBTRACT_MASTER_BACKGROUND'] = True
DEFAULT_RUN['MEASURE_TARGET_CENTROID'] = False  # Commented out in MIRI LRS
DEFAULT_RUN['CORRECT_RESIDUAL_FRINGE'] = True
DEFAULT_RUN['EXTRACT_1D_SPECTRUM'] = True
DEFAULT_RUN['APPLY_PHOTOMETRIC_CALIBRATION'] = True
DEFAULT_RUN['RESAMPLE_IMAGES'] = True

# -----------------------------------------------------------------------------
# Step description
STEP_DESCRIPTION = ('Whether to perform the step: {0}. '
                    'Each step should contiain the following:'
                    '\n - RUN: bool, whether to run the step'
                    '\n - MODE: str, the mode to use for the step'
                    '\n - KWARGS: dict, any additional keyword arguments')

STEP_DESCS = dict()
STEP_DESCS['INITIALIZE_DETECTOR_DATA'] = dict()
STEP_DESCS['INITIALIZE_DETECTOR_DATA']['jwst'] = """
No kwargs for initialization step
"""

STEP_DESCS['DETECT_AND_FLAG_JUMPS'] = dict()
STEP_DESCS['DETECT_AND_FLAG_JUMPS']['jwst'] = """
Kwargs for jump detection:
- rejection_threshold: float, the sigma threshold for jump detection
- max_shower_amplitude: float
- three_group_rejection_threshold: float
- four_group_rejection_threshold:  float
- only_use_ints: bool 
"""
# -----------------------------------------------------------------------------
# Step output filenames (for skipping)
STEP_SUFFIX = dict()
# Detector1 level steps (calwebb_detector1.py)
STEP_SUFFIX['INITIALIZE_DETECTOR_DATA'] = '_saturationstep.fits'
STEP_SUFFIX['APPLY_INTERPIXEL_CAPACITANCE'] = '_ipcstep.fits'
STEP_SUFFIX['SUBTRACT_SUPERBIAS'] = '_superbiasstep.fits'
STEP_SUFFIX['APPLY_REFERENCE_PIXEL_CORRECTION'] = '_refpixstep.fits'
STEP_SUFFIX['APPLY_RSCD_CORRECTION'] = '_rscdstep.fits'
STEP_SUFFIX['REMOVE_FIRST_FRAME_SIGNAL'] = '_firstframestep.fits'
STEP_SUFFIX['REMOVE_LAST_FRAME_SIGNAL'] = '_lastframestep.fits'
STEP_SUFFIX['APPLY_LINEARITY_CORRECTION'] = '_linearitystep.fits'
STEP_SUFFIX['SUBTRACT_DARK_CURRENT'] = '_darkcurrentstep.fits'
STEP_SUFFIX['CORRECT_RESET_ANOMALY'] = '_resetstep.fits'
STEP_SUFFIX['CORRECT_PERSISTENCE'] = '_persistencestep.fits'
STEP_SUFFIX['CORRECT_CHARGE_MIGRATION'] = '_chargemigrationstep.fits'
STEP_SUFFIX['DETECT_AND_FLAG_JUMPS'] = '_jump.fits'
STEP_SUFFIX['PICTURE_FRAME_STEP'] = '_pictureframestep.fits'
STEP_SUFFIX['REMOVE_FLICKER_NOISE'] = '_cleanflickernoisestep.fits'
STEP_SUFFIX['FIT_SIGNAL_RAMPS'] = '_rampfitstep.fits'
STEP_SUFFIX['APPLY_GAIN_SCALING'] = '_gainscalestep.fits'
# Image2/Spec2 level steps (calwebb_image2.py / calwebb_spec2.py)
STEP_SUFFIX['SUBTRACT_BACKGROUND'] = '_backgroundstep.fits'
STEP_SUFFIX['ASSIGN_WCS_SOLUTION'] = '_assignwcsstep.fits'
STEP_SUFFIX['EXTRACT_2D_SPECTRUM'] = '_extract2dstep.fits'
STEP_SUFFIX['EXTRACT_1D_SPECTRUM'] = '_extract1dstep.fits'
STEP_SUFFIX['SRCTYPE_DETERMINATION'] = '_srctypestep.fits'
STEP_SUFFIX['CORRECT_STRAY_LIGHT'] = '_straylightstep.fits'
STEP_SUFFIX['APPLY_FLAT_FIELD'] = '_flatfieldstep.fits'
STEP_SUFFIX['CORRECT_FRINGE'] = '_fringestep.fits'
STEP_SUFFIX['CORRECT_PATH_LOSS'] = '_pathlossstep.fits'
STEP_SUFFIX['CORRECT_BAR_SHADOW'] = '_barshadowstep.fits'
STEP_SUFFIX['CORRECT_WFSS_CONTAMINATION'] = '_wfsscontamstep.fits'
STEP_SUFFIX['CORRECT_WAVELENGTH'] = '_wavecorrstep.fits'
STEP_SUFFIX['SUBTRACT_MASTER_BACKGROUND'] = '_masterbackgroundstep.fits'
STEP_SUFFIX['MEASURE_TARGET_CENTROID'] = '_targcentroidstep.fits'
STEP_SUFFIX['CORRECT_RESIDUAL_FRINGE'] = '_residualfringestep.fits'
STEP_SUFFIX['APPLY_PHOTOMETRIC_CALIBRATION'] = '_photomstep.fits'
STEP_SUFFIX['RESAMPLE_IMAGES'] = '_resamplestep.fits'

# -----------------------------------------------------------------------------
# Loop around all steps to create constant
for step in STEPS:
    # setup each step value
    value = dict()
    value['RUN'] = DEFAULT_RUN.get(step, False)
    value['FLAVOUR'] = DEFAULT_FLAVOURS.get(step, 'None')
    value['KWARGS'] = dict()
    value['SUFFIX'] = STEP_SUFFIX.get(step, None)
    # deal with additional step descriptions
    desc = STEP_DESCRIPTION
    if value['FLAVOUR'] in STEP_DESCS:
        if step in STEP_DESCS[value['FLAVOUR']]:
            desc = STEP_DESCRIPTION + '\n' + STEP_DESCS[value['FLAVOUR']]
    # give the step name
    step_name = step.replace('_', ' ').title()
    # push into a normal POGOS constant
    TSOVORE_CDict.add(step, value=value, dtype=dict,
                      source=__NAME__, user=True, active=True,
                      group=cgroup,
                      description=desc.format(step_name))


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

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
                 user=False, active=False, group=cgroup,
                 description='Temporary result folder or path to the output folder.'
                             '\nIf this is an aboslute path it will be used as is'
                             '\n otherwise it will be relative to '
                             'GLOBAL.DATA_PATH/tsovore/')

# Output results folder
TSOVORE_CDict.add('OUTPUT_PATH', value='outputs', dtype=str,
                 source=__NAME__,
                 user=False, active=False, group=cgroup,
                 description='Output result folder or path to the output folder.'
                             '\nIf this is an aboslute path it will be used as is'
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
         'REMOVE_FIRST_FRAME_SIGNAL',
         'REMOVE_LAST_FRAME_SIGNAL',
         'CORRECT_RESET_ANOMALY',
         'APPLY_LINEARITY_CORRECTION',
         'APPLY_RSCD_CORRECTION',
         'SUBTRACT_DARK_CURRENT',
         'APPLY_REFERENCE_PIXEL_CORRECTION',
         'CORRECT_CHARGE_MIGRATION',
         'DETECT_AND_FLAG_JUMPS',
         'REMOVE_FLICKER_NOISE',
         'FIT_SIGNAL_RAMPS',
         'APPLY_GAIN_SCALING',
         'SUBTRACT_BACKGROUND',
         'ASSIGN_WCS_SOLUTION',
         'APPLY_FLAT_FIELD',
         'APPLY_PHOTOMETRIC_CALIBRATION']
# default mode for each step
DEFAULT_MODES = dict()
DEFAULT_MODES['INITIALIZE_DETECTOR_DATA'] = 'jwst'
DEFAULT_MODES['APPLY_INTERPIXEL_CAPACTIANCE'] = 'jwst'
DEFAULT_MODES['REMOVE_FIRST_FRAME_SIGNAL'] = 'jwst'
DEFAULT_MODES['REMOVE_LAST_FRAME_SIGNAL'] = 'jwst'
DEFAULT_MODES['CORRECT_RESET_ANOMALY'] = 'jwst'
DEFAULT_MODES['APPLY_LINEARITY_CORRECTION'] = 'jwst'
DEFAULT_MODES['APPLY_RSCD_CORRECTION'] = 'jwst'
DEFAULT_MODES['SUBTRACT_DARK_CURRENT'] = 'jwst'
DEFAULT_MODES['APPLY_REFERENCE_PIXEL_CORRECTION'] = 'jwst'
DEFAULT_MODES['CORRECT_CHARGE_MIGRATION'] = 'tsovore'
DEFAULT_MODES['DETECT_AND_FLAG_JUMPS'] = 'jwst'
DEFAULT_MODES['REMOVE_FLICKER_NOISE'] = 'tsovore'
DEFAULT_MODES['FIT_SIGNAL_RAMPS'] = 'jwst'
DEFAULT_MODES['APPLY_GAIN_SCALING'] = 'jwst'
DEFAULT_MODES['SUBTRACT_BACKGROUND'] = 'tsovore'
DEFAULT_MODES['ASSIGN_WCS_SOLUTION'] = 'jwst'
DEFAULT_MODES['APPLY_FLAT_FIELD'] = 'jwst'
DEFAULT_MODES['APPLY_PHOTOMETRIC_CALIBRATION'] = 'jwst'

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
STEP_SUFFIX['INITIALIZE_DETECTOR_DATA'] = '_saturationstep.fits'
STEP_SUFFIX['APPLY_INTERPIXEL_CAPACITANCE'] = '_ipcstep.fits'
STEP_SUFFIX['REMOVE_FIRST_FRAME_SIGNAL'] = '_firstframestep.fits'
STEP_SUFFIX['REMOVE_LAST_FRAME_SIGNAL'] = '_lastframestep.fits'
STEP_SUFFIX['CORRECT_RESET_ANOMALY'] = '_resetstep.fits'
STEP_SUFFIX['APPLY_LINEARITY_CORRECTION'] = '_linearitystep.fits'
STEP_SUFFIX['APPLY_RSCD_CORRECTION'] = '_rscdstep.fits'
STEP_SUFFIX['SUBTRACT_DARK_CURRENT'] = '_darkcurrentstep.fits'
STEP_SUFFIX['APPLY_REFERENCE_PIXEL_CORRECTION'] = '_refpixstep.fits'
STEP_SUFFIX['CORRECT_CHARGE_MIGRATION'] = '_chargemigrationstep.fits' # TODO: Check
STEP_SUFFIX['DETECT_AND_FLAG_JUMPS'] = '_jump.fits'
STEP_SUFFIX['REMOVE_FLICKER_NOISE'] = '_flickernoisestep.fits' # TODO: Check
STEP_SUFFIX['FIT_SIGNAL_RAMPS'] = '_1_rampfitstep.fits' # TODO: 0 or 1?
STEP_SUFFIX['APPLY_GAIN_SCALING'] = '_1_gainscalestep.fits' # TODO: 0 or 1?
STEP_SUFFIX['SUBTRACT_BACKGROUND'] = '_1_backgroundstep.fits' # TODO: Check
STEP_SUFFIX['ASSIGN_WCS_SOLUTION'] = '_1_assignwcsstep.fits' # TODO: 0 or 1?
STEP_SUFFIX['APPLY_FLAT_FIELD'] = '_1_flatfieldstep.fits' # TODO: 0 or 1?
STEP_SUFFIX['APPLY_PHOTOMETRIC_CALIBRATION'] = '_1_photomstep.fits' # TODO: 0 or 1?

# -----------------------------------------------------------------------------
# loop around all steps to create constant
for step in STEPS:
    # setup each step value
    value = dict()
    value['RUN'] = True
    value['MODE'] = DEFAULT_MODES.get(step, 'None')
    value['KWARGS'] = dict()
    value['SUFFIX'] = STEP_SUFFIX.get(step, None)
    # deal with additional step descriptions
    desc = STEP_DESCRIPTION
    if value['MODE'] in STEP_DESCS:
        if step in STEP_DESCS[value['MODE']]:
            desc = STEP_DESCRIPTION + '\n' + STEP_DESCS[value['MODE']]
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

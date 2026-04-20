#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2024-10-29 at 09:30

@author: cook
"""
from stpipe.entry_points import STEPS_GROUP

from aperocore.constants import constant_functions

from pogos.core import base
from pogos.tsovore.core import misc as ts_misc

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
# set the group for all general constants
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
# Create a Step list to manage adding steps
STEPS = ts_misc.StepList()


# -----------------------------------------------------------------------------
# Detector1 level steps (calwebb_detector1.py)
# -----------------------------------------------------------------------------
# description for initialize detector data
jwst_initialize_desc = 'No kwargs for initialization step'
# Initialize detector data
STEPS.add_step(name='INITIALIZE_DETECTOR_DATA',
               flavour='jwst', fname='_saturationstep.fits',
               ftype='suffix', run=True,
               modes=STEPS.all_modes(),
               descs=dict(jwst=jwst_initialize_desc))
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Apply interpixel capacitance
STEPS.add_step(name='APPLY_INTERPIXEL_CAPACITANCE',
               flavour='jwst', fname='_ipcstep.fits',
               ftype='suffix', run=True,
               modes=STEPS.not_modes('JWST.NIRISS.SOSS'))
# Remove first frame signal
STEPS.add_step(name='REMOVE_FIRST_FRAME_SIGNAL',
               flavour='jwst', fname='_firstframestep.fits',
               ftype='suffix', run=True,
               modes=STEPS.not_modes('JWST.NIRISS.SOSS'))
# Remove last frame signal
STEPS.add_step(name='REMOVE_LAST_FRAME_SIGNAL',
               flavour='jwst', fname='_lastframestep.fits',
               ftype='suffix', run=True,
               modes=STEPS.not_modes('JWST.NIRISS.SOSS'))
# Correct reset anomaly
STEPS.add_step(name='CORRECT_RESET_ANOMALY',
               flavour='jwst', fname='_resetstep.fits',
               ftype='suffix', run=True,
               modes=STEPS.not_modes('JWST.NIRISS.SOSS'))
# Apply linearity correction
STEPS.add_step(name='APPLY_LINEARITY_CORRECTION',
               flavour='jwst', fname='_linearitystep.fits',
               ftype='suffix', run=True,
               modes=STEPS.not_modes('JWST.NIRISS.SOSS'))
# Apply RSCD correction
STEPS.add_step(name='APPLY_RSCD_CORRECTION',
               flavour='jwst', fname='_rscdstep.fits',
               ftype='suffix', run=True,
               modes=STEPS.not_modes('JWST.NIRISS.SOSS'))
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Build deepstack spectrace product
STEPS.add_step(name='GET_SPECTRACE',
               flavour='tso', fname='_spectrace0.fits',
               ftype='common', run=True,
               modes=['JWST.NIRISS.SOSS'])
# Stack multisegment deepstack products
STEPS.add_step(name='STACK_MULTISEGMENTS',
               flavour='tso', fname='_deepstack.fits',
               ftype='common', run=True,
               modes=['JWST.NIRISS.SOSS'])
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Apply reference pixel correction
STEPS.add_step(name='APPLY_REFERENCE_PIXEL_CORRECTION',
               flavour='jwst', fname='_refpixstep.fits',
               ftype='suffix', run=True,
               modes=STEPS.all_modes())
# Subtract dark current
STEPS.add_step(name='SUBTRACT_DARK_CURRENT',
               flavour='jwst', fname='_darkcurrentstep.fits',
               ftype='suffix', run=True,
               modes=STEPS.not_modes('JWST.NIRISS.SOSS'))
# Correct persistence
STEPS.add_step(name='CORRECT_PERSISTENCE',
               flavour='jwst', fname='_persistencestep.fits',
               ftype='suffix', run=False,
               modes=STEPS.not_modes('JWST.NIRISS.SOSS',
                                     'JWST.MIRI.IMAGING'))
# Correct charge migration
STEPS.add_step(name='CORRECT_CHARGE_MIGRATION',
               flavour='jwst', fname='_chargemigrationstep.fits',
               ftype='suffix', run=True,
               modes=STEPS.not_modes('JWST.NIRISS.SOSS'))
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# description for jump detection kwargs (flavour=jwst)
jwst_jump_desc = ('Kwargs for jump detection:\n'
                  '- rejection_threshold: float, the sigma threshold '
                  'for jump detection\n'
                  '- max_shower_amplitude: float\n'
                  '- three_group_rejection_threshold: float\n'
                  '- four_group_rejection_threshold:  float\n'
                  '- only_use_ints: bool')
# Detect and flag jumps
STEPS.add_step(name='DETECT_AND_FLAG_JUMPS',
               flavour='jwst', fname='_jump.fits',
               ftype='suffix', run=True,
               descs=dict(jwst=jwst_jump_desc),
               modes=STEPS.all_modes())
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Run picture frame correction
STEPS.add_step(name='PICTURE_FRAME_STEP',
               flavour='jwst', fname='_pictureframestep.fits',
               ftype='suffix', run=True,
               modes=STEPS.not_modes('JWST.NIRISS.SOSS'))
# Remove flicker noise
STEPS.add_step(name='REMOVE_FLICKER_NOISE',
               flavour='jwst', fname='_cleanflickernoisestep.fits',
               ftype='suffix', run=True,
               modes=STEPS.not_modes('JWST.NIRISS.SOSS'))
# Fit signal ramps
STEPS.add_step(name='FIT_SIGNAL_RAMPS',
               flavour='jwst', fname='_1_rampfitstep.fits',
               ftype='suffix', run=True,
               modes=STEPS.all_modes())
# Apply gain scaling
STEPS.add_step(name='APPLY_GAIN_SCALING',
               flavour='jwst', fname='_1_gainscalestep.fits',
               ftype='suffix', run=True,
               modes=STEPS.not_modes('JWST.MIRI.IMAGING'))
# -----------------------------------------------------------------------------
# Image2/Spec2 level steps (calwebb_image2.py / calwebb_spec2.py)
# -----------------------------------------------------------------------------
# Subtract background
STEPS.add_step(name='SUBTRACT_BACKGROUND',
               flavour='jwst', fname='_backgroundstep.fits',
               ftype='suffix', run=True,
               modes=STEPS.not_modes('JWST.NIRISS.SOSS'))
# Assign WCS solution
STEPS.add_step(name='ASSIGN_WCS_SOLUTION',
               flavour='jwst', fname='_assignwcsstep.fits',
               ftype='suffix', run=True,
               modes=STEPS.all_modes())
# Apply flat field
STEPS.add_step(name='APPLY_FLAT_FIELD',
               flavour='jwst', fname='_flatfieldstep.fits',
               ftype='suffix', run=True,
               modes=STEPS.all_modes())
# SOSS Background correction
STEPS.add_step(name='SOSS_CORRECT_BADPIX',
               flavour='tso', fname='_badpixinterp.fits',
               ftype='suffix', run=True,
               modes=['JWST.NIRISS.SOSS'])
# Determine source type
STEPS.add_step(name='SRCTYPE_DETERMINATION',
               flavour='jwst', fname='_sourcetypestep.fits',
               ftype='suffix', run=True,
               modes=STEPS.not_modes('JWST.MIRI.IMAGING'))
# Extract 1D spectrum
STEPS.add_step(name='EXTRACT_1D_SPECTRUM',
               flavour='jwst', fname='_extract1dstep.fits',
               ftype='suffix', run=True,
               modes=STEPS.not_modes('JWST.MIRI.IMAGING'))
# Apply photometric calibration
STEPS.add_step(name='APPLY_PHOTOMETRIC_CALIBRATION',
               flavour='jwst', fname='_photomstep.fits',
               ftype='suffix', run=True,
               modes=STEPS.all_modes())

# -----------------------------------------------------------------------------
# Not used?
# -----------------------------------------------------------------------------
# Subtract superbias
# STEPS.add_step(name='SUBTRACT_SUPERBIAS',
#                flavour='jwst', fname='_superbiasstep.fits',
#                ftype='suffix', run=True)

# Extract 2D spectrum
# STEPS.add_step(name='EXTRACT_2D_SPECTRUM',
#                flavour='jwst', fname='_extract2dstep.fits',
#                ftype='suffix', run=True)

# Correct stray light
# STEPS.add_step(name='CORRECT_STRAY_LIGHT',
#                flavour='jwst', fname='_straylightstep.fits',
#                ftype='suffix', run=True)

# Correct fringe
# STEPS.add_step(name='CORRECT_FRINGE',
#                flavour='jwst', fname='_fringestep.fits',
#                ftype='suffix', run=True)
# Correct path loss
# STEPS.add_step(name='CORRECT_PATH_LOSS',
#                flavour='jwst', fname='_pathlossstep.fits',
#                ftype='suffix', run=True)
# Correct bar shadow
# STEPS.add_step(name='CORRECT_BAR_SHADOW',
#                flavour='jwst', fname='_barshadowstep.fits',
#                ftype='suffix', run=True)
# Correct WFSS contamination
# STEPS.add_step(name='CORRECT_WFSS_CONTAMINATION',
#                flavour='jwst', fname='_wfsscontamstep.fits',
#                ftype='suffix', run=True)
# Correct wavelength
# STEPS.add_step(name='CORRECT_WAVELENGTH',
#                flavour='jwst', fname='_wavecorrstep.fits',
#                ftype='suffix', run=True)
# Subtract master background
# STEPS.add_step(name='SUBTRACT_MASTER_BACKGROUND',
#                flavour='jwst', fname='_masterbackgroundstep.fits',
#                ftype='suffix', run=True)
# Measure target centroid
# STEPS.add_step(name='MEASURE_TARGET_CENTROID',
#                flavour='jwst', fname='_targcentroidstep.fits',
#                ftype='suffix', run=False)
# Correct residual fringe
# STEPS.add_step(name='CORRECT_RESIDUAL_FRINGE',
#                flavour='jwst', fname='_residualfringestep.fits',
#                ftype='suffix', run=True)
# # Resample images
# STEPS.add_step(name='RESAMPLE_IMAGES',
#                flavour='jwst', fname='_resamplestep.fits',
#                ftype='suffix', run=True)

# -----------------------------------------------------------------------------
# push all steps into cdict
STEPS.to_cdict(TSOVORE_CDict, source=__NAME__, group=cgroup)


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

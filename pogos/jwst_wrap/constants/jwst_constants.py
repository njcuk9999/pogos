#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

Constants for the POGOS JWST "standard pipeline" wrapper (jwst_wrap).

This mirrors the eureka_wrap constants (Eureka_CDict) but wraps the official
``jwst`` calibration pipeline.  The three JWST stages map onto the POGOS
reduction steps as follows:

    Pre-extraction  [RUN.PRE_JWST]  -> Stage 1 + Stage 2
    Extraction      [RUN.EXT_JWST]  -> Stage 3
    Post-extraction [RUN.POST_JWST] -> any additional / custom steps

Created on 2026-06-26

@author: cook
"""
from aperocore.constants import constant_functions

from pogos.core import base

try:
    import jwst
    jversion = jwst.__version__
    try:
        jdate = jwst.__date__
    except AttributeError:
        jdate = 'Unknown'
except ImportError:
    jversion = 'Unknown'
    jdate = 'Unknown'

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'jwst_wrap.constants.jwst_constants.py'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__

# Constants definition
Const = constant_functions.Const
ConstDict = constant_functions.ConstantsDict

# =============================================================================
# constants for the JWST pipeline wrapper
# =============================================================================
JWST_CDict = ConstDict(__NAME__)

# set the title for output yaml files
JWST_CDict.title = JWST_CDict.yaml_title('JWST Pipeline Module',
                                         setup_program=None,
                                         version=jversion,
                                         date=jdate)

# =============================================================================
# General settings (generally don't touch these)
# =============================================================================
cgroup = 'GENERAL'
JWST_CDict.add_group(cgroup, description='General configs for the JWST pipeline',
                     source=__NAME__, user=True, active=True)

# add the sub-directory (used when a default path is required)
JWST_CDict.add('SUBDIRECTORY', value=None, dtype=str, source=__NAME__,
               user=True, active=True, group=cgroup, not_none=True,
               description='The sub-directory to use for this JWST run. '
                           'This should be descriptive and unique. '
                           '\nIt should contain no whitespaces or special '
                           'characters other than underscores.'
                           '\nAll JWST data will be stored in '
                           '{GLOBAL.DATA_PATH}/jwst/{SUBDIRECTORY}/'
                           '\n\nWe suggest {OBJNAME}-{INST.MODE}-{STEP}-{YYYYMMDD}')

# describe what we are running through the JWST pipeline
JWST_CDict.add('DESCRIPTION', value='', dtype=str, source=__NAME__,
               user=True, active=True, group=cgroup,
               description='Description of the POGOS run e.g. object name, '
                           'date of observation, is it a transit or '
                           'an eclipse etc.')

# Define whether we are in test mode (skips actually running the pipeline)
JWST_CDict.add('TESTMODE', value=False, dtype=bool, source=__NAME__,
               user=True, active=True, group=cgroup,
               description='Define whether we are in test mode (sets up '
                           'directories but does not run the pipeline)')

# Number of CPU cores the JWST steps are allowed to use
JWST_CDict.add('MAXIMUM_CORES', value='half', dtype=str,
               options=['none', 'quarter', 'half', 'all'], source=__NAME__,
               user=True, active=True, group=cgroup,
               description="Number of cores to use for multiprocessing steps "
                           "(e.g. jump, ramp_fit). Options: 'none', 'quarter', "
                           "'half', 'all'")


# =============================================================================
# Define the paths
# =============================================================================
cgroup = 'PATHS'
JWST_CDict.add_group(cgroup, description='POGOS paths for the JWST pipeline',
                     source=__NAME__, user=True, active=True)

# absolute input/output paths per stage (filled in by POGOS, not the user)
for _stage in [1, 2, 3]:
    JWST_CDict.add('IN_S{0}_PATH'.format(_stage), value=None, dtype=str,
                   source=__NAME__, user=False, active=False, group=cgroup,
                   description='POGOS full path to Stage {0} '
                               'input'.format(_stage))
    JWST_CDict.add('OUT_S{0}_PATH'.format(_stage), value=None, dtype=str,
                   source=__NAME__, user=False, active=False, group=cgroup,
                   description='POGOS full path to Stage {0} '
                               'output'.format(_stage))


# =============================================================================
# Stage groups
# =============================================================================
group_desc = ['JWST Stage 1 (calwebb_detector1) metadata (required for '
              'Pre-extraction Step [RUN.PRE_JWST=True])',
              'JWST Stage 2 (calwebb_spec2/image2) metadata (required for '
              'Pre-extraction Step [RUN.PRE_JWST=True])',
              'JWST Stage 3 (calwebb_tso3/spec3/image3) metadata (required for '
              'Extraction Step [RUN.EXT_JWST=True])']

for _stage in range(3):
    cgroup = 'STAGE{0}'.format(_stage + 1)
    JWST_CDict.add_group(cgroup, description=group_desc[_stage],
                         source=__NAME__, user=True, active=True)


# -----------------------------------------------------------------------------
# Stage 1 - calwebb_detector1 (Detector1Pipeline)
# -----------------------------------------------------------------------------
cgroup = 'STAGE1'
# suffix of the input files this stage consumes
JWST_CDict.add('input_suffix', value='uncal', dtype=str, source=__NAME__,
               user=True, active=True, group=cgroup,
               description='The file suffix the Stage 1 pipeline reads in '
                           '(JWST raw files are *_uncal.fits)')
JWST_CDict.add('save_results', value=True, dtype=bool, source=__NAME__,
               user=True, active=True, group=cgroup,
               description='Whether to save the Stage 1 pipeline outputs '
                           '(*_rateints.fits) to disk')
JWST_CDict.add('skip_jump', value=False, dtype=bool, source=__NAME__,
               user=True, active=True, group=cgroup,
               description='Skip the jump (cosmic ray) detection step')
JWST_CDict.add('jump_rejection_threshold', value=4.0, dtype=float,
               source=__NAME__, user=True, active=True, group=cgroup,
               description='Cosmic ray sigma rejection threshold for the jump '
                           'step (a larger value is usually recommended for '
                           'TSO data)')
JWST_CDict.add('skip_dark_current', value=False, dtype=bool, source=__NAME__,
               user=True, active=True, group=cgroup,
               description='Skip the dark current subtraction step')
JWST_CDict.add('inputdir', value='Uncalibrated', dtype=str, source=__NAME__,
               user=True, active=True, not_none=True, group=cgroup,
               description='Folder (relative to the run sub-directory) '
                           'containing the *_uncal.fits input files')
JWST_CDict.add('outputdir', value='Stage1', dtype=str, source=__NAME__,
               user=True, active=True, not_none=True, group=cgroup,
               description='Folder (relative to the run sub-directory) the '
                           'Stage 1 outputs are written to')
JWST_CDict.add('topdir', value=None, dtype='path', source=__NAME__,
               user=True, active=False, group=cgroup,
               description='Absolute top directory for this run (set by POGOS)')


# -----------------------------------------------------------------------------
# Stage 2 - calwebb_spec2 / calwebb_image2 (Spec2Pipeline / Image2Pipeline)
# -----------------------------------------------------------------------------
cgroup = 'STAGE2'
JWST_CDict.add('input_suffix', value='rateints', dtype=str, source=__NAME__,
               user=True, active=True, group=cgroup,
               description='The file suffix the Stage 2 pipeline reads in '
                           '(Stage 1 outputs are *_rateints.fits)')
JWST_CDict.add('save_results', value=True, dtype=bool, source=__NAME__,
               user=True, active=True, group=cgroup,
               description='Whether to save the Stage 2 pipeline outputs '
                           '(*_calints.fits) to disk')
JWST_CDict.add('skip_photom', value=True, dtype=bool, source=__NAME__,
               user=True, active=True, group=cgroup,
               description='Skip the photometric calibration step (often '
                           'recommended for TSO spectroscopy)')
JWST_CDict.add('inputdir', value='Stage1', dtype=str, source=__NAME__,
               user=True, active=True, not_none=True, group=cgroup,
               description='Folder (relative to the run sub-directory) '
                           'containing the Stage 2 input files')
JWST_CDict.add('outputdir', value='Stage2', dtype=str, source=__NAME__,
               user=True, active=True, not_none=True, group=cgroup,
               description='Folder (relative to the run sub-directory) the '
                           'Stage 2 outputs are written to')
JWST_CDict.add('topdir', value=None, dtype='path', source=__NAME__,
               user=True, active=False, group=cgroup,
               description='Absolute top directory for this run (set by POGOS)')


# -----------------------------------------------------------------------------
# Stage 3 - calwebb_tso3 / calwebb_spec3 / calwebb_image3
# -----------------------------------------------------------------------------
cgroup = 'STAGE3'
JWST_CDict.add('input_suffix', value='calints', dtype=str, source=__NAME__,
               user=True, active=True, group=cgroup,
               description='The file suffix the Stage 3 pipeline reads in '
                           '(Stage 2 outputs are *_calints.fits)')
JWST_CDict.add('save_results', value=True, dtype=bool, source=__NAME__,
               user=True, active=True, group=cgroup,
               description='Whether to save the Stage 3 pipeline outputs to '
                           'disk')
JWST_CDict.add('product_name', value='pogos_jwst', dtype=str, source=__NAME__,
               user=True, active=True, group=cgroup,
               description='The base product name used for the Stage 3 '
                           'association and output files')
JWST_CDict.add('inputdir', value='Stage2', dtype=str, source=__NAME__,
               user=True, active=True, not_none=True, group=cgroup,
               description='Folder (relative to the run sub-directory) '
                           'containing the Stage 3 input files')
JWST_CDict.add('outputdir', value='Stage3', dtype=str, source=__NAME__,
               user=True, active=True, not_none=True, group=cgroup,
               description='Folder (relative to the run sub-directory) the '
                           'Stage 3 outputs are written to')
JWST_CDict.add('topdir', value=None, dtype='path', source=__NAME__,
               user=True, active=False, group=cgroup,
               description='Absolute top directory for this run (set by POGOS)')


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================


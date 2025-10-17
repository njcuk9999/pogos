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
# constants from MIRIAM
# =============================================================================
MIRIAM_CDict = ConstDict(__NAME__)

# set the title for output yaml files
MIRIAM_CDict.title = MIRIAM_CDict.yaml_title('MIRIAM: MIRI Image Analysis '
                                             'Module',
                                             setup_program=None,
                                             version=base.MIRIAM_VERSION,
                                             date=base.MIRIAM_DATE)

# =============================================================================
# General settings (generally don't touch these)
# =============================================================================
# set the group for all WLCTA constants
cgroup = 'GENERAL'
MIRIAM_CDict.add_group(cgroup, description='General configs for SORBET',
                       source=__NAME__, user=True, active=True)
# add the sid (to be used when default path required)
MIRIAM_CDict.add('SID', value=None, dtype=str, source=__NAME__,
                 user=True, active=True, group=cgroup,
                 description='A string ID for the observation (used for '
                             'default paths etc)')

# define what we are running through SORBET
MIRIAM_CDict.add('DESCRIPTION', value='', dtype=str, source=__NAME__,
                 user=True, active=True, group=cgroup,
                 description='Description of the MIRIAM run')

# =============================================================================
# Path settings
# =============================================================================
cgroup = 'PATHS'
MIRIAM_CDict.add_group(cgroup, description='Definition of paths (normally '
                                           'created at run time but can be '
                                           'overridden)',
                       source=__NAME__, user=False, active=False)
# Input data folder or path to the input folderinput path
MIRIAM_CDict.add('INPUT_PATH', value='inputs', dtype=str, source=__NAME__,
                 user=False, active=False, group=cgroup,
                 description='Input data folder or path to the input folder.')

# Output results folder
MIRIAM_CDict.add('OUTPUT_PATH', value='results', dtype=str,
                 source=__NAME__,
                 user=False, active=False, group=cgroup,
                 description='Output result folder or path to the output folder.'
                             '\nIf this is an aboslute path it will be used as is'
                             '\n otherwise it will be relative to '
                             'GLOBAL.DATA_PATH/miriam/')
# the plot path
MIRIAM_CDict.add('PLOT_PATH', value='plots', dtype=str,
                 source=__NAME__, active=False, user=False, group=cgroup,
                 description='The plot path')

# =============================================================================
# Definition of inputs related to plots
# =============================================================================
cgroup = 'PLOTS'
MIRIAM_CDict.add_group(cgroup,
                       description='Definition of inputs related to plots',
                       source=__NAME__, user=True, active=True)
# -----------------------------------------------------------------------------
# Or you can use the following to always show plots regardless of the username
MIRIAM_CDict.add('SHOW', value=False, dtype=bool,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description='Or you can use the following to always show '
                             'plots regardless of the username')
# -----------------------------------------------------------------------------
# output(s) type of figure
MIRIAM_CDict.add('FIGURE_TYPES', value=['png', 'pdf'], dtype=list, dtypei=str,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description='output(s) type of figure')

# =============================================================================
# Input settings
# =============================================================================
cgroup = 'INPUTS'
MIRIAM_CDict.add_group(cgroup, source=__NAME__, user=True, active=True,
                       description='Definition of inputs related to the data')
# -----------------------------------------------------------------------------
# Raw files
fdesc = ('List of files to be processed in form: '
         '\nFILES:\n - file1\n - file2\n - file3'
         '\n\nBy default these should be placed in '
         '{GLOBAL.DATA_PATH}/{MIRIAM.PATHS.INTPUT_PATH}/'
         '\n or whatever is set in {MIRIAM.PATHS.INTPUT_PATH} (if absolute)')
MIRIAM_CDict.add('FILES', value=None, dtype=list, dtypei=str, not_none=False,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=fdesc)

# List of integrations to skip (0-indexed)
MIRIAM_CDict.add('SKIP_INTEGRATIONS', value=None, dtype=list, dtypei=int,
                 not_none=False, source=__NAME__, user=True, active=True,
                 group=cgroup,
                 description='List of integrations to skip (0-indexed)')

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

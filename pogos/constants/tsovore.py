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
# add the sid (to be used when default path required)
TSOVORE_CDict.add('SID', value=None, dtype=str, source=__NAME__,
                 user=True, active=True, group=cgroup,
                 description='A string ID for the observation (used for '
                             'default paths etc)')
# define what we are running through MIRIAM
TSOVORE_CDict.add('DESCRIPTION', value='', dtype=str, source=__NAME__,
                  user=True, active=True, group=cgroup,
                  description='Description of the TSOVORE run')

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
# Raw files
fdesc = ('List of files to be processed in form: '
         '\nFILES:\n - file1\n - file2\n - file3'
         '\n\nBy default these should be placed in '
         '{GLOBAL.DATA_PATH}/{MIRIAM.PATHS.INTPUT_PATH}/'
         '\n or whatever is set in {TSOVORE.PATHS.INTPUT_PATH} (if absolute)')
TSOVORE_CDict.add('FILES', value=None, dtype=list, dtypei=str, not_none=False,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=fdesc)




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

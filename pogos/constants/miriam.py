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
group = 'GENERAL'
MIRIAM_CDict.add_group(group, description='General configs for SORBET',
                source=__NAME__, user=True, active=True)
# add the sid (to be used when default path required)
MIRIAM_CDict.add('SID', value=None, dtype=str, source=__NAME__,
                 user=True, active=True, group=group,
                 description='A string ID for the observation (used for '
                             'default paths etc)')

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
         '<SOSSIOPATH>/{OBJECTNAME>/rawdata/'
         '\n or whatever is set in <PATHS.RAW> (if defined)')
MIRIAM_CDict.add('FILES', value=None, dtype=list, dtypei=str, not_none=False,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=fdesc)

# List of integrations to skip (0-indexed)
MIRIAM_CDict.add('SKIP_INTEGRATIONS', value=None, dtype=list, dtypei=int,
                 not_none=False, source=__NAME__, user=True, active=True,
                 group=cgroup,
                 description='List of integrations to skip (0-indexed)')

# Output results folder
MIRIAM_CDict.add('OUTPUT_PATH', value='results', dtype=str,
                source=__NAME__,
                user=True, active=True, group=group,
                description='Output result folder or path to the output folder.'
                            '\nIf this is an aboslute path it will be used as is'
                            '\n otherwise it will be relative to '
                            'GLOBAL.DATA_PATH/miriam/')


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

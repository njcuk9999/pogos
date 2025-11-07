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
CDict = ConstDict(__NAME__)

# set the title for output yaml files
CDict.title = CDict.yaml_title('POGOS', setup_program='pogos_setup.py',
                               version=__version__, date=__date__)


# =============================================================================
# global settings (generally don't touch these)
# =============================================================================
cgroup = 'GLOBAL'
CDict.add_group(cgroup, description='global settings (generally '
                                    'don\'t touch these)',
                source=__NAME__, user=True, active=True)

# Yaml file
CDict.add('YAML_FILE', value=None, dtype=str, source=__NAME__,
                 user=False, active=False, group=cgroup, not_none=True,
                 cmd_arg='yamlfile',
                 cmd_kwargs=dict(nargs='?', type=str, default=None,
                                 action='store'),
          description='the absolute path and filename of the configuration file '
                      '(yaml file) to create which '
                      '(if not using a previous yaml file). '
                      'This file will contain all parameters required to '
                      'run POGOS. '
                      '\n\nE.g. /users/albert/pogo-data/yaml/pogos_test.yaml'
                      '\nE.g. /home/cook/pogo-data/yaml/pogos_test.yaml'
                      '\nE.g. C:\\users\\bob\\pogo-data\\yamls\\pogos_test.yaml')

# Define data path
CDict.add('DATA_PATH', value=None, dtype=str,
          source=__NAME__, user=True,
          active=True, group=cgroup, not_none=True, cmd_arg='data_path',
          description='the absolute path to where all input and output data '
                      'for POGOS will be stored. '
                      '\n\nPlease note a /data/ subdirectory will be created '
                      'for data with the modes in. '
                      '\n\nE.g. /users/albert/pogo-data/'
                      '\nE.g. /home/albert/pogo-data/'
                      '\nE.g. C:\\users\\bob\\pogo-data')

# Instrument mode i.e. JWST.NIRISS.SOSS or JWST.NIRISS.PRISM
CDict.add('INSTRUMENTMODE', value=None, dtype=str, not_none=True,
          source=__NAME__, user=True, active=True,
          options=base.INSTRUMENTS,
          cmd_arg='instmode', group=cgroup,
          description='instrument mode e.g. one of the following: {0}'
                      ''.format('\n\t'.join(base.INSTRUMENTS)))

# =============================================================================
# Switches to turn of major features
# =============================================================================
group = 'RUN'
CDict.add_group(group, description='Switches to turn on major features',
                source=__NAME__, user=True, active=True)

# Run TSOVORE
CDict.add('TSOVORE', value=None, dtype=bool, source=__NAME__,
          user=True, active=True, group=group, not_none=True,
          description='Run TSOVORE')

# Run SOSSISSE
CDict.add('SOSSISSE', value=None, dtype=bool, source=__NAME__,
          user=True, active=True, group=group, not_none=True,
          description='Run SOSSISSE')

# Run MIRIAM
CDict.add('MIRIAM', value=None, dtype=bool, source=__NAME__,
          user=True, active=True, group=group, not_none=True,
          description='Run MIRIAM')

# Run SORBET
CDict.add('SORBET', value=None, dtype=bool, source=__NAME__,
          user=True, active=True, group=group, not_none=True,
          description='Run SORBET')

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

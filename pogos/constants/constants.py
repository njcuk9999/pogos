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
from pogos.core import definitions

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
                      '\n\nE.g. /users/albert/pogo-data/'
                      '\nE.g. /home/albert/pogo-data/'
                      '\nE.g. C:\\users\\bob\\pogo-data')

# Instrument mode i.e. JWST.NIRISS.SOSS or JWST.NIRISS.PRISM
instrument_names = [mode.name for mode in definitions.ENABLED_INST_MODES]
CDict.add('INSTRUMENTMODE', value=None, dtype=str, not_none=True,
          source=__NAME__, user=True, active=True,
          options=instrument_names,
          cmd_arg='instmode', group=cgroup,
          description='instrument mode e.g. one of the following: {0}'
                      ''.format('\n\t'.join(instrument_names)))

# Only used for copying
CDict.add('DEMO_FILE', value=None, dtype=str, source=__NAME__, user=False,
          active=False, cmd_arg='demo_file', group=cgroup,
          description='the absolute path and filename of a demo yaml file to '
                      'use as a template for creating a new yaml file/file '
                      'structure. ')

# Used when user wishes to list the available yaml files
CDict.add('LIST_YAMLS', value=False, dtype=bool, source=__NAME__, user=False,
          active=False, cmd_arg='list', group=cgroup,
          description='lists the available yaml files '
                      '(in the current directory) and exits.')

# Only used for downloading data
CDict.add('LOCAL_DOWNLOAD_DATA', value=None, dtype=str, source=__NAME__,
          user=False, active=False, cmd_arg='demolocal', group=cgroup,
          description='the absolute path to where demo data is stored locally'
                      ' this overrides any downloading of data from online.')

# only used for donwloading data
CDict.add('DEMO_SYMLINK_DATA', value=False, dtype=bool, source=__NAME__,
          user=False, active=False, cmd_arg='demosymlink', group=cgroup,
          description='if downloading demo data, symlink the data from the '
                      'local download location rather than copying it.')

# Pre-answer the instrument selection prompt (1-based index into the
#   instrument list) - skips the interactive prompt in core_setup
CDict.add('INSTRUMENT_SELECT', value=None, dtype=int, source=__NAME__,
          user=False, active=False, cmd_arg='instrument_select', group=cgroup,
          description='Pre-answer the "Select instrument" prompt with the '
                      '1-based option number (skips the interactive prompt).')

# Pre-answer the instrument mode prompt (1-based index into the mode list for
#   the selected instrument) - skips the interactive prompt in core_setup
CDict.add('INSTRUMENT_MODE', value=None, dtype=int, source=__NAME__,
          user=False, active=False, cmd_arg='instrument_mode', group=cgroup,
          description='Pre-answer the "Select instrument mode" prompt with the '
                      '1-based option number (skips the interactive prompt).')

# Pre-answer the Pre-extraction reduction step prompt (0=Skip, else the option
#   number shown) - skips the interactive prompt in ask_reduction_steps
CDict.add('PREEXTRACT_STEP', value=None, dtype=int, source=__NAME__,
          user=False, active=False, cmd_arg='preextract_step', group=cgroup,
          description='Pre-answer the Pre-extraction step prompt with the '
                      'option number (0=Skip).')

# Pre-answer the Extraction reduction step prompt (0=Skip, else the option
#   number shown) - skips the interactive prompt in ask_reduction_steps
CDict.add('EXTRACT_STEP', value=None, dtype=int, source=__NAME__,
          user=False, active=False, cmd_arg='extract_step', group=cgroup,
          description='Pre-answer the Extraction step prompt with the option '
                      'number (0=Skip).')

# Pre-answer the Post-extraction reduction step prompt - comma separated option
#   numbers as this step allows multiple choices (0=Skip) - skips the
#   interactive prompt in ask_reduction_steps
CDict.add('POSTEXTRACT_STEP', value=None, dtype=str, source=__NAME__,
          user=False, active=False, cmd_arg='postextract_step', group=cgroup,
          description='Pre-answer the Post-extraction step prompt with comma '
                      'separated option number(s) (0=Skip), e.g. "1,2".')

# =============================================================================
# Switches to turn of major features
# =============================================================================
group = 'RUN'
CDict.add_group(group, description='Switches to turn on major features',
                source=__NAME__, user=True, active=True)

# Add one switch for every authoritative reduction-step definition.
for reduction_step in definitions.RED_STEPS:
    description = 'Run {0} [{1}]'.format(reduction_step.name,
                                         reduction_step.level.name)
    CDict.add(reduction_step.name, value=False, dtype=bool, source=__NAME__,
              user=True, active=True, group=group, not_none=True,
              description=description)


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

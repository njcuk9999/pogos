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

    from eureka.S1_detector_processing import S1MetaClass

except ImportError:
    emsg = 'Please install Eurkea'
    raise base.PogosException(emsg)

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
Eureka_CDict = ConstDict(__NAME__)

# set the title for output yaml files
Eureka_CDict.title = Eureka_CDict.yaml_title('EUREKA! Module',
                                             setup_program=None,
                                             version=eureka.__version__,
                                             date=eureka.__date__)

# =============================================================================
# General settings (generally don't touch these)
# =============================================================================
# stage 1 parameters
cgroup = 'Stage 1'
Eureka_CDict.add_group(cgroup, description='Eureka! S1 metadata',
                       source=__NAME__, user=True, active=True)

# stage 2 parameters
cgroup = 'Stage 2'
Eureka_CDict.add_group(cgroup, description='Eureka! S2 metadata',
                       source=__NAME__, user=True, active=True)

# stage 3 parameters
cgroup = 'Stage 3'
Eureka_CDict.add_group(cgroup, description='Eureka! S3 metadata',
                       source=__NAME__, user=True, active=True)

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

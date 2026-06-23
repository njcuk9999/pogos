#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2025-01-31 at 15:03

@author: cook
"""
from pogos.eureka_wrap.core import general
from pogos.eureka_wrap.constants import eureka_constants

# =============================================================================
# Define variables
# =============================================================================
# constants
Eureka_CDict = eureka_constants.Eureka_CDict

# setup eurkea
setup_eureka_pre_extract = general.setup_eureka_pre_extract
setup_eureka_extract = general.setup_eureka_extract
setup_eureka_post_extract = general.setup_eureka_post_extract

# run eureka
run_eureka_pre_extract = general.run_eureka_pre_extract
run_eureka_extract = general.run_eureka_extract
run_eureka_post_extract = general.run_eureka_post_extract

# =============================================================================
# End of code
# =============================================================================

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

POGOS wrapper around the NAMELESS JWST NIRISS/SOSS reduction code. Mirrors the
eureka_wrap module. NAMELESS maps onto the POGOS reduction steps as:

    Pre-extraction  [RUN.PRE_NAMELESS]  -> run_s1, run_s2, run_prep, run_cst
    Extraction      [RUN.EXT_NAMELESS]  -> run_ext
    (there is no post-extraction step for NAMELESS)

Created on 2026-06-26

@author: cook
"""
from pogos.nameless_wrap.core import general
from pogos.nameless_wrap.constants import nameless_constants

# =============================================================================
# Define variables
# =============================================================================
# constants
NAMELESS_CDict = nameless_constants.NAMELESS_CDict

# setup nameless
setup_nameless_pre_extract = general.setup_nameless_pre_extract
setup_nameless_extract = general.setup_nameless_extract

# run nameless
run_nameless_pre_extract = general.run_nameless_pre_extract
run_nameless_extract = general.run_nameless_extract

# =============================================================================
# End of code
# =============================================================================


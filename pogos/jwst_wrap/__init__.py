#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

POGOS wrapper around the official JWST calibration pipeline. Mirrors the
eureka_wrap module but runs the "standard" JWST pipeline stages:

    Pre-extraction  [RUN.PRE_JWST]  -> Stage 1 + Stage 2
    Extraction      [RUN.EXT_JWST]  -> Stage 3
    Post-extraction [RUN.POST_JWST] -> additional / custom steps

Created on 2026-06-26

@author: cook
"""
from pogos.jwst_wrap.core import general
from pogos.jwst_wrap.constants import jwst_constants

# =============================================================================
# Define variables
# =============================================================================
# constants
JWST_CDict = jwst_constants.JWST_CDict

# setup jwst
setup_jwst_pre_extract = general.setup_jwst_pre_extract
setup_jwst_extract = general.setup_jwst_extract
setup_jwst_post_extract = general.setup_jwst_post_extract

# run jwst
run_jwst_pre_extract = general.run_jwst_pre_extract
run_jwst_extract = general.run_jwst_extract
run_jwst_post_extract = general.run_jwst_post_extract

# =============================================================================
# End of code
# =============================================================================


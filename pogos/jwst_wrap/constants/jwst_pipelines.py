#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

Mapping between POGOS instrument modes and the "standard" JWST calibration
pipeline classes for each reduction stage.

This module deliberately stores the pipeline class *names* (as strings) and
the python module they live in, rather than importing them.  This means the
mapping can be imported (e.g. by jwst_constants.py) without requiring the
(heavy) ``jwst`` package to be installed.  The actual classes are resolved
lazily inside ``jwst_wrap.core.general`` only when a stage is actually run.

The JWST "standard pipeline" has three stages:

    Stage 1 - calwebb_detector1  (Detector1Pipeline)  ramp-fitting
    Stage 2 - calwebb_spec2 / image2 (Spec2Pipeline / Image2Pipeline)
    Stage 3 - calwebb_tso3 / spec3 / image3 (Tso3Pipeline / Spec3Pipeline ...)

POGOS is a time-series pipeline so Stage 3 generally uses the TSO variant.

Created on 2026-06-26

@author: cook
"""
from pogos.core import base

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'pogos.jwst_wrap.constants.jwst_pipelines.py'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__

# Where each pipeline class lives (used for the lazy import in general.py)
PIPELINE_MODULES = dict()
PIPELINE_MODULES['Detector1Pipeline'] = 'jwst.pipeline'
PIPELINE_MODULES['Spec2Pipeline'] = 'jwst.pipeline'
PIPELINE_MODULES['Image2Pipeline'] = 'jwst.pipeline'
PIPELINE_MODULES['Tso3Pipeline'] = 'jwst.pipeline'
PIPELINE_MODULES['Spec3Pipeline'] = 'jwst.pipeline'
PIPELINE_MODULES['Image3Pipeline'] = 'jwst.pipeline'

# Stage 1 (calwebb_detector1) - the same for every instrument mode
S1_PIPELINES = dict()
for _mode in base.INSTRUMENTS:
    S1_PIPELINES[_mode] = 'Detector1Pipeline'

# Stage 2 (calwebb_spec2 / calwebb_image2)
S2_PIPELINES = dict()
S2_PIPELINES['JWST.NIRISS.SOSS'] = 'Spec2Pipeline'
S2_PIPELINES['JWST.NIRISS.FGS'] = 'Image2Pipeline'
S2_PIPELINES['JWST.NIRSPEC.BOTS.PRISM'] = 'Spec2Pipeline'
S2_PIPELINES['JWST.NIRSPEC.BOTS.G395M'] = 'Spec2Pipeline'
S2_PIPELINES['JWST.NIRSPEC.BOTS.G235M'] = 'Spec2Pipeline'
S2_PIPELINES['JWST.NIRSPEC.BOTS.G140M'] = 'Spec2Pipeline'
S2_PIPELINES['JWST.NIRSPEC.BOTS.G395H'] = 'Spec2Pipeline'
S2_PIPELINES['JWST.NIRSPEC.BOTS.G235H'] = 'Spec2Pipeline'
S2_PIPELINES['JWST.NIRSPEC.BOTS.G140H'] = 'Spec2Pipeline'
S2_PIPELINES['JWST.NIRCAM.IMAGING'] = 'Image2Pipeline'
S2_PIPELINES['JWST.NIRCAM.WFSS'] = 'Spec2Pipeline'
S2_PIPELINES['JWST.MIRI.IMAGING'] = 'Image2Pipeline'
S2_PIPELINES['JWST.MIRI.LRS'] = 'Spec2Pipeline'

# Stage 3 (calwebb_tso3 / calwebb_spec3 / calwebb_image3)
#   POGOS is time-series focused so the TSO variant is used where possible
S3_PIPELINES = dict()
S3_PIPELINES['JWST.NIRISS.SOSS'] = 'Tso3Pipeline'
S3_PIPELINES['JWST.NIRISS.FGS'] = 'Image3Pipeline'
S3_PIPELINES['JWST.NIRSPEC.BOTS.PRISM'] = 'Tso3Pipeline'
S3_PIPELINES['JWST.NIRSPEC.BOTS.G395M'] = 'Tso3Pipeline'
S3_PIPELINES['JWST.NIRSPEC.BOTS.G235M'] = 'Tso3Pipeline'
S3_PIPELINES['JWST.NIRSPEC.BOTS.G140M'] = 'Tso3Pipeline'
S3_PIPELINES['JWST.NIRSPEC.BOTS.G395H'] = 'Tso3Pipeline'
S3_PIPELINES['JWST.NIRSPEC.BOTS.G235H'] = 'Tso3Pipeline'
S3_PIPELINES['JWST.NIRSPEC.BOTS.G140H'] = 'Tso3Pipeline'
S3_PIPELINES['JWST.NIRCAM.IMAGING'] = 'Tso3Pipeline'
S3_PIPELINES['JWST.NIRCAM.WFSS'] = 'Spec3Pipeline'
S3_PIPELINES['JWST.MIRI.IMAGING'] = 'Tso3Pipeline'
S3_PIPELINES['JWST.MIRI.LRS'] = 'Tso3Pipeline'

# convenience lookup keyed by stage number
STAGE_PIPELINES = {1: S1_PIPELINES, 2: S2_PIPELINES, 3: S3_PIPELINES}


# =============================================================================
# Define functions
# =============================================================================
def get_pipeline_name(stage: int, instmode: str):
    """
    Return the JWST pipeline class name for a given stage + instrument mode.

    :param stage: int, the JWST stage number (1, 2 or 3)
    :param instmode: str, the POGOS instrument mode (GLOBAL.INSTRUMENTMODE)
    :return: str or None, the pipeline class name (e.g. 'Tso3Pipeline') or
             None if no standard pipeline is defined for this combination
    """
    mapping = STAGE_PIPELINES.get(stage, dict())
    return mapping.get(instmode, None)


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================


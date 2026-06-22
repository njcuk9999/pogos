#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2026-06-17 10:35:00

@author: cook
"""
import os

from aperocore.constants.param_functions import ParamDict
from aperocore.core import drs_log
from aperocore.core import drs_misc
from pogos.core import base

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'pogos.sossisse_wrap.core.core'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__
# get the Drs Exceptions
AperoCodedException = drs_log.AperoCodedException
AperoCodedWarning = drs_log.AperoCodedWarning
# get display func
display_func = drs_misc.display_func
# Get Logging function
WLOG = drs_log.wlog

# =============================================================================
# Define functions
# =============================================================================
def setup_eureka_pre_extract(params: ParamDict) -> ParamDict:

    # Try importing Eureka
    params, eplots, s1, s2, s3, s4, s5, s6 = import_eureka(params)

    # deal with user (or pogos) not running pre-extract Eureka steps
    if not params['RUN.PRE_EUREKA']:
        # return updated params
        return params

    # Make the directories
    make_eureka_dirs()

    # return updated params
    return params


def setup_eureka_extract(params: ParamDict) -> ParamDict:
    # Try importing Eureka
    params, eplots, s1, s2, s3, s4, s5, s6 = import_eureka(params)

    # deal with user (or pogos) not running pre-extract Eureka steps
    if not params['RUN.EXT_EUREKA']:
        # return updated params
        return params
    # Make the directories
    make_eureka_dirs()

    # return updated params
    return params


def setup_eureka_post_extract(params: ParamDict) -> ParamDict:
    # Try importing Eureka
    params, eplots, s1, s2, s3, s4, s5, s6 = import_eureka(params)

    # deal with user (or pogos) not running pre-extract Eureka steps
    if not params['RUN.POST_EUREKA']:
        # return updated params
        return params
    # Make the directories
    make_eureka_dirs()

    # return updated params
    return params


def run_eureka_pre_extract():

    # Make the directories
    make_eureka_dirs()

    meta = s1.rampfitJWST(eventlabel, ecf_path=ecf_path)

    meta = s2.calibrateJWST(eventlabel, ecf_path=ecf_path)


def run_eureka_extract():
    spec, meta = s3.reduce(eventlabel, ecf_path=ecf_path)


def run_eureka_post_extract():
    spec, lc, meta = s4.genlc(eventlabel, ecf_path=ecf_path)

    meta = s5.fitlc(eventlabel, ecf_path=ecf_path)

    meta, lc = s6.plot_spectra(eventlabel, ecf_path=ecf_path)


# =============================================================================
# Define worker function
# =============================================================================
def import_eureka(params: ParamDict):
    # set function name
    func_name = f'{__NAME__}.import_eureka()'
    try:
        import eureka.lib.plots as eplots
        import eureka.S1_detector_processing.s1_process as s1
        import eureka.S2_calibrations.s2_calibrate as s2
        import eureka.S3_data_reduction.s3_reduce as s3
        import eureka.S4_generate_lightcurves.s4_genLC as s4
        import eureka.S5_lightcurve_fitting.s5_fit as s5
        import eureka.S6_planet_spectra.s6_spectra as s6
        return params, eplots, s1, s2, s3, s4, s5, s6
    except ImportError:
        # set RUN.*_EUREKA to False
        params.set('RUN.PRE_EUREKA', value=False, source=func_name)
        params.set('RUN.EXT_EUREKA', value=False, source=func_name)
        params.set('RUN.POST_EUREKA', value=False, source=func_name)
        # log a message that Eureka is not installed
        wmsg = 'Eureka is not installed. Skipping Eureka'
        WLOG(params, 'warning', wmsg)
        return params, None, None, None, None, None, None, None


def make_eureka_dirs():
    pass



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

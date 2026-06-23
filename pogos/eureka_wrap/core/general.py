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
from pogos.core import general as pogos_general
from pogos.eureka_wrap.constants import eureka_ecf as ecf

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
    # deal with user (or pogos) not running pre-extract Eureka steps
    if not params['RUN.PRE_EUREKA']:
        # return updated params
        return params

    # Make the directories
    make_eureka_dirs(params, stage=1)
    make_eureka_dirs(params, stage=2)

    # return updated params
    return params


def setup_eureka_extract(params: ParamDict) -> ParamDict:
    # deal with user (or pogos) not running pre-extract Eureka steps
    if not params['RUN.EXT_EUREKA']:
        # return updated params
        return params
    # Make the directories
    make_eureka_dirs(params, stage=3)

    # return updated params
    return params


def setup_eureka_post_extract(params: ParamDict) -> ParamDict:
    # deal with user (or pogos) not running pre-extract Eureka steps
    if not params['RUN.POST_EUREKA']:
        # return updated params
        return params
    # Make the directories
    make_eureka_dirs(params, stage=4)
    make_eureka_dirs(params, stage=5)
    make_eureka_dirs(params, stage=6)

    # return updated params
    return params


def run_eureka_pre_extract(params: ParamDict) -> ParamDict:
    # Try importing Eureka
    params, eplots, s1, s2, s3, s4, s5, s6 = import_eureka(params)
    # deal with user (or pogos) not running pre-extract Eureka steps
    if not params['RUN.PRE_EUREKA']:
        # return updated params
        return params
    # -------------------------------------------------------------------------
    # Make the directories
    make_eureka_dirs(params, stage=1)
    make_eureka_dirs(params, stage=2)
    # -------------------------------------------------------------------------
    # get the event label and ecf_path + generate ecf_file
    eventlabel = params['EUREKA.GENERAL.EVENTLABEL']
    ecf_path = ecf.ecf_from_params(params.get('EUREKA.STAGE1'), stage=1)
    _ = ecf.ecf_from_params(params.get('EUREKA.STAGE2'), stage=2)

    # deal with test mode (return here)
    if params['EUREKA.GENERAL.TESTMODE']:
        return params
    # -------------------------------------------------------------------------
    # Run the Stage 1 + Stage 2 steps from Eureka
    # -------------------------------------------------------------------------
    meta = s1.rampfitJWST(eventlabel, ecf_path=ecf_path)
    meta = s2.calibrateJWST(eventlabel, ecf_path=ecf_path)
    # return params
    return params


def run_eureka_extract(params: ParamDict) -> ParamDict:
    # Try importing Eureka
    params, eplots, s1, s2, s3, s4, s5, s6 = import_eureka(params)
    # deal with user (or pogos) not running pre-extract Eureka steps
    if not params['RUN.EXT_EUREKA']:
        # return updated params
        return params
    # -------------------------------------------------------------------------
    # Make the directories
    make_eureka_dirs(params, stage=3)
    # -------------------------------------------------------------------------
    # get the event label and ecf_path + generate ecf_file
    eventlabel = params['EUREKA.GENERAL.EVENTLABEL']
    ecf_path = ecf.ecf_from_params(params.get('EUREKA.STAGE3'), stage=3)

    # deal with test mode (return here)
    if params['EUREKA.GENERAL.TESTMODE']:
        return params
    # -------------------------------------------------------------------------
    # Run the Stage 3 steps from Eureka
    # -------------------------------------------------------------------------
    spec, meta = s3.reduce(eventlabel, ecf_path=ecf_path)
    # return params
    return params


def run_eureka_post_extract(params: ParamDict) -> ParamDict:
    # Try importing Eureka
    params, eplots, s1, s2, s3, s4, s5, s6 = import_eureka(params)
    # deal with user (or pogos) not running pre-extract Eureka steps
    if not params['RUN.POST_EUREKA']:
        # return updated params
        return params
    # Make the directories
    make_eureka_dirs(params, stage=4)
    make_eureka_dirs(params, stage=5)
    make_eureka_dirs(params, stage=6)
    # -------------------------------------------------------------------------
    # get the event label and ecf_path + generate ecf_file
    eventlabel = params['EUREKA.GENERAL.EVENTLABEL']
    ecf_path = ecf.ecf_from_params(params.get('EUREKA.STAGE4'), stage=4)
    _ = ecf.ecf_from_params(params.get('EUREKA.STAGE5'), stage=5)
    _ = ecf.ecf_from_params(params.get('EUREKA.STAGE6'), stage=6)
    # deal with test mode (return here)
    if params['EUREKA.GENERAL.TESTMODE']:
        return params
    # -------------------------------------------------------------------------
    # Run the Stage 4+5+6 steps from Eureka
    # -------------------------------------------------------------------------
    spec, lc, meta = s4.genlc(eventlabel, ecf_path=ecf_path)
    meta = s5.fitlc(eventlabel, ecf_path=ecf_path)
    meta, lc = s6.plot_spectra(eventlabel, ecf_path=ecf_path)
    # return params
    return params


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
        if not params['EUREKA.GENERAL.TESTMODE']:
            params.set('RUN.PRE_EUREKA', value=False, source=func_name)
            params.set('RUN.EXT_EUREKA', value=False, source=func_name)
            params.set('RUN.POST_EUREKA', value=False, source=func_name)
        # log a message that Eureka is not installed
        wmsg = 'Eureka is not installed. Skipping Eureka'
        WLOG(params, 'warning', wmsg)
        return params, None, None, None, None, None, None, None


def make_eureka_dirs(params: ParamDict, stage: int = None):
    # set the function name
    func_name = f'{__NAME__}.make_eureka_dirs()'
    # set basid prepare directory parameters
    sid_path = 'EUREKA.GENERAL.SUBDIRECTORY'
    sid_null = eureka_unique_id()
    mode = 'eureka'

    # set topdir
    topdir = os.path.join(params['GLOBAL.DATA_PATH'], mode, params[sid_path])

    # Deal with the stages
    for _stage in [1, 2, 3]:
        if stage in [None, _stage]:
            # set the absolute pogos in path
            pogos_inkey = f'EUREKA.PATHS.IN_S{_stage}_PATH'
            pogos_outkey = f'EUREKA.PATHS.OUT_S{_stage}_PATH'
            # get the inpath and outpath from Eureka
            e_inpath = str(params[f'EUREKA.STAGE{_stage}.inputdir'])
            e_outpath = str(params[f'EUREKA.STAGE{_stage}.outputdir'])
            # starting point is setting the pogos_inkey to the eureka in key
            params.set(pogos_inkey, value=e_inpath, source=func_name)
            # similarly for outkey
            params.set(pogos_outkey, value=e_outpath, source=func_name)
            # run the prepare directory function
            pogos_general.prepare_directory(params, 'input', sid_path,
                                            sid_null, pogos_inkey, mode)
            pogos_general.prepare_directory(params, 'output', sid_path,
                                            sid_null, pogos_outkey, mode)
            # set top path
            params.set(f'EUREKA.STAGE{_stage}.topdir', value=topdir,
                       source=func_name)
    # push top dir into ecf path / ecf
    ecf_path = os.path.join(topdir, 'ecf')
    params.set('EUREKA.PATHS.ECF_PATH', value=ecf_path, source=func_name)


def eureka_unique_id() -> str:
    """
    Assign a miriam id based on the time now and return it and the
    time now

    :return: the process id and the human time at creation
    :rtype: Tuple[str, str]
    """
    # get unix char code
    unixtime, humantime, rval = pogos_general.unix_char_code()
    # write sid
    sid = 'MID-{0:020d}-{1}'.format(int(unixtime), rval)
    # return sid
    return sid


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

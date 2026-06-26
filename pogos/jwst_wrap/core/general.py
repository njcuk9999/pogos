#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

Core functions for the POGOS JWST "standard pipeline" wrapper.

This mirrors ``pogos.eureka_wrap.core.general`` but runs the official JWST
calibration pipeline stages instead of Eureka!:

    setup_jwst_pre_extract  / run_jwst_pre_extract   -> Stage 1 + Stage 2
    setup_jwst_extract      / run_jwst_extract       -> Stage 3
    setup_jwst_post_extract / run_jwst_post_extract  -> any additional steps

Created on 2026-06-26

@author: cook
"""
import glob
import os

from aperocore.constants.param_functions import ParamDict
from aperocore.core import drs_log
from aperocore.core import drs_misc
from pogos.core import base
from pogos.core import general as pogos_general
from pogos.jwst_wrap.constants import jwst_pipelines

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'pogos.jwst_wrap.core.general'
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
# Define setup functions
# =============================================================================
def setup_jwst_pre_extract(params: ParamDict) -> ParamDict:
    # deal with user (or pogos) not running the JWST pre-extract steps
    if not params['RUN.PRE_JWST']:
        # return updated params
        return params
    # Make the directories
    make_jwst_dirs(params, stage=1)
    make_jwst_dirs(params, stage=2)
    # return updated params
    return params


def setup_jwst_extract(params: ParamDict) -> ParamDict:
    # deal with user (or pogos) not running the JWST extract step
    if not params['RUN.EXT_JWST']:
        # return updated params
        return params
    # Make the directories
    make_jwst_dirs(params, stage=3)
    # return updated params
    return params


def setup_jwst_post_extract(params: ParamDict) -> ParamDict:
    # deal with user (or pogos) not running the JWST post-extract step
    if not params['RUN.POST_JWST']:
        # return updated params
        return params
    # The standard JWST pipeline ends at Stage 3, the post-extraction step is
    #   reserved for any additional / custom steps (no directories required yet)
    # return updated params
    return params


# =============================================================================
# Define run functions
# =============================================================================
def run_jwst_pre_extract(params: ParamDict) -> ParamDict:
    # Try importing the JWST pipeline classes
    params, pipelines = import_jwst(params)
    # deal with user (or pogos) not running the JWST pre-extract steps
    if not params['RUN.PRE_JWST']:
        # nothing produced -> no instance to pass on
        return None
    # -------------------------------------------------------------------------
    # Make the directories
    make_jwst_dirs(params, stage=1)
    make_jwst_dirs(params, stage=2)
    # -------------------------------------------------------------------------
    # deal with test mode (return here)
    if params['JWST.GENERAL.TESTMODE']:
        return _jwst_result(params, stage=2)
    # -------------------------------------------------------------------------
    # Run Stage 1 (calwebb_detector1) + Stage 2 (calwebb_spec2/image2)
    # -------------------------------------------------------------------------
    run_jwst_stage(params, pipelines, stage=1)
    run_jwst_stage(params, pipelines, stage=2)
    # return the Stage 2 result (the input for the extraction step)
    return _jwst_result(params, stage=2)


def run_jwst_extract(params: ParamDict, pre_inst=None) -> ParamDict:
    # Try importing the JWST pipeline classes
    params, pipelines = import_jwst(params)
    # deal with user (or pogos) not running the JWST extract step
    if not params['RUN.EXT_JWST']:
        # nothing produced -> no instance to pass on
        return None
    # -------------------------------------------------------------------------
    # Make the directories
    make_jwst_dirs(params, stage=3)
    # -------------------------------------------------------------------------
    # push the outputs from the pre-extraction step into the Stage 3 input
    #   directory (mirrors TSOVORE -> SOSSISSE/MIRIAM)
    pogos_general.route_step_inputs(params, pre_inst,
                                    params.get('JWST.PATHS.IN_S3_PATH'))
    # -------------------------------------------------------------------------
    # deal with test mode (return here)
    if params['JWST.GENERAL.TESTMODE']:
        return _jwst_result(params, stage=3)
    # -------------------------------------------------------------------------
    # Run Stage 3 (calwebb_tso3/spec3/image3)
    # -------------------------------------------------------------------------
    run_jwst_stage(params, pipelines, stage=3)
    # return the Stage 3 result (the input for the post-extraction step)
    return _jwst_result(params, stage=3)


def run_jwst_post_extract(params: ParamDict, ext_inst=None) -> ParamDict:
    # Try importing the JWST pipeline classes
    params, pipelines = import_jwst(params)
    # deal with user (or pogos) not running the JWST post-extract step
    if not params['RUN.POST_JWST']:
        # nothing produced -> no instance to pass on
        return None
    # -------------------------------------------------------------------------
    # deal with test mode (return here)
    if params['JWST.GENERAL.TESTMODE']:
        return None
    # -------------------------------------------------------------------------
    # The standard JWST pipeline ends after Stage 3 (handled by the extraction
    #   step). The post-extraction step is reserved here for any additional
    #   custom processing the user may wish to add. The extraction-step
    #   instances are available via ext_inst (e.g. ext_inst['ext_jwst']) for
    #   any such processing.
    WLOG(params, '', 'JWST post-extraction: no additional standard JWST '
                     'stages to run.')
    # return params
    return None


# =============================================================================
# Define worker functions
# =============================================================================
def _jwst_result(params: ParamDict, stage: int) -> dict:
    """
    Build a uniform POGOS step-result for a JWST stage so the next reduction
    level can pick up its outputs (mirrors the TSOVORE/SOSSISSE instances).

    :param params: ParamDict, the parameter dictionary of constants
    :param stage: int, the JWST stage that produced the outputs
    :return: dict, the step result
    """
    # get the output directory for this stage
    output_dir = params.get(f'JWST.PATHS.OUT_S{stage}_PATH', None)
    # build and return the uniform step result
    return pogos_general.make_step_result('jwst', output_dir, stage=stage)


def import_jwst(params: ParamDict):
    """
    Try to import the standard JWST pipeline classes.

    :param params: ParamDict, the parameters dictionary
    :return: tuple, the (possibly updated) params and a dictionary mapping
             pipeline class names to the pipeline classes (or None if the
             jwst package is not installed)
    """
    # set function name
    func_name = f'{__NAME__}.import_jwst()'
    # storage for the pipeline classes
    pipelines = dict()
    try:
        # lazily import every pipeline class referenced by the mapping
        import importlib
        for name, module_name in jwst_pipelines.PIPELINE_MODULES.items():
            module = importlib.import_module(module_name)
            pipelines[name] = getattr(module, name)
        return params, pipelines
    except ImportError:
        # turn off the JWST steps if the package is not installed
        if not params['JWST.GENERAL.TESTMODE']:
            params.set('RUN.PRE_JWST', value=False, source=func_name)
            params.set('RUN.EXT_JWST', value=False, source=func_name)
            params.set('RUN.POST_JWST', value=False, source=func_name)
        # log a message that the JWST pipeline is not installed
        wmsg = 'The jwst package is not installed. Skipping JWST pipeline.'
        WLOG(params, 'warning', wmsg)
        return params, None


def run_jwst_stage(params: ParamDict, pipelines: dict, stage: int):
    """
    Run a single JWST pipeline stage on every input file found for that stage.

    :param params: ParamDict, the parameters dictionary
    :param pipelines: dict, mapping of pipeline class names -> classes
    :param stage: int, the JWST stage number (1, 2 or 3)
    :return: None
    """
    # set the function name
    func_name = f'{__NAME__}.run_jwst_stage()'
    # deal with no pipelines (jwst not installed)
    if pipelines is None:
        return
    # -------------------------------------------------------------------------
    # get the pipeline class for this stage + instrument mode
    pipe_class = get_pipeline_class(params, stage, pipelines)
    if pipe_class is None:
        return
    # -------------------------------------------------------------------------
    # get the input/output paths and the suffix we are looking for
    inpath = params[f'JWST.PATHS.IN_S{stage}_PATH']
    outpath = params[f'JWST.PATHS.OUT_S{stage}_PATH']
    suffix = params[f'JWST.STAGE{stage}.input_suffix']
    save_results = params[f'JWST.STAGE{stage}.save_results']
    # -------------------------------------------------------------------------
    # find the input files for this stage
    pattern = os.path.join(inpath, f'*_{suffix}.fits')
    files = sorted(glob.glob(pattern))
    # deal with no files found
    if len(files) == 0:
        wmsg = 'No Stage {0} input files found (looking for {1})'
        WLOG(params, 'warning', wmsg.format(stage, pattern))
        return
    # -------------------------------------------------------------------------
    # print progress
    msg = 'Running JWST Stage {0} [{1}] on {2} file(s)'
    margs = [stage, pipe_class.__name__, len(files)]
    WLOG(params, 'info', msg.format(*margs))
    # -------------------------------------------------------------------------
    # Stages 1 and 2 run per-exposure
    if stage in [1, 2]:
        for filename in files:
            WLOG(params, '', '\tProcessing {0}'.format(
                    os.path.basename(filename)))
            pipe_class.call(filename, output_dir=outpath,
                            save_results=save_results)
    # Stage 3 runs once on a level-3 association built from the inputs
    else:
        asn_file = build_stage3_association(params, files, outpath)
        pipe_class.call(asn_file, output_dir=outpath,
                        save_results=save_results)


def get_pipeline_class(params: ParamDict, stage: int, pipelines: dict):
    """
    Return the JWST pipeline class for a given stage and instrument mode.

    :param params: ParamDict, the parameters dictionary
    :param stage: int, the JWST stage number (1, 2 or 3)
    :param pipelines: dict, mapping of pipeline class names -> classes
    :return: the pipeline class or None if not available
    """
    # get the instrument mode
    instmode = params['GLOBAL.INSTRUMENTMODE']
    # get the pipeline class name for this stage + instrument mode
    name = jwst_pipelines.get_pipeline_name(stage, instmode)
    # deal with no pipeline defined for this combination
    if name is None:
        wmsg = ('No standard JWST Stage {0} pipeline defined for instrument '
                'mode {1}. Skipping.')
        WLOG(params, 'warning', wmsg.format(stage, instmode))
        return None
    # return the pipeline class
    return pipelines.get(name, None)


def build_stage3_association(params: ParamDict, files: list,
                             outpath: str) -> str:
    """
    Build a JWST level-3 association file from a list of Stage 2 outputs.

    :param params: ParamDict, the parameters dictionary
    :param files: list of str, the input files (*_calints.fits)
    :param outpath: str, the directory to write the association file into
    :return: str, the path to the written association (json) file
    """
    # lazily import the JWST association helpers
    from jwst.associations.asn_from_list import asn_from_list
    from jwst.associations.lib.rules_level3_base import DMS_Level3_Base
    # get the product name
    product_name = params['JWST.STAGE3.product_name']
    # build the association
    asn = asn_from_list(files, rule=DMS_Level3_Base, product_name=product_name)
    # serialise to json
    _, serialised = asn.dump(format='json')
    # construct the association file path
    asn_file = os.path.join(outpath, '{0}_asn.json'.format(product_name))
    # write the association file
    with open(asn_file, 'w') as afile:
        afile.write(serialised)
    # return the association file path
    return asn_file


def make_jwst_dirs(params: ParamDict, stage: int = None):
    """
    Prepare the input/output directories for the JWST pipeline stages.

    :param params: ParamDict, the parameters dictionary
    :param stage: int or None, only prepare this stage (or all stages if None)
    :return: None
    """
    # set the function name
    func_name = f'{__NAME__}.make_jwst_dirs()'
    # set basic prepare-directory parameters
    sid_path = 'JWST.GENERAL.SUBDIRECTORY'
    sid_null = jwst_unique_id()
    mode = 'jwst'
    # set topdir
    topdir = os.path.join(params['GLOBAL.DATA_PATH'], mode, params[sid_path])
    # Deal with the stages
    for _stage in [1, 2, 3]:
        if stage in [None, _stage]:
            # set the absolute pogos in/out path keys
            pogos_inkey = f'JWST.PATHS.IN_S{_stage}_PATH'
            pogos_outkey = f'JWST.PATHS.OUT_S{_stage}_PATH'
            # get the relative in/out directory names from the constants
            j_inpath = str(params[f'JWST.STAGE{_stage}.inputdir'])
            j_outpath = str(params[f'JWST.STAGE{_stage}.outputdir'])
            # starting point is setting the pogos in/out keys to these
            params.set(pogos_inkey, value=j_inpath, source=func_name)
            params.set(pogos_outkey, value=j_outpath, source=func_name)
            # run the prepare directory function for input and output
            pogos_general.prepare_directory(params, 'input', sid_path,
                                            sid_null, pogos_inkey, mode)
            pogos_general.prepare_directory(params, 'output', sid_path,
                                            sid_null, pogos_outkey, mode)
            # set the top path
            params.set(f'JWST.STAGE{_stage}.topdir', value=topdir,
                       source=func_name)


def jwst_unique_id() -> str:
    """
    Assign a unique JWST id based on the time now and return it.

    :return: str, the unique id
    """
    # get unix char code
    unixtime, humantime, rval = pogos_general.unix_char_code()
    # write sid
    sid = 'JID-{0:020d}-{1}'.format(int(unixtime), rval)
    # return sid
    return sid


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================


#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2024-10-29 at 10:16

@author: cook
"""
import os
import random
import string
import time
from typing import Any, Dict, List, Optional, Tuple

import glob
import shutil
import numpy as np
from astropy.time import Time

from aperocore.constants import param_functions
from aperocore.core import drs_log

from pogos.core import base

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'pogos.core.general.py'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__
# get parameter dictionary
ParamDict = param_functions.ParamDict
# get the logger
WLOG = drs_log.wlog
# get all chars
CHARS = string.ascii_uppercase + string.digits


# =============================================================================
# Define functions
# =============================================================================
def start_splash(name: str):
    """
    Print the start splash

    :return: None, prints to screen
    """
    WLOG(None, 'info', drs_log.MPARAMS['LOG.HEADER'], colour='magenta')
    WLOG(None, 'info', name, colour='magenta')
    vargs = [__version__, __date__]
    WLOG(None, 'info', 'v{0} [{1}]'.format(*vargs), colour='magenta')
    WLOG(None, 'info', drs_log.MPARAMS['LOG.HEADER'], colour='magenta')


def end_splash():
    """
    Print the end splash

    :return: None, prints to screen
    """
    WLOG(None, 'info', drs_log.MPARAMS['LOG.HEADER'], colour='magenta')
    WLOG(None, 'info', 'End of code', colour='magenta')
    WLOG(None, 'info', drs_log.MPARAMS['LOG.HEADER'], colour='magenta')


def unix_char_code() -> Tuple[float, str, str]:
    """
    Get the time now (using astropy.Time) and return the unix time
    human time and a random code of 4 characters

    :return: tuple, 1. the unix time now, 2. the human time now, 3. a random
             set of 4 characters
    """
    # set function name
    # _ = display_func('unix_char_code', __NAME__)
    # we need a random seed
    np.random.seed(random.randint(1, 2 ** 30))
    # generate a random number (in case time is too similar)
    #  -- happens a lot in multiprocessing
    rint = np.random.randint(1000, 9999, 1)[0] / 1e7
    # wait a fraction of time (between 1us and 1ms)
    time.sleep(float(rint))
    # get the time now from astropy
    timenow = Time.now()
    # get unix and human time from astropy time now
    unixtime = timenow.unix * 1e7
    humantime = timenow.iso
    # generate random four characters to make sure sid is unique
    rval = ''.join(np.random.choice(list(CHARS), size=4))
    return unixtime, humantime, rval


def prepare_directory(params: ParamDict, pkind: str, sid_path: str,
                      sid_null: str, file_path: str, pmode: str,
                      verbose: bool = True):
    """
    Prepare either an input or output directory for use in POGOS
    :param params:
    :param pkind:
    :param sid_path:
    :param file_path:
    :param mode:
    :return:
    """
    func_name = f'{__NAME__}.prepare_directory()'
    # generate SUBDIRECTORY if not given
    if params[sid_path] is None:
        params[sid_path] = sid_null
    # get the output path from the params
    path_constant = params[file_path]
    # get this to inputs by default
    if os.path.exists(os.path.realpath(path_constant)):
        my_path = os.path.realpath(path_constant)
    else:
        data_path = params.rget('GLOBAL.DATA_PATH', required=True)
        subdirectory = params.rget(sid_path, required=True)
        if path_constant is None:
            my_path = pkind
        else:
            my_path = str(path_constant)
        # if not, make it relative to the global database
        my_path = os.path.join(data_path, pmode, subdirectory, my_path)
    # make sure the path is in the params
    if not os.path.exists(my_path):
        os.makedirs(my_path)
    # update output path
    params.set(file_path, value=my_path, source=func_name)

# =============================================================================
# Step input/output routing (PRE_EXTRACT -> EXTRACT -> POST_EXTRACT)
# =============================================================================
def make_step_result(module: str, output_dir: Optional[str],
                     output_files: Optional[List[str]] = None,
                     **extra: Any) -> Dict[str, Any]:
    """
    Build a uniform "step result" describing the outputs of a reduction step.

    This is the object a step (e.g. a pre-extraction or extraction flavour)
    returns so that the next step (e.g. extraction or post-extraction) can pick
    up its outputs - this mirrors the way TSOVORE/SOSSISSE/MIRIAM instances are
    passed between steps via pre_inst / ext_inst.

    :param module: str, the name of the module/flavour (e.g. 'eureka', 'jwst')
    :param output_dir: str or None, the directory the step wrote its outputs to
    :param output_files: list of str or None, explicit output files (if known)
    :param extra: any additional keys to store on the result
    :return: dict, the step result
    """
    result = dict(module=module, output_dir=output_dir,
                  output_files=list(output_files) if output_files else [])
    result.update(extra)
    return result


def step_output_files(instance: Any) -> Tuple[Optional[str], List[str]]:
    """
    Best-effort extraction of the output directory and files from a step
    instance/result.

    Currently understands the uniform ``make_step_result`` dictionaries (used
    by the file-based flavours eureka/jwst). Other instance types (e.g. the
    in-memory TSOVORE/NAMELESS objects) are routed by their own dedicated
    helpers and are safely ignored here (returns no files).

    :param instance: the step instance/result to inspect
    :return: tuple (output_dir, output_files)
    """
    # uniform step-result dictionaries
    if isinstance(instance, dict) and 'output_dir' in instance:
        out_dir = instance.get('output_dir')
        files = list(instance.get('output_files') or [])
        # fall back to globbing the output directory if no explicit files
        if not files and out_dir is not None and os.path.exists(out_dir):
            files = sorted(glob.glob(os.path.join(out_dir, '*.fits')))
        return out_dir, files
    # unknown instance type -> no routable files
    return None, []


def route_step_inputs(params: ParamDict, instances: Optional[Dict[str, Any]],
                      dest_dir: Optional[str]):
    """
    Copy the outputs of predecessor step instances into a destination input
    directory.

    This is the generic equivalent of sossisse's ``tsovore_input`` /
    sorbet's ``sossisse_input``: it takes the instances produced by the
    previous reduction level (pre_inst for extraction, ext_inst for
    post-extraction) and copies their output files into the current step's
    input directory so the current step can find them.

    Copying is skipped when the source directory IS the destination directory
    (i.e. when the flavours already chain their directories internally, such as
    eureka/jwst Stage 2 output == Stage 3 input).

    :param params: ParamDict, the parameter dictionary of constants
    :param instances: dict or None, the predecessor step instances
    :param dest_dir: str or None, the destination input directory
    :return: None
    """
    # set function name
    func_name = f'{__NAME__}.route_step_inputs()'
    # deal with nothing to do
    if dest_dir is None or not instances:
        return
    # loop around the predecessor instances
    for key in instances:
        instance = instances[key]
        # skip empty instances
        if instance is None:
            continue
        # get the output directory and files from the instance
        out_dir, files = step_output_files(instance)
        # skip instances that don't expose routable files
        if len(files) == 0:
            continue
        # skip if the source directory is already the destination (internal
        #   directory chaining, e.g. within a single flavour)
        if out_dir is not None:
            if os.path.realpath(out_dir) == os.path.realpath(dest_dir):
                continue
        # make sure the destination exists
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        # copy each output file into the destination directory
        for src in files:
            dst = os.path.join(dest_dir, os.path.basename(src))
            # skip copying a file onto itself
            if os.path.realpath(src) == os.path.realpath(dst):
                continue
            # log the copy
            msg = 'Copying {0} output to next step input: {1}'
            WLOG(params, '', msg.format(key, os.path.basename(src)))
            # copy the file
            shutil.copy(src, dst)

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

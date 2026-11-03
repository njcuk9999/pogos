#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2025-02-18 at 14:13

@author: cook
"""
import os
import shutil
from typing import Any, Dict, Optional

from aperocore.constants.param_functions import ParamDict
from aperocore.core import drs_log
from aperocore.core import drs_misc
from pogos.core import base
from pogos.tsovore.instruments import default as ts_default

try:
    import sossisse
    from sossisse.core import const_funcs
    from sossisse.core.exceptions import SossisseFileException
    from sossisse.recipes import run_sossisse as sossisse_run
except ImportError:
    emsg = 'Please install sossisse'
    raise base.PogosException(emsg)

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
def _sossisse_parameters(params: ParamDict, sossisse_params):
    sparams = sossisse_params.as_param_dict()
    sparams['INPUTS.PROJECT_NAME'] = params.rget('GLOBAL.PROJECT_NAME',
                                               required=True)
    sparams['INPUTS.SOSSIOPATH'] = params.rget('GLOBAL.DATA_PATH', required=True)
    return sparams


def run_sossisse_module(params: ParamDict, pre_inst: Dict[str, Any]):
    """
    Run the sossisse run recipe

    :param params: ParamDict, the parameter dictionary of constants

    :return: None, runs sossisse run
    """
    # set the function name
    func_name = f'{__NAME__}.run_sossisse_module'
    # -------------------------------------------------------------------------
    # get the instances from the pre-extraction step
    tsovore_inst = pre_inst.get('tsovore', None)
    # -------------------------------------------------------------------------
    # if RUN.SOSSISSE is False skip
    if not params['RUN.SOSSISSE']:
        return
    # get the SOSSISSE sub-dictionary
    sossisse_params = params.get('SOSSISSE')
    # deal with SOSSISSE nested dictionary not in params
    if sossisse_params is None:
        WLOG(params, 'warning', 'SOSSISSE not in params - skipping.')
        return
    # convert to independent parameter dictionary
    sparams = _sossisse_parameters(params, sossisse_params)
    # make sure yaml file is set
    sparams['INPUTS.PARAM_FILE'] = str(params['GLOBAL.YAML_FILE'])

    # ----------------------------------------------------------------------
    # Deal with input from TSOVORE if available
    # ----------------------------------------------------------------------
    if tsovore_inst is not None:
        sparams = tsovore_input(params, tsovore_inst)
        # ---------------------------------------------------------------------
        # SOSSISSE requires raw data to be copied to a specific location
        # check here if that exists and if not prompt the user
        spath = sparams.rget('PATHS.RAWPATH', required=True)
        # deal with SOSSISSE raw data path not existing
        if not os.path.exists(spath):
            msg = ('\n\nSOSSISSE requires raw data to be in a '
                   'specific location:\n   {0}\n'
                   'Please copy the raw data to this location and re-run.\n'
                   'Skipping SOSSISSE run.')
            # create path if not there
            os.makedirs(spath, exist_ok=True)
            # return an error
            raise SossisseFileException(msg.format(spath))
    # -------------------------------------------------------------------------
    # run the sossisse recipe
    inst = sossisse_run.main(__YAML_DICT__=sparams)
    # get the output SOSSISSE directory
    return inst


def setup_sossisse_module(params: ParamDict, cdict):
    """
    Run the sossisse setup recipe

    :param params: ParamDict, the parameter dictionary of constants

    :return: None, runs sossisse setup
    """
    # set function name
    func_name = f'{__NAME__}.setup_sossisse_module()'
    # if RUN.SOSSISSE is False skip
    if not params['RUN.SOSSISSE']:
        return
    # get the SOSSISSE sub-dictionary
    sossisse_params = params.get('SOSSISSE')
    # deal with SOSSISSE nested dictionary not in params
    if sossisse_params is None:
        # we assume that if SOSSISSE is not there we don't want to run this
        return
    yaml_file = params.rget('GLOBAL.YAML_FILE', required=True)
    # convert to independent parameter dictionary
    sparams = _sossisse_parameters(params, sossisse_params)
    # make sure yaml file is set
    sparams['INPUTS.PARAM_FILE'] = str(yaml_file)
    # setup for SOSSISSE just uses "get_parameters" function
    inst = sossisse.get_parameters(__NAME__=__NAME__, setup_mode=True,
                                   log_level='setup', __YAML_DICT__=sparams)
    # -------------------------------------------------------------------------
    # get the SOSSISSE PATH params out of instrument class
    spaths = inst.params.get('PATHS')
    # update the SOSSISSE paths
    for path in spaths.keys():
        # get the key in POGOS parameters
        pkey = f'SOSSISSE.PATHS.{path}'
        # if the key exists update it
        if pkey in params:
            params.set(pkey, spaths[path], source=func_name)
    # -------------------------------------------------------------------------
    # re-save the yaml file after sossisse updates
    # print progress
    msg = 'Re-saving constants to yaml file after SOSSISSE setup: {0}'
    WLOG(params, '', msg.format(os.path.realpath(yaml_file)))
    # save the constants dictionary to yaml file
    cdict.save_yaml(params, outpath=yaml_file, log=False,
                    mode=params['GLOBAL.INSTRUMENTMODE'])
    # -------------------------------------------------------------------------
    # return the parameters
    return params


def tsovore_input(params: ParamDict,
                  tsovore_inst: Optional[ts_default.JWST] = None):
    """
    Copy TSOVORE science and wavelength files into SOSSISSE directories.

    NIRSpec calibrations are identified by their DETECTOR headers, copied
    with detector-prefixed basenames, and forwarded in NRS1/NRS2 order.
    Other instruments retain the last calibration as a single wave file.

    :param params: POGOS parameters; the SOSSISSE view is updated in place.
    :param tsovore_inst: Completed TSOVORE instance with OUT and CALIBS
        products. Required when the SOSSISSE parameter view exists.
    :return: Updated SOSSISSE parameters, or None without a SOSSISSE view.
    :raises SossisseFileException: Unknown or duplicate NIRSpec detector.
    """
    # set function name
    func_name = f'{__NAME__}.tsovore_input'
    # -------------------------------------------------------------------------
    # get the SOSSISSE sub-dictionary
    sossisse_params = params.get('SOSSISSE')
    # deal with SOSSISSE nested dictionary not in params
    if sossisse_params is None:
        # we assume that if SOSSISSE is not there we don't want to run this
        return
    # -------------------------------------------------------------------------
    # get tsovore files to copy
    tsovore_outputs = tsovore_inst.variables['OUT']
    # set the output files as input to SOSSISSE
    sossisse_params['GENERAL.FILES'] = tsovore_outputs
    # -------------------------------------------------------------------------
    # convert to independent parameter dictionary
    sparams = _sossisse_parameters(params, sossisse_params)
    # -------------------------------------------------------------------------
    # set the source of the parameters (POGOS)
    sparams['__SOURCE__'] = 'POGOS'
    # ---------------------------------------------------------------------
    # prepare input directory
    sparams = const_funcs.run_time_params(sparams, only_create=True)
    # Get the SOSSISSE input directory
    sossisse_input_dir = str(sparams['PATHS.RAWPATH'])
    # ---------------------------------------------------------------------
    # copy files to SOSSISSE input location
    for tsovore_output in tsovore_outputs:
        # get the filename
        filename = str(os.path.basename(tsovore_output))
        # define source and destination
        source = str(tsovore_output)
        dest = str(os.path.join(sossisse_input_dir, filename))
        # log the copy
        msg = f'Copying TSOVORE output file to SOSSISSE input: {filename}'
        WLOG(params, '', msg)
        # copy file
        shutil.copy(source, dest)
    # ---------------------------------------------------------------------
    # copy calibration files
    if 'X1D' in tsovore_inst.variables['CALIBS']:
        # get the calibration file
        calib_files = tsovore_inst.variables['CALIBS']['X1D']
        # deal with string / list
        if isinstance(calib_files, str):
            calib_files = [calib_files]
        if len(calib_files) > 0:
            calib_dir = sparams.rget('PATHS.CALIBPATH', required=True)
        # Keep detector-to-file associations independent of input ordering.
        wave_files = dict()
        # Prefer the backend mode while retaining the global fallback.
        instrument_mode = str(sossisse_params.get(
            'INPUTS.INSTRUMENTMODE',
            params.get('GLOBAL.INSTRUMENTMODE', '')))
        is_nirspec = instrument_mode.startswith('JWST.NIRSPEC')
        # Only NIRSpec needs detector headers to associate calibrations.
        for calib_file in calib_files:
            if is_nirspec:
                # Defer the FITS dependency until detector metadata is needed.
                from astropy.io import fits

                # Reject ambiguous associations instead of replacing a trace.
                calibration_header = fits.getheader(calib_file)
                detector = calibration_header.get('DETECTOR', '').upper()
                if detector not in ('NRS1', 'NRS2'):
                    message = f'Unknown calibration DETECTOR: {calib_file}'
                    raise SossisseFileException(message)
                if detector in wave_files:
                    message = f'Duplicate {detector} wavelength calibration'
                    raise SossisseFileException(message)
            else:
                # Reuse one slot to preserve legacy last-calibration behavior.
                detector = 'single'
            # define source and destination
            source = str(calib_file)
            basename = os.path.basename(calib_file)
            # Prevent equal input basenames from overwriting another detector.
            if is_nirspec:
                basename = f'{detector.lower()}_{basename}'
            dest = str(os.path.join(calib_dir, basename))
            # log the copy
            msg = (f'Copying TSOVORE calibration file to SOSSISSE calib dir: '
                   f'{os.path.basename(calib_file)}')
            WLOG(params, '', msg)
            # copy file
            shutil.copy(source, dest)
            # Store the copied basename, not its original absolute path.
            wave_files[detector] = basename
        # NIRSpec consumes an ordered list; other modes consume one filename.
        if wave_files:
            ordered_files = [wave_files[detector]
                             for detector in sorted(wave_files)]
            sossisse_params['GENERAL.WAVE_FILE'] = (
                ordered_files if is_nirspec else ordered_files[-1])
            # Use the backend's extension-1D wavelength format identifier.
            sossisse_params['GENERAL.WAVE_FILE_TYPE'] = 'ext1d'
    # ---------------------------------------------------------------------
    # push back into sossisse_params (for return) - as before this only in
    # sparams (due to being populated in run_time_params)
    for key in sparams:
        if key not in sossisse_params:
            sossisse_params[key] = sparams[key]
        elif sossisse_params[key] is None and sparams[key] is not None:
            sossisse_params[key] = sparams[key]
    # ---------------------------------------------------------------------
    sossisse_params['INPUTS.PROJECT_NAME'] = sparams['INPUTS.PROJECT_NAME']
    sossisse_params['INPUTS.SOSSIOPATH'] = sparams['INPUTS.SOSSIOPATH']
    # return params
    return sossisse_params


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

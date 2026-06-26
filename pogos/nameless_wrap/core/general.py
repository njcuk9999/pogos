#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

Core functions for the POGOS NAMELESS wrapper.

NAMELESS is a JWST NIRISS/SOSS-only time-series reduction code. This mirrors
``pogos.eureka_wrap.core.general`` but drives the NAMELESS reduction object.
The NAMELESS reduction maps onto the POGOS reduction steps as follows:

    Pre-extraction  [RUN.PRE_NAMELESS]  -> run_s1, run_s2, run_prep, run_cst
    Extraction      [RUN.EXT_NAMELESS]  -> run_ext
    (there is no post-extraction step for NAMELESS)

NAMELESS keeps reduction products in memory, so the extraction step needs the
prep/custom-step products produced by the pre-extraction step. Following the
POGOS flavour convention, the pre-extraction step returns the NAMELESS
reduction object which is then handed to the extraction step via ``pre_inst``.
NAMELESS normally stores outputs in a relative ``Reductions/`` directory; here
we override ``red_dir`` (and its sub-directories) so it acts like the
eureka_wrap topdir, i.e. {GLOBAL.DATA_PATH}/nameless/{SUBDIRECTORY}.

Created on 2026-06-26

@author: cook
"""
import glob
import os
import shutil
import tempfile
from typing import Any, Dict, Optional

from aperocore.constants.param_functions import ParamDict
from aperocore.core import drs_log
from aperocore.core import drs_misc
from pogos.core import base
from pogos.core import general as pogos_general

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'pogos.nameless_wrap.core.general'
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
# NAMELESS only supports JWST NIRISS/SOSS
NAMELESS_INSTMODE = 'JWST.NIRISS.SOSS'


# =============================================================================
# Define setup functions
# =============================================================================
def setup_nameless_pre_extract(params: ParamDict) -> ParamDict:
    # deal with user (or pogos) not running the NAMELESS pre-extract steps
    if not params['RUN.PRE_NAMELESS']:
        # return updated params
        return params
    # Make the directories
    make_nameless_dirs(params)
    # return updated params
    return params


def setup_nameless_extract(params: ParamDict) -> ParamDict:
    # deal with user (or pogos) not running the NAMELESS extract step
    if not params['RUN.EXT_NAMELESS']:
        # return updated params
        return params
    # Make the directories
    make_nameless_dirs(params)
    # return updated params
    return params


# =============================================================================
# Define run functions
# =============================================================================
def run_nameless_pre_extract(params: ParamDict):
    """
    Run the NAMELESS pre-extraction steps (Stage 1 + Stage 2 + prep + custom).

    :param params: ParamDict, the parameter dictionary of constants
    :return: the NAMELESS reduction object (or None if it was not run). This is
             passed to the extraction step via pre_inst.
    """
    # Try importing NAMELESS
    params, nameless_mod = import_nameless(params)
    # deal with user (or pogos) not running the NAMELESS pre-extract steps
    if not params['RUN.PRE_NAMELESS']:
        return None
    # NAMELESS only supports NIRISS/SOSS
    if not check_soss(params):
        return None
    # -------------------------------------------------------------------------
    # Make the directories
    make_nameless_dirs(params)
    # -------------------------------------------------------------------------
    # deal with test mode (return here)
    if params['NAMELESS.GENERAL.TESTMODE']:
        return None
    # deal with NAMELESS not installed
    if nameless_mod is None:
        return None
    # -------------------------------------------------------------------------
    # build the NAMELESS reduction object (red_dir == POGOS topdir)
    reduc = build_reduc(params, nameless_mod)
    if reduc is None:
        return None
    # build the settings dictionaries from the POGOS constants
    settings = build_settings(params)
    # -------------------------------------------------------------------------
    # run Stage 1, Stage 2, prep and custom steps (but not extraction)
    WLOG(params, 'info', 'Running NAMELESS pre-extraction (s1, s2, prep, cst)')
    reduc.run_reduction(run_s1=True, run_s2=True, run_prep=True, run_cst=True,
                        run_ext=False, **settings)
    # return the reduction object (handed to the extraction step)
    return reduc


def run_nameless_extract(params: ParamDict,
                         pre_inst: Optional[Dict[str, Any]] = None):
    """
    Run the NAMELESS extraction step (run_ext).

    :param params: ParamDict, the parameter dictionary of constants
    :param pre_inst: dict, the pre-extraction instances (expects the NAMELESS
                     reduction object under the 'pre_nameless' key)
    :return: the NAMELESS reduction object (or None if it was not run)
    """
    # Try importing NAMELESS
    params, nameless_mod = import_nameless(params)
    # deal with user (or pogos) not running the NAMELESS extract step
    if not params['RUN.EXT_NAMELESS']:
        return None
    # NAMELESS only supports NIRISS/SOSS
    if not check_soss(params):
        return None
    # -------------------------------------------------------------------------
    # Make the directories
    make_nameless_dirs(params)
    # -------------------------------------------------------------------------
    # deal with test mode (return here)
    if params['NAMELESS.GENERAL.TESTMODE']:
        return None
    # deal with NAMELESS not installed
    if nameless_mod is None:
        return None
    # build the settings dictionaries from the POGOS constants
    settings = build_settings(params)
    # -------------------------------------------------------------------------
    # primary path: use the reduction object from the pre-extraction step
    #   (NAMELESS keeps the prep/custom-step products in memory)
    reduc = None
    if pre_inst is not None:
        reduc = pre_inst.get('pre_nameless', None)
    # -------------------------------------------------------------------------
    if reduc is not None:
        WLOG(params, 'info', 'Running NAMELESS extraction (ext)')
        reduc.run_reduction(run_s1=False, run_s2=False, run_prep=False,
                            run_cst=False, run_ext=True, **settings)
        return reduc
    # -------------------------------------------------------------------------
    # fallback: no pre-extraction instance available in this session, so we
    #   rebuild the object and reconstruct the products from disk (requires the
    #   pre-extraction step to have run previously into the same sub-directory)
    wmsg = ('No NAMELESS pre-extraction instance found. Reconstructing from '
            'disk (requires RUN.PRE_NAMELESS to have been run into the same '
            'SUBDIRECTORY).')
    WLOG(params, 'warning', wmsg)
    reduc = build_reduc(params, nameless_mod)
    if reduc is None:
        return None
    # re-run the prep step to repopulate the trace/wavelength/time products
    #   (this reads the Stage 2 outputs already on disk)
    try:
        reduc.run_reduction(run_s1=False, run_s2=False, run_prep=True,
                            run_cst=False, run_ext=False, **settings)
        # reload the cleaned (custom-step) data from disk into data_cst
        data, err, dq, _, _ = reduc.collate(reduc.cst_dir, 'clean')
        reduc.data_cst, reduc.err_s2, reduc.dq_s2 = data, err, dq
    except Exception as err:
        emsg = ('Could not reconstruct NAMELESS products from disk: {0}\n'
                'Please run RUN.PRE_NAMELESS first.')
        WLOG(params, 'warning', emsg.format(str(err)))
        return None
    # now run the extraction
    WLOG(params, 'info', 'Running NAMELESS extraction (ext)')
    reduc.run_reduction(run_s1=False, run_s2=False, run_prep=False,
                        run_cst=False, run_ext=True, **settings)
    return reduc


# =============================================================================
# Define worker functions
# =============================================================================
def import_nameless(params: ParamDict):
    """
    Try to import the NAMELESS package.

    :param params: ParamDict, the parameters dictionary
    :return: tuple, the (possibly updated) params and the NAMELESS module (or
             None if the NAMELESS package is not installed)
    """
    # set function name
    func_name = f'{__NAME__}.import_nameless()'
    try:
        import NAMELESS.nameless as nameless_mod
        return params, nameless_mod
    except ImportError:
        # turn off the NAMELESS steps if the package is not installed
        if not params['NAMELESS.GENERAL.TESTMODE']:
            params.set('RUN.PRE_NAMELESS', value=False, source=func_name)
            params.set('RUN.EXT_NAMELESS', value=False, source=func_name)
        # log a message that NAMELESS is not installed
        wmsg = 'The NAMELESS package is not installed. Skipping NAMELESS.'
        WLOG(params, 'warning', wmsg)
        return params, None


def check_soss(params: ParamDict) -> bool:
    """
    Check the instrument mode is JWST NIRISS/SOSS (the only mode NAMELESS
    supports).

    :param params: ParamDict, the parameters dictionary
    :return: bool, True if the instrument mode is supported by NAMELESS
    """
    # get the instrument mode
    instmode = params['GLOBAL.INSTRUMENTMODE']
    # deal with unsupported instrument mode
    if instmode != NAMELESS_INSTMODE:
        wmsg = ('NAMELESS only supports {0} (got {1}). Skipping NAMELESS.')
        WLOG(params, 'warning', wmsg.format(NAMELESS_INSTMODE, instmode))
        return False
    return True


def build_settings(params: ParamDict) -> Dict[str, Dict[str, Any]]:
    """
    Build the NAMELESS settings dictionaries from the POGOS constants.

    :param params: ParamDict, the parameters dictionary
    :return: dict, the keyword arguments for nameless.run_reduction()
    """
    def _group(group: str, keys: list) -> Dict[str, Any]:
        return {key: params[f'NAMELESS.{group}.{key}'] for key in keys}
    # Stage 1 settings
    s1_settings = _group('S1_SETTINGS',
                         ['save_gs', 'save_dq', 'save_sat', 'save_sb',
                          'save_rp', 'save_lin', 'save_dc', 'save_jd',
                          'save_rf', 'save_gain', 'skip_dc', 'skip_jd',
                          'skip_gain'])
    # Stage 2 settings
    s2_settings = _group('S2_SETTINGS', ['save_wcs', 'save_ff', 'save_st'])
    # prep settings
    prep_settings = _group('PREP_SETTINGS',
                          ['wlc_pixs', 'trace_method', 'sampfac', 'nknots_o1',
                           'nknots_o2', 'xmin_o2', 'xmax_o2', 'plotting',
                           'dpi'])
    # custom step settings
    cst_settings = _group('CST_SETTINGS',
                         ['frac_int', 'interp_bp', 'inds1_bg', 'inds2_bg',
                          'bg_quant', 'wlc_pixs', 'nsig_CR', 'wlc_window',
                          'CR_window', 'ap_1f', 'median_ints', 'plotting',
                          'dpi'])
    # extraction settings
    ext_settings = _group('EXT_SETTINGS', ['ap_radius', 'plotting', 'dpi'])
    # return the run_reduction keyword arguments
    return dict(s1_settings=s1_settings, s2_settings=s2_settings,
                prep_settings=prep_settings, cst_settings=cst_settings,
                ext_settings=ext_settings)


def discover_files(params: ParamDict, in_path: str):
    """
    Determine the JWST file handle, number of segments and segment list.

    Uses the user-provided constants where available, otherwise auto-detects
    them from the *_uncal.fits files in the input path (mirroring NAMELESS).

    :param params: ParamDict, the parameters dictionary
    :param in_path: str, the path containing the *_uncal.fits files
    :return: tuple (handle, nseg, segs) or None if no files were found
    """
    # get the user-provided values (may be None)
    handle = params['NAMELESS.GENERAL.HANDLE']
    nseg = params['NAMELESS.GENERAL.NSEG']
    segs = params['NAMELESS.GENERAL.SEGS']
    # treat empty strings/lists as not provided
    if isinstance(handle, str) and handle.strip() == '':
        handle = None
    if isinstance(segs, (list, tuple)) and len(segs) == 0:
        segs = None
    # do we need to auto-detect anything?
    need_discovery = handle is None or nseg is None or segs is None
    if need_discovery:
        # glob the uncal files (mirroring NAMELESS file naming)
        uncal_files = sorted(glob.glob(os.path.join(in_path, '*uncal.fits')))
        # deal with no files found
        if len(uncal_files) == 0:
            wmsg = 'No *_uncal.fits files found in {0}'
            WLOG(params, 'warning', wmsg.format(in_path))
            return None
        basenames = [os.path.basename(f) for f in uncal_files]
        # handle is the first 25 characters of the filename
        if handle is None:
            handle = basenames[0][:25]
        # segments are characters 29:32 of the filename
        if segs is None:
            segs = sorted([bname[29:32] for bname in basenames])
        # number of segments
        if nseg is None:
            nseg = len(segs)
    # return the discovered (or provided) values
    return str(handle), int(nseg), list(segs)


def build_reduc(params: ParamDict, nameless_mod):
    """
    Construct a NAMELESS reduction object whose directories point at the POGOS
    paths (red_dir == topdir == {GLOBAL.DATA_PATH}/nameless/{SUBDIRECTORY}).

    :param params: ParamDict, the parameters dictionary
    :param nameless_mod: the imported NAMELESS.nameless module
    :return: the NAMELESS reduction object (or None on failure)
    """
    # get the POGOS paths
    in_path = params['NAMELESS.PATHS.IN_PATH']
    topdir = params['NAMELESS.PATHS.TOPDIR']
    ancil_path = params['NAMELESS.PATHS.ANCIL_PATH']
    # -------------------------------------------------------------------------
    # discover the file handle / segments
    discovered = discover_files(params, in_path)
    if discovered is None:
        return None
    handle, nseg, segs = discovered
    # -------------------------------------------------------------------------
    # NAMELESS makes (relative) directories in its __init__; construct it in a
    #   throw-away temporary working directory so no junk is left behind, then
    #   override the directories with the absolute POGOS paths below.
    cwd = os.getcwd()
    tmpdir = tempfile.mkdtemp(prefix='pogos_nameless_')
    try:
        os.chdir(tmpdir)
        reduc = nameless_mod.nameless(obs_folder='pogos', red_folder='pogos',
                                      nseg=nseg, segs=segs, handle=handle)
    finally:
        os.chdir(cwd)
        shutil.rmtree(tmpdir, ignore_errors=True)
    # -------------------------------------------------------------------------
    # override the directories to the absolute POGOS paths
    #   (self.red_dir acts like the eureka_wrap topdir)
    reduc.obs_dir = in_path
    reduc.red_dir = topdir
    reduc.s1_red_dir = os.path.join(topdir, 'stage1_outputs')
    reduc.s2_red_dir = os.path.join(topdir, 'stage2_outputs')
    reduc.prep_dir = os.path.join(topdir, 'prep_step_outputs')
    reduc.cst_dir = os.path.join(topdir, 'custom_steps_outputs')
    reduc.ext_dir = os.path.join(topdir, 'extraction_outputs')
    # point at the NAMELESS Auxiliary directory (if provided)
    if ancil_path not in [None, 'None', '']:
        reduc.ancil_dir = str(ancil_path)
    # -------------------------------------------------------------------------
    # make sure all of the POGOS directories exist
    for directory in [reduc.red_dir, reduc.s1_red_dir, reduc.s2_red_dir,
                      reduc.prep_dir, reduc.cst_dir, reduc.ext_dir]:
        if not os.path.exists(directory):
            os.makedirs(directory)
    # attach the full settings to the object (mirrors example_run_nameless)
    reduc.config = build_settings(params)
    # return the reduction object
    return reduc


def make_nameless_dirs(params: ParamDict):
    """
    Prepare the input directory and the NAMELESS reduction (top) directory.

    :param params: ParamDict, the parameters dictionary
    :return: None
    """
    # set the function name
    func_name = f'{__NAME__}.make_nameless_dirs()'
    # set basic prepare-directory parameters
    sid_path = 'NAMELESS.GENERAL.SUBDIRECTORY'
    sid_null = nameless_unique_id()
    mode = 'nameless'
    # -------------------------------------------------------------------------
    # prepare the input directory (where the uncal files live)
    inkey = 'NAMELESS.PATHS.IN_PATH'
    params.set(inkey, value=str(params['NAMELESS.GENERAL.INPUTDIR']),
               source=func_name)
    pogos_general.prepare_directory(params, 'input', sid_path, sid_null, inkey,
                                    mode)
    # -------------------------------------------------------------------------
    # set the reduction (top) directory == {DATA_PATH}/nameless/{SUBDIRECTORY}
    #   (prepare_directory above guarantees sid_path is now set)
    topdir = os.path.join(params['GLOBAL.DATA_PATH'], mode, params[sid_path])
    params.set('NAMELESS.PATHS.TOPDIR', value=topdir, source=func_name)
    # make the top directory
    if not os.path.exists(topdir):
        os.makedirs(topdir)


def nameless_unique_id() -> str:
    """
    Assign a unique NAMELESS id based on the time now and return it.

    :return: str, the unique id
    """
    # get unix char code
    unixtime, humantime, rval = pogos_general.unix_char_code()
    # write sid
    sid = 'NID-{0:020d}-{1}'.format(int(unixtime), rval)
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


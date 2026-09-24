#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2026-09-23 at 09:00

@author: cook
"""
import os
import shutil
from typing import Dict, List, Optional, Tuple

from aperocore.constants import param_functions
from aperocore.core import drs_log

from pogos.core import base
from pogos.core import definitions

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'pogos.core.reset.py'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__
# get parameter dictionary
ParamDict = param_functions.ParamDict
# get the logger
WLOG = drs_log.wlog
# Eureka post-extraction (Stages 4-6) output sub-folders, relative to
# {GLOBAL.DATA_PATH}/eureka/{SUBDIRECTORY} - these have no fixed PATHS.*
# constant (unlike Stages 1-3) so they are computed here directly
EUREKA_POST_STAGES = [4, 5, 6]
# NAMELESS output sub-folders, relative to
# {GLOBAL.DATA_PATH}/nameless/{SUBDIRECTORY} (the reduction/top directory).
# NAMELESS keeps its raw-input copy inside this same top directory (in the
# NAMELESS.GENERAL.INPUTDIR sub-folder), so we reset only these known
# output sub-folders rather than the whole top directory.
NAMELESS_OUTPUT_SUBFOLDERS = ['stage1_outputs', 'stage2_outputs',
                              'prep_step_outputs', 'custom_steps_outputs',
                              'extraction_outputs']


# =============================================================================
# Define functions
# =============================================================================
def _resolve_subdir_path(params: ParamDict, sid_path: str, pmode: str,
                         file_path_key: str) -> Optional[str]:
    """
    Read-only re-implementation of the path formula used by
    pogos.core.general.prepare_directory - i.e. figure out what absolute
    directory a module's PATHS.* constant resolves to for this profile,
    without creating anything or mutating params.

    :param params: ParamDict, the loaded yaml parameters for one profile
    :param sid_path: str, the key holding this module's SUBDIRECTORY value
    :param pmode: str, the module directory name (e.g. 'tsovore')
    :param file_path_key: str, the PATHS.* key to resolve (its value is a
                          folder name relative to
                          {GLOBAL.DATA_PATH}/{pmode}/{SUBDIRECTORY})

    :return: str or None, the absolute directory path (may not exist on
             disk), or None if the profile was never set up
    """
    subdirectory = params.get(sid_path, None)
    data_path = params.get('GLOBAL.DATA_PATH', None)
    value = params.get(file_path_key, None)
    if subdirectory is None or data_path is None or value is None:
        return None
    return os.path.normpath(os.path.join(str(data_path), pmode,
                                         str(subdirectory), str(value)))


def _module_topdir(params: ParamDict, sid_path: str,
                   pmode: str) -> Optional[str]:
    """
    Return {GLOBAL.DATA_PATH}/{pmode}/{SUBDIRECTORY} for this profile, or
    None if the profile was never set up.
    """
    subdirectory = params.get(sid_path, None)
    data_path = params.get('GLOBAL.DATA_PATH', None)
    if subdirectory is None or data_path is None:
        return None
    return os.path.normpath(os.path.join(str(data_path), pmode,
                                         str(subdirectory)))


def get_reset_targets(params: ParamDict
                      ) -> Tuple[Dict[str, List[str]], List[str]]:
    """
    Work out which directories pogos_reset should wipe for the enabled
    reduction steps in this profile (outputs/plots/temporary/other
    directories POGOS created), and which directories must never be
    touched (raw inputs, calibration/reference files, or paths shared
    across profiles such as SOSSISSE.PATHS.YAMLPATH).

    :param params: ParamDict, the loaded yaml parameters for one profile

    :return: tuple, 1. dict of step name -> list of target directories to
             wipe, 2. list of protected absolute directories that must
             survive
    """
    targets: Dict[str, List[str]] = dict()
    protected: List[str] = []

    def add_target(step_name: str, paths: List[Optional[str]]):
        clean = [p for p in paths if p is not None]
        if len(clean) > 0:
            targets.setdefault(step_name, [])
            targets[step_name].extend(clean)

    def add_protected(paths: List[Optional[str]]):
        protected.extend([p for p in paths if p is not None])

    # -------------------------------------------------------------------
    # TSOVORE
    # -------------------------------------------------------------------
    if definitions.TSOVORE.is_enabled(params):
        sid, mode = 'TSOVORE.GENERAL.SUBDIRECTORY', 'tsovore'
        add_target('TSOVORE', [
            _resolve_subdir_path(params, sid, mode, 'TSOVORE.PATHS.TEMP_PATH'),
            _resolve_subdir_path(params, sid, mode, 'TSOVORE.PATHS.OUTPUT_PATH'),
            _resolve_subdir_path(params, sid, mode, 'TSOVORE.PATHS.PLOT_PATH'),
        ])
        add_protected([_resolve_subdir_path(params, sid, mode,
                                            'TSOVORE.PATHS.INPUT_PATH')])

    # -------------------------------------------------------------------
    # MIRIAM
    # -------------------------------------------------------------------
    if definitions.MIRIAM.is_enabled(params):
        sid, mode = 'MIRIAM.GENERAL.SUBDIRECTORY', 'miriam'
        add_target('MIRIAM', [
            _resolve_subdir_path(params, sid, mode, 'MIRIAM.PATHS.TEMP_PATH'),
            _resolve_subdir_path(params, sid, mode, 'MIRIAM.PATHS.OUTPUT_PATH'),
            _resolve_subdir_path(params, sid, mode, 'MIRIAM.PATHS.PLOT_PATH'),
        ])
        add_protected([_resolve_subdir_path(params, sid, mode,
                                            'MIRIAM.PATHS.INPUT_PATH')])

    # -------------------------------------------------------------------
    # SOSSISSE (uses its own package's path layout, not prepare_directory)
    # -------------------------------------------------------------------
    if definitions.SOSSISSE.is_enabled(params):
        sossiopath = params.get('SOSSISSE.INPUTS.SOSSIOPATH', None)
        subdirectory = params.get('SOSSISSE.INPUTS.SUBDIRECTORY', None)
        if sossiopath is not None and subdirectory is not None:
            subdir_path = os.path.join(str(sossiopath), str(subdirectory))
            add_target('SOSSISSE', [
                os.path.normpath(os.path.join(subdir_path, 'temporary')),
                os.path.normpath(os.path.join(subdir_path, 'plots')),
                os.path.normpath(os.path.join(subdir_path, 'other')),
                os.path.normpath(os.path.join(subdir_path, 'outputs')),
            ])
            add_protected([
                os.path.normpath(os.path.join(subdir_path, 'inputs')),
                os.path.normpath(os.path.join(subdir_path, 'calibration')),
            ])
        # note: SOSSISSE.PATHS.YAMLPATH is shared by every SUBDIRECTORY
        # under this mode (it is not nested inside subdir_path) so it is
        # never a reset target for a single profile

    # -------------------------------------------------------------------
    # SORBET (WLCA / SLCA)
    # -------------------------------------------------------------------
    sid, mode = 'SORBET.GENERAL.SUBDIRECTORY', 'sorbet'
    if definitions.SORBET_WLCA.is_enabled(params):
        add_target('SORBET.WLCA', [
            _resolve_subdir_path(params, sid, mode, 'SORBET.WLCA.OUTPUT_PATH'),
            _resolve_subdir_path(params, sid, mode, 'SORBET.WLCA.PLOT_PATH'),
        ])
        add_protected([_resolve_subdir_path(params, sid, mode,
                                            'SORBET.WLCA.INPUT_PATH')])
    if definitions.SORBET_SLCA.is_enabled(params):
        add_target('SORBET.SLCA', [
            _resolve_subdir_path(params, sid, mode, 'SORBET.SLCA.OUTPUT_PATH'),
            _resolve_subdir_path(params, sid, mode, 'SORBET.SLCA.PLOT_PATH'),
        ])
        add_protected([_resolve_subdir_path(params, sid, mode,
                                            'SORBET.SLCA.INPUT_PATH')])

    # -------------------------------------------------------------------
    # EUREKA (PRE / EXT / POST)
    # -------------------------------------------------------------------
    sid, mode = 'EUREKA.GENERAL.SUBDIRECTORY', 'eureka'
    if definitions.PRE_EUREKA.is_enabled(params):
        add_target('PRE_EUREKA', [
            _resolve_subdir_path(params, sid, mode, 'EUREKA.PATHS.OUT_S1_PATH'),
            _resolve_subdir_path(params, sid, mode, 'EUREKA.PATHS.OUT_S2_PATH'),
        ])
        add_protected([
            _resolve_subdir_path(params, sid, mode, 'EUREKA.PATHS.IN_S1_PATH'),
            _resolve_subdir_path(params, sid, mode, 'EUREKA.PATHS.IN_S2_PATH'),
        ])
    if definitions.EXT_EUREKA.is_enabled(params):
        add_target('EXT_EUREKA', [
            _resolve_subdir_path(params, sid, mode, 'EUREKA.PATHS.OUT_S3_PATH'),
        ])
        add_protected([_resolve_subdir_path(params, sid, mode,
                                            'EUREKA.PATHS.IN_S3_PATH')])
    if definitions.POST_EUREKA.is_enabled(params):
        topdir = _module_topdir(params, sid, mode)
        if topdir is not None:
            stage_dirs = []
            for stage in EUREKA_POST_STAGES:
                outputdir = params.get(f'EUREKA.STAGE{stage}.outputdir', None)
                if outputdir is not None:
                    stage_dirs.append(os.path.normpath(
                        os.path.join(topdir, str(outputdir))))
            stage_dirs.append(os.path.normpath(os.path.join(topdir, 'ecf')))
            add_target('POST_EUREKA', stage_dirs)

    # -------------------------------------------------------------------
    # STD_JWST (PRE / EXT) - POST_JWST creates no directories of its own
    # -------------------------------------------------------------------
    sid, mode = 'STD_JWST.GENERAL.SUBDIRECTORY', 'jwst'
    if definitions.PRE_JWST.is_enabled(params):
        add_target('PRE_JWST', [
            _resolve_subdir_path(params, sid, mode, 'STD_JWST.PATHS.OUT_S1_PATH'),
            _resolve_subdir_path(params, sid, mode, 'STD_JWST.PATHS.OUT_S2_PATH'),
        ])
        add_protected([
            _resolve_subdir_path(params, sid, mode, 'STD_JWST.PATHS.IN_S1_PATH'),
            _resolve_subdir_path(params, sid, mode, 'STD_JWST.PATHS.IN_S2_PATH'),
        ])
    if definitions.EXT_JWST.is_enabled(params):
        add_target('EXT_JWST', [
            _resolve_subdir_path(params, sid, mode, 'STD_JWST.PATHS.OUT_S3_PATH'),
        ])
        add_protected([_resolve_subdir_path(params, sid, mode,
                                            'STD_JWST.PATHS.IN_S3_PATH')])

    # -------------------------------------------------------------------
    # NAMELESS (PRE / EXT share one reduction/top directory)
    # -------------------------------------------------------------------
    sid, mode = 'NAMELESS.GENERAL.SUBDIRECTORY', 'nameless'
    if definitions.PRE_NAMELESS.is_enabled(params) or \
            definitions.EXT_NAMELESS.is_enabled(params):
        topdir = _module_topdir(params, sid, mode)
        if topdir is not None:
            add_target('NAMELESS', [
                os.path.normpath(os.path.join(topdir, folder))
                for folder in NAMELESS_OUTPUT_SUBFOLDERS])
        inputdir = params.get('NAMELESS.GENERAL.INPUTDIR', None)
        if topdir is not None and inputdir is not None:
            add_protected([os.path.normpath(os.path.join(topdir,
                                                          str(inputdir)))])
        ancil_path = params.get('NAMELESS.PATHS.ANCIL_PATH', None)
        if ancil_path is not None:
            add_protected([os.path.normpath(str(ancil_path))])

    return targets, protected


def _is_subpath(path: str, parent: str) -> bool:
    """
    Return whether `path` is `parent` itself or lives anywhere underneath
    it (OS-independent, works with any path separator).
    """
    path = os.path.normpath(path)
    parent = os.path.normpath(parent)
    if path == parent:
        return True
    return path.startswith(parent + os.sep)


def _is_safe_to_delete(path: str, data_path: str,
                       protected: List[str]) -> Tuple[bool, str]:
    """
    Refuse to delete anything that is not cleanly inside
    GLOBAL.DATA_PATH, that is GLOBAL.DATA_PATH itself, or that overlaps
    (in either direction) with a protected (input/calibration/shared)
    directory.
    """
    norm_path = os.path.normpath(path)
    norm_data = os.path.normpath(data_path)
    if norm_path == norm_data or not _is_subpath(norm_path, norm_data):
        return False, 'not inside GLOBAL.DATA_PATH'
    for prot in protected:
        if _is_subpath(prot, norm_path) or _is_subpath(norm_path, prot):
            return False, f'overlaps a protected path ({prot})'
    return True, ''


def filter_safe_targets(params: ParamDict, targets: Dict[str, List[str]],
                        protected: List[str]
                        ) -> Tuple[Dict[str, List[str]], List[str]]:
    """
    Drop targets that do not exist on disk, are duplicated, or fail the
    safety checks in `_is_safe_to_delete`.

    :return: tuple, 1. filtered dict of step name -> existing target
             directories, 2. list of warning messages for skipped targets
    """
    data_path = str(params['GLOBAL.DATA_PATH'])
    seen = set()
    filtered: Dict[str, List[str]] = dict()
    warnings: List[str] = []
    for step_name, dirs in targets.items():
        keep = []
        for path in dirs:
            if path in seen:
                continue
            safe, reason = _is_safe_to_delete(path, data_path, protected)
            if not safe:
                warnings.append(f'Skipping {path} ({reason})')
                continue
            seen.add(path)
            if not os.path.isdir(path):
                # nothing on disk to reset - already clean
                continue
            keep.append(path)
        if len(keep) > 0:
            filtered[step_name] = keep
    return filtered, warnings


def _dir_stats(path: str) -> Tuple[int, float]:
    """
    Count files and total size (in MB) of everything under `path`.
    """
    nfiles = 0
    nbytes = 0
    for root, _dirs, files in os.walk(path):
        for filename in files:
            nfiles += 1
            try:
                nbytes += os.path.getsize(os.path.join(root, filename))
            except OSError:
                pass
    return nfiles, nbytes / (1024.0 ** 2)


def print_summary(params: ParamDict, targets: Dict[str, List[str]]) -> int:
    """
    Print every directory that will be wiped (with file counts/sizes).

    :return: int, the total number of directories that will be reset
    """
    count = 0
    for step_name in targets:
        WLOG(params, 'info', f'{step_name}:', colour='magenta')
        for path in targets[step_name]:
            nfiles, mbytes = _dir_stats(path)
            msg = '    - {0}  ({1} files, {2:.2f} MB)'
            margs = [path, nfiles, mbytes]
            WLOG(params, '', msg.format(*margs), no_timestamp=True,
                colour='magenta')
            count += 1
    return count


def perform_reset(params: ParamDict, targets: Dict[str, List[str]]):
    """
    Delete and recreate (empty) every directory in `targets`.
    """
    for step_name in targets:
        for path in targets[step_name]:
            WLOG(params, '', f'Resetting: {path}')
            shutil.rmtree(path)
            os.makedirs(path)

# =============================================================================
# End of code
# =============================================================================

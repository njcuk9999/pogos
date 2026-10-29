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
EUREKA_POST_STAGES = [4, 5, 6]
NAMELESS_OUTPUT_SUBFOLDERS = ['stage1_outputs', 'stage2_outputs',
                              'prep_step_outputs', 'custom_steps_outputs',
                              'extraction_outputs']


# =============================================================================
# Define functions
# =============================================================================
def _module_topdir(params: ParamDict, pmode: str) -> Optional[str]:
    """Return the module directory beneath the single global project."""
    project_name = params.get('GLOBAL.PROJECT_NAME', None)
    data_path = params.get('GLOBAL.DATA_PATH', None)
    if project_name is None or data_path is None:
        return None
    return os.path.abspath(os.path.join(str(data_path), 'projects',
                                        str(project_name), pmode))


def _resolve_module_path(params: ParamDict, pmode: str,
                         file_path_key: str, default: str) -> Optional[str]:
    """Resolve a path exactly as general.prepare_directory, without mutation."""
    value = params.get(file_path_key, None)
    if value is not None and os.path.isabs(value):
        return os.path.abspath(value)
    topdir = _module_topdir(params, pmode)
    if topdir is None:
        return None
    return os.path.abspath(os.path.join(topdir, str(value)
                                        if value is not None else default))


def _sossisse_path(params: ParamDict, run_path: Optional[str],
                   key: str, default: str) -> Optional[str]:
    """Honor SOSSISSE overrides as supplied, relative to the runtime cwd."""
    value = params.get(f'SOSSISSE.PATHS.{key}', None)
    if value is not None:
        return os.path.abspath(value)
    if run_path is None:
        return None
    return os.path.abspath(os.path.join(run_path, default))


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

    for step in (definitions.TSOVORE, definitions.MIRIAM):
        if not step.is_enabled(params):
            continue
        mode = step.name.lower()
        add_target(step.name, [
            _resolve_module_path(params, mode, f'{step.name}.PATHS.{kind}_PATH',
                                 kind.lower())
            for kind in ('TEMP', 'OUTPUT', 'PLOT')])
        add_protected([_resolve_module_path(
            params, mode, f'{step.name}.PATHS.INPUT_PATH', 'input')])

    if definitions.SOSSISSE.is_enabled(params):
        run_path = _sossisse_path(params, None, 'RUN_PATH', '')
        if run_path is None:
            run_path = _module_topdir(params, 'sossisse')
        add_target('SOSSISSE', [
            _sossisse_path(params, run_path, key, default)
            for key, default in [('TEMP_PATH', 'temporary'),
                                 ('PLOT_PATH', 'plots'),
                                 ('OTHER_PATH', 'other'),
                                 ('OUT_PATH', 'outputs')]])
        add_protected([
            _sossisse_path(params, run_path, key, default)
            for key, default in [('RAWPATH', 'inputs'),
                                 ('CALIBPATH', 'calibration'),
                                 ('YAMLPATH', 'yamls')]])

    for step in (definitions.SORBET_WLCA, definitions.SORBET_SLCA):
        if not step.is_enabled(params):
            continue
        add_target(step.name, [
            _resolve_module_path(params, 'sorbet', f'{step.name}.{kind}_PATH',
                                 kind.lower())
            for kind in ('OUTPUT', 'PLOT')])
        add_protected([_resolve_module_path(
            params, 'sorbet', f'{step.name}.INPUT_PATH', 'input')])

    for prefix, mode, pre_step, ext_step in (
            ('EUREKA', 'eureka', definitions.PRE_EUREKA, definitions.EXT_EUREKA),
            ('STD_JWST', 'jwst', definitions.PRE_JWST, definitions.EXT_JWST)):
        for step, stages in ((pre_step, (1, 2)), (ext_step, (3,))):
            if not step.is_enabled(params):
                continue
            add_target(step.name, [
                _resolve_module_path(params, mode,
                                     f'{prefix}.PATHS.OUT_S{stage}_PATH',
                                     'output') for stage in stages])
            add_protected([
                _resolve_module_path(params, mode,
                                     f'{prefix}.PATHS.IN_S{stage}_PATH',
                                     'input') for stage in stages])

    if definitions.POST_EUREKA.is_enabled(params):
        topdir = _module_topdir(params, 'eureka')
        if topdir is not None:
            stage_dirs = []
            for stage in EUREKA_POST_STAGES:
                outputdir = params.get(f'EUREKA.STAGE{stage}.outputdir', None)
                if outputdir is not None:
                    stage_dirs.append(os.path.normpath(
                        os.path.join(topdir, str(outputdir))))
            stage_dirs.append(os.path.normpath(os.path.join(topdir, 'ecf')))
            add_target('POST_EUREKA', stage_dirs)

    nameless_enabled = (definitions.PRE_NAMELESS.is_enabled(params)
                        or definitions.EXT_NAMELESS.is_enabled(params))
    if nameless_enabled:
        topdir = _module_topdir(params, 'nameless')
        if topdir is not None:
            add_target('NAMELESS', [
                os.path.normpath(os.path.join(topdir, folder))
                for folder in NAMELESS_OUTPUT_SUBFOLDERS])
        add_protected([_resolve_module_path(
            params, 'nameless', 'NAMELESS.GENERAL.INPUTDIR', 'input')])
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
    norm_path = os.path.realpath(path)
    norm_data = os.path.realpath(data_path)
    if norm_path == norm_data or not _is_subpath(norm_path, norm_data):
        return False, 'not inside GLOBAL.DATA_PATH'
    for prot in protected:
        real_protected = os.path.realpath(prot)
        if (_is_subpath(real_protected, norm_path)
                or _is_subpath(norm_path, real_protected)
                or _is_subpath(os.path.abspath(prot), os.path.abspath(path))
                or _is_subpath(os.path.abspath(path), os.path.abspath(prot))):
            return False, f'overlaps a protected path ({prot})'
    if os.path.islink(path):
        return False, 'target is a symbolic link'
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
    Delete and recreate safe target directories, rechecking before deletion.
    """
    data_path = str(params['GLOBAL.DATA_PATH'])
    _, protected = get_reset_targets(params)
    for step_name in targets:
        for path in targets[step_name]:
            safe, reason = _is_safe_to_delete(path, data_path, protected)
            if not safe:
                WLOG(params, 'warning', f'Skipping {path} ({reason})')
                continue
            if not os.path.isdir(path):
                continue
            WLOG(params, '', f'Resetting: {path}')
            shutil.rmtree(path)
            os.makedirs(path)

# =============================================================================
# End of code
# =============================================================================

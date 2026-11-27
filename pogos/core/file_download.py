#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Obtain POGOS input files from their source (local, MAST or POGOS server)

Every file constant (FileObjectConst) of an enabled reduction step is
checked: online files (source: mast / pogos) are downloaded when missing and
the yaml file is updated with the filelist so later runs use the local copy.

The main input of a step (e.g. SOSSISSE.GENERAL.FILES) is not downloaded
when an earlier reduction level is enabled in the same run - it will be
produced by that step instead (e.g. TSOVORE -> SOSSISSE).

Online files are kept once in {GLOBAL.DATA_PATH}/downloads/ (see
aperocore.constants.file_sources) and symlinked into the run directories;
files already there are linked instead of downloaded again.

Created on 2026-11-25

@author: cook
"""
import os
from typing import Any, Dict, List, Optional

from aperocore.constants import custom_const_classes
from aperocore.constants import file_sources
from aperocore.constants.param_functions import ParamDict
from aperocore.core import drs_log

from pogos.core import definitions
from pogos.core import general

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'pogos.core.file_download'
# get the logger
WLOG = drs_log.wlog
# The main input of each step: replaced by outputs of an earlier level
#   (key -> name of the step it belongs to)
MAIN_INPUTS = {'TSOVORE.INPUTS.FILES': 'TSOVORE',
               'SOSSISSE.GENERAL.FILES': 'SOSSISSE',
               'MIRIAM.INPUTS.FILES': 'MIRIAM',
               'SORBET.WLCA.INPUT_FILE': 'SORBET.WLCA',
               'SORBET.SLCA.INPUT_FILE': 'SORBET.SLCA'}
# The default directory names for SOSSISSE path keys (relative to RUN_PATH)
SOSSISSE_DIRS = {'RAWPATH': 'inputs', 'CALIBPATH': 'calibration'}
# The download cache directory (relative to GLOBAL.DATA_PATH)
DOWNLOAD_DIR = 'downloads'
# Ordered reduction levels
LEVELS = [level.name for level in definitions.REDUCTION_LEVELS]


# =============================================================================
# Define functions
# =============================================================================
def step_for_key(key: str) -> Optional[Any]:
    """
    Get the reduction step a parameter key belongs to

    :param key: str, the parameter key e.g. SOSSISSE.GENERAL.FLATFILE

    :return: RedStep or None, the longest matching step name prefix
    """
    # longest prefix wins (SORBET.WLCA before SORBET)
    best = None
    for step in definitions.RED_STEPS:
        if key.upper().startswith(step.name.upper() + '.'):
            if best is None or len(step.name) > len(best.name):
                best = step
    return best


def chained_keys(params: ParamDict) -> List[str]:
    """
    Main input keys that an earlier enabled reduction level produces

    :param params: ParamDict, the parameter dictionary of constants

    :return: list of str, keys that must not be downloaded
    """
    # the levels that have at least one enabled step
    enabled_levels = set()
    for step in definitions.RED_STEPS:
        if step.is_enabled(params):
            enabled_levels.add(step.level.name)
    # a main input is chained if any earlier level is enabled
    keys = []
    for key, step_name in MAIN_INPUTS.items():
        step = step_for_key(key)
        if step is None:
            continue
        level_index = LEVELS.index(step.level.name)
        if any(level in enabled_levels for level in LEVELS[:level_index]):
            keys.append(key)
    return keys


def enabled_file_keys(params: ParamDict) -> List[str]:
    """
    File object keys that belong to enabled reduction steps

    :param params: ParamDict, the parameter dictionary of constants

    :return: list of str, the parameter keys
    """
    keys = []
    for key in file_sources.find_file_keys(params):
        step = step_for_key(key)
        if step is not None and step.is_enabled(params):
            keys.append(key)
    return keys


def download_directory(params: ParamDict) -> str:
    """
    The shared download cache of a POGOS path

    :param params: ParamDict, the parameter dictionary of constants

    :return: str, {GLOBAL.DATA_PATH}/downloads
    """
    data_path = params.rget('GLOBAL.DATA_PATH', required=True)
    return os.path.join(os.path.abspath(str(data_path)), DOWNLOAD_DIR)


def module_directory(params: ParamDict, key: str, path_key: str) -> str:
    """
    Absolute directory for a module path key (even if still relative)

    :param params: ParamDict, the parameter dictionary of constants
    :param key: str, the file parameter key (unused, for the callback API)
    :param path_key: str, the directory parameter key

    :return: str, the absolute directory
    """
    _ = key
    # SOSSISSE has its own directory layout
    if path_key.upper().startswith('SOSSISSE.PATHS.'):
        return _sossisse_directory(params, path_key)
    # other modules use the POGOS layout
    step = step_for_key(path_key)
    pmode = path_key.split('.')[0].lower() if step is None else (
        step.name.split('.')[0].lower())
    return general.resolve_directory(params, 'input', path_key, pmode)


def online_summary(params: ParamDict,
                   keys: Optional[List[str]] = None) -> Dict[str, str]:
    """
    Describe the online file parameters that still need downloading

    :param params: ParamDict, the parameter dictionary of constants
    :param keys: list of keys to check (default: enabled steps)

    :return: dict, key -> source for each key needing a download
    """
    if keys is None:
        keys = enabled_file_keys(params)
    skip = set(key.upper() for key in chained_keys(params))
    summary = dict()
    for key in keys:
        fileobj = custom_const_classes.get_fileobj(params[key])
        if fileobj is None or not fileobj.online or key.upper() in skip:
            continue
        instance = params.instances.get(key)
        path_key = (file_sources.module_prefix(key, instance)
                    + instance.path_key)
        directory = module_directory(params, key, path_key)
        download_dir = download_directory(params)
        if file_sources.needs_download(fileobj, directory, download_dir):
            summary[key] = fileobj.source
    return summary


def download_files(params: ParamDict, yaml_file: Optional[str] = None,
                   demolocal: Optional[str] = None,
                   demosymlink: bool = False) -> Dict[str, Any]:
    """
    Download all online files of enabled steps (if not already present)

    :param params: ParamDict, the parameter dictionary of constants (updated)
    :param yaml_file: str or None, the yaml file to update with filelists
    :param demolocal: str or None, local mirror of the POGOS data server
    :param demosymlink: bool, symlink (True) or copy (False) from demolocal

    :return: dict, key -> new yaml value for updated keys
    """
    keys = enabled_file_keys(params)
    skip = chained_keys(params)
    # nothing to do if there are no online files
    if len(online_summary(params, keys)) == 0:
        return dict()
    WLOG(params, 'info', 'Checking online input files')
    rkwargs = dict(keys=keys, skip_keys=skip, yaml_file=yaml_file,
                   demolocal=demolocal, demosymlink=demosymlink,
                   get_directory=module_directory,
                   download_dir=download_directory(params))
    return file_sources.resolve_files(params, **rkwargs)


def link_downloaded(params: ParamDict) -> None:
    """
    Symlink files already in the download cache into the run directories
    (never goes online)

    :param params: ParamDict, the parameter dictionary of constants

    :return: None
    """
    rkwargs = dict(keys=enabled_file_keys(params),
                   skip_keys=chained_keys(params),
                   get_directory=module_directory,
                   download_dir=download_directory(params), link_only=True)
    file_sources.resolve_files(params, **rkwargs)


def setup_downloads(params: ParamDict, ask: bool = True) -> Dict[str, Any]:
    """
    Setup-time handling of online input files

    Uses GLOBAL.LOCAL_DOWNLOAD_DATA / GLOBAL.DEMO_SYMLINK_DATA if set,
    otherwise asks the user whether to download now or at the first run.

    :param params: ParamDict, the parameter dictionary of constants
    :param ask: bool, if False download now without asking

    :return: dict, key -> new yaml value for updated keys
    """
    # files downloaded before (e.g. by another project) are linked first
    link_downloaded(params)
    summary = online_summary(params)
    # nothing to download
    if len(summary) == 0:
        return dict()
    # command line / yaml choice of a local mirror
    demolocal = params.get('GLOBAL.LOCAL_DOWNLOAD_DATA', None)
    demosymlink = bool(params.get('GLOBAL.DEMO_SYMLINK_DATA', False))
    # command line pre-answer of the download prompt (--download=now/run)
    download_mode = params.get('GLOBAL.DOWNLOAD_MODE', None)
    if demolocal is None and download_mode is not None:
        # "run": leave the downloads for the first run (no prompt)
        if str(download_mode).lower() == 'run':
            msg = ('Online input files will be downloaded at the start of '
                   'the first run')
            WLOG(params, 'info', msg)
            return dict()
        # "now": download without asking
        ask = False
    # ask the user (unless a local mirror was given)
    if ask and demolocal is None:
        now, demolocal, demosymlink = file_sources.ask_download_now(params,
                                                                    summary)
        if not now:
            msg = ('Online input files will be downloaded at the start of '
                   'the first run')
            WLOG(params, 'info', msg)
            return dict()
    # download (yaml updated in place)
    yaml_file = params.get('GLOBAL.YAML_FILE', None)
    dkwargs = dict(yaml_file=yaml_file, demolocal=demolocal,
                   demosymlink=demosymlink)
    return download_files(params, **dkwargs)


# =============================================================================
# Define worker functions
# =============================================================================
def _sossisse_directory(params: ParamDict, path_key: str) -> str:
    """
    Absolute SOSSISSE directory (mirrors sossisse run_time_params)

    :param params: ParamDict, the parameter dictionary of constants
    :param path_key: str, e.g. SOSSISSE.PATHS.RAWPATH

    :return: str, the absolute directory
    """
    value = params.get(path_key, None)
    if value is not None:
        return os.path.abspath(str(value))
    # the run path defaults to DATA_PATH/projects/PROJECT/sossisse
    run_path = params.get('SOSSISSE.PATHS.RUN_PATH', None)
    if run_path is None:
        data_path = params.rget('GLOBAL.DATA_PATH', required=True)
        project = params.rget('GLOBAL.PROJECT_NAME', required=True)
        run_path = os.path.join(data_path, 'projects', project, 'sossisse')
    name = path_key.split('.')[-1].upper()
    subdir = SOSSISSE_DIRS.get(name, name.lower())
    return os.path.abspath(os.path.join(str(run_path), subdir))


# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    print('Hello World!')

# =============================================================================
# End of code
# =============================================================================

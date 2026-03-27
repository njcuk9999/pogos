#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2026-01-28 at 11:59

@author: cook
"""
import shutil
from typing import Dict, List
from pathlib import Path

from aperocore.constants import load_functions
from aperocore.constants import param_functions
from aperocore.core import drs_log
from pogos.constants.constants import CDict
from pogos.core import base
from pogos.core import general
from pogos.core import startup
from pogos.resources import demos

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'pogos.recipes.pogos_setup'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__
# get the logger
WLOG = drs_log.wlog
# get param dict
ParamDict = param_functions.ParamDict
# set description
__description__ = ('Setup the POGOS recipes starting from a demo.'
                   'Creates a configuration (yaml) file and a file structure')
__inputs__ = ['GLOBAL.YAML_FILE', 'GLOBAL.DATA_PATH']
# Path to look for raw data
SEARCH_PATH = '/scratch3/jwst/pogos-data/'
# path to copy raw data to
DEMO_COPY_PATH = '/scratch3/jwst/pogos-raw-data/'
# demo path

# -----------------------------------------------------------------------------

# =============================================================================
# Define functions
# =============================================================================
def get_demo_files(params: ParamDict):

    # deal with "DEMOS" not in demos
    if not hasattr(demos, 'DEMOS'):
        raise ImportError('pogos.resources.demos.DEMOS does not exist')

    # get the demo codes
    demo_codes = demos.DEMOS
    # storage for output files
    demo_files = dict()
    # loop around demo instruments
    for demo_inst in demo_codes:
        # loop around demos in each instrument
        for demo_name in demo_codes[demo_inst]:
            # get the module call
            demo_module = demo_codes[demo_inst][demo_name]
            # deal with URL not existing
            if not hasattr(demo_module, 'URL'):
                raise ImportError('pogos.resources.demos.{} does not have '
                                  'URL'.format(demo_name))
            # deal with DOWNLOAD not existing
            if not hasattr(demo_module, 'DOWNLOAD'):
                raise ImportError('pogos.resources.demos.{} does not have '
                                  'DOWNLOAD'.format(demo_name))
            # deal with Cdict not existing
            if not hasattr(demo_module, 'Cdict'):
                raise ImportError('pogos.resources.demos.{} does not have '
                                  'Cdict'.format(demo_name))

            # print progress
            msg = 'Analysing demo {0}:{1}'
            margs = [demo_inst, demo_name]
            WLOG(params, 'info', msg.format(*margs))
            # get url
            url = demo_module.URL
            # get last directory of url (should be an instrument)
            inst = url.strip('/').split('/')[-1]
            # look in the DOWNLOAD variable and get parameters
            cdict_keys = demo_module.DOWNLOAD.keys()
            # look in cdict for their values
            cdict_values = []
            for cdict_key in cdict_keys:
                if cdict_key in demo_module.Cdict:
                    # get the value from Cdict storage
                    value = demo_module.Cdict.get(cdict_key).value
                    # skip if value is None
                    if value is None:
                        continue
                    # deal with a list
                    if isinstance(value, list):
                        cdict_values += value
                    # otherwise assume a single value
                    else:
                        cdict_values.append(value)
            # print how many values found
            msg = '\tFound {0} files'
            margs = [len(cdict_values)]
            WLOG(params, '', msg.format(*margs))
            # deal with no files added
            if len(cdict_values) == 0:
                continue
            # push into inst
            if inst not in demo_files:
                demo_files[inst] = []
            # get a unique set of files
            ufiles = list(set(demo_files[inst] + cdict_values))
            # update demo_files (remove None entries)
            demo_files[inst] = [f_it for f_it in ufiles if f_it is not None]
    # print complete finding files
    WLOG(params, '', 'Completed finding files')
    # Summary of how many files found
    for inst in demo_files:
        # print how many values found
        msg = '\tTotal unique files for {0}: = {1}'
        margs = [inst, len(demo_files[inst])]
        WLOG(params, '', msg.format(*margs))

    return demo_files


def search_for_demo_files(params: ParamDict,
                          demo_files: Dict[str, List[str]],
                          search_path: str) -> tuple:
    """
    Search for demo files in SEARCH_PATH and match them to demo_files

    :param params: ParamDict instance
    :param demo_files: dict of instrument -> list of filenames
    :param search_path: path to search for files in
    :return: tuple of (found_files dict, unfound_files dict)
    """


    # storage for found files
    found_files = dict()
    # storage for unfound files
    unfound_files = dict()

    # get the search path
    search_path = Path(search_path)

    # check if search path exists
    if not search_path.exists():
        emsg = f'Search path does not exist: {search_path}'
        WLOG(params, 'error', emsg)
        # if search path doesn't exist, all files are unfound
        for inst in demo_files:
            unfound_files[inst] = demo_files[inst].copy()
            found_files[inst] = []
        return found_files, unfound_files

    # print progress
    msg = f'Searching for files in {search_path}'
    WLOG(params, 'info', msg)

    # loop around instruments
    for inst in demo_files:
        # print progress
        msg = f'\tSearching for {inst} files'
        WLOG(params, '', msg)

        # create storage for this instrument
        found_files[inst] = []
        unfound_files[inst] = []

        # loop through demo files for this instrument
        for demo_file in demo_files[inst]:
            # search recursively for this file
            matches = list(search_path.rglob(demo_file))

            # deal with no matches
            if len(matches) == 0:
                msg = f'\t\tFile not found: {demo_file}'
                WLOG(params, 'warning', msg)
                unfound_files[inst].append(demo_file)
                continue

            # deal with multiple matches
            if len(matches) > 1:
                msg = f'\t\tMultiple matches found for: {demo_file}'
                WLOG(params, 'warning', msg)
                for match in matches:
                    WLOG(params, '', f'\t\t\t{match}')
                msg = f'\t\t\tUsing first match: {matches[0]}'
                WLOG(params, '', msg)

            # add the first match to found files
            found_files[inst].append(str(matches[0]))
            msg = f'\t\tFound: {matches[0].name}'
            WLOG(params, '', msg)

    # print summary
    WLOG(params, '', 'Completed searching for files')
    for inst in found_files:
        msg = (f'\tFound {len(found_files[inst])}/{len(demo_files[inst])} '
               f'files for {inst}')
        WLOG(params, '', msg)

    # print unfound files summary
    WLOG(params, '', 'Summary of unfound files:')
    for inst in unfound_files:
        if len(unfound_files[inst]) > 0:
            msg = f'\t{inst}: {len(unfound_files[inst])} files not found'
            WLOG(params, 'warning', msg)
            for unfound_file in unfound_files[inst]:
                WLOG(params, '', f'\t\t- {unfound_file}')

    return found_files, unfound_files

def copy_demo_files(params: ParamDict, demo_files: Dict[str, List[str]],
                    outpath: str):
    """
    Copy found demo files to output path maintaining instrument structure

    :param params: ParamDict instance
    :param demo_files: dict of instrument -> list of full file paths
    :param outpath: output path to copy files to
    """
    # get the output path
    out_path = Path(outpath)
    # create output path if it doesn't exist
    if not out_path.exists():
        out_path.mkdir(parents=True, exist_ok=True)
        msg = f'Created output path: {out_path}'
        WLOG(params, 'info', msg)

    # print progress
    msg = f'Copying files to {outpath}'
    WLOG(params, 'info', msg)

    # loop around instruments
    for inst in demo_files:
        # print progress
        msg = f'\tCopying {inst} files'
        WLOG(params, '', msg)

        # create instrument directory
        inst_out_path = out_path / inst
        inst_out_path.mkdir(parents=True, exist_ok=True)

        # loop through found files
        for file_path in demo_files[inst]:
            source = Path(file_path)
            destination = inst_out_path / source.name

            # check if file already exists
            if destination.exists():
                msg = f'\t\tFile already exists, skipping: {source.name}'
                WLOG(params, '', msg)
                continue

            # copy file
            try:
                shutil.copy2(source, destination)
                msg = f'\t\tCopied: {source.name}'
                WLOG(params, '', msg)
            except Exception as e:
                msg = f'\t\tError copying {source.name}: {e}'
                WLOG(params, 'warning', msg)

    # print summary
    WLOG(params, '', 'Completed copying files')
    for inst in demo_files:
        msg = f'\tCopied {len(demo_files[inst])} files for {inst}'
        WLOG(params, '', msg)


def main(**kwargs):
    # print splash
    general.start_splash('POGOS: PRDD')
    # get other configs (either internal like SORBET or external like SOSSISSE)
    other_const = startup.initial_setup()
    # get parameters
    params = load_functions.get_all_params(name=__NAME__,
                                           description=__description__,
                                           inputargs=__inputs__,
                                           config_list=[CDict],
                                           from_file=False,
                                           external_const=other_const,
                                           kwargs=kwargs)
    # -------------------------------------------------------------------------
    # Step 1: get a list of all files
    demo_files = get_demo_files(params)
    # -------------------------------------------------------------------------
    # Step 2: search for those files in the search path
    found_files, unfound_files = search_for_demo_files(params, demo_files,
                                                        SEARCH_PATH)
    # -------------------------------------------------------------------------
    # warn user that some files were not found
    for inst in unfound_files:
        if len(unfound_files[inst]) > 0:
            msg = (f'Warning: Not all files were found for instrument '
                   f'{0}. \n\tMissing files are:')
            for unfound_file in unfound_files[inst]:
                msg += f'\n\t- {unfound_file}'
            # print the warning
            WLOG(params, 'warning', msg)
    # -------------------------------------------------------------------------
    # Step 3: copy files to demo copy path
    copy_demo_files(params, found_files, DEMO_COPY_PATH)
    # -------------------------------------------------------------------------



# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    main()



# =============================================================================
# End of code
# =============================================================================

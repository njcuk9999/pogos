#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2025-10-17 at 13:22

@author: cook
"""
import os
from typing import List, Optional, Tuple

import numpy as np
from astropy.io import fits
from astropy.table import Table
from tqdm import tqdm

from aperocore.constants.param_functions import ParamDict
from aperocore.core import drs_log
from aperocore.core import drs_misc
from pogos.core import base
from pogos.miriam.core import base as miriam_base

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'pogos.miriam.general.science'
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
# -----------------------------------------------------------------------------


# =============================================================================
# Define functions
# =============================================================================
MergedReturn = Tuple[np.ndarray, np.ndarray, Table, np.ndarray]


def merged_from_previous(params: ParamDict, input_basenames: List[str]
                         ) -> Optional[MergedReturn]:
    # get MIRIAM params
    mparams = params.get('MIRIAM')
    # get temporary directory
    temp_dir = mparams['PATHS.TEMP_PATH']
    # -------------------------------------------------------------------------
    # Check for merged data file (in temporary directory)
    # -------------------------------------------------------------------------
    # construct merged file name
    merged_cube_file = os.path.join(temp_dir, 'merged_cube.fits')
    # if the merged cube exists already, load and return it
    if not os.path.exists(merged_cube_file):
        return None
    # read the header and check we have all input filenames
    hdr = fits.getheader(merged_cube_file, 0)
    infiles = list(hdr['INFILE*'])
    # loop around basenames
    for input_basename in input_basenames:
        if input_basename not in infiles:
            msg = 'Merged cube file exists but does not contain'
            msg += f'all input files. Re-merging...'
            WLOG(params, 'info', msg)
            return None
    # open the merged cube file
    with fits.open(merged_cube_file) as hdul:
        cube = hdul['CUBE'].data
        cube_err = hdul['CUBE_ERR'].data
        weights = hdul['WEIGHTS'].data
    # open the table as a astropy table
    mtbl = Table.read(merged_cube_file, hdu='MTBL')
    # return the merged data
    return cube, cube_err, mtbl, weights


def merge_inputs(params: ParamDict) -> MergedReturn:

    # get MIRIAM params
    mparams = params.get('MIRIAM')
    # get input directory
    input_dir = mparams['PATHS.INPUT_PATH']
    # -------------------------------------------------------------------------
    # get list of input files
    input_files = mparams['INPUTS.FILES']
    # store input paths
    input_paths, input_basenames = [], []
    # check that all input files exist
    for it, input_file in enumerate(input_files):
        # construct path
        if os.path.exists(input_file):
            input_path = str(input_file)
        else:
            input_path = os.path.join(input_dir, input_file)
        if not os.path.exists(input_path):
            emsg = 'MIRIAM.PATHS.INPUT_PATH.FILES[{0}]'
            emsg += ' file does not exist: {1}'
            eargs = [it, input_path]
            raise miriam_base.MiriamException(emsg.format(*eargs))
        else:
            input_paths.append(input_path)
            input_basenames.append(os.path.basename(input_path))
    # -------------------------------------------------------------------------
    # attempt to load merged data from previous run
    if mparams['INPUTS.USE_PREVIOUS_MERGED_DATA']:
        merged_data = None
    else:
        merged_data = merged_from_previous(params, input_basenames)
    # if we have merged data use it
    if merged_data is not None:
        cube, cube_err, mtbl, weights = merged_data
        return cube, cube_err, mtbl, weights
    # -------------------------------------------------------------------------
    # storage for tables
    mtbls = None
    all_cubes = None
    all_cube_errs = None
    # loop around all files
    for ncube in tqdm(range(len(input_paths))):
        # load this iterations cube
        cube = fits.getdata(input_paths[ncube], extname='SCI')
        cube_err = fits.getdata(input_paths[ncube], extname='ERR')
        # storage of the x-pixels
        xpix = np.arange(cube.shape[2])
        # loop around integrations
        for islice in range(cube.shape[0]):
            # get the integration
            integration = cube[islice, :, :]
            # process the integration
            cleaned_integration = process_integration(integration, xpix,
                                                      njumps=4)
            # store back the cleaned integration
            cube[islice, :, :] = cleaned_integration
        # ---------------------------------------------------------------------
        # cut down the cube and error cube
        cut_cube, cut_cube_error = cut_down_cubes(params, cube, cube_err)
        # append
        if all_cubes is None:
            all_cubes = np.array(cut_cube)
            all_cube_errs = np.array(cut_cube_error)
        else:
            all_cubes = np.append(all_cubes, cut_cube, axis=0)
            all_cube_errs = np.append(all_cube_errs, cut_cube_error, axis=0)
        # ---------------------------------------------------------------------
        # Read the integration table for this file
        mtbl_n = Table.read(input_paths[ncube], hdu='INT_TIMES')
        # add the filename to the table
        mtbl_n['FILENAME'] = [input_basenames[ncube]] * len(mtbl_n)
        # stack the tables
        if mtbls is None:
            mtbls = Table(mtbl_n)
        else:
            mtbls = Table(np.vstack([mtbls, mtbl_n]))
    # -------------------------------------------------------------------------
    # write merged data to temporary file

    # TODO: Got to here
    # TODO: Remember to add header INPUT files


    # TODO: remove placeholder
    cube = np.array([])
    cube_err = np.array([])
    mtbl = Table()
    weights = np.array([])

    return cube, cube_err, mtbl, weights


def correct_systematics(params: ParamDict, cube: np.ndarray,
                        cube_err: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:

    # TODO: remove placeholder
    corrected_cube = cube
    corrected_cube_err = cube_err

    return corrected_cube, corrected_cube_err


def cube2phot(params: ParamDict, cube: np.ndarray,
              cube_err: np.ndarray, mtbl: Table, weights: np.ndarray,
              d2flag: bool = True) -> Table:

    # TODO: remove placeholder
    ptbl = Table()

    return ptbl


def write_photometry_results(params: ParamDict, ptbl0: Table,
                             ptbl1: Table):
    pass


# =============================================================================
# worker functions
# =============================================================================
# TODO: Needs a better name and needs an explaination of why
def process_integration(integration: np.ndarray,
                        xpix: np.ndarray,
                        njumps: int = 4) -> np.ndarray:
    # do this iteratively
    for jt in range(2):
        # subtract the median of every 4th column off the integration
        for irow in range(njumps):
            # median of the ith column
            row_med = np.nanmedian(integration[:, irow::njumps])
            # subtract of the integration itself
            integration[:, irow::njumps] -= row_med
        # calculate the median of the whole integration (across y-axis)
        col_med = np.nanmedian(integration, axis=0)
        # fit this median
        col_fit = np.polyfit(xpix, col_med, 1)
        # subtract this off each column
        for y_it in range(integration.shape[0]):
            integration[y_it, :] -= col_fit[0] * xpix + col_fit[1]
        # subtract the median of every 4th row off the integration
        for icol in range(njumps):
            # median of the ith column
            col_med = np.nanmedian(integration[icol::njumps, :])
            # subtract of the integration itself
            integration[icol::njumps, :] -= col_med
    # return the cleaned integration
    return integration


def cut_down_cubes(params: ParamDict, cube: np.ndarray,
                   cube_err: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    # get MIRIAM params
    mparams = params.get('MIRIAM')
    # get the y-pixel range
    cut_size = mparams['INPUTS.CUT_DOWNSIZE']
    # get the center offset
    center_offset = mparams['INPUTS.CUT_DOWNSIZE_CENTER_OFFSET']
    # get the size of the images
    nbxpix, nbypix = cube[0].shape
    # get start and end points
    xstart = (nbxpix // 2) - cut_size // 2 + center_offset[0]
    xend = (nbxpix // 2) + cut_size // 2 + center_offset[0]
    ystart = (nbypix // 2) - cut_size // 2 + center_offset[1]
    yend = (nbypix // 2) + cut_size // 2 + center_offset[1]
    # cut down the cubes
    cut_cube = cube[:, ystart:yend, xstart:xend]
    cut_cube_err = cube_err[:, ystart:yend, xstart:xend]
    # return the cut cubes
    return cut_cube, cut_cube_err


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

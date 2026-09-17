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
from astropy.table import Table, vstack
from scipy.optimize import curve_fit
from scipy.special import erf
from tqdm import tqdm

from aperocore import math as mp
from aperocore.constants.param_functions import ParamDict
from aperocore.constants import load_functions
from aperocore.core import drs_log
from aperocore.core import drs_misc
from pogos.core import base
from pogos.core import input_validation
from pogos.miriam.core import base as mc_base
from pogos.miriam.general import plots as mc_plots

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
MergedReturn = Tuple[np.ndarray, np.ndarray, Table, np.ndarray, float, float]


def merged_from_previous(params: ParamDict, input_basenames: List[str],
                         merged_cube_file: str) -> Optional[MergedReturn]:
    # get MIRIAM params
    mparams = params.get('MIRIAM')
    # -------------------------------------------------------------------------
    # Check for merged data file (in temporary directory)
    # if the merged cube exists already, load and return it
    if not os.path.exists(merged_cube_file):
        return None
    # -------------------------------------------------------------------------
    # read the header and check we have all input filenames
    hdr = fits.getheader(merged_cube_file, 0)
    # -------------------------------------------------------------------------
    # Make sure header contains all input files (if it doesn't we need
    # to re-merge)
    # -------------------------------------------------------------------------
    # get the infile keys from header
    infile_keys = list(hdr['INFILE*'])
    # get the infile values
    infiles = [hdr[key] for key in infile_keys]
    # loop around basenames
    for input_basename in input_basenames:
        if input_basename not in infiles:
            msg = 'Merged cube file exists but does not contain '
            msg += f'all input files. Re-merging...'
            WLOG(params, 'warning', msg)
            return None
    # -------------------------------------------------------------------------
    # Make sure header contains all skipped exposures (if it doesn't we need
    # to re-merge)
    # -------------------------------------------------------------------------
    skip_keys = list(hdr['SKIP*'])
    skips = [hdr[key] for key in skip_keys]
    skipped_exposures = mparams['INPUTS.SKIP_INTEGRATIONS']
    if skipped_exposures is None:
        skipped_exposures = []
    # loop around all skips
    for skip in skipped_exposures:
        # if we are missing this skip re-merge
        if skip not in skips:
            msg = 'Merged cube file exists but does not contain'
            msg += f'all skipped exposures. Re-merging...'
            WLOG(params, 'warning', msg)
            return None
    # -------------------------------------------------------------------------
    # Make sure radius is the same for the pedestal meean calculation
    # -------------------------------------------------------------------------
    prev_mean_ped_rad = hdr['MPED_RAD']
    curr_mean_ped_rad = mparams['INPUTS.MEAN_PEDESTAL_RADIUS']
    if prev_mean_ped_rad != curr_mean_ped_rad:
        msg = 'Merged cube file exists but mean pedestal radius'
        msg += ' is different. Re-merging...'
        WLOG(params, 'warning', msg)
        return None
    # -------------------------------------------------------------------------
    # open the merged cube file
    # -------------------------------------------------------------------------
    try:
        with fits.open(merged_cube_file) as hdul:
            hdr = hdul[0].header
            cube = np.array(hdul['CUBE'].data)
            cube_err = np.array(hdul['CUBE_ERR'].data)
            weights = np.array(hdul['WEIGHTS'].data)
        # print progress
        msg = f'Loaded merged cube from previous run: {merged_cube_file}'
        WLOG(params, '', msg)
        # open the table as a astropy table
        mtbl = Table.read(merged_cube_file, hdu='MTBL')
        # get the xcent and ycent from header
        xstart = hdr['XSTART']
        ystart = hdr['YSTART']
        # return the merged data
        return cube, cube_err, mtbl, weights, xstart, ystart
    except Exception as e:
        msg = 'Failed to read merged cube from previous run: '
        msg += f'{merged_cube_file}\nError: {e}'
        msg += '\nRe-merging...'
        WLOG(params, 'warning', msg)
        return None


def merge_inputs(params: ParamDict) -> MergedReturn:

    # get MIRIAM params
    mparams = params.get('MIRIAM')
    # get input directory
    input_dir = mparams['PATHS.INPUT_PATH']
    # get the temporary directory
    temp_dir = mparams['PATHS.TEMP_PATH']
    # -------------------------------------------------------------------------
    # construct merged file name
    merged_cube_file = os.path.join(temp_dir, 'merged_cube.fits')
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
        # Normalize every resolved input before checking and validation.
        input_path = os.path.abspath(input_path)
        if not os.path.exists(input_path):
            emsg = 'MIRIAM.PATHS.INPUT_PATH.FILES[{0}]'
            emsg += ' file does not exist: {1}'
            eargs = [it, input_path]
            raise mc_base.MiriamException(emsg.format(*eargs))
        else:
            input_paths.append(input_path)
            input_basenames.append(os.path.basename(input_path))
    # Validate the resolved imaging inputs before loading or merging arrays.
    input_validation.check_input_data_headers(params, input_paths)
    # -------------------------------------------------------------------------
    # set prefix (for use in output files)
    mparams['INPUTS']['PREFIX'] = load_functions.common_prefix(input_basenames)
    # -------------------------------------------------------------------------
    # attempt to load merged data from previous run
    if mparams['INPUTS.USE_PREVIOUS_MERGED_DATA']:
        merged_data = None
    else:
        merged_data = merged_from_previous(params, input_basenames,
                                           merged_cube_file)
    # -------------------------------------------------------------------------
    # Now if we have data we can return it
    # -------------------------------------------------------------------------
    # if we have merged data use it
    if merged_data is not None:
        cube, cube_err, mtbl, weights, xstart, ystart = merged_data
        return cube, cube_err, mtbl, weights, xstart, ystart
    # -------------------------------------------------------------------------
    # storage for tables
    mtbls = None
    all_cubes = None
    all_cube_errs = None
    xstart, ystart = -1.0, -1.0
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
            integration = np.array(cube[islice, :, :])
            # process the integration
            cleaned_integration = process_integration(integration, xpix,
                                                      njumps=4)
            # store back the cleaned integration
            cube[islice, :, :] = cleaned_integration
        # ---------------------------------------------------------------------
        # cut down the cube and error cube
        cd_out = cut_down_cubes(params, cube, cube_err)
        cut_cube, cut_cube_error, xstart, ystart = cd_out
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
        # add the segment number to the table
        mtbl_n['SEGMENT'] = [ncube] * len(mtbl_n)
        # stack the tables
        if mtbls is None:
            mtbls = Table(mtbl_n)
        else:
            mtbls = vstack([mtbls, mtbl_n])
    # -------------------------------------------------------------------------
    # sanity check that the length of mtls matches all_cubes/all_cube_errs
    n_integrations = len(mtbls)
    cond1 = n_integrations == all_cubes.shape[0]
    cond2 = n_integrations == all_cube_errs.shape[0]
    if not (cond1 and cond2):
        emsg = 'Length of merged table ({0}) does not match number of '
        emsg += 'integrations in cubes ({1}, {2})'
        eargs = [n_integrations, all_cubes.shape[0], all_cube_errs.shape[0]]
        raise mc_base.MiriamException(emsg.format(*eargs))
    # -------------------------------------------------------------------------
    # Deal with remove the exposures that are not used
    skipped_exposures = mparams['INPUTS.SKIP_INTEGRATIONS']
    if skipped_exposures is None:
        skipped_exposures = []

    # create mask of exposures to keep
    keep_mask = np.ones(n_integrations, dtype=bool)
    for skip in skipped_exposures:
        if 0 <= skip < n_integrations:
            keep_mask[skip] = False
    # -------------------------------------------------------------------------
    # cut down all cubes and table
    all_cubes = all_cubes[keep_mask, :, :]
    all_cube_err = all_cube_errs[keep_mask, :, :]
    mtbls = mtbls[keep_mask]
    # -------------------------------------------------------------------------
    # work out the mean pedestal of all frames
    pedestal_mean, weights = calc_mean_pedestal(params, all_cubes)
    # push the pedestal mean into the table
    mtbls['pedestal_mean'] = pedestal_mean
    # -------------------------------------------------------------------------
    # write merged data to temporary file
    # -------------------------------------------------------------------------
    # construct header
    header = fits.Header()
    # add input files to header
    for it, input_basename in enumerate(input_basenames):
        header[f'INFILE{it:04d}'] = (input_basename, 'Input filename')
    # add skipped exposures to header
    for iskip, skip in enumerate(skipped_exposures):
        header[f'SKIP{iskip:04d}'] = (skip, 'Skipped exposure (0-indexed)')
    # add mean pedestal radius to header
    header['MPED_RAD'] = (mparams['INPUTS.MEAN_PEDESTAL_RADIUS'],
                          'Mean pedestal radius (pixels)')
    # add the number of integrations
    header['NINTS'] = (all_cubes.shape[0], 'Number of integrations in '
                                           'merged cube')
    # add the center (related to the full image size)
    header['XSTART'] = (xstart, 'x start of cut-out in full frame image')
    header['YSTART'] = (ystart, 'y start of cut-out in full frame image')
    # -------------------------------------------------------------------------
    # create HDU list
    hdulist = fits.HDUList()
    hdulist.append(fits.PrimaryHDU(header=header))
    # cube
    hdu_cube = fits.ImageHDU(data=all_cubes, name='CUBE')
    hdulist.append(hdu_cube)
    # cube error
    hdu_cube_err = fits.ImageHDU(data=all_cube_err, name='CUBE_ERR')
    hdulist.append(hdu_cube_err)
    # mtbl
    hdu_mtbl = fits.BinTableHDU(data=mtbls, name='MTBL')
    hdulist.append(hdu_mtbl)
    # weights
    hdu_weights = fits.ImageHDU(data=weights, name='WEIGHTS')
    hdulist.append(hdu_weights)
    # -------------------------------------------------------------------------
    # print message
    msg = f'Writing merged cube to temporary file: {merged_cube_file}'
    WLOG(params, '', msg)
    # write to temporary file
    hdulist.writeto(merged_cube_file, overwrite=True)
    # -------------------------------------------------------------------------
    return all_cubes, all_cube_errs, mtbls, weights, xstart, ystart


def remove_background_cube(params: ParamDict, cube: np.ndarray,
                           mtbl: Table) -> Tuple[np.ndarray, Table]:
    # print progress
    msg = 'Removing background from cube...'
    WLOG(params, '', msg)
    # if a 4D hypercube is given, we loop through each cube.
    if len(cube.shape) == 4:
        # the pedestal for each hyper cube
        pedestal = np.zeros((cube.shape[0], cube.shape[1]))
        # loop around each cube
        for it in tqdm(range(cube.shape[0]), leave=False):
            cube[it], pedestal[it] = remove_from_3d(cube[it])
    else:
        cube, pedestal = remove_from_3d(cube)
    # push the pedestal into the table
    mtbl['pedestal_psf'] = pedestal
    # return the corrected cube and table
    return cube, mtbl


def calculate_cube_errors(params: ParamDict, cube: np.ndarray
                          ) -> Tuple[np.ndarray, np.ndarray]:
    # We find the errors in the cube by calculating the 16th and 84th percentiles
    # for each slice. It may be a 3d or 4d cube.
    if len(cube.shape) == 4:
        cube_err = np.zeros_like(cube)
        # print process
        msg = 'Calculating the errors in the hypercube'
        WLOG(params, '', msg)
        # loop around all cubes
        for it in tqdm(range(cube.shape[0]), leave=False):
            tmp1, tmp2 = noise_cube(cube[it])
            # update cube
            cube[it] = tmp1
            cube_err[it] = tmp2
    else:
        cube, cube_err = noise_cube(cube)
    # return the corrected cube and cube errors
    return cube, cube_err


def cube2phot(params: ParamDict, cube: np.ndarray,
              cube_err: np.ndarray, mtbl: Table, weights: np.ndarray,
              xstart: float, ystart: float, d2flag: bool = True) -> Table:
    # This function takes as an input a cube and returns the photometry
    # derived from the cube.
    # -------------------------------------------------------------------------
    # TODO be consistent with rateints
    if cube_err is None:
        # We assume that the error is the square root of the cube
        cube_err = np.sqrt(np.abs(cube))
    else:
        cube_err = np.array(cube_err)
    # -------------------------------------------------------------------------
    # Step 1: Normalize the cube
    # -------------------------------------------------------------------------
    # Normalize the cube data. We first calculate the median of the cube
    # and then do a linear fit to the median. We then divide the cube by
    # the linear fit to normalize the data.
    cube_normalize = normalize_cube(cube, weights)
    # -------------------------------------------------------------------------
    # Step 2: Get the fit parameters for the linear reconstruction
    # -------------------------------------------------------------------------
    psf, gradx, grady, psf2ortho = get_fit_params(cube_normalize, weights)
    # plot these four
    mc_plots.plot_fit_params(params, psf, gradx, grady, psf2ortho)
    # -------------------------------------------------------------------------
    # Step 3: Fit the PSF module to the cube data
    # -------------------------------------------------------------------------
    ptbl = fit_cube_psf(params, cube, cube_err, weights, mtbl,
                        psf, gradx, grady, psf2ortho, d2flag)
    # -------------------------------------------------------------------------
    # Step 4: Print stats about global RMS
    # -------------------------------------------------------------------------
    # get the amplitude from the table
    amps = ptbl['amps']
    # estimate the global RMS
    rms = mp.estimate_sigma(amps)
    # estimate the point-to-point RMS
    p2p_rms = mp.estimate_sigma(amps - np.roll(amps, 1))/np.sqrt(2)
    # print the RMS values
    msg = ('Global RMS = {0:.2f} ppm, Point-to-point RMS = {1:.2f} ppm '
           '(d2flag={2})')
    margs = (rms * 1e6, p2p_rms * 1e6, d2flag)
    WLOG(params, '', msg.format(*margs))
    # -------------------------------------------------------------------------
    # Step 5: get the centroid positions and add to table
    # -------------------------------------------------------------------------
    # fit a sinc to the psf
    popt = fit_sinc_func(psf)
    # push the centers into the table
    ptbl['cent_x'] = xstart + popt[3] + ptbl['dxs']
    ptbl['cent_y'] = ystart + popt[4] + ptbl['dys']
    # -------------------------------------------------------------------------
    # return the photometry table
    return ptbl


# =============================================================================
# worker functions
# =============================================================================
# TODO: Needs a better name and needs an explaination of why
def process_integration(integration: np.ndarray,
                        xpix: np.ndarray,
                        njumps: int = 4) -> np.ndarray:
    # do this iteratively
    for jt in range(2):
        # subtract the median of every njump x-value off the integration
        for ix in range(njumps):
            # median of the x values (every njump x)
            xjump_med = np.nanmedian(integration[:, ix::njumps])
            # subtract of the integration itself
            integration[:, ix::njumps] -= xjump_med
        # calculate the median of the whole integration (across y-axis)
        y_med = np.nanmedian(integration, axis=0)
        # fit this median
        y_fit = np.polyfit(xpix, y_med, 1)
        # subtract this off each column
        for y_it in range(integration.shape[0]):
            integration[y_it, :] -= y_fit[0] * xpix + y_fit[1]
        # subtract the median of every njump y-value off the integration
        for iy in range(njumps):
            # median of the ith column
            yjump_med = np.nanmedian(integration[iy::njumps, :])
            # subtract of the integration itself
            integration[iy::njumps, :] -= yjump_med
    # return the cleaned integration
    return integration


def cut_down_cubes(params: ParamDict, cube: np.ndarray,
                   cube_err: np.ndarray
                   ) -> Tuple[np.ndarray, np.ndarray, float, float]:
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
    return cut_cube, cut_cube_err, xstart, ystart


def calc_mean_pedestal(params: ParamDict, cube: np.ndarray
                       ) -> Tuple[np.ndarray:, np.ndarray]:

    # get the MIRIAM params
    mparams = params.get('MIRIAM')
    # get the mean pedestal radius
    mean_ped_rad = mparams['INPUTS.MEAN_PEDESTAL_RADIUS']

    # get the indices (with an integration) in y and x
    y_indices, x_indices = np.indices(cube[0].shape)
    # offset to be relative to center
    y_offsets = y_indices - (cube.shape[1] // 2)
    x_offsets = x_indices - (cube.shape[2] // 2)
    # calculate the radius
    radii = np.sqrt(x_offsets**2 + y_offsets**2) - mean_ped_rad

    # this is a soft-edged mask of ones and zeros
    ww = 1 - ((erf(radii * 2) / 2) + 0.5)
    ww_invert = 1 - ww
    # storage for return (one per integration)
    pedestal_mean = np.zeros(cube.shape[0])
    # loop around all integrations
    for iframe in range(cube.shape[0]):
        # get this integration
        integration = cube[iframe, :, :]
        # only keep valid pixels (finite)
        valid = np.isfinite(integration)
        # calculate the mean pedestal
        part1 = (integration * ww_invert)[valid]
        part2 = ww_invert[valid]
        ped_mean = np.sum(part1) / np.sum(part2)
        # store the mean pedestal
        pedestal_mean[iframe] = ped_mean
    # return the pedestal mean per integration
    return pedestal_mean, ww


def remove_from_3d(cube3d: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    pedestal = np.zeros(cube3d.shape[0])
    # Loop through each slice of the cube. We do this as a 3D cube to avoid
    # but this may go into a 4D hypercube.
    for iframe in tqdm(range(cube3d.shape[0]), leave=False):
        # get the integration slice
        integration = cube3d[iframe, :, :]
        # get the overall median of this integration
        med0 = np.nanmedian(integration)
        # Subtract the median of each quadrant
        integration[::2, ::2] -= np.nanmedian(integration[::2, ::2])
        integration[1::2, ::2] -= np.nanmedian(integration[1::2, ::2])
        integration[::2, 1::2] -= np.nanmedian(integration[::2, 1::2])
        integration[1::2, 1::2] -= np.nanmedian(integration[1::2, 1::2])
        # add back on the overall median
        integration2 = np.array(integration + med0)
        # set the cube slice and pedestal using remove_background2d
        popt = fit_sinc_func(integration2)
        # get the integration and pedestal
        integration3, int_ped = integration2-popt[2], popt[2]

        cube3d[iframe, :, :], pedestal[iframe] = integration3, int_ped
    # return the full corrected cube and pedestal per integration
    return cube3d, pedestal


def sinc2d(xy: np.ndarray, amp: float, per: float, pedestal_psf: float,
           xcen: float, ycen: float, bwidth: float = 0.1):
    """
    2D Sinc function with bandpass and pedestal

    :param xy: np.ndarray, the x and y positions as a 2xN array
    :param amp: float, the amplitude of the sinc
    :param per: float, the period of the sinc
    :param pedestal_psf: float, the pedestal level
    :param xcen: float, the x center of the sinc
    :param ycen: float, the y center of the sinc
    :param bwidth: float, the bandwidth of the sinc (default 0.1)
    :return:
    """
    # get x and y out of the xy array
    x,y = xy
    # offset by the center in y and y
    x0 = x-xcen
    y0 = y-ycen
    # work out the distance from center
    rad = np.sqrt(x0**2 + y0**2)
    # we create 5 sinc to simulate bandpass
    dband = 1+(np.arange(5)-2)/4.0*bwidth
    # storage for output profile
    outprofile = np.zeros_like(rad).astype(float)
    # loop around the different bandpasses
    for dd in dband:
        per2 = per*dd
        outprofile += (amp/len(dband)) * np.sinc(rad / np.pi/per2) ** 2
    # return the output profile plus pedestal
    return outprofile + pedestal_psf


def fit_sinc_func(image: np.ndarray):
    """

    Remove the background from a 2D image.

    This is done by fitting a sinc2d with a pedestal. We only
    subtract the pedestal and return the image. The sinc2d
    function is just there to remove the bias from the PSF and
    not subtracted in the end.

    """
    # we construct the 2d pixel values
    ypix, xpix = np.indices(image.shape)
    # we find valid pixels
    valid = np.isfinite(image)
    # we ravel this into a 1d array for posterity
    xy = np.array([xpix[valid], ypix[valid]])
    # best guess as the psf center. this is the brightest pixel
    xmax = np.nanargmax(image) % image.shape[1]
    ymax = np.nanargmax(image) // image.shape[1]
    # amplitude best guess is image peak
    # sinc with =3 in pixels
    # pedestal = median
    # xmax and y max are best guess of psf center
    # 0.2 is the psf bandwidth guess
    p0 = np.array([np.nanmax(image), 3.0, np.nanmedian(image), xmax, ymax, 0.2])

    try:
        popt, _ = curve_fit(sinc2d, xy, image[valid], p0=p0)
    except Exception:
        popt = [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]

    # item [2] is the pedestal that we subtract
    return popt

def neighbourbad(image):
    # for each NaN pixel, find the 3x3 box (less if at the edge) and fit a
    # 2d 2nd order polynomial for find the best estimate of the missing pixel
    ybad, xbad = np.where(~np.isfinite(image))
    # create a 3x3 grid around each bad pixel
    ypixgrid, xpixgrid = np.meshgrid([-1, 0, 1], [-1, 0, 1])
    # loop around all bad pixels
    for ibad in range(len(xbad)):
        xpix = xbad[ibad] + xpixgrid
        ypix = ybad[ibad] + ypixgrid
        # remove xpix and ypix that would be off the edge of the image.shape
        rem_pix = (xpix < 0) | (xpix >= image.shape[1])
        rem_pix |= (ypix < 0) | (ypix >= image.shape[0])
        xpix = xpix[~rem_pix]
        ypix = ypix[~rem_pix]
        # Fit a 2D polynomial to the surrounding pixels
        z = image[ypix, xpix]
        # set bad pixels to the mean of surrounding pixels
        image[ybad[ibad], xbad[ibad]] = np.nanmean(z)

    return image


def noise_cube(cube: np.ndarray):
    # Calculate the 16th, 50th (median), and 84th percentiles
    #     along the first axis
    n1, med, p1 = np.nanpercentile(cube, [16, 50, 84], axis=0)
    # Define negative and positive cut thresholds
    cut_neg = med - 25 * (med - n1)
    cut_pos = med + 25 * (p1 - med)
    # Initialize an array for cube errors
    cube_err = np.zeros_like(cube)
    nanbad = ~np.isfinite(cube)

    # Loop through each slice of the cube
    for i in range(cube.shape[0]):
        # Identify bad pixels that are outside the cut thresholds
        bad = (cube[i] < cut_neg) | (cube[i] > cut_pos)
        # Calculate the error for each pixel
        cube_err[i] = (p1 - n1) / 2
        # Set the error of bad pixels to NaN
        cube_err[i][bad] = np.inf
        # correct the bad pixels using neighbourbad
        cube[i] = neighbourbad(cube[i])
    cube_err[nanbad] = np.inf

    return cube, cube_err


def normalize_cube(cube: np.ndarray, weights: np.ndarray):
    """
    Normalize the cube data. We first calculate the median of the cube
    and then do a linear fit to the median. We then divide the cube by
    the linear fit to normalize the data.

    :param cube:
    :param weights:
    :return:
    """

    # TODO: this could be trimmed, for ex the first readouts that
    #       have a different morphology.

    # storage for the normalized cube
    cube_normalize = np.array(cube)
    psf_guess = np.nanmedian(cube_normalize, axis=0)
    # loop around each itegration
    for iframe in range(cube.shape[0]):
        # We make a copy of the median and set the invalid values to NaN
        # this is to avoid the using a NaN value in the linear fit.
        # Also, this is done at each slice since the NaNs are different
        # for each slice.
        psf_guess0 = np.array(psf_guess)
        valid = np.isfinite(cube[iframe])
        psf_guess0[~valid] = np.nan
        # get the amplitude
        part1 = cube[iframe] * psf_guess0 * (weights**2)
        part2 = (psf_guess0 * weights) ** 2
        amp = np.nansum(part1) / np.nansum(part2)
        # We normalize the data by the linear fit
        cube_normalize[iframe] = cube_normalize[iframe] / amp
    return cube_normalize


def get_fit_params(cube_normalize: np.ndarray, weights: np.ndarray):
    """
    Get the fit parameters for the PSF fitting.

    :param psf:
    :param weights:
    :return:
    """
    # calculate the psf from the normalized cube
    psf = np.nanmedian(cube_normalize, axis=0)
    # deal with shape of the PSF (2D or 3D)
    if len(psf.shape) == 2:
        grady, gradx = np.gradient(psf)
    else:
        grady, gradx, _ = np.gradient(psf)
    # get the squared PSF
    psf2 = psf**2
    # orthogonalize the gradients to the PSF
    bad = ~np.isfinite(psf)
    ww_masked = np.array(weights)
    ww_masked[bad] = 0
    K = np.nansum(psf*psf2*ww_masked**2)/np.nansum(psf**2*ww_masked**2)
    psf2ortho = (psf2 - K * psf)

    return psf, gradx, grady, psf2ortho


def fit_cube_psf(params: ParamDict, cube: np.ndarray,
                 cube_err: np.ndarray, weights: np.ndarray,
                 mtbl: Table,
                 psf: np.ndarray, gradx: np.ndarray, grady: np.ndarray,
                 psf2ortho: np.ndarray, d2flag: bool = True) -> Table:

    # Initial guess for the PSF model parameters. We assume a scale of 1
    # and no gradients. This is a good starting point for the fit.
    p0 = [0.95, 0.1, 0.1, 1e-5]
    p0 = np.array(p0, dtype=np.float32)
    # -------------------------------------------------------------------------
    # Initialize arrays to store the fit results and errors
    amps = np.zeros(cube.shape[0])
    amps_err = np.zeros(cube.shape[0])
    dxs = np.zeros(cube.shape[0])
    dxs_err = np.zeros(cube.shape[0])
    dys = np.zeros(cube.shape[0])
    dys_err = np.zeros(cube.shape[0])
    d2s = np.zeros(cube.shape[0])
    d2s_err = np.zeros(cube.shape[0])
    # storage correlation between model and data
    corr = np.zeros(cube.shape[0])
    # -------------------------------------------------------------------------
    # print progress
    WLOG(params, '', 'Fitting PDF model to cube')
    # loop around each integration of the cube to fit the PSF model
    for iframe in tqdm(range(cube.shape[0])):
        # get integration and error
        integration = np.array(cube[iframe, :, :]).astype(np.float32)
        integration_err = np.array(cube_err[iframe, :, :]).astype(np.float32)
        # get valid pixels
        valid = np.isfinite(integration) & np.isfinite(integration_err)
        # set invalid pixels to zero
        integration = np.array(integration)
        integration[~valid] = 0.0
        # set bad pixels to errors of infinity
        integration_err[~valid] = np.inf
        # ---------------------------------------------------------------------
        # set up least_square arguments
        if d2flag:
            lkwargs = dict(psf=psf.ravel(),
                           gradx=gradx.ravel(), grady=grady.ravel(),
                           psf2ortho=psf2ortho.ravel())
        else:
            lkwargs = dict(psf=psf.ravel(),
                           gradx=gradx.ravel(), grady=grady.ravel())
        # ---------------------------------------------------------------------
        # minimize the least squares function to fit the PSF model
        lfit, lsig = least_squares(integration.ravel(), integration_err.ravel(),
                                   **lkwargs)
        # ---------------------------------------------------------------------
        # reconstruct the psf
        if d2flag:
            model_psf = (lfit[0] * psf +
                         lfit[1] * gradx +
                         lfit[2] * grady +
                         lfit[3] * psf2ortho)
        else:
            model_psf = (lfit[0] * psf +
                         lfit[1] * gradx +
                         lfit[2] * grady)
        # ---------------------------------------------------------------------
        # calculate correlation between model and data
        corr[iframe] = np.nansum(model_psf*weights) / np.nansum(psf * weights)
        # ---------------------------------------------------------------------
        # store the fit results and errors
        # ---------------------------------------------------------------------
        # amplitude of the PSF
        amps[iframe] = corr[iframe]
        # error in the amplitude
        amps_err[iframe] = lsig[0]
        # offset in x
        dxs[iframe] = lfit[1]
        # error in the offset in x
        dxs_err[iframe] = lsig[1]
        # offset in y
        dys[iframe] = lfit[2]
        # error in the offset in y
        dys_err[iframe] = lsig[2]
        if d2flag:
            # 2nd order gradient, representative of the FWHM
            d2s[iframe] = lfit[3]
            # error in the 2nd order gradient
            d2s_err[iframe] = lsig[3]
    # -------------------------------------------------------------------------
    # normalize the amplitude by the median
    median_amp = np.nanmedian(amps)
    amps /= median_amp
    amps_err /= median_amp
    # -------------------------------------------------------------------------
    # create the photometry table
    # -------------------------------------------------------------------------
    # we start from the merged table
    if mtbl is None:
        ptbl = Table()
    else:
        ptbl = Table(mtbl)
    # push these results into the mtbl
    ptbl['amps'] = amps
    ptbl['amps_err'] = amps_err
    ptbl['dxs'] = dxs
    ptbl['dxs_err'] = dxs_err
    ptbl['dys'] = dys
    ptbl['dys_err'] = dys_err
    ptbl['d2s'] = d2s
    ptbl['d2s_err'] = d2s_err
    # return the photometry table
    return ptbl


def least_squares(data: np.ndarray, data_err: np.ndarray, psf: np.ndarray,
                  gradx: np.ndarray, grady: np.ndarray,
                  psf2ortho: Optional[np.ndarray] = None):
    # Flatten basis arrays to match all_cds2
    if psf2ortho is not None:
        basis = np.vstack([
                           psf.flatten(),
                           gradx.flatten(),
                           grady.flatten(),
                           psf2ortho.flatten()
                           ]).T  # shape (Npix, 4)
    else:
        basis = np.vstack([
                           psf.flatten(),
                           gradx.flatten(),
                           grady.flatten()
                           ]).T  # shape (Npix, 3)
    # Only use finite data and errors
    mask = np.isfinite(data) & np.isfinite(data_err)
    ydata = data[mask]
    sigma = data_err[mask]
    amp = basis[mask]
    # Weighted least squares: minimize sum(((amp @ x - ydata)/sigma)**2)
    # Solution: x = inv(amp^T weight amp) @ (amp^T weight ydata)
    #           weight = diag(1/sigma^2)
    weight = 1.0 / sigma ** 2
    amp_weight = amp * weight[:, None]
    covariance = np.linalg.inv(amp_weight.T @ amp)
    least_square_fit = covariance @ (amp_weight.T @ ydata)
    least_square_sig = np.sqrt(np.diag(covariance))
    # return the fit and the sigma
    return least_square_fit, least_square_sig



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

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TSO Vore science functions (wrapped in a tso class)
"""
import os
import shutil
from typing import List, Optional

import numpy as np
from astropy.io import fits
from jwst import datamodels
from jwst.extract_1d import Extract1dStep
from scipy.interpolate import griddata
from scipy.signal import medfilt2d

from aperocore import math as mp
from aperocore.constants import param_functions
from aperocore.core import drs_log
from pogos.core import base as pogos_base

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'tsovore.science.tso.py'
__version__ = pogos_base.__version__
__date__ = pogos_base.__date__
__authors__ = pogos_base.__authors__
# Get parameter dictionary
ParamDict = param_functions.ParamDict
# Get Logging function
WLOG = drs_log.wlog
# -----------------------------------------------------------------------------


# =============================================================================
# Define functions
# =============================================================================
class Tso():
    def __init__(self, params: ParamDict, instrument: str):
        self.params = params
        self.instrument = instrument

        # set filenames (to be able to access throughout)
        self.file_block_name = 'block_{num:.0f}_{basename}.fits'
        self.file_bpblock_name = 'block_badpix_{num:.0f}_{basename}.fits'
        self.file_badpixinterp = '{seg}_badpixinterp.fits'
        self.file_badpixelmask = '{seg}_badpixelmask.fits'
        self.file_secondderiv = 'toto_secondderivatives.fits'

        self.file_deepstack = 'deepstack_1of_{basename}.fits'
        self.file_deepstack_rms = 'deepstack_1of_rms_{basename}.fits'

    # -------------------------------------------------------------------------
    # SOSS functions
    # -------------------------------------------------------------------------
    def soss_correct_badpix(self, postrampfitting_list: List[str],
                            save_results: bool = False,
                            nblocks: Optional[int] = None,
                            ddx2_nsigma: float = 10,
                            ddy2_nsigma: float = 10) -> List[str]:
        """
        Correction of badpixels for SOSS

        Two steps:
          1) use the idea of Louis-Philippe Coulombe (second derivative
             deviants)
          2) include the DQ map which should mostly come from the flat
             field bad pixels (if cosmic rays were handled prior)
          3) Read a text file that user can edit to add pixels

        Expect the list of fits files for all segments in a TSO. The analysis
        will be performed block by block, i.e. the detector will be divided in
        nblocks and for each, a all integrations of the TSO across segments
        will be read and used for the analysis.
        """
        # get tsovore params
        tparams = self.params['TSOVORE']

        # print progress
        msg = ('soss_correct_badpix - flagging bad pixels using thresholds '
               f'ddx2_nsigma = {ddx2_nsigma}, ddy2_nsigma={ddy2_nsigma}')
        WLOG(self.params, '', msg)
        # ---------------------------------------------------------------------
        #Establish what the directory is and the basename for the files
        # as well as the names of temporary block files.
        outdir = tparams['PATHS.TEMP_PATH']
        # get the number of segments
        nsegments = len(postrampfitting_list)
        # store a list of segment base names
        segment_basename_list = []
        # storage for tso basename
        tso_basename = ''
        # loop around
        for nseg in range(nsegments):
            # remove the extension of the file
            tmp = os.path.splitext(postrampfitting_list[nseg])[0]
            # get the basename of the file
            tmp = os.path.basename(tmp)
            tmp = tmp.split('_nis')[0] + '_nis'
            segment_basename_list.append(tmp)
            tso_basename = tmp.split('-seg')[0]
        # ---------------------------------------------------------------------
        if nblocks is None:
            # any divider of 2048 would do
            nblok = len(postrampfitting_list)*2
        else:
            nblok = int(nblocks)
        #nblocks = 2  # any divider of 2048 would do
        #blocksize = 2048 // nblocks
        # no need for common divider of 2048
        blocksize = int(np.ceil(2048 / nblok))
        # ---------------------------------------------------------------------
        # Set the name of temporary fits files where each corrected
        # block is saved
        block_name_list = []
        bpblock_name_list = []
        for it in range(nblok):
            # construct filenames
            bkwargs = dict(num=it+1, basename=tso_basename)
            block_name_file = self.file_block_name.format(**bkwargs)
            bpblock_name_file = self.file_bpblock_name.format(**bkwargs)
            # push into a list of paths
            block_name_list.append(os.path.join(outdir, block_name_file))
            bpblock_name_list.append(os.path.join(outdir, bpblock_name_file))
        # ---------------------------------------------------------------------
        # print progress
        msg = ('soss_correct_badpix - Integrations stacking of all '
               f'{nsegments} segments in the time-series in '
               f'{nblok} blocks of {blocksize} columns')
        WLOG(self.params, '', msg)
        # ---------------------------------------------------------------------
        # Open each file in the list to directly measure the total number of
        # integrations rather than relying on the .meta.exposure.nints has a
        # sneaky user could forge their input segments making the meta
        # structure unreliable...
        segments_nints = [0]
        nints = 0
        for segment in range(nsegments):
            tmp = datamodels.open(postrampfitting_list[segment])
            segments_nints.append(np.shape(tmp.data)[0])
            nints += np.shape(tmp.data)[0]
            tmp.close()
        del tmp
        # ---------------------------------------------------------------------
        # Loop for each image block
        for b_it in range(nblok):
            # print progress
            msg = f'soss_correct_badpix - sub image block {b_it} of {nblok}'
            WLOG(self.params, '', msg)
            # -----------------------------------------------------------------
            # Set the x-axis limits of this block of columns
            firstcol, lastcol = b_it * blocksize, (b_it + 1) * blocksize
            # Check that the last column is never above 2048
            lastcol = np.min([2048, lastcol])
            currentblocksize = lastcol - firstcol
            # -----------------------------------------------------------------
            # print progress
            msg = ('soss_correct_badpix - current block is between '
                   f'firstcol={firstcol} and lastcol={lastcol} and '
                   f'has size of {currentblocksize} columns')
            WLOG(self.params, '', msg)
            # -----------------------------------------------------------------
            # storage arrays
            data, dq = np.array([]), np.array([])
            # For each block of columns, loop over all segments
            for segment in range(nsegments):
                # Fill the data cube and groupdq cube for block b
                seg = datamodels.open(postrampfitting_list[segment])
                # i_start = seg.meta.exposure.integration_start
                # i_end = seg.meta.exposure.integration_end
                i_start = (np.cumsum(segments_nints[:segment+1])+1)[segment]
                i_end = (np.cumsum(segments_nints[:segment+2]))[segment+1]
                #if (i_start == None) & (i_end == None):
                if nsegments == 1:
                    # it means that this is a time-series NOT split into
                    # segments
                    #i_start, i_end = 1, seg.meta.exposure.nints
                    i_start, i_end = 1, nints
                # -------------------------------------------------------------
                # print progress
                msg = (f'soss_correct_badpix - integration_start = {i_start}, '
                       f'integration_end = {i_end}')
                WLOG(self.params, '', msg)
                # -------------------------------------------------------------
                # deal with first segment
                if segment == 0:
                    # First segment, initialize cubes of proper size
                    _, dimy, dimx = np.shape(seg.data)
                    #nints = seg.meta.exposure.nints
                    #nints = sum(segments_nints[1:])
                    #print('nints = {:}'.format(nints))
                    data = np.zeros((nints, dimy, currentblocksize)) * np.nan
                    dq = np.zeros((nints, dimy, currentblocksize))
                    #print('shape data = ', np.shape(data))

                # the current segment data and pixel DQ
                #print('shape seg.data = ', np.shape(data))
                data_tmp = np.copy(seg.data[:, :, firstcol:lastcol])
                dq_tmp = np.copy(seg.dq[:, :, firstcol:lastcol])
                data[i_start-1:i_end, :, :] = data_tmp
                dq[i_start-1:i_end, :, :] = dq_tmp
            # -----------------------------------------------------------------
            # Now run the bad pixel flagging on the block containing all
            # integrations in the TSO for these pixels.
            bp = self.badpixel_flag_seconderivative(data,
                                                    ddx2_nsigma=ddx2_nsigma,
                                                    ddy2_nsigma=ddy2_nsigma)
            # -----------------------------------------------------------------
            # Check also the input DQ map
            bp[dq != 0] = 1
            # Check also for the presence of any NaN
            bp[~np.isfinite(data)] = 1
            # Write the bad pixel files on disk
            fits.writeto(bpblock_name_list[b_it], bp, overwrite=True)
            # -----------------------------------------------------------------
            # Now correct the bad pixels
            datacorr = self.interpolate_badpixels_cubic(data, bp,
                                                        integ_halfwidth=4)
            # -----------------------------------------------------------------
            # Now save this block on disk in nblok separate files.
            # Later stage will merge those into segment files.
            fits.writeto(bpblock_name_list[b_it], datacorr, overwrite=True)
            # -----------------------------------------------------------------
            # Delete big arrays to reduce memory usage
            del bp, data, dq, datacorr
        # ---------------------------------------------------------------------
        # Blocks have all been run. Time to reconstruct corrected segments
        # from corrected blocks saved on this
        # ---------------------------------------------------------------------
        # print progress
        msg = ('soss_correct_badpix - Now save the corrected segments...')
        WLOG(self.params, '', msg)
        # ---------------------------------------------------------------------
        outfiles = []
        # loop around segments
        for segment in range(nsegments):
            # print progress
            msg = ('soss_correct_badpix - segment '
                  f'{segment+1:2.0f} of {nsegments:2.0f}')
            WLOG(self.params, '', msg)
            # -----------------------------------------------------------------
            # open the data model of the current segment
            seg = datamodels.open(postrampfitting_list[segment])
            # i_start = seg.meta.exposure.integration_start
            # i_end = seg.meta.exposure.integration_end
            i_start = (np.cumsum(segments_nints[:segment + 1]) + 1)[segment]
            i_end = (np.cumsum(segments_nints[:segment + 2]))[segment + 1]
            # create a file to store this segment's bad pixels
            badpix_segment = seg.data*0
            # -----------------------------------------------------------------
            #if (i_start is None) & (i_end is None):
            if nsegments == 1:
                # it means that this is a time-series NOT split into segments
                #i_start, i_end = 1, seg.meta.exposure.nints
                i_start, i_end = 1, nints
            # -----------------------------------------------------------------
            # loop around the blocks
            for b_it in range(nblok):
                # print progress
                msg = (f'soss_correct_badpix - sub image block '
                       f'{b_it + 1} of {nblok}')
                WLOG(self.params, '', msg)
                # get this blocks data
                thisblock = fits.getdata(block_name_list[b_it])
                # Set the x-axis limits of this block of columns
                firstcol, lastcol = b_it * blocksize, (b_it + 1) * blocksize
                # Check that the last column is never above 2048
                lastcol = np.min([2048, lastcol])
                #currentblocksize = lastcol - firstcol, keep for now
                karray = np.array(thisblock[i_start - 1:i_end, :, :])
                seg.data[:,:,firstcol:lastcol] = karray
                # Assign corrected pixels with a DQ = 0
                seg.dq[:,:,firstcol:lastcol] = 0
                # Do the same for the bad pixel file
                thisblock = fits.getdata(bpblock_name_list[nblok])
                karray = np.array(thisblock[i_start - 1:i_end, :, :])
                badpix_segment[:,:,firstcol:lastcol] = karray
            # -----------------------------------------------------------------
            if not save_results:
                msg = ('soss_correct_badpix - Only option is to save outputs. '
                       'save_results must be True')
                WLOG(self.params, 'warning', msg)
            # -----------------------------------------------------------------
            # construct dict for file args
            skwargs = seg=segment_basename_list[segment]
            # construct seg file (after bad pixel interp)
            seg_file = self.file_badpixinterp.format(**skwargs)
            seg_outpath = os.path.join(outdir, seg_file)
            # construct mask file
            maskfile = self.file_badpixelmask.format(**skwargs)
            mask_outpath = os.path.join(outdir, maskfile)
            # -----------------------------------------------------------------
            # print progress
            msg = (f'soss_correct_badpix - saving {seg_file}')
            WLOG(self.params, '', msg)
            # -----------------------------------------------------------------
            # update meta data
            seg.meta.filename = seg_file
            # -----------------------------------------------------------------
            # write update seg file
            seg.write(seg.meta.filename)
            # TODO: Is there a better way to do this and preserve the seg
            #       file - maybe we need to copy the datamodel somehow?
            shutil.copy(seg.meta.filename, seg_outpath)
            # write mask file
            fits.writeto(mask_outpath, maskfile, overwrite=True)
            # -----------------------------------------------------------------
            # TODO: Loic, erase the temporary block files from disk once this
            #  step has been debugged

        return outfiles

    def badpixel_flag_seconderivative(self, data: np.ndarray,
                                      ddx2_nsigma: float = 10,
                                      ddy2_nsigma: float = 10) -> np.ndarray:
        """
        Flag badpixels using second deriviate

        Accepts a cube of data (nints, dimy, dimx) and returns a cube of same size
        with 0 for good pixels, 1 for bad pixels.
        """
        # get tsovore params
        tparams = self.params['TSOVORE']
        #Establish what the directory is and the basename for the files
        # as well as the names of temporary block files.
        outdir = tparams['PATHS.TEMP_PATH']
        # Expect data to be 3-dimensional (integrations, y, x)
        nint, dimy, dimx = np.shape(data)

        # Initialize the corrected data
        # data_corr = np.array(data)
        # Initialize the array of bad pixel flags
        flags = np.zeros_like(data)
        # make sure there is no NaN, if so flag them as bad pixels
        flags[~np.isfinite(flags)] = 1

        # Compute the second derivative in x and y for all integrations at once
        ddx = np.gradient(data, axis=-1)
        ddx2 = -np.gradient(ddx, axis=-1)
        ddy = np.gradient(data, axis=-2)
        ddy2 = -np.gradient(ddy, axis=-2)
        # Compute the median and median deviation along the integrations axis
        ddx2_med = np.median(ddx2, axis=0)
        ddx2_mdv = _mediandev(ddx2, axis=0)
        ddy2_med = np.median(ddy2, axis=0)
        ddy2_mdv = _mediandev(ddy2, axis=0)
        # Smooth a little the scatter map to make bad pixels wash out from the
        # stats
        ddx2_med = medfilt2d(ddx2_med, kernel_size=3)
        ddx2_mdv = medfilt2d(ddx2_mdv, kernel_size=3)
        ddy2_med = medfilt2d(ddy2_med, kernel_size=3)
        ddy2_mdv = medfilt2d(ddy2_mdv, kernel_size=3)
        # ---------------------------------------------------------------------
        # Identify 5-sigma outliers as bad pixels then interpolate to correct
        for it in range(nint):
            ddx2_nsig = np.abs((ddx2[it] - ddx2_med)) / ddx2_mdv
            ddy2_nsig = np.abs((ddy2[it] - ddy2_med)) / ddy2_mdv
            # Use 5 sigma as threshold because a normal distribution
            # yields less than 1 such random outlier for 2048x256 pixels
            badpixels = (ddx2_nsig > ddx2_nsigma) & (ddy2_nsig > ddy2_nsigma)
            flags[it][badpixels] = 1
            # ------------------------------------------------------------------
            # TODO: Neil doesn't understand why you are only saving
            #       nint = 3
            if it == 3:
                file_secondderiv = self.file_secondderiv
                filepath = os.path.join(outdir, file_secondderiv)
                # print progress
                msg = 'Saving {0}'.format(filepath)
                msg += f'\n\tddx2_nsigma = {ddx2_nsigma}'
                msg += f'\n\tddy2_nsigma = {ddy2_nsigma}'
                WLOG(self.params, '', msg)
                # Primary HDU of a fits file should be header only
                hdulist = fits.HDUList([fits.PrimaryHDU])
                # Add all other extensions
                hdulist.append(fits.ImageHDU(data[it], name='DATA'))
                hdulist.append(fits.ImageHDU(flags[it], name='FLAGS'))
                hdulist.append(fits.ImageHDU(data=ddx2_nsig, name="DDX2_NSIG"))
                hdulist.append(fits.ImageHDU(data=ddx2_med, name="DDX2_MED"))
                hdulist.append(fits.ImageHDU(data=ddx2_mdv, name="DDX2_MDV"))
                hdulist.append(fits.ImageHDU(data=ddy2_nsig, name="DDY2_NSIG"))
                hdulist.append(fits.ImageHDU(data=ddy2_med, name="DDY2_MED"))
                hdulist.append(fits.ImageHDU(data=ddy2_mdv, name="DDY2_MDV"))
                #outdir = ('/Users/albert/NIRISS/sossisse/sossisse/sossiopath/
                #          'JWST.NIRISS.SOSS/01201_101/loic_processing')
                #outdir = self.tparams['PATHS.TEMP_PATH']
                hdulist.writeto(filepath, overwrite=True)

        return flags

    def interpolate_badpixels_cubic(self, image_3d: np.ndarray,
                                    flag_3d: np.ndarray,
                                    integ_halfwidth: int = 4) -> np.ndarray:
        """
        Squeeze the integ_halfwidth*2+1 integrations into a 2D median of higher SNR.
        Then interpolate the bad pixels using that median.

        flag3D is 0 for good pixels, 1 or more for bad pixels
        """
        # copy the image
        image_3d_corr = np.copy(image_3d)
        # get the number of integration from the shape of the input
        nint = np.shape(image_3d)[0]

        for it in range(nint):
            # print progress
            msg = ('interpolate_badpixels_cubic - integration {it+1} of {nint}')
            WLOG(self.params, '', msg)
            # Determine the integration indices to retain in the medianing
            imin = max([0, it - integ_halfwidth])
            imax = min([nint - 1, it + integ_halfwidth])
            icur = it - imin
            # -----------------------------------------------------------------
            # Create temporary cubes for only the nearby integrations
            data = np.array(image_3d[imin:imax + 1, :, :])
            goodpix = np.array(flag_3d[imin:imax + 1, :, :])
            datacorr = np.copy(data)
            # -----------------------------------------------------------------
            # Make sure that the data has all bad pixels set to NaN
            data[~(goodpix == 0)] = np.nan
            # -----------------------------------------------------------------
            # Create a high SNR representative integration centered on the
            # current integration
            integ_median = np.nanmedian(data, axis=0)
            # -----------------------------------------------------------------
            # calculate the number of nans to interpolate from
            n_nans = np.sum(~np.isfinite(integ_median))
            # -----------------------------------------------------------------
            # print progress
            msg = ('interpolate_badpixels_cubic - number of NaNs in the '
                   f'image to interpolate from: {n_nans}')
            WLOG(self.params, '', msg)
            # -----------------------------------------------------------------
            # Expect a tuple of 2 x 1D arrays for the good pixels
            # usually obtained points = np.where(np.isfinite(im))
            # points (pairs of x,y)
            points = np.where(np.isfinite(integ_median))
            values = integ_median[points]
            # -----------------------------------------------------------------
            # location positions of bad pixels
            badpix_y, badpix_x = np.where(~np.isfinite(integ_median))
            # -----------------------------------------------------------------
            # interpolate
            val_best = griddata(points, values, (badpix_y, badpix_x),
                                method='cubic')
            # -----------------------------------------------------------------
            # Replace bad pixels by best interpolation method (cubic)
            # If some NaNs remain, replace using the back up method (nearest)
            if (~np.isfinite(val_best)).sum() >= 1:
                # Interpolation using the method nearest that works all the time
                val_safe = griddata(points, values, (badpix_y, badpix_x),
                                    method='nearest')
                ind = np.where(~np.isfinite(val_best))
                toto = np.array(val_best)
                toto[ind] = np.array(val_safe[ind])
                # -------------------------------------------------------------
                # calculate the number of remaining nans
                num_nans = np.sum(~np.isfinite(val_best))
                # -------------------------------------------------------------
                # print progress
                msg = ('interpolate_badpixels_cubic - remaining number of '
                       f'bad pixels after griddata correction: {num_nans}')
                WLOG(self.params, '', msg)
                # -------------------------------------------------------------
                # update the corrected data cube
                datacorr[icur, badpix_y, badpix_x] = np.array(toto)
            else:
                # print progress - no nans remain
                msg = ('interpolate_badpixels_cubic - no NaN remaining after '
                       'griddata correction')
                WLOG(self.params, '', msg)
                # -------------------------------------------------------------
                # update the corrected data cube
                datacorr[icur, badpix_y, badpix_x] = np.array(val_best)
            # -----------------------------------------------------------------
            # print the number of nans left after full process
            num_nans = np.sum(~np.isfinite(datacorr[icur, :, :]))
            msg = ('interpolate_badpixels_cubic - remaining number of bad '
                   'pixels in the end: {num_nans}')
            WLOG(self.params, '', msg)
            # -----------------------------------------------------------------
            image_3d_corr[it] = np.array(datacorr[icur])
        # ---------------------------------------------------------------------
        # clean up the data (remove arrays)
        del data, datacorr, goodpix, badpix_y, badpix_x

        # TODO: Loic, padd the blocks to prevent border effects

        return image_3d_corr

    def get_spectrace(self, infiles: List[str]):

        # Use the first integration in the list as the data model
        model = infiles[0]

        # Instantiate the extract1d step (absolutely needed for the rest to work)
        step = Extract1dStep()

        # Get the most appropriate reference file name for this data model
        # specprofile_name = step.get_reference_file(model,'specprofile')
        pastasoss_name = step.get_reference_file(model, 'pastasoss')

        # Open the pastasoss reference file and find the x, y, throughput info
        ref = datamodels.open(pastasoss_name)

        spectrace = {
            'x_o1': ref.traces[0].trace[:, 0],
            'x_o2': ref.traces[1].trace[:, 0],
            'x_o3': ref.traces[2].trace[:, 0],
            'y_o1': ref.traces[0].trace[:, 1],
            'y_o2': ref.traces[1].trace[:, 1],
            'y_o3': ref.traces[2].trace[:, 1],
            'wave_o1': ref.throughputs[0].wavelength,
            'wave_o2': ref.throughputs[1].wavelength,
            'wave_o3': ref.throughputs[2].wavelength,
            'throughput_o1': ref.throughputs[0].throughput,
            'throughput_o2': ref.throughputs[1].throughput,
            'throughput_o3': ref.throughputs[2].throughput
        }

        # TODO: Save to tmp directory

        return spectrace

    def stack_multisegments(self, segment_list: List[str], save_results=True,
                            stack_nblocks=None) -> List[str]:
        """
        Produces a deep stack of all integrations across all segments of
        a SOSS TSO.

        Does so by processing on blocks of columns rather than full data
        set to limit memory usage. Assumes that the input segments are
        4-dimensional, i.e. they have not been through the ramp fitting
        step yet.

        :param segment_list: list[str], list of segments to stack
        :param outdir: str, path to output directory
        :param save_results: bool, whether to save results to file
        :param stack_nblocks: int, number of column blocks to divide the
                              images into for processing

        :return: array, the stacked image which is a median of all integrations.
        """
        nsegements = len(segment_list)
        #
        tparams = self.params['TSOVORE']
        # deal with no stack nlocks
        if stack_nblocks is None:
            # any divider of 2048 would do
            # Number of blocks depends on number of segments but also
            # subarray size
            seg = datamodels.open(segment_list[0])
            if seg.meta.subarray.name == 'FULL':
                nblocks = nsegements * 2 * 8
            elif seg.meta.subarray.name == 'SUBSTRIP256':
                nblocks = nsegements * 2
            elif seg.meta.subarray.name == 'SUBSTRIP96':
                nblocks = nsegements * 2
            else:
                print('SUBARRAY is not supported. Try something.')
                nblocks = nsegements * 2
        else:
            nblocks = np.copy(stack_nblocks)
        # -------------------------------------------------------------------------
        #nblocks = 2  # any divider of 2048 would do
        #blocksize = 2048 // nblocks
        # no need for common divider of 2048
        blocksize = int(np.ceil(2048 / nblocks))
        # -------------------------------------------------------------------------
        # print progress
        msg = (f'1/f stacking of all {nsegements} segments in the time-series in '
               f'{nblocks} blocks of {blocksize} columns')
        WLOG(self.params, '', msg)
        # set for output (updated in loop)
        pid, obsnbr = None, None
        # storage for outside for loop
        data, mask = np.array([]), np.array([])
        deepstack, rms = np.array([]), np.array([])
        ngroups, dimy, dimx = np.shape(data)
        # -------------------------------------------------------------------------
        # loop around blocks
        for b_it in range(nblocks):
            # ---------------------------------------------------------------------
            # print progress
            msg = 'Block {:}'.format(b_it + 1)
            WLOG(self.params, '', msg)
            # ---------------------------------------------------------------------
            # Set the x-axis limits of this block of columns
            firstcol, lastcol = b_it * blocksize, (b_it + 1) * blocksize
            # ---------------------------------------------------------------------
            # Check that the last column is never above 2048
            lastcol = np.min([2048, lastcol])
            currentblocksize = lastcol - firstcol
            # ---------------------------------------------------------------------
            # print progress
            msg = (f'\tCurent block is between firstcol={firstcol} and '
                   f'lastcol={lastcol} and has size of {currentblocksize} columns')
            WLOG(self.params, '', msg)
            # ---------------------------------------------------------------------
            # For each block of columns, loop over all segments
            for segment in range(nsegements):
                # Fill the data cube and groupdq cube for block b
                seg = datamodels.open(segment_list[segment])
                i_start = seg.meta.exposure.integration_start
                i_end = seg.meta.exposure.integration_end
                # it means that this is a time-series NOT split into segments
                if (i_start is None) and (i_end is None):
                    i_start, i_end = 1, seg.meta.exposure.nints
                # -----------------------------------------------------------------
                # print progress
                msg = ('\ti_start = {:}, i_end = {:}'.format(i_start, i_end))
                WLOG(self.params, '', msg)
                # -----------------------------------------------------------------
                if segment == 0:
                    # First segment, initialize cubes of proper size
                    _, ngroups, dimy, dimx = np.shape(seg.data)
                    nints = seg.meta.exposure.nints
                    data = np.full((nints, ngroups, dimy, currentblocksize), np.nan)
                    mask = np.full((nints, ngroups, dimy, currentblocksize), np.nan)
                # the current segment data, group DQ and pixel DQ
                data_tmp = np.copy(seg.data[:, :, :, firstcol:lastcol])
                data[i_start-1:i_end, :, :, :] = data_tmp
                gdq = np.copy(seg.groupdq[:, :, :, firstcol:lastcol])
                pdq = np.copy(seg.pixeldq[:, firstcol:lastcol])
                # Add to the mask the group dq (4 dimensional)
                segmask = np.where(gdq != 0, np.nan, 1)
                mask[i_start-1:i_end, :, :, :] = np.copy(segmask)
                # Add to the mask the pixel dq (2 dimensional)
                segmask = np.where(pdq != 0, np.nan, 1)
                mask[i_start-1:i_end, :] = mask[i_start-1:i_end, :] * segmask
                # retain the program ID and observation number for output filename
                pid = seg.meta.observation.program_number
                obsnbr = seg.meta.observation.observation_number
            # Stack that block, all bad pixels are NaNs
            if b_it == 0:
                # First block, initialize the final products with proper size
                deepstack = np.zeros((ngroups, dimy, dimx)) * np.nan
                rms = np.zeros((ngroups, dimy, dimx)) * np.nan
            block_stack = np.nanmedian(data * mask, axis=0)
            block_rms = _mediandev(data * mask - block_stack, axis=0)
            deepstack[:, :, firstcol:lastcol] = np.copy(block_stack)
            rms[:, :, firstcol:lastcol] = np.copy(block_rms)

            # clean up large arrays
            del seg, segmask, gdq, pdq
            del data, mask, block_stack
        # -------------------------------------------------------------------------
        # # deal with saving files
        # -------------------------------------------------------------------------
        datadir = tparams['PATH.TEMP_PATH']

        # datadir = self.tparams['PATHS.TEMP_PATH'] DOESN'T WORK,
        #           loic_niriss not a class
        # Name of this TSO forged from its PID and observation number
        # basename = os.path.basename(os.path.splitext(segment1name)[0])
        # basename_ts = tsobasename(segment1name)
        basename_ts = pid + obsnbr
        # ---------------------------------------------------------------------
        # construct the filename
        tkwargs = dict(basename=basename_ts)
        deepstackname = self.file_deepstack.format(**tkwargs)
        rmsname = self.file_deepstack_rms.format(**tkwargs)

        deepstack_out = os.path.join(datadir, deepstackname)
        rms_out = os.path.join(datadir, rmsname)
        # -------------------------------------------------------------------------
        if save_results:
            # save results to fits files
            fits.writeto(deepstack_out, deepstack, overwrite=True)
            fits.writeto(rms_out, rms, overwrite=True)

        return segment_list

    # -------------------------------------------------------------------------
    # class worker functions
    # -------------------------------------------------------------------------



# =============================================================================
# Define worker functions
# =============================================================================
def _mediandev(x: np.ndarray, axis: Optional[int] = None):
    """
    Calculate the median deviation normalized to the normal distribution.

    :param x: np.ndarray, array-like
    :param axis: int, optional, the axis along which to median
    """
    med = np.nanmedian(x, axis=axis)
    # reutrn the median devis
    return np.nanmedian(np.abs(x - med), axis=axis) / mp.inv_normal_fraction()

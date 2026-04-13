#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2026-01-29 at 11:50

@author: cook
"""
import numpy as np
from astropy.io import fits
from jwst import datamodels
import os
from scipy import interpolate
from scipy.signal import medfilt2d
from scipy.interpolate import griddata


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'loic_niriss.py'

# Example scale factor
GROUP_SCALE_SIZE = 1.2

# -----------------------------------------------------------------------------

# =============================================================================
# Define functions
# =============================================================================



def soss_correct_badpix(postrampfitting_list, save_results=False,
                        nblocks=None, ddx2_nsigma=10, ddy2_nsigma=10):

    # Two steps:
    # 1) use the idea of Louis-Philippe Coulombe (second derivative deviants)
    # 2) include the DQ map which should mostly come from the flat field bad pixels (if cosmic rays were handled prior)
    # 3) Read a text file that user can edit to add pixels

    # Expect the list of fits files for all segments in a TSO. The analysis
    # will be performed block by block, i.e. the detector will be divided in
    # nblocks and for each, a all integrations of the TSO across segments will
    # be read and used for the analysis.

    print('soss_correct_badpix - flagging bad pixels using thresholds ddx2_nsigma = {:}, ddy2_nsigma={:}'.format(ddx2_nsigma, ddy2_nsigma))

    #Establish what the directory is and the basename for the files
    # as well as the names of temporary block files.
    # outdir = self.tparams['PATHS.TEMP_PATH']
    # TODO: the above line method does not work, come up with a way to have the
    #  outdir. Neil job.
    outdir = '/Users/albert/Downloads/'


    nsegments = np.size(postrampfitting_list)
    segment_basename_list = []
    for i in range(nsegments):
        tmp = os.path.splitext(postrampfitting_list[i])[0]
        tmp = os.path.basename(postrampfitting_list[i])
        tmp = tmp.split('_nis')[0] + '_nis'
        segment_basename_list.append(tmp)
        tso_basename = tmp.split('-seg')[0]

    if nblocks == None:
        # any divider of 2048 would do
        nblok = np.size(postrampfitting_list)*2
    else:
        nblok = np.copy(nblocks)
    #nblocks = 2  # any divider of 2048 would do
    #blocksize = 2048 // nblocks
    blocksize = int(np.ceil(2048 / nblok)) # no need for common divider of 2048

    # Set the name of temporary fits files where each corrected block is saved
    block_name_list = []
    bpblock_name_list = []
    for i in range(nblok):
        block_name_list.append(outdir + '/block_{:.0F}_'.format(i + 1) + tso_basename + '.fits')
        bpblock_name_list.append(outdir + '/block_badpix_{:.0F}_'.format(i + 1) + tso_basename + '.fits')

    print('soss_correct_badpix - Integrations stacking of all {:} segments in the time-series in {:} blocks of {:} columns'.format(
        np.size(postrampfitting_list), nblok, blocksize))

    # Open each file in the list to directly measure the total number of integrations
    # rather than relying on the .meta.exposure.nints has a sneaky user could forge
    # their input segments making the meta structure unreliable...
    segments_nints = [0]
    nints = 0
    for segment in range(np.size(postrampfitting_list)):
        tmp = datamodels.open(postrampfitting_list[segment])
        segments_nints.append(np.shape(tmp.data)[0])
        nints += np.shape(tmp.data)[0]
        tmp.close()
    del tmp

    # Loop for each image block
    for b in range(nblok):
        print('soss_correct_badpix - sub image block {:} of {:}'.format(b+1, nblok))
        # Set the x-axis limits of this block of columns
        firstcol, lastcol = b * blocksize, (b + 1) * blocksize
        # Check that the last column is never above 2048
        lastcol = np.min([2048, lastcol])
        currentblocksize = lastcol - firstcol
        print('soss_correct_badpix - curent block is between firstcol={:} and lastcol={:} and has size of {:} columns'.format(
            firstcol, lastcol, currentblocksize))

        # For each block of columns, loop over all segments
        for segment in range(np.size(postrampfitting_list)):
            # Fill the data cube and groupdq cube for block b
            seg = datamodels.open(postrampfitting_list[segment])
            #i_start, i_end = seg.meta.exposure.integration_start, seg.meta.exposure.integration_end
            i_start = (np.cumsum(segments_nints[:segment+1])+1)[segment]
            i_end = (np.cumsum(segments_nints[:segment+2]))[segment+1]
            #if (i_start == None) & (i_end == None):
            if np.size(postrampfitting_list) == 1:
                # it means that this is a time-series NOT split into segments
                #i_start, i_end = 1, seg.meta.exposure.nints
                i_start, i_end = 1, nints
            print('soss_correct_badpix - integration_start = {:}, integration_end = {:}'.format(i_start, i_end))
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
            data[i_start-1:i_end, :, :] = np.copy(seg.data[:, :, firstcol:lastcol])
            dq[i_start-1:i_end, :, :] = np.copy(seg.dq[:, :, firstcol:lastcol])

        # Now run the bad pixel flagging on the block containing all integrations
        # in the TSO for these pixels.
        bp = badpixel_flag_seconderivative(data, outdir, ddx2_nsigma=ddx2_nsigma, ddy2_nsigma=ddy2_nsigma)
        # Check also the input DQ map
        bp[dq != 0] = 1
        # Check also for the presence of any NaN
        bp[~np.isfinite(data)] = 1
        # Write the bad pixel files on disk
        hdu = fits.PrimaryHDU(bp)
        hdu.writeto(bpblock_name_list[b], overwrite=True)

        # Now correct the bad pixels
        datacorr = interpolate_badpixels_cubic(data, bp, outdir, integ_halfwidth=4)

        # Now save this block on disk in nblok separate files.
        # Later stage will merge those into segment files.
        hdu = fits.PrimaryHDU(datacorr)
        hdu.writeto(block_name_list[b], overwrite=True)

        # Delete big arrays to reduce memory usage
        del bp, data, dq, datacorr

    # Blocks have all been ran. Time to reconstruct corrected segments
    # from corrected blocks saved on this
    print('soss_correct_badpix - Now save the corrected segments...')
    outfiles = []
    for segment in range(np.size(postrampfitting_list)):
        print('soss_correct_badpix - segment {:2.0F} of {:2.0F}'.format(segment+1, np.size(postrampfitting_list)))
        seg = datamodels.open(postrampfitting_list[segment])
        #i_start, i_end = seg.meta.exposure.integration_start, seg.meta.exposure.integration_end
        i_start = (np.cumsum(segments_nints[:segment + 1]) + 1)[segment]
        i_end = (np.cumsum(segments_nints[:segment + 2]))[segment + 1]
        # create a file to store this segment's bad pixels
        badpix_segment = seg.data*0
        # Go
        #if (i_start == None) & (i_end == None):
        if np.size(postrampfitting_list) == 1:
            # it means that this is a time-series NOT split into segments
            #i_start, i_end = 1, seg.meta.exposure.nints
            i_start, i_end = 1, nints

        for b in range(nblok):
            print('soss_correct_badpix - sub image block {:} of {:}'.format(b + 1, nblok))
            thisblock = fits.getdata(block_name_list[b])
            # Set the x-axis limits of this block of columns
            firstcol, lastcol = b * blocksize, (b + 1) * blocksize
            # Check that the last column is never above 2048
            lastcol = np.min([2048, lastcol])
            #currentblocksize = lastcol - firstcol, keep for now
            seg.data[:,:,firstcol:lastcol] = thisblock[i_start - 1:i_end, :, :]*1
            # Assign corrected pixels with a DQ = 0
            seg.dq[:,:,firstcol:lastcol] = 0
            # Do the same for the bad pixel file
            thisblock = fits.getdata(bpblock_name_list[b])
            badpix_segment[:,:,firstcol:lastcol] = thisblock[i_start - 1:i_end, :, :]*1

        if save_results:
            #TODO: Neil, change the saved name. As is, the file in temporary is
            # named ..._nis_badpixinterp_sourcetypestep.fits after it goes
            # through the next source_type step.
            seg.meta.filename = segment_basename_list[segment] + '_badpixinterp.fits'
            seg.write(outdir + '/' + seg.meta.filename)
            print('soss_correct_badpix - saving ', seg.meta.filename)
            hdu = fits.PrimaryHDU(badpix_segment)
            hdu.writeto(outdir + '/' + segment_basename_list[segment] + '_badpixelmask.fits', overwrite=True)
        else:
            # still have to save it because can't return the list of opened datamodel
            # segments
            print('soss_correct_badpix - Only option is to save outputs. save_results must be True')
            seg.meta.filename = segment_basename_list[segment] + '_badpixinterp.fits'
            seg.write(outdir + '/' + seg.meta.filename)
            print('soss_correct_badpix - saving ', seg.meta.filename)
            hdu = fits.PrimaryHDU(badpix_segment)
            hdu.writeto(outdir + '/' + segment_basename_list[segment] + '_badpixelmask.fits', overwrite=True)
            outfiles.append(outdir + '/' + seg.meta.filename)

        # TODO: Loic, erase the temporary block files from disk once this step has
        #  been debugged

    return outfiles

def badpixel_flag_seconderivative(data, outdir, ddx2_nsigma=10, ddy2_nsigma=10):

    '''
    Accepts a cube of data (nints, dimy, dimx) and returns a cube of same size
    with 0 for good pixels, 1 for bad pixels.
    '''

    # Expect data to be 3-dimensional (integrations, y, x)
    nint, dimy, dimx = np.shape(data)

    # Initialize the corrected data
    # data_corr = data * 1
    # Initialize the array of bad pixel flags
    flags = data*0
    # make sure there is no NaN, if so flag them as bad pixels
    flags[~np.isfinite(flags)] = 1

    # Compute the second derivative in x and y for all integrations at once
    ddx = np.gradient(data, axis=-1)
    ddx2 = -np.gradient(ddx, axis=-1)
    ddy = np.gradient(data, axis=-2)
    ddy2 = -np.gradient(ddy, axis=-2)
    # Compute the median and median deviation along the integrations axis
    ddx2_med = np.median(ddx2, axis=0)
    ddx2_mdv = mediandev(ddx2, axis=0)
    ddy2_med = np.median(ddy2, axis=0)
    ddy2_mdv = mediandev(ddy2, axis=0)
    # Smooth a little the scatter map to make bad pixels wash out from the
    # stats
    ddx2_med = medfilt2d(ddx2_med, kernel_size=3)
    ddx2_mdv = medfilt2d(ddx2_mdv, kernel_size=3)
    ddy2_med = medfilt2d(ddy2_med, kernel_size=3)
    ddy2_mdv = medfilt2d(ddy2_mdv, kernel_size=3)

    # Identify 5-sigma outliers as bad pixels then interpolate to correct
    for i in range(nint):
        ddx2_nsig = np.abs((ddx2[i] - ddx2_med)) / ddx2_mdv
        ddy2_nsig = np.abs((ddy2[i] - ddy2_med)) / ddy2_mdv
        # Use 5 sigma as threshold because a normal distribution
        # yields less than 1 such random outlier for 2048x256 pixels
        badpixels = (ddx2_nsig > ddx2_nsigma) & (ddy2_nsig > ddy2_nsigma)
        flags[i][badpixels] = 1
        if i == 3:
            print('ddx2_nsigma = ', ddx2_nsigma)
            print('ddy2_nsigma = ', ddy2_nsigma)
            hdu = fits.PrimaryHDU([data[i], flags[i], ddx2_nsig, ddx2_med, ddx2_mdv, ddy2_nsig, ddy2_med, ddy2_mdv])
            #outdir = '/Users/albert/NIRISS/sossisse/sossisse/sossiopath/JWST.NIRISS.SOSS/01201_101/loic_processing'
            #outdir = self.tparams['PATHS.TEMP_PATH']
            #TODO: instead of passing outdir to this function, can it get it itself?
            hdu.writeto(outdir + '/toto_secondderivatives.fits', overwrite=True)

    return flags



def interpolate_badpixels_cubic(image3D, flag3D, outdir, integ_halfwidth=4):
    '''
    Squeeze the integ_halfwidth*2+1 integrations into a 2D median of higher SNR.
    Then interpolate the bad pixels using that median.

    flag3D is 0 for good pixels, 1 or more for bad pixels
    '''

    image3Dcorr = np.copy(image3D)

    nint = np.shape(image3D)[0]

    for i in range(nint):
        print(
            'interpolate_badpixels_cubic - integration {:} of {:}'.format(i + 1,
                                                                          nint))
        # Determine the integration indices to retain in the medianing
        imin = max([0, i - integ_halfwidth])
        imax = min([nint - 1, i + integ_halfwidth])
        icur = i - imin

        # Create temporary cubes for only the nearby integrations
        data = image3D[imin:imax + 1, :, :] * 1
        goodpix = flag3D[imin:imax + 1, :, :] * 1
        datacorr = np.copy(data)

        # Make sure that the data has all bad pixels set to NaN
        data[~(goodpix == 0)] = np.nan

        # Create a high SNR representative integration centered on the current integration
        integ_median = np.nanmedian(data, axis=0)
        print(
            'interpolate_badpixels_cubic - number of NaNs in the image to interpolate from',
            (~np.isfinite(integ_median)).sum())

        # Expect a tuple of 2 x 1D arrays for the good pixels
        # usually obyained points = np.where(np.isfinite(im))
        # points (pairs of x,y)
        points = np.where(np.isfinite(integ_median))
        values = integ_median[points]

        badpix_y, badpix_x = np.where(~np.isfinite(integ_median))

        val_best = griddata(points, values, (badpix_y, badpix_x),
                            method='cubic')
        # Replace bad pixels by best interpolation method (cubic)
        # If some NaNs remain, replace using the back up method (nearest)
        if (~np.isfinite(val_best)).sum() >= 1:
            # Interpolation using the method nearest that works all the time
            val_safe = griddata(points, values, (badpix_y, badpix_x),
                                method='nearest')
            ind = np.where(~np.isfinite(val_best))
            toto = val_best * 1
            toto[ind] = val_safe[ind] * 1
            print(
                'interpolate_badpixels_cubic - remaining number of bad pixels after griddata correction:',
                (~np.isfinite(val_best)).sum())
            datacorr[icur, badpix_y, badpix_x] = toto * 1
        else:
            print(
                'interpolate_badpixels_cubic - no NaN remaining after griddata correction')
            print(val_best)
            datacorr[icur, badpix_y, badpix_x] = val_best * 1

        print(
            'interpolate_badpixels_cubic - remaining number of bad pixels in the end: ',
            (~np.isfinite(datacorr[icur, :, :])).sum())

        image3Dcorr[i] = datacorr[icur] * 1

    del data, datacorr, goodpix, badpix_y, badpix_x

    # TODO: Loic, padd the blocks to prevent border effects

    return image3Dcorr




def get_spectrace(infiles: list):

    import asdf
    from jwst.extract_1d import Extract1dStep

    # Use the first integration in the list as the data model
    model = infiles[0]

    # Instantiate the extract1d step (absolutely needed for the rest to work)
    step = Extract1dStep()

    # Get the most appropriate reference file name for this data model
    #specprofile_name = step.get_reference_file(model,'specprofile')
    pastasoss_name = step.get_reference_file(model,'pastasoss')

    # Open the pastasoss reference file and find the x, y, throughput info
    pastasoss_name = step.get_reference_file(model, "pastasoss")
    ref = datamodels.open(pastasoss_name)

    spectrace = {
        'x_o1': ref.traces[0].trace[:,0],
        'x_o2': ref.traces[1].trace[:,0],
        'x_o3': ref.traces[2].trace[:,0],
        'y_o1': ref.traces[0].trace[:,1],
        'y_o2': ref.traces[1].trace[:,1],
        'y_o3': ref.traces[2].trace[:,1],
        'wave_o1': ref.throughputs[0].wavelength,
        'wave_o2': ref.throughputs[1].wavelength,
        'wave_o3': ref.throughputs[2].wavelength,
        'throughput_o1': ref.throughputs[0].throughput,
        'throughput_o2': ref.throughputs[1].throughput,
        'throughput_o3': ref.throughputs[2].throughput
    }

    return spectrace


def mediandev(x, axis=None):
    med = np.nanmedian(x, axis=axis)

    return np.nanmedian(np.abs(x - med), axis=axis) / 0.67449

def stack_multisegments(segment_list, outdir=None, save_results=True,
                        stack_nblocks=None):
    '''
    Produces a deep stack of all integrations across all segments of a SOSS TSO.
    Does so by processing on blocks of columns rather than full data set to
    limit memory usage. Assumes that the input segments are 4-dimensional, i.e.
    they have not been through the ramp fitting step yet.

    :param segment_list: list[str], list of segments to stack
    :param outdir: str, path to output directory
    :param save_results: bool, whether to save results to file
    :param stack_nblocks: int, number of column blocks to divide the images into
    for processing

    :return: array, the stacked image which is a median of all integrations.
    '''

    if stack_nblocks == None:
        # any divider of 2048 would do
        # Number of blocks depends on number of segments but also subarray size
        seg = datamodels.open(segment_list[0])
        if seg.meta.subarray.name == 'FULL':
            nblocks = np.size(segment_list) * 2 * 8
        elif seg.meta.subarray.name == 'SUBSTRIP256':
            nblocks = np.size(segment_list) * 2
        elif seg.meta.subarray.name == 'SUBSTRIP96':
            nblocks = np.size(segment_list) * 2
        else:
            print('SUBARRAY is not supported. Try something.')
            nblocks = np.size(segment_list)*2
    else:
        nblocks = np.copy(stack_nblocks)
    #nblocks = 2  # any divider of 2048 would do
    #blocksize = 2048 // nblocks
    blocksize = int(np.ceil(2048 / nblocks)) # no need for common divider of 2048

    print('1/f stacking of all {:} segments in the time-series in {:} blocks of {:} columns'.format(
        np.size(segment_list), nblocks, blocksize))

    for b in range(nblocks):
        print('Block {:}'.format(b+1))
        # Set the x-axis limits of this block of columns
        firstcol, lastcol = b * blocksize, (b + 1) * blocksize
        # Check that the last column is never above 2048
        lastcol = np.min([2048, lastcol])
        currentblocksize = lastcol - firstcol
        print('Curent block is between firstcol={:} and lastcol={:} and has size of {:} columns'.format(
            firstcol, lastcol, currentblocksize))

        # For each block of columns, loop over all segments
        for segment in range(np.size(segment_list)):
            # Fill the data cube and groupdq cube for block b
            seg = datamodels.open(segment_list[segment])
            i_start, i_end = seg.meta.exposure.integration_start, seg.meta.exposure.integration_end
            if (i_start == None) & (i_end == None):
                # it means that this is a time-series NOT split into segments
                i_start, i_end = 1, seg.meta.exposure.nints
            print('i_start = {:}, i_end = {:}'.format(i_start, i_end))
            if segment == 0:
                # First segment, initialize cubes of proper size
                _, ngroups, dimy, dimx = np.shape(seg.data)
                nints = seg.meta.exposure.nints
                data = np.zeros((nints, ngroups, dimy, currentblocksize)) * np.nan
                mask = np.zeros((nints, ngroups, dimy, currentblocksize)) * np.nan
            # the current segment data, group DQ and pixel DQ
            data[i_start-1:i_end, :, :, :] = np.copy(seg.data[:, :, :, firstcol:lastcol])
            gdq = np.copy(seg.groupdq[:, :, :, firstcol:lastcol])
            pdq = np.copy(seg.pixeldq[:, firstcol:lastcol])
            # Add to the mask the group dq (4 dimensional)
            segmask = np.where(gdq != 0, np.nan, 1)
            mask[i_start-1:i_end, :, :, :] = np.copy(segmask)
            # Add to the mask the pixel dq (2 dimensional)
            segmask = np.where(pdq != 0, np.nan, 1)
            mask[i_start-1:i_end, :] = mask[i_start-1:i_end, :] * segmask

        # Stack that block, all bad pixels are NaNs
        if b == 0:
            # First block, initialize the final products with proper size
            deepstack = np.zeros((ngroups, dimy, dimx)) * np.nan
            rms = np.zeros((ngroups, dimy, dimx)) * np.nan
        block_stack = np.nanmedian(data * mask, axis=0)
        block_rms = mediandev(data * mask - block_stack, axis=0)
        deepstack[:, :, firstcol:lastcol] = np.copy(block_stack)
        rms[:, :, firstcol:lastcol] = np.copy(block_rms)

        # retain the program ID and observation number for output filename
        pid = seg.meta.observation.program_number
        obsnbr = seg.meta.observation.observation_number

        del seg, segmask, gdq, pdq
        del data, mask, block_stack

    if save_results:
        # Recover names and directory
        segment1name = segment_list[0]
        if outdir == None:
            # get parameters from params
            # datadir = self.tparams['PATHS.TEMP_PATH'] DOESN'T WORK, loic_niriss not a class
            datadir = '/Users/albert/Downloads/'
        # Name of this TSO forged from its PID and observation number
        #basename = os.path.basename(os.path.splitext(segment1name)[0])
        #basename_ts = tsobasename(segment1name)
        basename_ts = pid+obsnbr
        # Save as fits files
        deepstackname = datadir+'/deepstack_1of_'+basename_ts+'.fits'
        rmsname = datadir+'/deepstack_1of_rms_'+basename_ts+'.fits'

        hdu = fits.PrimaryHDU(deepstack)
        hdu.writeto(deepstackname, overwrite=True)
        hdu = fits.PrimaryHDU(rms)
        hdu.writeto(rmsname, overwrite=True)

    return deepstackname





def loic_group_scale_step(self, infiles: list) -> list:
    """
    Scale group data to account for on-chip amplifier effects.

    :param infiles: list[str], list of input files
    :return: list[str], list of output files
    """
    # set function name
    func_name = f"{__NAME__}.JWST.loic_group_scale_step"
    # get params from step constant
    run_step, flavour, kwargs, suffix = self.from_step_args(func_name)
    # deal with skipping step
    run_step, infiles = self.skip_step(
        run_step, 'GROUP_SCALE_STEP', suffix, infiles)
    # deal with not running this step
    if not run_step:
        return infiles
    # get parameters from params
    datadir = self.tparams['PATHS.TEMP_PATH']
    # storage for output files
    outfiles = []
    # loop around infiles
    for it, filename in enumerate(infiles):

        # =====================================================================
        # NOTE: THIS IS THE BIT TO CHANGE
        # =====================================================================

        # Read input segments files from disk
        input_data = fits.getdata(filename)

        # do something with the data
        output_data = input_data * GROUP_SCALE_SIZE

        # construct output filename
        output_filename = filename.replace('.fits', '_scaled.fits')


        # =====================================================================
        # Don't change anything else here (other than writing to file line)
        # =====================================================================
        # get output path
        outfile = self.get_output_path(it, datadir, output_filename)

        # write output file to disk in the correct output directory
        fits.writeto(outfile, output_data, overwrite=True)

        # To limit disk usage, erase the file from the previously saved step
        self.remove_intermediate_files(filename)

        outfiles.append(outfile)

    return outfiles


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # print 'Hello World!'
    print("Hello World!")
    print("To run, type at the command line in the proper conda environment, for example:")
    print("pogos_run --yamlfile DEMO_T1b.20220718.JWST.NIRISS.SOSS.TSOVORE.yaml")

# =============================================================================
# End of code
# =============================================================================

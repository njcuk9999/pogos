#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2026-01-29 at 11:50

@author: cook
"""
from astropy.io import fits


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

# =============================================================================
# End of code
# =============================================================================

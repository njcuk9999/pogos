#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2025-10-31 at 10:57

@author: cook
"""
import os

import numpy as np
from astropy.table import Table

from aperocore.constants.param_functions import ParamDict
from aperocore.core import drs_log
from aperocore.core import drs_misc
from pogos.core import base
from pogos.core import io as pogos_io
from pogos.miriam.core import base as mc_base

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


# =============================================================================
# Define functions
# =============================================================================
def write_photometry_results(params: ParamDict, ptbl0: Table,
                             ptbl1: Table) -> ParamDict:
    # get output directory
    tmp_dir = params.get('MIRIAM.PATHS.TEMP_PATH')


    output_fits = None

    # loop around the two tables
    for d2flag, ptbl in zip([True, False], [ptbl0, ptbl1]):
        # construct output filename
        output_fits = os.path.join(tmp_dir, 'miriam_photometry{0}.fits')
        output_rdb = os.path.join(tmp_dir, 'miriam_photometry{0}.rdb')

        if d2flag:
            output_fits = output_fits.format('_d2flag')
            output_rdb = output_rdb.format('_d2flag')
        else:
            output_fits = output_fits.format('')
            output_rdb = output_rdb.format('')

        # print progress
        msg = f'Writing photometry results to: {output_fits}'
        WLOG(params, '', msg)
        # write fits file
        ptbl.write(output_fits, format='fits', overwrite=True)
        # print progress
        msg = f'Writing photometry results to: {output_rdb}'
        WLOG(params, '', msg)
        # write rdb file
        ptbl.write(output_rdb, format='ascii.rdb', overwrite=True)

    # Create SOSSISSE-like output
    wlc_file = out_wlc_file(params, ptbl0)

    # Create the Eureka-like output
    eureka_file = save_eureka(params, ptbl0)

    # output ParamDict
    outputs = ParamDict()
    outputs['wlc_file'] = wlc_file
    outputs['eureka'] = eureka_file

    return outputs


def out_wlc_file(params: ParamDict, ptbl: Table) -> str:
    """
    Write the white light curve file in fits format (similar to SOSSISSE)

    :param params: ParamDict, parameter dictionary
    :param ptbl: Table, photometry table

    :return: str, the filename of the written white light curve fits file
    """
    # get the output directory
    output_dir = params.get('MIRIAM.PATHS.OUTPUT_PATH')
    # get columns names to keep
    rtable = Table()
    rtable['Time'] = ptbl['int_start_BJD_TDB']
    rtable['RelFlux'] = ptbl['amps']
    rtable['RelFlux_Err'] = ptbl['amps_err']
    rtable['Centroid_X'] = ptbl['cent_x']
    rtable['Centroid_Y'] = ptbl['cent_y']
    # generate the param snapshot table
    psnapshot = params.snapshot_table(include_zero_counts=True)
    # -------------------------------------------------------------------------
    # storage for fits data writing
    datalist = []
    datatypes = []
    datanames = []
    # push into data list
    datalist.append(rtable)
    datatypes.append('table')
    datanames.append(f'WLC_TABLE')
    # add the param table
    datalist.append(psnapshot)
    datatypes.append('table')
    datanames.append('PARAMS')
    # -------------------------------------------------------------------------
    # Add header keys
    meta_data = dict()
    meta_data['POGOS_EM'] = ('MIRAM', 'POGOS extraction module')
    meta_data['POGOS_V'] = (base.__version__, 'POGOS Version')
    meta_data['POGOS_EV'] = (base.MIRIAM_VERSION, 'POGOS extraction version')
    # -------------------------------------------------------------------------
    # construct the fits filename
    filename = os.path.join(output_dir, 'white_light_curve.fits')
    # save the fits file
    pogos_io.save_fits(params, filename, datalist=datalist,
                       datatypes=datatypes, datanames=datanames,
                       meta=meta_data)
    # --------------------------------------------------------------------------
    # return the filename
    return filename


def save_eureka(params: ParamDict, ptbl: Table) -> str:
    """
    Save the white light curve in Eureka format (h5)

    :param params: ParamDict, parameter dictionary
    :param ptbl: Table, photometry table

    :return: str, the filename of the written white light curve h5 file
    """
    # set function name
    func_name = __NAME__ + '.save_eureka()'

    # get the output directory
    output_dir = params.get('MIRIAM.PATHS.OUTPUT_PATH')
    # -------------------------------------------------------------------------
    # construct the fits filename
    filename = os.path.join(output_dir, 'white_light_curve.h5')
    # -------------------------------------------------------------------------
    # attempt to install astraeus package
    try:
        from astraeus import xarrayIO as xrio
    except ImportError:
        emsg = ('Please install the astraeus package manually to use '
                f'"{func_name}" with the following: \n'
                'pip install git+https://github.com/kevin218/Astraeus.git')
        raise mc_base.MiriamException(emsg)
    # -------------------------------------------------------------------------
    # flux and flux_error should be of shape time x wavelength
    # wavelength should be in descending order (and in microns)
    # time in BJD_TBD
    # outfile is the name you want to save your file as
    # -------------------------------------------------------------------------
    # make h5 data set
    outdata = xrio.makeDataset()
    # add the time array
    outdata['time'] = np.array(ptbl['int_start_BJD_TDB'])
    outdata['aplev'] = np.array(ptbl['amps'])
    outdata['aperr'] = np.array(ptbl['amps_err'])
    outdata['centroid_x'] = np.array(ptbl['cent_x'])
    outdata['centroid_y'] = np.array(ptbl['cent_y'])
    # -------------------------------------------------------------------------
    # write file
    xrio.writeXR(filename, outdata, verbose=False)
    # -------------------------------------------------------------------------
    return filename


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

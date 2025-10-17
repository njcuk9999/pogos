#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2025-10-17 at 13:22

@author: cook
"""
import string
import os
import numpy as np
from astropy.table import Table
from typing import Tuple


from aperocore.constants.param_functions import ParamDict
from aperocore.core import drs_log
from aperocore.core import drs_misc
from pogos.core import base
from pogos.core import general as pogos_general
from pogos.miriam.core import base as miriam_base
from sossisse.core import misc
from pogos.miriam.core import general as mc_general


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
def merge_inputs(params: ParamDict) -> Tuple[np.ndarray, np.ndarray,
                                             Table, np.ndarray]:

    # TODO: remove placeholder
    cube = np.array([])
    cube_err = np.array([])
    mtbl = Table()
    weights = np.array([])

    return cube, cube_err, mtbl. weights


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

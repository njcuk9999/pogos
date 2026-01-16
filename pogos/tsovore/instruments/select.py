#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2024-08-13 at 11:25

@author: cook
"""
from typing import Any, Dict

from aperocore.constants import param_functions

from pogos.core import base as pogos_base
from pogos.tsovore.core import base as ts_base
from pogos.tsovore.instruments import default as ts_default

from pogos.tsovore.instruments import miri as ts_miri

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'tsovore.instruments.select'
__version__ = pogos_base.__version__
__date__ = pogos_base.__date__
__authors__ = pogos_base.__authors__
# Get parameter dictionary
ParamDict = param_functions.ParamDict

# =============================================================================
# Define instruments
# =============================================================================
INSTRUMENTS = dict()
# -----------------------------------------------------------------------------
# add instrument classes here
# -----------------------------------------------------------------------------
# JWST MIRI IMAGING
INSTRUMENTS['JWST.MIRI.IMAGING'] = ts_miri.MiriImaging


# check that instrument/mode is in base instruments list
for instrument in INSTRUMENTS.keys():
    if instrument not in pogos_base.INSTRUMENTS:
        emsg = 'Instrument "{}" must be in base.INSTRUMENTS'
        eargs = ['instruments']
        raise ts_base.TSOvoreException(emsg.format(*eargs))


# =============================================================================
# Define functions
# =============================================================================
def load_instrument(params: ParamDict) -> ts_default.JWST:
    """
    Load the instrument class

    :param params: dict, the parameters for the instrument
    :return: the instrument class
    """
    instrument_mode = params['TSOVORE.INPUTS.INSTRUMENTMODE']
    # if we have the instrument return it
    if instrument_mode in INSTRUMENTS:
        return INSTRUMENTS[instrument_mode](params)
    else:
        emsg = 'Instrument mode "{0}" not recognised'
        eargs = [instrument_mode]
        raise ts_base.TSOvoreException(emsg.format(*eargs))


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

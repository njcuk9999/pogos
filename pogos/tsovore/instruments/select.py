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
from pogos.tsovore.instruments import niriss as ts_niriss
from pogos.tsovore.instruments import nirspec as ts_nirspec
from pogos.tsovore.instruments import nircam as ts_nircam

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
# JWST NIRISS
INSTRUMENTS['JWST.NIRISS.SOSS'] = ts_niriss.NirissSoss
# INSTRUMENTS['JWST.NIRISS.SOSS.SUPERSTRIPE'] = ts_niriss.NirissSossSuperstripe

# JWST NIRSPEC
INSTRUMENTS['JWST.NIRSPEC.BOTS.PRISM'] = ts_nirspec.NirspecBotsPrism
INSTRUMENTS['JWST.NIRSPEC.BOTS.G395M'] = ts_nirspec.NirspecBotsMedium
INSTRUMENTS['JWST.NIRSPEC.BOTS.G235M'] = ts_nirspec.NirspecBotsMedium
INSTRUMENTS['JWST.NIRSPEC.BOTS.G140M'] = ts_nirspec.NirspecBotsMedium
INSTRUMENTS['JWST.NIRSPEC.BOTS.G395H'] = ts_nirspec.NirspecBotsHigh
INSTRUMENTS['JWST.NIRSPEC.BOTS.G235H'] = ts_nirspec.NirspecBotsHigh
INSTRUMENTS['JWST.NIRSPEC.BOTS.G140H'] = ts_nirspec.NirspecBotsHigh

# JWST NIRCam
INSTRUMENTS['JWST.NIRCAM.IMAGING'] = ts_nircam.NircamImaging
INSTRUMENTS['JWST.NIRCAM.WFSS'] = ts_nircam.NircamGrism
# INSTRUMENTS['JWST.NIRCAM.MULTISTRIPE'] = ts_nircam.NircamMultistripe

# JWST MIRI
INSTRUMENTS['JWST.MIRI.IMAGING'] = ts_miri.MiriImaging
INSTRUMENTS['JWST.MIRI.LRS'] = ts_miri.MiriLrs


# check that instrument/mode is in base instruments list
for instrument in INSTRUMENTS.keys():
    if instrument not in pogos_base.INSTRUMENTS:
        emsg = 'Instrument "{}" must be in base.INSTRUMENTS'
        eargs = [instrument]
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

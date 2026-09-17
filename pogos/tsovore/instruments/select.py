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
from pogos.core import definitions
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
INSTRUMENTS[definitions.NIRISS_SOSS] = ts_niriss.NirissSoss
# INSTRUMENTS['JWST.NIRISS.SOSS.SUPERSTRIPE'] = ts_niriss.NirissSossSuperstripe

# JWST NIRSPEC
INSTRUMENTS[definitions.NIRSPEC_BOTS_PRISM] = ts_nirspec.NirspecBotsPrism
INSTRUMENTS[definitions.NIRSPEC_BOTS_G395M] = ts_nirspec.NirspecBotsMedium
INSTRUMENTS[definitions.NIRSPEC_BOTS_G235M] = ts_nirspec.NirspecBotsMedium
INSTRUMENTS[definitions.NIRSPEC_BOTS_G140M] = ts_nirspec.NirspecBotsMedium
INSTRUMENTS[definitions.NIRSPEC_BOTS_G395H] = ts_nirspec.NirspecBotsHigh
INSTRUMENTS[definitions.NIRSPEC_BOTS_G235H] = ts_nirspec.NirspecBotsHigh
INSTRUMENTS[definitions.NIRSPEC_BOTS_G140H] = ts_nirspec.NirspecBotsHigh

# JWST NIRCam
INSTRUMENTS[definitions.NIRCAM_IMAGING] = ts_nircam.NircamImaging
INSTRUMENTS[definitions.NIRCAM_WFSS] = ts_nircam.NircamGrism
# INSTRUMENTS['JWST.NIRCAM.MULTISTRIPE'] = ts_nircam.NircamMultistripe

# JWST MIRI
INSTRUMENTS[definitions.MIRI_IMAGING] = ts_miri.MiriImaging
INSTRUMENTS[definitions.MIRI_LRS] = ts_miri.MiriLrs


# check that instrument/mode is in base instruments list
for instrument_mode in INSTRUMENTS:
    if instrument_mode not in definitions.INST_MODES:
        emsg = 'Instrument mode "{}" is not a registered InstMode'
        raise ts_base.TSOvoreException(emsg.format(instrument_mode.name))


# =============================================================================
# Define functions
# =============================================================================
def load_instrument(params: ParamDict) -> ts_default.JWST:
    """
    Load the instrument class

    :param params: dict, the parameters for the instrument
    :return: the instrument class
    """
    instrument_name = params['TSOVORE.INPUTS.INSTRUMENTMODE']
    instrument_mode = definitions.MODE_BY_NAME.get(instrument_name)
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

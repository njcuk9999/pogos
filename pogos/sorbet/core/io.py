#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# sorbet.core.io.py

# utils function for compatibility with SORBET

Created on 2025-02-19 at 13:04

@author: cook, CharlesCadieux
"""

from aperocore.core import drs_misc
from aperocore.core import drs_log

from pogos.core import base

from typing import Union, List


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'pogos.sorbet.core.io'
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
def convert_to_number(
    value: Union[str, List[Union[str, float, int]], float, int]
) -> Union[float, List[Union[float, None]], int]:
    """
    Convert a string or a list of strings from the yaml config file to a float 
    or a list of floats.

    :param value: str, list of str, float, or int
    :return: Converted float, list of floats, or int
    """
    if isinstance(value, str):  # Convert string to float
        return float(value)
    elif isinstance(value, list):  # Convert list of strings to floats
        return [
            float(v) if isinstance(v, str)
            else v if isinstance(v, (float, int))
            else None
            for v in value
        ]
    elif isinstance(value, (float, int)):  # Ensure value is a float or an int
        return value
    else:
        raise TypeError("Value must be of type str, list of str, float, or int")


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
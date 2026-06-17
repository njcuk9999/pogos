#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2024-10-29 at 09:30

@author: cook
"""
import os
import re
from typing import Any, Optional, Tuple, Type, Union

from aperocore.constants import constant_functions

from pogos.core import base


try:
    import eureka

    from eureka.S1_detector_processing import S1MetaClass

except ImportError:
    emsg = 'Please install Eurkea'
    raise base.PogosException(emsg)

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'pogos.eureka_wrap.constants.eureka_ecf.py'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__

# Constants definition
Const = constant_functions.Const
ConstDict = constant_functions.ConstantsDict

# JWST Eureka ecfs
DEMO_URL = 'https://github.com/kevin218/Eureka/tree/main/demos/JWST'

# Define which S1 ecf files go to which instrument
S1_FILES = dict()
S1_FILES['JWST.NIRISS.SOSS'] = 'nirx_template'
# S1_FILES['JWST.NIRISS.SOSS.SUPERSTRIPE'] = 'nirx_template'
S1_FILES['JWST.NIRISS.FGS'] = None
S1_FILES['JWST.NIRSPEC.BOTS.PRISM'] = 'nirx_template'
S1_FILES['JWST.NIRSPEC.BOTS.G395M'] = 'nirx_template'
S1_FILES['JWST.NIRSPEC.BOTS.G235M'] = 'nirx_template'
S1_FILES['JWST.NIRSPEC.BOTS.G140M'] = 'nirx_template'
S1_FILES['JWST.NIRSPEC.BOTS.G395H'] = 'nirx_template'
S1_FILES['JWST.NIRSPEC.BOTS.G235H'] = 'nirx_template'
S1_FILES['JWST.NIRSPEC.BOTS.G140H'] = 'nirx_template'
S1_FILES['JWST.NIRCAM.IMAGING'] = None
S1_FILES['JWST.NIRCAM.WFSS'] = 'nirx_template'
# S1_FILES['JWST.NIRCAM.MULTISTRIPE'] = 'nirx_template'
S1_FILES['JWST.MIRI.IMAGING'] = None
S1_FILES['JWST.MIRI.LRS'] = 'miri_template'

# Define which S2 ecf files go to which instrument
S2_FILES = dict()
S2_FILES['JWST.NIRISS.SOSS'] = 'niriss_soss'
# S2_FILES['JWST.NIRISS.SOSS.SUPERSTRIPE'] = 'nirx_template'
S2_FILES['JWST.NIRISS.FGS'] = None
S2_FILES['JWST.NIRSPEC.BOTS.PRISM'] = 'nirspec_fs_template'
S2_FILES['JWST.NIRSPEC.BOTS.G395M'] = 'nirspec_fs_template'
S2_FILES['JWST.NIRSPEC.BOTS.G235M'] = 'nirspec_fs_template'
S2_FILES['JWST.NIRSPEC.BOTS.G140M'] = 'nirspec_fs_template'
S2_FILES['JWST.NIRSPEC.BOTS.G395H'] = 'nirspec_fs_template'
S2_FILES['JWST.NIRSPEC.BOTS.G235H'] = 'nirspec_fs_template'
S2_FILES['JWST.NIRSPEC.BOTS.G140H'] = 'nirspec_fs_template'
S2_FILES['JWST.NIRCAM.IMAGING'] = 'imaging_template'
S2_FILES['JWST.NIRCAM.WFSS'] = 'nircam_wfss_template'
# S2_FILES['JWST.NIRCAM.MULTISTRIPE'] = 'nirx_template'
S2_FILES['JWST.MIRI.IMAGING'] = 'imaging_template'
S2_FILES['JWST.MIRI.LRS'] = 'miri_lrs_template'

# Define which S3 ecf files go to which instrument
S3_FILES = dict()
S3_FILES['JWST.NIRISS.SOSS'] = 'niriss_soss'
# S3_FILES['JWST.NIRISS.SOSS.SUPERSTRIPE'] = 'nirx_template'
S3_FILES['JWST.NIRISS.FGS'] = None
S3_FILES['JWST.NIRSPEC.BOTS.PRISM'] = 'nirspec_fs_template'
S3_FILES['JWST.NIRSPEC.BOTS.G395M'] = 'nirspec_fs_template'
S3_FILES['JWST.NIRSPEC.BOTS.G235M'] = 'nirspec_fs_template'
S3_FILES['JWST.NIRSPEC.BOTS.G140M'] = 'nirspec_fs_template'
S3_FILES['JWST.NIRSPEC.BOTS.G395H'] = 'nirspec_fs_template'
S3_FILES['JWST.NIRSPEC.BOTS.G235H'] = 'nirspec_fs_template'
S3_FILES['JWST.NIRSPEC.BOTS.G140H'] = 'nirspec_fs_template'
S3_FILES['JWST.NIRCAM.IMAGING'] = 'nircam_photometry_template'
S3_FILES['JWST.NIRCAM.WFSS'] = 'nircam_wfss_template'
# S3_FILES['JWST.NIRCAM.MULTISTRIPE'] = 'nirx_template'
S3_FILES['JWST.MIRI.IMAGING'] = 'miri_photometry_template'
S3_FILES['JWST.MIRI.LRS'] = 'miri_lrs_template'


# =============================================================================
# Define functions
# =============================================================================
def get_all_ecf():
    pass


def _ecf_group_name(text: str) -> str:
    """Convert a section-header comment to an uppercase group key."""
    return re.sub(r'[^A-Z0-9]+', '_', text.upper()).strip('_')


def _parse_ecf_value(value_str: str) -> Tuple[Any, Optional[Union[Type, str]]]:
    """Parse a raw ECF value string, returning (value, dtype)."""
    # quoted string → str
    if (len(value_str) >= 2
            and value_str[0] in ('"', "'")
            and value_str[-1] == value_str[0]):
        return value_str[1:-1], str
    # booleans
    if value_str == 'True':
        return True, bool
    if value_str == 'False':
        return False, bool
    # None
    if value_str in ('None', 'null', 'NONE'):
        return None, None
    # file path
    if value_str.startswith('/'):
        return value_str, 'path'
    # int
    try:
        return int(value_str), int
    except ValueError:
        pass
    # float
    try:
        return float(value_str), float
    except ValueError:
        pass
    # fallback: plain string
    return value_str, str


def _parse_ecf_options(description: Optional[str]) -> Optional[list]:
    """Extract an options list from a comment like \"Options are 'a', 'b'\"."""
    if description is None:
        return None
    if 'options are' in description.lower():
        opts = re.findall(r"'([^']*)'", description)
        return opts if opts else None
    return None


def interpret_ecf(filename: str) -> ConstDict:
    """Read a Eureka! ECF file and return a populated ConstantsDict.

    Each data line ``name   value  # comment`` becomes a Const with:
      - ``name``  : first whitespace-delimited token
      - ``value`` : second token, typed (bool/int/float/str/path)
      - ``dtype`` : inferred from the value
      - ``description``: inline comment text (if present)
      - ``options``: extracted when the comment contains "Options are '...'"
      - ``group`` : the most recent section-header comment (after the first
                   data variable has been seen)
    """
    with open(filename, 'r') as fh:
        lines = fh.readlines()

    cdict = ConstDict(filename)
    group_name = None
    seen_data = False  # file-header comments skipped until first data line

    for line in lines:
        line = line.rstrip()
        if not line.strip():
            continue

        # comment-only line
        if line.lstrip().startswith('#'):
            if seen_data:
                text = line.strip().lstrip('#').strip()
                if text and 'http' not in text:
                    group_name = _ecf_group_name(text)
                    cdict.add_group(group_name, description=text)
            continue

        # data line
        seen_data = True
        parts = line.split(None, 1)
        if len(parts) < 2:
            continue

        name = parts[0].strip()
        rest = parts[1].strip()

        if '#' in rest:
            value_str, comment_str = rest.split('#', 1)
            value_str = value_str.strip()
            description = comment_str.strip() or None
        else:
            value_str = rest.strip()
            description = None

        value, dtype = _parse_ecf_value(value_str)
        options = _parse_ecf_options(description)

        cdict.add(name, value=value, dtype=dtype, description=description,
                  options=options, source=filename, group=group_name,
                  user=True, active=True)

    return cdict



def get_s1_parameters(instrument_mode: str = None):
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

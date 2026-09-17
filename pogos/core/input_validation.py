#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Validation for input files after a reduction module resolves their paths."""
import os
from typing import Sequence

from pogos.core import base
from pogos.core import definitions


def _load_fits_header(filename: str):
    """Load one primary FITS header without importing Astropy at startup."""
    from astropy.io import fits
    return fits.getheader(filename, ext=0)


def check_input_data_headers(params, files: Sequence[str]):
    """
    Check resolved input FITS files against GLOBAL.INSTRUMENTMODE.

    Every filename must already be an absolute path whose existence was checked
    by the owning reduction module. Files are checked in order and validation
    stops at the first mismatch.

    :param params: POGOS parameter mapping
    :param files: ordered absolute input FITS filenames
    :return: None, raises PogosException on invalid input
    """
    mode_name = params['GLOBAL.INSTRUMENTMODE']
    mode = definitions.MODE_BY_NAME.get(mode_name)
    if mode is None or not mode.enabled:
        raise base.PogosException(f'Unsupported instrument mode: {mode_name}')
    if len(files) == 0:
        raise base.PogosException(
            f'No input files were found for {mode.name} header validation.')
    expected = mode.header_values()
    for filename in files:
        if not os.path.isabs(filename):
            raise base.PogosException(
                f'Input file must be an absolute path: {filename}')
        if not os.path.isfile(filename):
            raise base.PogosException(f'Input file does not exist: {filename}')
        try:
            header = _load_fits_header(filename)
        except Exception as error:
            emsg = f'Cannot read primary FITS header: {filename}\n{error}'
            raise base.PogosException(emsg)
        for key, accepted in expected.items():
            value = header.get(key)
            normalized = str(value).strip().upper() if value is not None else ''
            if normalized in accepted:
                continue
            expected_text = ', '.join(sorted(accepted))
            found_text = normalized if normalized else '<missing>'
            emsg = (f'Input data does not match {mode.name}\n\n'
                    f'File: {filename}\n\n'
                    f'Header: {key}={found_text}; '
                    f'expected {expected_text}.')
            raise base.PogosException(emsg)
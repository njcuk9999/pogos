from pathlib import Path

import pytest

from pogos.core import input_validation


def test_input_headers_require_resolved_absolute_paths():
    params = {'GLOBAL.INSTRUMENTMODE': 'JWST.NIRISS.SOSS'}
    with pytest.raises(Exception, match='absolute path'):
        input_validation.check_input_data_headers(params, ['relative.fits'])


def test_input_headers_check_files_in_order(tmp_path, monkeypatch):
    first = tmp_path / 'first.fits'
    second = tmp_path / 'second.fits'
    first.write_text('first')
    second.write_text('second')
    seen = []

    def load_header(filename):
        seen.append(Path(filename).name)
        grating = 'G395M' if filename == str(first) else 'G395H'
        return {'INSTRUME': 'NIRSPEC', 'DETECTOR': 'NRS1',
                'EXP_TYPE': 'NRS_BRIGHTOBJ', 'GRATING': grating}

    monkeypatch.setattr(input_validation, '_load_fits_header', load_header)
    params = {'GLOBAL.INSTRUMENTMODE': 'JWST.NIRSPEC.BOTS.G395M'}
    with pytest.raises(Exception) as excinfo:
        input_validation.check_input_data_headers(
            params, [str(first.resolve()), str(second.resolve())])
    message = str(excinfo.value)
    assert 'Input data does not match JWST.NIRSPEC.BOTS.G395M' in message
    assert f'File: {second.resolve()}' in message
    assert 'Header: GRATING=G395H; expected G395M.' in message
    assert seen == ['first.fits', 'second.fits']

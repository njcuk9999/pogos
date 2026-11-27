#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for the download cache listing / deleting of the POGOS gui
"""
import json
import os

from pogos.gui import downloads


def make_cache(root):
    """A POGOS path with one cached MAST file linked from two projects."""
    cached = root / 'downloads' / 'mast' / 'jw01366' / 'o001'
    cached.mkdir(parents=True)
    data = cached / 'jw01366001001_nis_rateints.fits'
    data.write_text('data')
    links = dict()
    for project in ['A', 'B']:
        inputs = root / 'projects' / project / 'sossisse' / 'inputs'
        inputs.mkdir(parents=True)
        link = inputs / data.name
        os.symlink(str(data), str(link))
        links[str(link)] = 'SOSSISSE.GENERAL.FILES'
    # the record written by aperocore.constants.file_sources (B unknown)
    meta = root / 'downloads' / '.meta' / 'mast' / 'jw01366' / 'o001'
    meta.mkdir(parents=True)
    del links[str(root / 'projects' / 'B' / 'sossisse' / 'inputs'
                  / data.name)]
    record = dict(source='mast', origin='jw01366 o001', product=None,
                  downloaded=123.0, links=links)
    (meta / (data.name + '.json')).write_text(json.dumps(record))
    return data


def test_list_downloads_joins_records_and_links(tmp_path):
    data = make_cache(tmp_path)
    out = downloads.list_downloads(str(tmp_path))
    assert out['nfiles'] == 1 and out['nlinks'] == 2
    item = out['files'][0]
    assert item['path'] == str(data)
    assert item['source'] == 'mast'
    # the type comes from the file name when not recorded
    assert item['product'] == 'rateints'
    assert item['downloaded'] == 123.0
    keys = {link['project']: link['key'] for link in item['links']}
    assert keys == {'A': 'SOSSISSE.GENERAL.FILES', 'B': None}


def test_delete_download_reports_broken_links(tmp_path):
    data = make_cache(tmp_path)
    out = downloads.delete_downloads(str(tmp_path), [str(data)])
    assert out['success'] and out['deleted'] == [str(data)]
    assert len(out['broken']) == 2
    assert not data.exists()
    # the record and empty directories are gone too
    assert not (tmp_path / 'downloads' / 'mast').exists()
    assert downloads.list_downloads(str(tmp_path))['nfiles'] == 0


def test_delete_refuses_files_outside_the_cache(tmp_path):
    make_cache(tmp_path)
    other = tmp_path / 'yamls.yaml'
    other.write_text('x')
    record = next((tmp_path / 'downloads' / '.meta').rglob('*.json'))
    out = downloads.delete_downloads(str(tmp_path),
                                     [str(other), str(record)])
    assert not out['success'] and len(out['errors']) == 2
    assert other.exists() and record.exists()


def test_reset_downloads_removes_everything(tmp_path):
    make_cache(tmp_path)
    out = downloads.reset_downloads(str(tmp_path))
    assert out['success'] and len(out['broken']) == 2
    assert os.listdir(str(tmp_path / 'downloads')) == []
    # project links are kept (broken) - the next run downloads again
    link = (tmp_path / 'projects' / 'A' / 'sossisse' / 'inputs'
            / 'jw01366001001_nis_rateints.fits')
    assert os.path.islink(str(link)) and not link.exists()

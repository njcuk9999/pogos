#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The download cache of a POGOS path for the POGOS gui

Online input files (source: pogos / mast, or copied from a local mirror)
are stored once in {path}/downloads/ and symlinked into the project
directories (see aperocore.constants.file_sources). Every cached file has a
json record in {path}/downloads/.meta/ with where / when it was obtained and
the parameter key behind each symlink.

This module lists the cached files with the projects / parameters using
them, and deletes cached files (which breaks those symlinks - the next run
downloads them again). It only uses the standard library so the gui stays
fast.

Created on 2026-11-27

@author: cook
"""
import json
import os
import re
import shutil
from typing import Any, Dict, List, Optional

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'pogos.gui.downloads.py'
# the download cache directory of a POGOS path (pogos.core.file_download)
DOWNLOAD_DIR = 'downloads'
# the hidden record directory (aperocore.constants.file_sources)
META_DIR = '.meta'
# the projects directory of a POGOS path
PROJECT_DIR = 'projects'
# the data type of a JWST file name e.g. jw..._nrs1_rateints.fits
PRODUCT_RE = re.compile(r'_([A-Za-z0-9]+)\.fits(\.gz)?$')
# the download sources (first directory below the cache)
SOURCES = ['pogos', 'mast']


# =============================================================================
# Define functions
# =============================================================================
def download_dir(path: str) -> str:
    """
    Get the download cache directory of a POGOS path

    :param path: str, the POGOS path

    :return: str, {path}/downloads
    """
    return os.path.join(path, DOWNLOAD_DIR)


def list_downloads(path: str) -> Dict[str, Any]:
    """
    List the cached files with the projects / parameters linking to them

    :param path: str, the POGOS path

    :return: dict(path, files, nfiles, size, nlinks) - each file is
             dict(path, rel, name, size, mtime, source, origin, product,
             downloaded, links) and each link dict(path, key, project)
    """
    root = download_dir(path)
    out = dict(path=root, files=[], nfiles=0, size=0, nlinks=0)
    if not os.path.isdir(root):
        return out
    # the symlinks into the cache found in the projects (the truth)
    found = _scan_project_links(path, root)
    for full in _cached_files(root):
        try:
            info = os.stat(full)
        except OSError:
            continue
        rel = os.path.relpath(full, root)
        meta = _read_meta(root, full)
        real = os.path.realpath(full)
        # links: recorded ones that still point here + any found
        links = dict()
        for link, key in (meta.get('links') or dict()).items():
            if _links_to(link, real):
                links[link] = key
        for link in found.get(real, []):
            links.setdefault(link, None)
        link_list = [dict(path=link, key=key,
                          project=_project_of(path, link))
                     for link, key in sorted(links.items())]
        first = rel.split(os.sep)[0]
        out['files'].append(dict(
            path=full, rel=rel, name=os.path.basename(full),
            size=info.st_size, mtime=info.st_mtime,
            source=meta.get('source') or (first if first in SOURCES
                                          else 'unknown'),
            origin=meta.get('origin'),
            product=meta.get('product') or _product_of(full),
            downloaded=meta.get('downloaded') or info.st_mtime,
            links=link_list))
        out['size'] += info.st_size
        out['nlinks'] += len(link_list)
    out['nfiles'] = len(out['files'])
    return out


def delete_downloads(path: str, files: List[str]) -> Dict[str, Any]:
    """
    Delete cached files (and their records)

    The symlinks to them break; the next run downloads the files again.

    :param path: str, the POGOS path
    :param files: list of str, the cached files to delete

    :return: dict(success, message, deleted, broken, errors)
    """
    root = download_dir(path)
    listing = {item['path']: item for item in list_downloads(path)['files']}
    deleted, broken, errors = [], [], []
    for filename in files:
        full = os.path.abspath(str(filename))
        # only files of the cache (never the records or anything else)
        if not _inside(full, root) or _inside(full, os.path.join(root,
                                                                 META_DIR)):
            errors.append('not a downloaded file: {0}'.format(full))
            continue
        if not os.path.isfile(full) or os.path.islink(full):
            errors.append('no such downloaded file: {0}'.format(full))
            continue
        item = listing.get(full, dict(links=[]))
        try:
            os.remove(full)
        except OSError as error:
            errors.append('{0}: {1}'.format(full, error))
            continue
        meta_file = _meta_path(root, full)
        if os.path.exists(meta_file):
            os.remove(meta_file)
        # remove empty directories left behind
        _prune(os.path.dirname(full), root)
        _prune(os.path.dirname(meta_file), root)
        deleted.append(full)
        broken += [link['path'] for link in item['links']]
    message = 'Deleted {0} downloaded file(s)'.format(len(deleted))
    if broken:
        message += ' - {0} link(s) in projects are now broken'.format(
            len(broken))
    if errors:
        message += ' ({0} error(s))'.format(len(errors))
    return dict(success=not errors, message=message, deleted=deleted,
                broken=broken, errors=errors)


def reset_downloads(path: str) -> Dict[str, Any]:
    """
    Delete the whole download cache (every cached file and record)

    :param path: str, the POGOS path

    :return: dict(success, message, deleted, broken, errors)
    """
    root = download_dir(path)
    listing = list_downloads(path)
    broken = [link['path'] for item in listing['files']
              for link in item['links']]
    errors = []
    if os.path.isdir(root):
        for name in os.listdir(root):
            full = os.path.join(root, name)
            try:
                if os.path.isdir(full) and not os.path.islink(full):
                    shutil.rmtree(full)
                else:
                    os.remove(full)
            except OSError as error:
                errors.append('{0}: {1}'.format(full, error))
    message = ('Removed all downloaded data ({0} file(s)) - {1} link(s) in '
               'projects are now broken'.format(listing['nfiles'],
                                                len(broken)))
    if errors:
        message += ' ({0} error(s))'.format(len(errors))
    return dict(success=not errors, message=message,
                deleted=[item['path'] for item in listing['files']],
                broken=broken, errors=errors)


# =============================================================================
# Define worker functions
# =============================================================================
def _cached_files(root: str) -> List[str]:
    """Every cached file below root (not the records, not .part files)."""
    files = []
    for dirpath, dirs, names in os.walk(root):
        # skip the records and other hidden directories
        dirs[:] = sorted(name for name in dirs if not name.startswith('.'))
        for name in sorted(names):
            if name.startswith('.') or name.endswith('.part'):
                continue
            full = os.path.join(dirpath, name)
            if os.path.isfile(full) and not os.path.islink(full):
                files.append(full)
    return files


def _scan_project_links(path: str, root: str) -> Dict[str, List[str]]:
    """
    Find the symlinks in the projects that point into the cache

    :param path: str, the POGOS path
    :param root: str, the download cache directory

    :return: dict, cached file (real path) -> list of link paths
    """
    found: Dict[str, List[str]] = dict()
    real_root = os.path.realpath(root) + os.sep
    projects = os.path.join(path, PROJECT_DIR)
    for dirpath, _, names in os.walk(projects):
        for name in names:
            full = os.path.join(dirpath, name)
            if not os.path.islink(full):
                continue
            real = os.path.realpath(full)
            if real.startswith(real_root):
                found.setdefault(real, []).append(os.path.abspath(full))
    return found


def _meta_path(root: str, full: str) -> str:
    """The json record of a cached file (see file_sources)."""
    rel = os.path.relpath(full, root)
    return os.path.join(root, META_DIR, rel + '.json')


def _read_meta(root: str, full: str) -> Dict[str, Any]:
    """Read the json record of a cached file (empty dict if none)."""
    try:
        with open(_meta_path(root, full), 'r') as mfile:
            meta = json.load(mfile)
    except (OSError, ValueError):
        return dict()
    return meta if isinstance(meta, dict) else dict()


def _links_to(link: str, real: str) -> bool:
    """True if link is a symlink resolving to real."""
    return os.path.islink(link) and os.path.realpath(link) == real


def _project_of(path: str, link: str) -> Optional[str]:
    """The POGOS project a link belongs to (None if outside projects)."""
    projects = os.path.abspath(os.path.join(path, PROJECT_DIR)) + os.sep
    if not os.path.abspath(link).startswith(projects):
        return None
    return os.path.abspath(link)[len(projects):].split(os.sep)[0]


def _product_of(filename: str) -> Optional[str]:
    """The data type from a JWST file name (e.g. rateints)."""
    match = PRODUCT_RE.search(os.path.basename(filename))
    return match.group(1) if match else None


def _inside(full: str, root: str) -> bool:
    """True if full is strictly inside root (real paths)."""
    real_root = os.path.realpath(root) + os.sep
    return os.path.realpath(full).startswith(real_root)


def _prune(directory: str, root: str) -> None:
    """Remove empty directories from directory up to (not incl.) root."""
    root = os.path.abspath(root)
    directory = os.path.abspath(directory)
    while directory != root and directory.startswith(root + os.sep):
        try:
            os.rmdir(directory)
        except OSError:
            return
        directory = os.path.dirname(directory)


# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    print('Hello World!')

# =============================================================================
# End of code
# =============================================================================

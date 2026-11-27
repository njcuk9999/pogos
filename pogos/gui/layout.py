#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
POGOS directory layout helpers for the POGOS gui

The POGOS path (GLOBAL.DATA_PATH) holds:

    {path}/yamls/                       the yaml configuration files
    {path}/projects/{PROJECT}/{module}/  inputs / outputs / plots / ...
    {path}/pogos_gui/                    gui state (process registry,
                                         console logs, batch templates and
                                         scripts, yaml backups)

This module lists and summarises yaml files, projects and plots. It only
uses the standard library and PyYAML (no POGOS runtime) so the gui stays
fast.

Created on 2026-11-26

@author: cook
"""
import glob
import os
import re
import time
from typing import Any, Dict, List, Optional

import yaml

from aperocore.gui import files as gui_files

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'pogos.gui.layout.py'
# sub-directory names of the POGOS path
YAML_DIR = 'yamls'
PROJECT_DIR = 'projects'
STATE_DIR = 'pogos_gui'
BACKUP_DIR = 'yaml_backups'
BATCH_DIR = 'batch_scripts'
# yaml file endings
YAML_EXTS = ['.yaml', '.yml']
# header comment lines with the POGOS version / date
VERSION_RE = re.compile(r'^#\s*Version\s*=\s*(\S+)')
DATE_RE = re.compile(r'^#\s*(?:Version\s+)?Date\s*=\s*(\S+)')
# the image types shown on the plots page
PLOT_EXTS = ['.png', '.jpg', '.jpeg', '.gif', '.svg']
# a cache of yaml summaries: path -> (mtime, size, summary)
_SUMMARY_CACHE: Dict[str, Any] = dict()
# the plot description file written next to the plots (pogos / sossisse)
PLOT_INFO_FILE = 'plots.yaml'
# a cache of plot description files: path -> (mtime, blocks)
_PLOT_INFO_CACHE: Dict[str, Any] = dict()


# =============================================================================
# Define path functions
# =============================================================================
def yaml_dir(path: str) -> str:
    """
    Get the yaml directory of a POGOS path

    :param path: str, the POGOS path

    :return: str, {path}/yamls
    """
    return os.path.join(path, YAML_DIR)


def project_dir(path: str, project: Optional[str] = None) -> str:
    """
    Get the projects directory (or one project) of a POGOS path

    :param path: str, the POGOS path
    :param project: str or None, a project name

    :return: str, {path}/projects[/{project}]
    """
    if project is None:
        return os.path.join(path, PROJECT_DIR)
    return os.path.join(path, PROJECT_DIR, project)


def state_dir(path: str) -> str:
    """
    Get (and create) the gui state directory of a POGOS path

    :param path: str, the POGOS path

    :return: str, {path}/pogos_gui
    """
    directory = os.path.join(path, STATE_DIR)
    os.makedirs(directory, exist_ok=True)
    return directory


def backup_dir(path: str) -> str:
    """
    Get the yaml backup directory (inside the gui state directory)

    :param path: str, the POGOS path

    :return: str, {path}/pogos_gui/yaml_backups
    """
    return os.path.join(state_dir(path), BACKUP_DIR)


def batch_dir(path: str) -> str:
    """
    Get (and create) the batch script directory

    :param path: str, the POGOS path

    :return: str, {path}/pogos_gui/batch_scripts
    """
    directory = os.path.join(state_dir(path), BATCH_DIR)
    os.makedirs(directory, exist_ok=True)
    return directory


def check_pogos_path(path: str) -> Dict[str, Any]:
    """
    Describe a candidate POGOS path (for the path bar)

    :param path: str, the candidate path

    :return: dict(path, exists, writable, is_dir, nyamls, nprojects,
             looks_like_pogos)
    """
    real = os.path.realpath(os.path.expanduser(str(path).strip()))
    out = dict(path=real, exists=os.path.exists(real),
               is_dir=os.path.isdir(real), writable=False, nyamls=0,
               nprojects=0, looks_like_pogos=False)
    if out['is_dir']:
        out['writable'] = os.access(real, os.W_OK)
        out['nyamls'] = len(list_yaml_files(real))
        projects = project_dir(real)
        if os.path.isdir(projects):
            out['nprojects'] = len([name for name in os.listdir(projects)
                                    if os.path.isdir(os.path.join(projects,
                                                                  name))])
        out['looks_like_pogos'] = (os.path.isdir(yaml_dir(real))
                                   or os.path.isdir(projects))
    return out


def make_pogos_path(path: str) -> str:
    """
    Create a POGOS path (and its yamls / projects directories)

    :param path: str, the POGOS path

    :return: str, the real path
    """
    real = os.path.realpath(os.path.expanduser(str(path).strip()))
    os.makedirs(yaml_dir(real), exist_ok=True)
    os.makedirs(project_dir(real), exist_ok=True)
    return real


# =============================================================================
# Define yaml functions
# =============================================================================
def list_yaml_files(path: str) -> List[str]:
    """
    List the yaml files in {path}/yamls (sorted by name)

    :param path: str, the POGOS path

    :return: list of str, absolute yaml file paths
    """
    directory = yaml_dir(path)
    if not os.path.isdir(directory):
        return []
    names = [name for name in os.listdir(directory)
             if any(name.endswith(ext) for ext in YAML_EXTS)
             and not name.startswith('.')]
    return [os.path.join(directory, name) for name in sorted(names)]


def _enabled_steps(run: Any, prefix: str = '') -> List[str]:
    """
    Get the enabled reduction steps from the RUN section of a yaml

    :param run: dict, the RUN section (nested for e.g. SORBET.WLCA)
    :param prefix: str, the parent step name

    :return: list of str, the enabled step names (e.g. SORBET.WLCA)
    """
    steps = []
    if not isinstance(run, dict):
        return steps
    for key, value in run.items():
        name = '{0}.{1}'.format(prefix, key) if prefix else str(key)
        if isinstance(value, dict):
            steps += _enabled_steps(value, name)
        elif value is True:
            steps.append(name)
    return steps


def yaml_summary(yaml_path: str) -> Dict[str, Any]:
    """
    Summarise a POGOS yaml file (cached by modification time)

    :param yaml_path: str, the yaml file

    :return: dict(path, name, pogos, version, date, instmode, project,
             data_path, steps, description, mtime, size, error)
    """
    out: Dict[str, Any] = dict(path=yaml_path,
                               name=os.path.basename(yaml_path),
                               pogos=False, version=None, date=None,
                               instmode=None, project=None, data_path=None,
                               steps=[], mtime=None, size=None, error=None)
    try:
        info = os.stat(yaml_path)
    except OSError as error:
        out['error'] = str(error)
        return out
    out['mtime'], out['size'] = info.st_mtime, info.st_size
    cached = _SUMMARY_CACHE.get(yaml_path)
    if cached is not None and cached[0] == (info.st_mtime, info.st_size):
        return dict(cached[1])
    try:
        with open(yaml_path, 'r') as yfile:
            text = yfile.read()
        # the version comes from the header comments
        for line in text.splitlines()[:12]:
            if 'POGOS' in line:
                out['pogos'] = True
            vmatch = VERSION_RE.match(line.strip())
            if vmatch and out['version'] is None:
                out['version'] = vmatch.group(1)
            dmatch = DATE_RE.match(line.strip())
            if dmatch and out['date'] is None:
                out['date'] = dmatch.group(1)
        values = yaml.safe_load(text) or dict()
        if isinstance(values, dict):
            global_section = values.get('GLOBAL') or dict()
            if isinstance(global_section, dict):
                out['instmode'] = global_section.get('INSTRUMENTMODE')
                out['project'] = global_section.get('PROJECT_NAME')
                out['data_path'] = global_section.get('DATA_PATH')
            out['steps'] = _enabled_steps(values.get('RUN'))
    except (OSError, yaml.YAMLError) as error:
        out['error'] = '{0}: {1}'.format(type(error).__name__, error)
    _SUMMARY_CACHE[yaml_path] = ((info.st_mtime, info.st_size), dict(out))
    return out


def list_backups(path: str, yaml_path: str) -> List[Dict[str, Any]]:
    """
    List the gui backups of one yaml file (newest first)

    :param path: str, the POGOS path
    :param yaml_path: str, the yaml file

    :return: list of dict(path, name, mtime, size)
    """
    pattern = os.path.join(backup_dir(path),
                           glob.escape(os.path.basename(yaml_path))
                           + '.*.bak')
    backups = []
    for bpath in glob.glob(pattern):
        info = os.stat(bpath)
        backups.append(dict(path=bpath, name=os.path.basename(bpath),
                            mtime=info.st_mtime, size=info.st_size))
    backups.sort(key=lambda item: item['mtime'], reverse=True)
    return backups


def snapshot_yaml(path: str, yaml_path: str) -> str:
    """
    Copy a yaml file into the backup directory (e.g. before pogos_config
    may change it) so the gui can show what changed

    :param path: str, the POGOS path
    :param yaml_path: str, the yaml file

    :return: str, the backup path
    """
    directory = backup_dir(path)
    os.makedirs(directory, exist_ok=True)
    stamp = time.strftime('%Y%m%d-%H%M%S')
    backup = os.path.join(directory, '{0}.{1}.bak'.format(
        os.path.basename(yaml_path), stamp))
    with open(yaml_path, 'rb') as rfile:
        data = rfile.read()
    with open(backup, 'wb') as wfile:
        wfile.write(data)
    return backup


# =============================================================================
# Define project functions
# =============================================================================
def list_projects(path: str) -> List[Dict[str, Any]]:
    """
    List the projects of a POGOS path (fast - no sizes)

    :param path: str, the POGOS path

    :return: list of dict(name, path, modules, mtime, yamls) where yamls
             are the yaml files in {path}/yamls using this project
    """
    projects_path = project_dir(path)
    if not os.path.isdir(projects_path):
        return []
    # which yamls use which project
    users: Dict[str, List[str]] = dict()
    for ypath in list_yaml_files(path):
        summary = yaml_summary(ypath)
        if summary['project']:
            users.setdefault(str(summary['project']), []).append(ypath)
    projects = []
    for name in sorted(os.listdir(projects_path)):
        full = os.path.join(projects_path, name)
        if not os.path.isdir(full) or name.startswith('.'):
            continue
        modules = sorted(sub for sub in os.listdir(full)
                         if os.path.isdir(os.path.join(full, sub)))
        projects.append(dict(name=name, path=full, modules=modules,
                             mtime=os.path.getmtime(full),
                             yamls=users.get(name, [])))
    return projects


def project_stats(path: str, project: str) -> Dict[str, Any]:
    """
    Count files and sizes of one project (per module)

    :param path: str, the POGOS path
    :param project: str, the project name

    :return: dict(name, nfiles, size, mtime, modules=dict(module -> stats))
    """
    full = project_dir(path, project)
    out: Dict[str, Any] = dict(name=project, nfiles=0, size=0, mtime=None,
                               modules=dict())
    if not os.path.isdir(full):
        return out
    for module in sorted(os.listdir(full)):
        mpath = os.path.join(full, module)
        if not os.path.isdir(mpath):
            continue
        stats = gui_files.dir_stats(mpath)
        out['modules'][module] = stats
        out['nfiles'] += stats['nfiles']
        out['size'] += stats['size']
        if stats['mtime'] and (out['mtime'] is None
                               or stats['mtime'] > out['mtime']):
            out['mtime'] = stats['mtime']
    return out


# =============================================================================
# Define plot functions
# =============================================================================
def plot_info(directory: str) -> Dict[str, Dict[str, Any]]:
    """
    Read the plot descriptions of a plot directory ({directory}/plots.yaml,
    one block per plot name: title, description, func, time - written by
    save_show_plot) - cached by modification time

    :param directory: str, the plot directory

    :return: dict, plot name (file name without extension) -> block
    """
    path = os.path.join(directory, PLOT_INFO_FILE)
    try:
        mtime = os.path.getmtime(path)
    except OSError:
        return dict()
    cached = _PLOT_INFO_CACHE.get(path)
    if cached is not None and cached[0] == mtime:
        return cached[1]
    try:
        with open(path, 'r') as pfile:
            blocks = yaml.safe_load(pfile) or dict()
    except (OSError, yaml.YAMLError):
        blocks = dict()
    if not isinstance(blocks, dict):
        blocks = dict()
    blocks = {str(key): value for key, value in blocks.items()
              if isinstance(value, dict)}
    _PLOT_INFO_CACHE[path] = (mtime, blocks)
    return blocks


def collect_plots(path: str) -> Dict[str, Any]:
    """
    Collect the plot images of every project, organised as a tree
    project -> module -> directory (relative to the module)

    :param path: str, the POGOS path

    :return: dict(projects=list of dict(name, modules=list of dict(name,
             dirs=list of dict(dir, images)))), total, newest) - images are
             dict(path, name, size, mtime, title, description, func) (the
             last three from plots.yaml, None if not described)
    """
    out: Dict[str, Any] = dict(projects=[], total=0, newest=None)
    for project in list_projects(path):
        pentry: Dict[str, Any] = dict(name=project['name'], modules=[],
                                      count=0)
        for module in project['modules']:
            mpath = os.path.join(project['path'], module)
            images = gui_files.find_images(mpath, exts=PLOT_EXTS)
            if len(images) == 0:
                continue
            # group by directory (relative to the module)
            dirs: Dict[str, List[Dict[str, Any]]] = dict()
            for image in images:
                # the title / description saved with the plot (if any)
                info = plot_info(os.path.dirname(image['path'])).get(
                    os.path.splitext(image['name'])[0], dict())
                dirs.setdefault(image['dir'], []).append(
                    dict(path=image['path'], name=image['name'],
                         size=image['size'], mtime=image['mtime'],
                         title=info.get('title'),
                         description=info.get('description'),
                         func=info.get('func')))
                if out['newest'] is None or image['mtime'] > out['newest']:
                    out['newest'] = image['mtime']
            dir_list = [dict(dir=name, images=dirs[name])
                        for name in sorted(dirs)]
            pentry['modules'].append(dict(name=module, dirs=dir_list,
                                          count=len(images)))
            pentry['count'] += len(images)
        if pentry['count'] > 0:
            out['projects'].append(pentry)
            out['total'] += pentry['count']
    return out


# =============================================================================
# End of code
# =============================================================================

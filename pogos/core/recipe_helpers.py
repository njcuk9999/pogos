#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Shared helpers used by thin top-level POGOS recipes."""
import os
import sys
from importlib import import_module
from typing import Iterable, Tuple

from aperocore.constants import load_functions
from aperocore.core import drs_text


def load_modules(names: Iterable[str]) -> Tuple[object, ...]:
    """Import POGOS submodules lazily and return them in input order."""
    return tuple(import_module(f'pogos.{name}') for name in names)


def allow_stale_yaml_version(params, yaml_file: str, version: str,
                             version_error: str, logger) -> bool:
    """Check a YAML version and handle interactive/scripted overrides."""
    version_ok = load_functions._check_yaml_version(
        yaml_file, version, version_error, raise_exception=False)
    if version_ok:
        return True
    logger(params, 'warning', version_error.format(yaml_file, version))
    override = os.environ.get('POGOS_ACCEPT_OLD_YAML', '').strip().lower()
    if override in ['1', 'true', 'yes', 'y']:
        logger(params, 'warning', 'Continuing with stale yaml because '
                                  'POGOS_ACCEPT_OLD_YAML is set.')
        return True
    if not sys.stdin.isatty():
        emsg = ('Yaml version mismatch detected in non-interactive mode. '
                'Set POGOS_ACCEPT_OLD_YAML=1 to continue anyway.')
        logger(params, 'error', emsg)
    question = ('\nYaml version appears to be incompatible and something '
                'could break.\nDo you want to continue anyway?')
    return drs_text.user_input(question, dtype='YN', required=True)


def is_ci_mode(kwargs) -> bool:
    """Return whether a recipe should use non-interactive CI behavior."""
    if kwargs.get('ci', False):
        return True
    ci_value = os.environ.get('CI', '').strip().lower()
    return ci_value in ['1', 'true', 'yes', 'y']

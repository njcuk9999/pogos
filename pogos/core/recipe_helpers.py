#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Shared helpers used by thin top-level POGOS recipes."""
import os
import sys
import time
from importlib import import_module

from aperocore.constants import load_functions
from aperocore.core import drs_text

from pogos.core import definitions

# Module setup order: (steps enabling it, backend name, setup function name)
SETUP_STEPS = (
    ((definitions.TSOVORE,), 'tsovore', 'setup_tsovore_module'),
    ((definitions.PRE_EUREKA,), 'eureka_wrap', 'setup_eureka_pre_extract'),
    ((definitions.PRE_JWST,), 'jwst_wrap', 'setup_jwst_pre_extract'),
    ((definitions.PRE_NAMELESS,), 'nameless_wrap',
     'setup_nameless_pre_extract'),
    ((definitions.SOSSISSE,), 'sossisse_wrap', 'setup_sossisse_module'),
    ((definitions.MIRIAM,), 'miriam', 'setup_miriam_module'),
    ((definitions.EXT_EUREKA,), 'eureka_wrap', 'setup_eureka_extract'),
    ((definitions.EXT_JWST,), 'jwst_wrap', 'setup_jwst_extract'),
    ((definitions.EXT_NAMELESS,), 'nameless_wrap', 'setup_nameless_extract'),
    ((definitions.SORBET_WLCA, definitions.SORBET_SLCA), 'sorbet',
     'setup_sorbet_module'),
    ((definitions.POST_EUREKA,), 'eureka_wrap', 'setup_eureka_post_extract'),
    ((definitions.POST_JWST,), 'jwst_wrap', 'setup_jwst_post_extract'),
)


def load_module(params, name: str, logger):
    """Import one POGOS backend on first use and log how long it took."""
    module_name = f'pogos.{name}'
    if module_name in sys.modules:
        return sys.modules[module_name]
    logger(params, '', f'Loading {module_name}')
    start = time.time()
    module = import_module(module_name)
    logger(params, '', f'Loaded {module_name} in {time.time() - start:.1f} s')
    return module


def any_enabled(params, steps) -> bool:
    """Return whether any of the given reduction steps is enabled."""
    return any(step.is_enabled(params) for step in steps)


def setup_enabled_modules(params, cdict, logger):
    """Run module setup only for enabled steps, importing backends lazily."""
    for steps, name, func_name in SETUP_STEPS:
        if not any_enabled(params, steps):
            continue
        module = load_module(params, name, logger)
        setup_func = getattr(module, func_name)
        if name == 'sossisse_wrap':
            setup_func(params, cdict)
        else:
            params = setup_func(params)
    return params


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

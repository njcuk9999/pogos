#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2026-09-10 at 14:10

@author: cook
"""
import sys
import textwrap
from pathlib import Path

# Fail fast if local folders would shadow installed packages.
_shadow_dirs = ('aperocore', 'pogos', 'sossisse')
if any((Path.cwd() / name).exists() for name in _shadow_dirs):
    raise SystemExit(
        f'Error: Current directory contains one of {"/".join(_shadow_dirs)}; '
        'please run pogos_setup from another directory.'
    )

from aperocore.core import drs_log

from pogos.core import base as pogos_base
from pogos.core import general
from pogos.core import startup

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'pogos.recipes.pogos_help'
__PACKAGE__ = pogos_base.__PACKAGE__
__version__ = pogos_base.__version__
__authors__ = pogos_base.__authors__
__date__ = pogos_base.__date__
__release__ = pogos_base.__release__
__description__ = ('Show a beginner-friendly overview of the main POGOS '
                   'commands and when to use them.')
WLOG = drs_log.wlog

_COMMANDS = [
    dict(name='pogos_help',
         purpose='Show this guided overview of the main commands.',
         use_when='You are not sure where to start or want a quick map.',
         examples=[]),
    dict(name='pogos_setup',
         purpose='Create a new yaml configuration and matching directory layout.',
         use_when='You are starting a new reduction or setting up a new dataset.',
         examples=['pogos_setup']),
    dict(name='pogos_copy',
         purpose='Copy an existing demo yaml and adapt it for a similar dataset.',
         use_when='A demo already looks close to your use case and you want '
                  'a head start.',
         examples=['pogos_copy --demo_file=<demo.yaml>']),
    dict(name='pogos_config',
         purpose='Check a yaml file for compatibility and optionally fix '
                 'invalid values.',
         use_when='You already have a yaml and want to validate or update it.',
         examples=['pogos_config <your.yaml>',
                   'pogos_config --yamlfile=<your.yaml>']),
    dict(name='pogos_run',
         purpose='Run the configured reduction pipeline for your dataset.',
         use_when='Your yaml is ready and your input data are in place.',
         examples=['pogos_run <your.yaml>',
                   'pogos_run --yamlfile=<your.yaml>']),
]


def _print_line(text: str = '', indent: int = 0):
    pad = ' ' * indent
    if text == '':
        WLOG(None, '', '')
        return
    for line in textwrap.wrap(text, width=88 - indent) or ['']:
        WLOG(None, '', f'{pad}{line}', no_timestamp=True)


def _print_header(title: str):
    bar = '=' * len(title)
    WLOG(None, 'info', bar, colour='magenta', no_timestamp=True)
    WLOG(None, 'info', title, colour='magenta', no_timestamp=True)
    WLOG(None, 'info', bar, colour='magenta', no_timestamp=True)


def _print_command(command):
    _print_header(command['name'])
    _print_line(f'What it does: {command["purpose"]}')
    _print_line(f'Use it when: {command["use_when"]}')
    if len(command['examples']) > 0:
        _print_line('Examples:')
        for example in command['examples']:
            _print_line(f'  {example}', indent=2)
    _print_line()


def _print_step_guide():
    _print_header('Recommended first steps')
    _print_line('1. Run pogos_setup if you are making a brand new configuration.')
    _print_line('2. Run pogos_copy if one of the demo yamls is already close to your data.')
    _print_line('3. Run pogos_config on an existing yaml before trusting an older file.')
    _print_line('4. Run pogos_run only after the yaml paths and switches look correct.')
    _print_line()


def _print_reduction_summary():
    _print_header('Available reduction stages')
    for stage, modules in pogos_base.RED_STEPS.items():
        WLOG(None, 'info', stage, colour='magenta', no_timestamp=True)
        for module, instruments in modules.items():
            if instruments is None:
                support = 'instrument support depends on the implementation'
            else:
                support = f'{len(instruments)} supported instrument mode(s)'
            _print_line(f'- {module}: {support}', indent=2)
        _print_line()


def main(**kwargs):
    general.start_splash('POGOS Help')
    if startup.quick_args(sys.argv):
        return

    _print_header('POGOS command guide')
    _print_line('POGOS usually follows a simple path: create or copy a yaml, '
                'check it, then run it.')
    _print_line()

    _print_step_guide()
    for command in _COMMANDS:
        _print_command(command)
    _print_reduction_summary()
    general.end_splash()


def run():
    _ = main()


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    _ = main()

# =============================================================================
# End of code
# =============================================================================

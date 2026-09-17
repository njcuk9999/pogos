#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Rendering for the beginner-facing POGOS command guide."""
import textwrap

from aperocore.core import drs_log

from pogos.core import definitions

WLOG = drs_log.wlog

COMMANDS = (
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
)


def print_line(text: str = '', indent: int = 0):
    """Print wrapped help text through the POGOS logger."""
    pad = ' ' * indent
    if text == '':
        WLOG(None, '', '')
        return
    for line in textwrap.wrap(text, width=88 - indent) or ['']:
        WLOG(None, '', f'{pad}{line}', no_timestamp=True)


def print_header(title: str):
    """Print a help-section header."""
    bar = '=' * len(title)
    WLOG(None, 'info', bar, colour='magenta', no_timestamp=True)
    WLOG(None, 'info', title, colour='magenta', no_timestamp=True)
    WLOG(None, 'info', bar, colour='magenta', no_timestamp=True)


def print_command(command):
    """Print one command description."""
    print_header(command['name'])
    print_line(f'What it does: {command["purpose"]}')
    print_line(f'Use it when: {command["use_when"]}')
    if len(command['examples']) > 0:
        print_line('Examples:')
        for example in command['examples']:
            print_line(f'  {example}', indent=2)
    print_line()


def print_help():
    """Print the complete command and reduction-stage guide."""
    print_header('POGOS command guide')
    print_line('POGOS usually follows a simple path: create or copy a yaml, '
               'check it, then run it.')
    print_line()
    print_header('Recommended first steps')
    print_line('1. Run pogos_setup if you are making a brand new configuration.')
    print_line('2. Run pogos_copy if one of the demo yamls is already close to your data.')
    print_line('3. Run pogos_config on an existing yaml before trusting an older file.')
    print_line('4. Run pogos_run only after the yaml paths and switches look correct.')
    print_line()
    for command in COMMANDS:
        print_command(command)
    print_header('Available reduction stages')
    for level in definitions.REDUCTION_LEVELS:
        WLOG(None, 'info', level.name, colour='magenta', no_timestamp=True)
        for step in definitions.steps_for_level(level):
            support = f'{len(step.supported_modes)} supported instrument mode(s)'
            print_line(f'- {step.name}: {support}', indent=2)
        print_line()

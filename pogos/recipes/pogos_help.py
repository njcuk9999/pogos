#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2026-09-10 at 14:10

@author: cook
"""
import sys
from pathlib import Path

# Fail fast if local folders would shadow installed packages.
_shadow_dirs = ('aperocore', 'pogos', 'sossisse')
if any((Path.cwd() / name).exists() for name in _shadow_dirs):
    raise SystemExit(
        f'Error: Current directory contains one of {"/".join(_shadow_dirs)}; '
        'please run pogos_setup from another directory.'
    )

from pogos.core import base as pogos_base
from pogos.core import general
from pogos.core import help_text
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
def main(**kwargs):
    general.start_splash('POGOS Help')
    if startup.quick_args(sys.argv):
        return

    help_text.print_help()
    general.end_splash()

# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    _ = main()

# =============================================================================
# End of code
# =============================================================================

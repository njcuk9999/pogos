#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
pogos_gui - the POGOS browser gui

Starts a small web server (localhost only by default) and opens the POGOS
gui in a browser: setup, edit, run (local or Slurm), config / reset
actions, processes, plots and a project file organiser.

Usage:
    pogos_gui [--path=POGOS_PATH] [--port=8097] [--host=127.0.0.1]
              [--headless]

Created on 2026-11-26

@author: cook
"""
import argparse
from pathlib import Path

# Fail fast if local folders would shadow installed packages.
_shadow_dirs = ('aperocore', 'pogos', 'sossisse')
if any((Path.cwd() / name).exists() for name in _shadow_dirs):
    raise SystemExit(
        f'Error: Current directory contains one of {"/".join(_shadow_dirs)}; '
        'please run pogos_gui from another directory.'
    )

from pogos.core import base as pogos_base

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'pogos.recipes.pogos_gui'
__PACKAGE__ = pogos_base.__PACKAGE__
__version__ = pogos_base.__version__
__authors__ = pogos_base.__authors__
__date__ = pogos_base.__date__
__release__ = pogos_base.__release__
# set description
__description__ = ('Start the POGOS browser gui (setup, edit, run, actions, '
                   'processes, plots and files).')
# the default port of the gui
DEFAULT_PORT = 8097


# =============================================================================
# Define functions
# =============================================================================
def main() -> None:
    """
    Parse the command line and start the POGOS gui (blocks until the gui
    is stopped with Ctrl+C or its Shutdown button)

    :return: None
    """
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument('--path', type=str, default=None,
                        help='the POGOS path (GLOBAL.DATA_PATH) holding '
                             'yamls/ and projects/ - can also be entered '
                             'in the gui')
    parser.add_argument('--port', type=int, default=DEFAULT_PORT,
                        help='the port to serve the gui on (the next free '
                             'port is used if taken, default %(default)s)')
    parser.add_argument('--host', type=str, default='127.0.0.1',
                        help='the host to listen on (default localhost '
                             'only - use an ssh tunnel from other machines)')
    parser.add_argument('--headless', action='store_true',
                        help='do not open a browser (just print the url)')
    args = parser.parse_args()
    # deferred import (keeps --help fast)
    from pogos.gui import app
    app.main(path=args.path, host=args.host, port=args.port,
             headless=args.headless)


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    main()

# =============================================================================
# End of code
# =============================================================================

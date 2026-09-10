#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Recipe package for POGOS.

Expose recipe modules lazily so importing one command does not force import of
all commands and their heavy runtime dependencies.

Created on 2024-10-29 at 09:21

@author: cook
"""
from importlib import import_module

__all__ = ['pogos_run', 'pogos_setup', 'pogos_copy', 'pogos_config',
           'pogos_help']


def __getattr__(name):
    if name in __all__:
        module = import_module(f'{__name__}.{name}')
        globals()[name] = module
        return module
    raise AttributeError(f'module {__name__!r} has no attribute {name!r}')

# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # print 'Hello World!'
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================

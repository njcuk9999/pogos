#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Top-level POGOS package.

Keep this module intentionally lightweight so command-line entrypoints do not
pay the cost of importing plotting / astropy stacks before they are needed.

Created on 2024-12-17 at 11:12

@author: cook
"""

from importlib import import_module
from pogos.core.base import __version__, __authors__, __date__, __release__

__all__ = ['recipes', 'tsovore', 'sossisse_wrap', 'miriam', 'sorbet',
           'eureka_wrap', 'jwst_wrap', 'nameless_wrap', 'constants']


def __getattr__(name):
    if name in __all__:
        module = import_module(f'{__name__}.{name}')
        globals()[name] = module
        return module
    raise AttributeError(f'module {__name__!r} has no attribute {name!r}')


# =============================================================================
# Define variables
# =============================================================================

# -----------------------------------------------------------------------------

# =============================================================================
# Define functions
# =============================================================================



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

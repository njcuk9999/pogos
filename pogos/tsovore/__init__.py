#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2025-01-31 at 15:03

@author: cook
"""
# Resolved lazily: importing core.general pulls in all JWST pipeline steps,
# which config-only imports (e.g. pogos.constants.tsovore) must not pay for.
_LAZY_ATTRS = ('run_tsovore', 'setup_tsovore_module')


def __getattr__(name):
    if name in _LAZY_ATTRS:
        from pogos.tsovore.core import general as ts_general
        return getattr(ts_general, name)
    raise AttributeError(f'module {__name__!r} has no attribute {name!r}')

# =============================================================================
# End of code
# =============================================================================

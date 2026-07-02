#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
POGOS constants package.

Keep this package lightweight so importing `pogos.constants.constants` for the
core/global config does not also import every submodule constant stack.

Created on 2024-10-29 at 09:30

@author: cook
"""
from importlib import import_module

from pogos.core import base

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'pogos.core.startup.py'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__

def __getattr__(name):
	module_map = {'tsovore': 'pogos.constants.tsovore',
				  'miriam': 'pogos.constants.miriam',
				  'sorbet': 'pogos.constants.sorbet'}
	cdict_map = {'TSOVORE_CDict': ('pogos.constants.tsovore', 'TSOVORE_CDict'),
				 'MIRIAM_CDict': ('pogos.constants.miriam', 'MIRIAM_CDict'),
				 'SORBET_CDict': ('pogos.constants.sorbet', 'SORBET_CDict')}

	if name in module_map:
		module = import_module(module_map[name])
		globals()[name] = module
		return module
	if name in cdict_map:
		mod_name, attr_name = cdict_map[name]
		module = import_module(mod_name)
		value = getattr(module, attr_name)
		globals()[name] = value
		return value
	raise AttributeError(f'module {__name__!r} has no attribute {name!r}')


# =============================================================================
# End of code
# =============================================================================

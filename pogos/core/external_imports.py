#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2026-02-02 at 13:54

@author: cook
"""
import sys
from io import StringIO

# =============================================================================
# Capture print output from juliet import (before other imports)
# =============================================================================
_old_stdout = sys.stdout
_old_stderr = sys.stderr
_captured_juliet_output = StringIO()
sys.stdout = _captured_juliet_output
sys.stderr = _captured_juliet_output
try:
    import juliet
finally:
    sys.stdout = _old_stdout
    sys.stderr = _old_stderr

# Store captured messages in a module-level list
JULIET_IMPORT_MESSAGES = _captured_juliet_output.getvalue().strip().split('\n')
# Remove empty strings from the list
JULIET_IMPORT_MESSAGES = [msg for msg in JULIET_IMPORT_MESSAGES if msg]

# =============================================================================
# Capture print output from exotic_ld import
# =============================================================================
_old_stdout = sys.stdout
_old_stderr = sys.stderr
_captured_exotic_ld_output = StringIO()
sys.stdout = _captured_exotic_ld_output
sys.stderr = _captured_exotic_ld_output
try:
    from exotic_ld import StellarLimbDarkening
finally:
    sys.stdout = _old_stdout
    sys.stderr = _old_stderr

# Store captured messages in a module-level list
EXOTIC_LD_IMPORT_MESSAGES = _captured_exotic_ld_output.getvalue().strip().split('\n')
# Remove empty strings from the list
EXOTIC_LD_IMPORT_MESSAGES = [msg for msg in EXOTIC_LD_IMPORT_MESSAGES if msg]

# =============================================================================
# End of code
# =============================================================================

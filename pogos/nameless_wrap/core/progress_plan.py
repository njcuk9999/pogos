#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The NAMELESS wrapper steps recorded for the pogos_gui Status tab
(aperocore.progress)

NAMELESS is an external package (its code is not changed). The wrapper
(pogos.nameless_wrap.core.general) calls NAMELESS run_reduction() once per
stage (it only dispatches the stages in order, so this is the same as one
call) so every stage is a step; the jwst pipeline steps of stages 1 and 2
are recorded from the stpipe log, and the custom correction methods of the
reduction object are recorded while they run (track_methods - the object
is restored afterwards).

Every step has (see aperocore.progress.named_node):

    XXXX       the step name (used by progress.start_substep in the code)
    XXXX_FUNC  the dotted path of the function doing the work
    XXXX_DESC  a (long) description - None: the gui shows the docstring of
               XXXX_FUNC

Created on 2026-11-26

@author: cook
"""
import contextlib
import functools
from typing import Any, Dict, Iterator, List

from aperocore import progress

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'pogos.nameless_wrap.core.progress_plan.py'
# the wrapper module / the NAMELESS reduction class
_GEN = 'pogos.nameless_wrap.core.general.'
_RED = 'NAMELESS.nameless.nameless.'
# -----------------------------------------------------------------------------
NL_IMPORT = 'Import NAMELESS'
NL_IMPORT_FUNC = _GEN + 'import_nameless'
NL_IMPORT_DESC = None
NL_DIRS = 'Directories'
NL_DIRS_FUNC = _GEN + 'make_nameless_dirs'
NL_DIRS_DESC = None
NL_BUILD = 'Build the reduction'
NL_BUILD_FUNC = _GEN + 'build_reduc'
NL_BUILD_DESC = None
NL_SETTINGS = 'Settings'
NL_SETTINGS_FUNC = _GEN + 'build_settings'
NL_SETTINGS_DESC = None
NL_S1 = 'Stage 1 (jwst pipeline)'
NL_S1_FUNC = 'NAMELESS.run_jwst_steps.run_stage1'
NL_S1_DESC = None
NL_S2 = 'Stage 2 (jwst pipeline)'
NL_S2_FUNC = 'NAMELESS.run_jwst_steps.run_stage2'
NL_S2_DESC = None
NL_PREP = 'Prepare the custom steps'
NL_PREP_FUNC = _RED + 'prep4cst'
NL_PREP_DESC = None
NL_CST = 'Custom corrections'
NL_CST_FUNC = _RED + 'run_reduction'
NL_CST_DESC = None
NL_BADPIX = 'Bad pixels'
NL_BADPIX_FUNC = _RED + 'badpixcorr'
NL_BADPIX_DESC = None
NL_BACKGROUND = 'Background'
NL_BACKGROUND_FUNC = _RED + 'bg_corr'
NL_BACKGROUND_DESC = None
NL_COSMICS = 'Cosmic rays'
NL_COSMICS_FUNC = _RED + 'cosmic_rays'
NL_COSMICS_DESC = None
NL_ONEF = '1/f correction'
NL_ONEF_FUNC = _RED + 'oneoverf'
NL_ONEF_DESC = None
NL_SAVECLEAN = 'Save clean data'
NL_SAVECLEAN_FUNC = _RED + 'saveclean'
NL_SAVECLEAN_DESC = None
NL_REBUILD = 'Rebuild products from disk'
NL_REBUILD_FUNC = _GEN + 'run_nameless_extract'
NL_REBUILD_DESC = ('Only when the pre-extraction step did not run in this '
                   'session: the reduction is rebuilt and the prep products '
                   'are recomputed from the Stage 2 files on disk.')
NL_EXTRACT = 'Extraction'
NL_EXTRACT_FUNC = _RED + 'extraction'
NL_EXTRACT_DESC = None
# the reduction methods run by the custom corrections (method, key)
CST_METHODS = [('badpixcorr', 'NL_BADPIX'), ('bg_corr', 'NL_BACKGROUND'),
               ('cosmic_rays', 'NL_COSMICS'), ('oneoverf', 'NL_ONEF'),
               ('saveclean', 'NL_SAVECLEAN')]


# =============================================================================
# Define functions
# =============================================================================
@contextlib.contextmanager
def track_methods(obj: Any, methods: List[Any]) -> Iterator[None]:
    """
    Record calls of some methods of one object as steps (the methods are
    wrapped on this object only and restored on exit)

    :param obj: the object (e.g. the NAMELESS reduction)
    :param methods: list of (method name, constant key of this module)

    :return: None (context manager)
    """
    if not progress.active() or obj is None:
        yield
        return
    wrapped = []
    for attr, key in methods:
        original = getattr(obj, attr, None)
        if original is None:
            continue

        def _make(func: Any, name: str) -> Any:
            @functools.wraps(func)
            def _wrapper(*args: Any, **kwargs: Any) -> Any:
                with progress.step(name):
                    return func(*args, **kwargs)
            return _wrapper

        setattr(obj, attr, _make(original, globals()[key]))
        wrapped.append(attr)
    try:
        yield
    finally:
        # drop the instance attributes (the class methods show again)
        for attr in wrapped:
            try:
                delattr(obj, attr)
            except AttributeError:
                continue


def get_plan(flavour: str) -> List[Dict[str, Any]]:
    """
    Get the plan of one NAMELESS wrapper run

    :param flavour: str, PRE_NAMELESS or EXT_NAMELESS

    :return: list of dict, aperocore.progress plan nodes
    """
    def _node(key: str, *children: Dict[str, Any]) -> Dict[str, Any]:
        return progress.named_node(globals(), key, *children)

    if flavour == 'PRE_NAMELESS':
        cst = _node('NL_CST', *[_node(key) for _, key in CST_METHODS])
        return [_node('NL_IMPORT'), _node('NL_DIRS'), _node('NL_BUILD'),
                _node('NL_SETTINGS'), _node('NL_S1'), _node('NL_S2'),
                _node('NL_PREP'), cst]
    if flavour == 'EXT_NAMELESS':
        return [_node('NL_IMPORT'), _node('NL_DIRS'), _node('NL_SETTINGS'),
                _node('NL_EXTRACT')]
    return []


# =============================================================================
# End of code
# =============================================================================

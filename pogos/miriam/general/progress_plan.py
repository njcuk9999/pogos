#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The MIRIAM steps recorded for the pogos_gui Status tab (aperocore.progress)

The plan lists every step MIRIAM marks (pogos.miriam.general.general and
science), in order, so the gui shows them as pending first. The input
segments are a loop: their items are announced when the files are known.

Every step has (see aperocore.progress.named_node):

    XXXX       the step name (used by progress.start_substep / step)
    XXXX_FUNC  the dotted path of the function doing the work
    XXXX_DESC  a (long) description - None: the gui shows the docstring of
               XXXX_FUNC

Created on 2026-11-26

@author: cook
"""
from typing import Any, Dict, List

from aperocore import progress

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'pogos.miriam.general.progress_plan.py'
# the MIRIAM modules
_GEN = 'pogos.miriam.general.general.'
_SCI = 'pogos.miriam.general.science.'
_PLT = 'pogos.miriam.general.plots.'
# -----------------------------------------------------------------------------
MI_PREPARE = 'Prepare directories'
MI_PREPARE_FUNC = _GEN + 'prepare_directories'
MI_PREPARE_DESC = None
MI_INPUTS = 'Inputs from TSOVORE'
MI_INPUTS_FUNC = _GEN + 'tsovore_input'
MI_INPUTS_DESC = None
MI_MERGE = 'Merge inputs'
MI_MERGE_FUNC = _SCI + 'merge_inputs'
MI_MERGE_DESC = None
MI_REUSE = 'Reuse the merged data of a previous run'
MI_REUSE_FUNC = _SCI + 'merged_from_previous'
MI_REUSE_DESC = None
MI_SEGMENT = 'Segment'
MI_SEGMENT_FUNC = _SCI + 'process_integration'
MI_SEGMENT_DESC = ('Load one input file (SCI + ERR), clean every '
                   'integration, cut the cube down and add its integration '
                   'times to the merged table.')
MI_SYSTEMATICS = 'Systematics correction'
MI_SYSTEMATICS_FUNC = _SCI + 'remove_background_cube'
MI_SYSTEMATICS_DESC = None
MI_ERRORS = 'Cube errors'
MI_ERRORS_FUNC = _SCI + 'calculate_cube_errors'
MI_ERRORS_DESC = None
MI_PHOT = 'Photometry'
MI_PHOT_FUNC = _SCI + 'cube2phot'
MI_PHOT_DESC = None
MI_PHOT_2D = '2D photometry'
MI_PHOT_2D_FUNC = _SCI + 'cube2phot'
MI_PHOT_2D_DESC = None
MI_PHOT_1D = '1D photometry'
MI_PHOT_1D_FUNC = _SCI + 'cube2phot'
MI_PHOT_1D_DESC = None
MI_PLOTS = 'Plots'
MI_PLOTS_FUNC = _PLT + 'plot_photometry'
MI_PLOTS_DESC = None
MI_SAVE = 'Save results'
MI_SAVE_FUNC = 'pogos.miriam.general.io.write_photometry_results'
MI_SAVE_DESC = None
MI_SUMMARY = 'Summary'
MI_SUMMARY_FUNC = 'pogos.core.io.summary_html'
MI_SUMMARY_DESC = None


# =============================================================================
# Define functions
# =============================================================================
def get_plan(params: Any = None) -> List[Dict[str, Any]]:
    """
    Get the MIRIAM plan

    :param params: ParamDict or None, the pogos_run parameters (unused)

    :return: list of dict, aperocore.progress plan nodes
    """
    _ = params

    def _node(key: str, *children: Dict[str, Any],
              loop: bool = False) -> Dict[str, Any]:
        return progress.named_node(globals(), key, *children, loop=loop)

    return [_node('MI_PREPARE'), _node('MI_INPUTS'),
            _node('MI_MERGE', _node('MI_SEGMENT', loop=True)),
            _node('MI_SYSTEMATICS'), _node('MI_ERRORS'),
            _node('MI_PHOT', _node('MI_PHOT_2D'), _node('MI_PHOT_1D')),
            _node('MI_PLOTS'), _node('MI_SAVE'), _node('MI_SUMMARY')]


# =============================================================================
# End of code
# =============================================================================

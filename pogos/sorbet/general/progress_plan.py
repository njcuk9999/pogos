#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The SORBET steps recorded for the pogos_gui Status tab (aperocore.progress)

The plan lists every step SORBET marks (pogos.sorbet.general.general), in
order, so the gui shows them as pending first. Traces, channels and
spectral bins are loops: their items are announced when they are known.

Every step has (see aperocore.progress.named_node):

    XXXX       the step name (used by progress.step / mark in the code)
    XXXX_FUNC  the dotted path of the function doing the work
    XXXX_DESC  a (long) description - None: the gui shows the docstring of
               XXXX_FUNC

Created on 2026-11-26

@author: cook
"""
from typing import Any, Dict, List, Optional

from aperocore import progress

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'pogos.sorbet.general.progress_plan.py'
# the SORBET modules
_GEN = 'pogos.sorbet.general.general.'
_SCI = 'pogos.sorbet.general.science.'
_PLT = 'pogos.sorbet.general.plots.'
# -----------------------------------------------------------------------------
# top level steps
SB_INPUTS = 'Inputs from the extraction step'
SB_INPUTS_FUNC = _GEN + 'sossisse_input'
SB_INPUTS_DESC = None
SB_WLCA = 'White light curve analysis (WLCA)'
SB_WLCA_FUNC = _GEN + 'run_sorbet_wlcta'
SB_WLCA_DESC = None
SB_SLCA = 'Spectral light curve analysis (SLCA)'
SB_SLCA_FUNC = _GEN + 'run_sorbet_slcta'
SB_SLCA_DESC = None
# -----------------------------------------------------------------------------
# loops (templates: one child step per item)
SB_TRACE = 'Trace'
SB_TRACE_FUNC = _GEN + '_trace_fit_params'
SB_TRACE_DESC = None
SB_CHANNEL = 'Channel'
SB_CHANNEL_FUNC = _GEN + '_run_sorbet_slcta'
SB_CHANNEL_DESC = None
SB_BIN = 'Spectral bin'
SB_BIN_FUNC = _GEN + '_run_sorbet_slcta'
SB_BIN_DESC = None
# the loop item names used when there is no numbered trace
ONE_TRACE = 'single trace'
# -----------------------------------------------------------------------------
# the sections of one white light curve fit
SB_W_LOAD = 'Load white light curve'
SB_W_LOAD_FUNC = _SCI + 'load_wlc'
SB_W_LOAD_DESC = None
SB_W_OUTLIERS = 'Outliers'
SB_W_OUTLIERS_FUNC = _SCI + 'find_outliers'
SB_W_OUTLIERS_DESC = None
SB_W_DATASET = 'Prepare dataset'
SB_W_DATASET_FUNC = _SCI + 'prepare_dataset'
SB_W_DATASET_DESC = None
SB_W_FIT = 'Fit transit'
SB_W_FIT_FUNC = _SCI + 'fit_transit'
SB_W_FIT_DESC = None
SB_W_SAVE = 'Save model'
SB_W_SAVE_FUNC = _SCI + 'save_transit_model'
SB_W_SAVE_DESC = None
SB_W_PLOTS = 'Plots'
SB_W_PLOTS_FUNC = _PLT + 'plot_transit'
SB_W_PLOTS_DESC = None
SB_W_SUMMARY = 'Summary'
SB_W_SUMMARY_FUNC = 'pogos.core.io.summary_html'
SB_W_SUMMARY_DESC = None
W_KEYS = ['SB_W_LOAD', 'SB_W_OUTLIERS', 'SB_W_DATASET', 'SB_W_FIT',
          'SB_W_SAVE', 'SB_W_PLOTS', 'SB_W_SUMMARY']
# -----------------------------------------------------------------------------
# the sections of one spectral light curve run (per trace)
SB_S_LOAD = 'Load spectral light curves'
SB_S_LOAD_FUNC = _SCI + 'load_slc'
SB_S_LOAD_DESC = None
SB_S_SPECTRUM = 'Transmission spectrum'
SB_S_SPECTRUM_FUNC = _SCI + 'save_transmission_spectrum'
SB_S_SPECTRUM_DESC = None
SB_S_SUMMARY = 'Summary'
SB_S_SUMMARY_FUNC = 'pogos.core.io.summary_html'
SB_S_SUMMARY_DESC = None
# the sections of one spectral bin
SB_B_OUTLIERS = 'Outliers'
SB_B_OUTLIERS_FUNC = _SCI + 'find_outliers'
SB_B_OUTLIERS_DESC = None
SB_B_DATASET = 'Prepare dataset'
SB_B_DATASET_FUNC = _SCI + 'prepare_dataset'
SB_B_DATASET_DESC = None
SB_B_FIT = 'Fit transit'
SB_B_FIT_FUNC = _SCI + 'fit_transit'
SB_B_FIT_DESC = None
SB_B_SAVE = 'Save model'
SB_B_SAVE_FUNC = _SCI + 'save_transit_model'
SB_B_SAVE_DESC = None
SB_B_PLOTS = 'Plots'
SB_B_PLOTS_FUNC = _PLT + 'plot_transit'
SB_B_PLOTS_DESC = None
SB_B_APPEND = 'Add to the spectrum'
SB_B_APPEND_FUNC = _SCI + 'append_transmission_spec'
SB_B_APPEND_DESC = None
B_KEYS = ['SB_B_OUTLIERS', 'SB_B_DATASET', 'SB_B_FIT', 'SB_B_SAVE',
          'SB_B_PLOTS', 'SB_B_APPEND']


# =============================================================================
# Define functions
# =============================================================================
def trace_labels(traces: Optional[List[Any]]) -> List[str]:
    """
    Get the loop item names of the selected traces

    :param traces: list or None, the trace numbers (None / [None]: one
                   unnumbered trace)

    :return: list of str, the item names
    """
    if not traces or traces == [None]:
        return [ONE_TRACE]
    return ['trace {0}'.format(trace) for trace in traces]


def bin_label(number: int) -> str:
    """
    Get the loop item name of a spectral bin

    :param number: int, the bin index (0-based)

    :return: str, the item name
    """
    return 'bin {0}'.format(number + 1)


def get_plan(params: Any) -> List[Dict[str, Any]]:
    """
    Get the SORBET plan (only the enabled analyses)

    :param params: ParamDict, the pogos_run parameters

    :return: list of dict, aperocore.progress plan nodes
    """
    def _node(key: str, *children: Dict[str, Any],
              loop: bool = False) -> Dict[str, Any]:
        return progress.named_node(globals(), key, *children, loop=loop)

    plan = [_node('SB_INPUTS')]
    if params.get('RUN.SORBET.WLCA', False):
        trace = _node('SB_TRACE', *[_node(key) for key in W_KEYS],
                      loop=True)
        plan.append(_node('SB_WLCA', trace))
    if params.get('RUN.SORBET.SLCA', False):
        sbin = _node('SB_BIN', *[_node(key) for key in B_KEYS], loop=True)
        channel = _node('SB_CHANNEL', _node('SB_S_LOAD'), sbin,
                        _node('SB_S_SPECTRUM'), loop=True)
        trace = _node('SB_TRACE', channel, _node('SB_S_SUMMARY'),
                      loop=True)
        plan.append(_node('SB_SLCA', trace))
    return plan


# =============================================================================
# End of code
# =============================================================================

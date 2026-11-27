#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The TSOVORE steps recorded for the pogos_gui Status tab
(aperocore.progress)

Every step has (see aperocore.progress.named_node / step_method):

    XXXX       the step name
    XXXX_DESC  a (long) description - None: the gui shows the docstring of
               the step's function
    XXXX_FUNC  (optional) the dotted path of the function shown as its
               code - default: the decorated method itself

The step methods of the instruments are decorated with @step('XXXX'), so
every call is recorded wherever it happens. The plan (the steps shown as
pending before a run) is read from the source of the selected instrument
mode's process() method: every decorated self.xxx(...) call, in order -
commented out steps are not code, so they never appear.

Created on 2026-11-26

@author: cook
"""
from typing import Any, Callable, Dict, List, Optional

from aperocore import progress

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'pogos.tsovore.core.progress_plan.py'
# -----------------------------------------------------------------------------
# the top level steps of a TSOVORE run (pogos.tsovore.core.general)
TS_PREPARE = 'Prepare directories'
TS_PREPARE_FUNC = 'pogos.tsovore.core.general.prepare_directories'
TS_PREPARE_DESC = None
TS_LOAD = 'Load instrument'
TS_LOAD_FUNC = 'pogos.tsovore.instruments.select.load_instrument'
TS_LOAD_DESC = None
TS_PROCESS = 'Process'
TS_PROCESS_FUNC = None
TS_PROCESS_DESC = ('Run the calibration steps of the instrument mode (its '
                   'process() method) - each step is listed below.')
TS_SUMMARY = 'Summary'
TS_SUMMARY_FUNC = 'pogos.tsovore.instruments.default.Instrument.summary'
TS_SUMMARY_DESC = None
# -----------------------------------------------------------------------------
# the calibration steps (methods of the instrument classes)
TS_INPUT = 'Input data'
TS_INPUT_DESC = None
TS_INIT = 'Initialise detector data'
TS_INIT_DESC = None
TS_SPECTRACE = 'Spectral trace reference'
TS_SPECTRACE_DESC = None
TS_STACK = 'Deep stack of the segments'
TS_STACK_DESC = None
TS_SUPERBIAS = 'Superbias'
TS_SUPERBIAS_DESC = None
TS_REFPIX = 'Reference pixels'
TS_REFPIX_DESC = None
TS_LINEARITY = 'Linearity'
TS_LINEARITY_DESC = None
TS_DARK = 'Dark current'
TS_DARK_DESC = None
TS_IPC = 'Interpixel capacitance'
TS_IPC_DESC = None
TS_RSCD = 'Reset switch charge decay (RSCD)'
TS_RSCD_DESC = None
TS_FIRSTFRAME = 'First frame'
TS_FIRSTFRAME_DESC = None
TS_LASTFRAME = 'Last frame'
TS_LASTFRAME_DESC = None
TS_RESET = 'Reset anomaly'
TS_RESET_DESC = None
TS_PERSISTENCE = 'Persistence'
TS_PERSISTENCE_DESC = None
TS_CHARGE = 'Charge migration'
TS_CHARGE_DESC = None
TS_JUMP = 'Jump detection'
TS_JUMP_DESC = None
TS_PICTURE = 'Picture frame'
TS_PICTURE_DESC = None
TS_FLICKER = '1/f noise (flicker)'
TS_FLICKER_DESC = None
TS_RAMP = 'Ramp fitting'
TS_RAMP_DESC = None
TS_GAIN = 'Gain scale'
TS_GAIN_DESC = None
TS_SAVE = 'Save'
TS_SAVE_DESC = None
TS_WCS = 'Assign WCS'
TS_WCS_DESC = None
TS_FLAT = 'Flat field'
TS_FLAT_DESC = None
TS_BACKGROUND = 'Background'
TS_BACKGROUND_DESC = None
TS_MASTER_BKG = 'Master background'
TS_MASTER_BKG_DESC = None
TS_BADPIX = 'Bad pixels (SOSS)'
TS_BADPIX_DESC = None
TS_SRCTYPE = 'Source type'
TS_SRCTYPE_DESC = None
TS_EXTRACT2D = 'Extract 2D'
TS_EXTRACT2D_DESC = None
TS_WAVECORR = 'Wavelength correction'
TS_WAVECORR_DESC = None
TS_BARSHADOW = 'Bar shadow'
TS_BARSHADOW_DESC = None
TS_PATHLOSS = 'Path loss'
TS_PATHLOSS_DESC = None
TS_STRAYLIGHT = 'Stray light'
TS_STRAYLIGHT_DESC = None
TS_FRINGE = 'Fringe'
TS_FRINGE_DESC = None
TS_RESFRINGE = 'Residual fringe'
TS_RESFRINGE_DESC = None
TS_WFSS = 'WFSS contamination'
TS_WFSS_DESC = None
TS_CENTROID = 'Target centroid'
TS_CENTROID_DESC = None
TS_EXTRACT1D = 'Extract 1D'
TS_EXTRACT1D_DESC = None
TS_PHOTOM = 'Photometric calibration'
TS_PHOTOM_DESC = None


# =============================================================================
# Define functions
# =============================================================================
def step(key: str, label_arg: Optional[int] = None) -> Callable[[Any], Any]:
    """
    Decorate an instrument method as the TSOVORE step named by a constant
    of this module (see aperocore.progress.step_method)

    :param key: str, the constant name (e.g. TS_LINEARITY)
    :param label_arg: int or None, a call argument added to the name (for
                      steps called several times, e.g. save_outputs)

    :return: the decorator
    """
    return progress.step_method(globals(), key, label_arg)


def get_plan(params: Any) -> List[Dict[str, Any]]:
    """
    Get the TSOVORE plan for the instrument mode of a run

    :param params: ParamDict, the pogos_run parameters

    :return: list of dict, aperocore.progress plan nodes
    """
    from pogos.core import definitions
    from pogos.tsovore.instruments import select
    name = params.get('TSOVORE.INPUTS.INSTRUMENTMODE', None)
    cls = select.INSTRUMENTS.get(definitions.MODE_BY_NAME.get(name))
    steps = [] if cls is None else progress.plan_from_calls(cls, 'process')
    process = progress.named_node(globals(), 'TS_PROCESS', *steps)
    if cls is not None and process['func'] is None:
        process['func'] = '{0}.{1}.process'.format(cls.__module__,
                                                    cls.__name__)
    return [progress.named_node(globals(), 'TS_PREPARE'),
            progress.named_node(globals(), 'TS_LOAD'), process,
            progress.named_node(globals(), 'TS_SUMMARY')]


# =============================================================================
# End of code
# =============================================================================

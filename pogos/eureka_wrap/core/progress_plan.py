#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The Eureka wrapper steps recorded for the pogos_gui Status tab
(aperocore.progress)

Eureka itself is an external package (its code is not changed), so only
the wrapper steps are marked (pogos.eureka_wrap.core.general): preparing
directories / ECF files / inputs and one step per Eureka stage (the Code
button shows the Eureka stage function).

Every step has (see aperocore.progress.named_node):

    XXXX       the step name (used by progress.start_substep in the code)
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
__NAME__ = 'pogos.eureka_wrap.core.progress_plan.py'
# the wrapper module
_GEN = 'pogos.eureka_wrap.core.general.'
# -----------------------------------------------------------------------------
# wrapper steps (shared by the pre-extraction / extraction / post-extraction
#   runs)
EU_IMPORT = 'Import Eureka'
EU_IMPORT_FUNC = _GEN + 'import_eureka'
EU_IMPORT_DESC = None
EU_DIRS = 'Directories'
EU_DIRS_FUNC = _GEN + 'make_eureka_dirs'
EU_DIRS_DESC = None
EU_ROUTE = 'Route inputs from the previous step'
EU_ROUTE_FUNC = 'pogos.core.general.route_step_inputs'
EU_ROUTE_DESC = None
EU_ECF = 'ECF files'
EU_ECF_FUNC = 'pogos.eureka_wrap.constants.eureka_ecf.ecf_from_params'
EU_ECF_DESC = None
EU_VALIDATE = 'Validate inputs'
EU_VALIDATE_FUNC = _GEN + '_validate_eureka_stage_inputs'
EU_VALIDATE_DESC = None
# -----------------------------------------------------------------------------
# the Eureka stages (external code)
EU_S1 = 'Stage 1: ramp fitting'
EU_S1_FUNC = 'eureka.S1_detector_processing.s1_process.rampfitJWST'
EU_S1_DESC = None
EU_S2 = 'Stage 2: calibration'
EU_S2_FUNC = 'eureka.S2_calibrations.s2_calibrate.calibrateJWST'
EU_S2_DESC = None
EU_S3 = 'Stage 3: spectral extraction'
EU_S3_FUNC = 'eureka.S3_data_reduction.s3_reduce.reduce'
EU_S3_DESC = None
EU_S4 = 'Stage 4: light curves'
EU_S4_FUNC = 'eureka.S4_generate_lightcurves.s4_genLC.genlc'
EU_S4_DESC = None
EU_S5 = 'Stage 5: light curve fitting'
EU_S5_FUNC = 'eureka.S5_lightcurve_fitting.s5_fit.fitlc'
EU_S5_DESC = None
EU_S6 = 'Stage 6: spectra'
EU_S6_FUNC = 'eureka.S6_planet_spectra.s6_spectra.plot_spectra'
EU_S6_DESC = None
# the step keys of each wrapper run (in order)
PLAN_KEYS = dict(
    PRE_EUREKA=['EU_IMPORT', 'EU_DIRS', 'EU_ECF', 'EU_VALIDATE', 'EU_S1',
                'EU_S2'],
    EXT_EUREKA=['EU_IMPORT', 'EU_DIRS', 'EU_ROUTE', 'EU_ECF', 'EU_VALIDATE',
                'EU_S3'],
    POST_EUREKA=['EU_IMPORT', 'EU_DIRS', 'EU_ROUTE', 'EU_ECF', 'EU_S4',
                 'EU_S5', 'EU_S6'])


# =============================================================================
# Define functions
# =============================================================================
def get_plan(flavour: str) -> List[Dict[str, Any]]:
    """
    Get the plan of one Eureka run

    :param flavour: str, PRE_EUREKA, EXT_EUREKA or POST_EUREKA

    :return: list of dict, aperocore.progress plan nodes
    """
    return [progress.named_node(globals(), key)
            for key in PLAN_KEYS.get(flavour, [])]


# =============================================================================
# End of code
# =============================================================================

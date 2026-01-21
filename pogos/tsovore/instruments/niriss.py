#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NIRISS Detector1 & Spec2 Pipeline - Benchmark Implementation

This module provides NIRISS detector-level and spectroscopic processing that
follow the official JWST calwebb_detector1 and calwebb_spec2 pipeline
structures.

SUPPORTED MODES:
================

1. NirissSoss (NIS_SOSS)
   - Time-series spectroscopy with SOSS/CLEARTSI configuration
   - Level 1: calwebb_detector1
   - Level 2: calwebb_spec2 with SOSS-specific processing
   - Level 2 steps: srctype → flat_field → straylight → fringe → pathloss
                    → barshadow → extract_1d → photom

2. NirissSossSuperstripe (NIS_SOSS with Superstripe mode)
   - Extended time-series with improved thermal background rejection
   - Same as NirissSoss but optimized for longer observations

REFERENCE:
==========
Official JWST Pipelines:
- Detector1:
  https://github.com/spacetelescope/jwst/blob/main/jwst/pipeline/
  calwebb_detector1.py
- Spec2:
  https://github.com/spacetelescope/jwst/blob/main/jwst/pipeline/
  calwebb_spec2.py

Created on 2025-01-16

@author: cook (benchmark implementation)
"""
from aperocore.constants import param_functions
from aperocore.core import drs_log
from pogos.core import base as pogos_base
from pogos.tsovore.instruments import default as ts_default

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'tsovore.instruments.niriss'
__version__ = pogos_base.__version__
__date__ = pogos_base.__date__
__authors__ = pogos_base.__authors__
# Get parameter dictionary
ParamDict = param_functions.ParamDict
# Get Logging function
WLOG = drs_log.wlog
# -----------------------------------------------------------------------------

# =============================================================================
# Define functions
# =============================================================================
class NirissSoss(ts_default.JWST):
    """
    NIRISS SOSS detector and spectroscopic processing following official JWST
    pipeline structure.

    Benchmark implementation for comparison against standard approaches.
    """
    def __init__(self, params):
        super().__init__(params, instrument='JWST.NIRISS.SOSS')

    def process(self):
        """
        Process NIRISS SOSS data through Level 1 (detector) and Level 2
        (spectroscopic) pipelines.

        Processing order matches:
        - Level 1:
          https://github.com/spacetelescope/jwst/blob/main/jwst/pipeline/
          calwebb_detector1.py
        - Level 2:
          https://github.com/spacetelescope/jwst/blob/main/jwst/pipeline/
          calwebb_spec2.py
        """
        # Initialize processing
        self.handle_input_data()

        # =====================================================================
        # LEVEL 1: Detector-Level Processing (calwebb_detector1)
        # =====================================================================
        msg = ('Applying Level 1 (detector) calibration steps to NIRISS '
               'SOSS data')
        WLOG(self.params, 'info', msg)

        # Group Scale Step
        self.group_scale_step()

        # DQ Init Step
        self.dq_init_step()

        # Saturation Step
        self.saturation_step()

        # IPC Step
        self.apply_interpixel_capacitance()

        # Superbias Step (NIR-specific)
        self.subtract_superbias()

        # Refpix Step
        self.apply_reference_pixel_correction()

        # Linearity Step
        self.apply_linearity_correction()

        # Dark Current Step
        self.subtract_dark_current()

        # Persistence Step (optional)
        # self.correct_persistence()

        # Charge Migration Step
        self.correct_charge_migration()

        # Jump Step
        self.detect_and_flag_jumps()

        # Clean Flicker Noise Step
        self.remove_flicker_noise()

        # TSO-only: Ramp Fit and ints_model logic removed; rely on LAST.

        # Gain Scale Step → save _rateints.fits
        self.apply_gain_scaling()
        self.save_outputs('_rateints.fits')

        # =====================================================================
        # LEVEL 2: Spectroscopic Processing (calwebb_spec2 - SOSS specific)
        # =====================================================================
        msg = ('Applying Level 2 (spectroscopic) calibration steps to NIRISS '
               'SOSS data')
        WLOG(self.params, 'info', msg)

        # Step 2.1: Assign WCS
        self.assign_wcs_solution()

        # Step 2.2: Optional Clean Flicker Noise
        self.remove_flicker_noise()

        # Step 2.3: Background Subtraction (usually skipped for TSO)
        self.subtract_background()

        # Step 2.4: Source Type (srctype)
        self.srctype_determination()

        # Step 2.5: Flat Field
        self.apply_flat_field()

        # Step 2.6: Stray Light Correction
        self.correct_stray_light()

        # Step 2.7: Fringe Correction
        self.correct_fringe()

        # Step 2.8: Path Loss Correction
        self.correct_path_loss()

        # Step 2.9: Bar Shadow Correction
        self.correct_bar_shadow()

        # Step 2.10: Extract 1D Spectrum → save _x1dints.fits
        x1d_files = self.extract_1d_spectrum()
        if x1d_files:
            # Save 1D extracted spectra overriding LAST
            self.save_outputs('_x1dints.fits', infiles=x1d_files)

        # Step 2.11: Photometric Calibration on LAST → save _calints.fits
        self.apply_photometric_calibration()
        self.save_outputs('_calints.fits')


class NirissSossSuperstripe(NirissSoss):
    """
    NIRISS SOSS Superstripe mode processing.

    Superstripe mode extends time-series configuration with improved thermal
    background rejection. Processing is identical to standard SOSS.
    """
    def __init__(self, params):
        super().__init__(params)
        self.instrument = 'JWST.NIRISS.SOSS.SUPERSTRIPE'


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================

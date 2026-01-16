#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NIRSpec Detector1 & Spec2 Pipeline - Benchmark Implementation

This module provides benchmark implementations of NIRSpec detector-level and
spectroscopic processing pipelines that follow the official JWST
calwebb_detector1 and calwebb_spec2 pipeline structures.

SUPPORTED MODES:
================

1. NirspecBotsPrism (NRS_PRISM - BOTS configuration)
   - Bright Object Time Series with prism mode
   - Level 1: calwebb_detector1
   - Level 2: calwebb_spec2 with NIRSpec slit processing
   - Level 2 steps: extract_2d → srctype → master_background_mos → wavecorr
                    → flat_field → pathloss → barshadow → photom → extract_1d

2. NirspecBotsMedium (NRS_MEDIUM_MEDIUM - BOTS configuration)
   - Bright Object Time Series with medium spectral resolution
   - Similar to Prism but using medium grating

3. NirspecBotsHigh (NRS_HIGH_HIGH - BOTS configuration)
   - Bright Object Time Series with high spectral resolution
   - Similar to other BOTS modes but using high grating

All NIRSpec slitless/slit modes use the same Level 2 processing order.

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
__NAME__ = 'tsovore.instruments.nirspec'
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
class NirspecBotsPrism(ts_default.JWST):
    """
    NIRSpec BOTS Prism detector and spectroscopic processing following official
    JWST pipeline structure.

    This is a benchmark implementation for comparing against standard
    approaches.
    """
    def __init__(self, params):
        super().__init__(params, instrument='JWST.NIRSPEC.BOTS.PRISM')

    def process(self):
        """
        Process NIRSpec BOTS Prism data through Level 1 (detector) and Level 2
        (spectroscopic) pipelines.

        Processing order matches:
        - Level 1:
          https://github.com/spacetelescope/jwst/blob/main/jwst/pipeline/
          calwebb_detector1.py
        - Level 2:
          https://github.com/spacetelescope/jwst/blob/main/jwst/pipeline/
          calwebb_spec2.py (slits processing)
        """
        # Initialize processing
        self.handle_input_data()

        # =====================================================================
        # LEVEL 1: Detector-Level Processing (calwebb_detector1)
        # =====================================================================
        msg = ('Applying Level 1 (detector) calibration steps to NIRSpec '
               'BOTS Prism data')
        WLOG(self.params, 'info', msg)

        # Group Scale Step
        self.group_scale_step()

        # DQ Init Step
        self.dq_init_step()

        # Saturation Step
        self.saturation_step()

        # IPC Step
        self.apply_interpixel_capacitance()

        # Superbias Step
        self.subtract_superbias()

        # Refpix Step
        self.apply_reference_pixel_correction()

        # Linearity Step
        self.apply_linearity_correction()

        # Dark Current Step
        self.subtract_dark_current()

        # Persistence Step (skipped for NIRSpec)
        # self.correct_persistence()

        # Charge Migration Step
        self.correct_charge_migration()

        # Jump Step
        self.detect_and_flag_jumps()

        # Picture Frame Step
        self.picture_frame_step()

        # Clean Flicker Noise Step
        self.remove_flicker_noise()

        # NOTE: Ramp Fit and ints_model handling are removed for TSO-only
        # workflows. We rely on updated LAST from each step.

        # Gain Scale Step
        self.apply_gain_scaling()
        # Save TSO-style integration product
        self.save_outputs('_rateints.fits')

        # =====================================================================
        # LEVEL 2: Spectroscopic Processing (calwebb_spec2 - NIRSpec slits)
        # =====================================================================
        msg = ('Applying Level 2 (spectroscopic) calibration steps to NIRSpec '
               'BOTS Prism data')
        WLOG(self.params, 'info', msg)

        # Step 2.1: Assign WCS
        self.assign_wcs_solution()

        # Step 2.2: Extract 2D
        self.extract_2d_spectrum()

        # Step 2.3: Source Type (srctype)
        self.srctype_determination()

        # Step 2.4: Master Background MOS (often skipped for BOTS)
        self.subtract_master_background()

        # Step 2.5: Wave Correction
        self.correct_wavelength()

        # Step 2.6: Flat Field
        self.apply_flat_field()

        # Step 2.7: Path Loss Correction
        self.correct_path_loss()

        # Step 2.8: Bar Shadow Correction
        self.correct_bar_shadow()

        # Step 2.9: Photometric Calibration
        self.apply_photometric_calibration()
        # Save TSO-style integration product
        self.save_outputs('_calints.fits')

        # Step 2.10: Extract 1D (x1d)
        x1d_files = self.extract_1d_spectrum()
        # Save 1D extracted spectrum overriding LAST
        if x1d_files:
            self.save_outputs('_x1dints.fits', infiles=x1d_files)


class NirspecBotsMedium(NirspecBotsPrism):
    """
    NIRSpec BOTS Medium grating detector and spectroscopic processing.

    Same processing as Prism but using medium spectral resolution grating.
    """
    def __init__(self, params):
        super().__init__(params)
        self.instrument = 'JWST.NIRSPEC.BOTS.MEDIUM'


class NirspecBotsHigh(NirspecBotsPrism):
    """
    NIRSpec BOTS High grating detector and spectroscopic processing.

    Same processing as Prism but using high spectral resolution grating.
    """
    def __init__(self, params):
        super().__init__(params)
        self.instrument = 'JWST.NIRSPEC.BOTS.HIGH'


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================

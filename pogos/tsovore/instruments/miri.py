#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MIRI Detector1 & Spec2 Pipeline - Benchmark Implementation

This module provides MIRI detector-level and spectroscopic processing that
follow the official JWST calwebb_detector1 and calwebb_spec2 pipeline
structures.

SUPPORTED MODES:
================

1. MiriImaging (MIR_IMAGE)
   - Direct imaging mode
   - Level 1: calwebb_detector1
   - Level 2: calwebb_image2
   - Level 2 steps: bkg_subtract → assign_wcs → flat_field → photom

2. MiriLrs (MIR_LRS-FIXEDSLIT / MIR_LRS-SLITLESS)
   - Low resolution spectroscopy
   - Level 1: calwebb_detector1
   - Level 2: calwebb_spec2 with LRS-specific processing
   - Level 2 steps: assign_wcs → srctype → straylight → flat_field →
                    fringe → barshadow → photom → residual_fringe → extract_1d

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

@author: cook
"""
from aperocore.constants import param_functions
from aperocore.core import drs_log
from pogos.core import base as pogos_base
from pogos.tsovore.instruments import default as ts_default

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'tsovore.instruments.miri'
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
class MiriImaging(ts_default.JWST):
    """
    MIRI Imaging detector-level processing following official JWST
    pipeline structure.

    This is a benchmark implementation for comparing against standard
    approaches.
    """
    def __init__(self, params):
        super().__init__(params, instrument='JWST.MIRI.IMAGING')

    def process(self):
        """
        Process the MIRI Imaging data - Following JWST
        calwebb_detector1 pipeline structure

        This implementation follows the official JWST pipeline structure
        more closely than the miri.py version, with explicit individual
        step calls and proper handling of multi-value returns (e.g., from
        ramp_fit).

        Processing order matches:
        https://github.com/spacetelescope/jwst/blob/main/jwst/pipeline/
        calwebb_detector1.py
        """
        # Initialize processing
        infiles = self.handle_input_data()

        # =====================================================================
        # MIRI-Specific Level 1 Processing (in official pipeline order)
        # =====================================================================
        msg = ('Applying Level 1 calibration steps to MIRI Imaging data')
        WLOG(self.params, 'info', msg)

        # Group Scale Step (1.1)
        # Scales group data to account for on-chip amplifier effects
        infiles = self.group_scale_step(infiles)

        # DQ Init Step (1.2)
        # Initialize the data quality flags
        infiles = self.dq_init_step(infiles)

        # Emi Corr Step (1.3)
        # Apply EMI (electro-magnetic interference) corrections
        infiles = self.emicorr_step(infiles)

        # Saturation Step (1.4)
        # Flag saturated pixels
        infiles = self.saturation_step(infiles)

        # IPC Step (1.5)
        # Correct for interpixel capacitance
        infiles = self.apply_interpixel_capacitance(infiles)

        # First Frame Step (1.6)
        # Remove or flag the first frame of data
        # TODO: Replace this step with a copy and simply change that
        #       so that more than 1 frame is set to DO NOT USE
        #       (if that is what Etienne needs)
        infiles = self.remove_first_frame_signal(infiles)

        # Last Frame Step (1.7)
        # Remove or flag the last frame of data
        infiles = self.remove_last_frame_signal(infiles)

        # Reset Step (1.8)
        # Correct for reset anomaly
        infiles = self.correct_reset_anomaly(infiles)

        # Linearity Step (1.9)
        # Apply linearity correction
        infiles = self.apply_linearity_correction(infiles)

        # RSCD Step (1.10)
        # Apply RSCD (Reset Switch Charge Decay) corrections
        infiles = self.apply_rscd_correction(infiles)

        # Dark Current Step (1.11)
        # Subtract dark current
        infiles = self.subtract_dark_current(infiles)

        # Ref Pix Step (1.12)
        # Apply reference pixel correction
        infiles = self.apply_reference_pixel_correction(infiles)

        # NOTE: Persistence step is skipped for MIRI in official pipeline
        # (MIRI team has not figured out algorithm yet)

        # =====================================================================
        # Common Processing Steps (applied to all instruments
        # after MIRI-specific)
        # =====================================================================

        # Charge Migration Step (1.13)
        # Correct for charge migration
        # NOTE: In official pipeline, this is called even though it may
        # be skipped
        infiles = self.correct_charge_migration(infiles)

        # Jump Step (1.14)
        # Detect and flag cosmic ray jumps
        infiles = self.detect_and_flag_jumps(infiles)

        # Picture Frame Step (1.15)
        # Correct for picture frame effect
        infiles = self.picture_frame_step(infiles)

        # Clean Flicker Noise Step (1.16)
        # Remove flicker noise
        # NOTE: In official pipeline, this is called even though it may
        # be skipped
        infiles = self.remove_flicker_noise(infiles)

        # Ramp Fit Step
        # Fit ramps to derive count rates
        infiles = self.fit_signal_ramps(infiles)

        # Gain Scale Step
        # Apply gain scaling to convert DN to electrons
        infiles = self.apply_gain_scaling(infiles)
        # Save TSO-style integration product
        infiles = self.save_outputs('_rateints.fits', infiles)

        # =====================================================================
        # Level 2 Processing Steps (calwebb_image2 - MIRI Imaging
        # specific)
        # =====================================================================
        # Reference:
        # https://github.com/spacetelescope/jwst/blob/main/jwst/pipeline/
        # calwebb_image2.py

        msg = ('Applying Level 2 calibration steps to MIRI Imaging data')
        WLOG(self.params, 'info', msg)

        # Step 2.1: Background Subtraction
        # Subtract background/dark exposures from science data
        # For time-series observations, typically skipped
        infiles = self.subtract_background(infiles)

        # Step 2.2: Assign WCS
        # Assign world coordinate system to the data
        infiles = self.assign_wcs_solution(infiles)

        # Step 2.3: Flat Field Correction
        # Apply flat field correction using reference files
        infiles = self.apply_flat_field(infiles)

        # Step 2.4: Photometric Calibration
        # Apply photometric calibration and convert DN/s to physical units
        infiles = self.apply_photometric_calibration(infiles)
        # Save TSO-style calibrated product
        infiles = self.save_outputs('_calints.fits', infiles)


class MiriLrs(ts_default.JWST):
    """
    MIRI Low Resolution Spectroscopy detector and spectroscopic
    processing following official JWST pipeline.

    This is a benchmark implementation for comparing against standard
    approaches. Supports both MIR_LRS-FIXEDSLIT and
    MIR_LRS-SLITLESS modes.
    """
    def __init__(self, params):
        super().__init__(params, instrument='JWST.MIRI.LRS')

    def process(self):
        """
        Process MIRI LRS data through Level 1 (detector) and Level 2
        (spectroscopic) pipelines.

        Processing order matches:
        - Level 1:
          https://github.com/spacetelescope/jwst/blob/main/jwst/
          pipeline/calwebb_detector1.py
        - Level 2:
          https://github.com/spacetelescope/jwst/blob/main/jwst/
          pipeline/calwebb_spec2.py (common processing for LRS)
        """
        # Initialize processing
        infiles = self.handle_input_data()

        # =====================================================================
        # LEVEL 1: Detector-Level Processing (calwebb_detector1)
        # =====================================================================
        msg = ('Applying Level 1 (detector) calibration steps to MIRI '
               'LRS data')
        WLOG(self.params, 'info', msg)

        # Group Scale Step (1.1)
        infiles = self.group_scale_step(infiles)

        # DQ Init Step (1.2)
        infiles = self.dq_init_step(infiles)

        # Emi Corr Step (1.3)
        infiles = self.emicorr_step(infiles)

        # Saturation Step (1.4)
        infiles = self.saturation_step(infiles)

        # IPC Step (1.5)
        infiles = self.apply_interpixel_capacitance(infiles)

        # First Frame Step (1.6)
        infiles = self.remove_first_frame_signal(infiles)

        # Last Frame Step (1.7)
        infiles = self.remove_last_frame_signal(infiles)

        # Reset Step (1.8)
        infiles = self.correct_reset_anomaly(infiles)

        # Linearity Step (1.9)
        infiles = self.apply_linearity_correction(infiles)

        # RSCD Step (1.10)
        infiles = self.apply_rscd_correction(infiles)

        # Dark Current Step (1.11)
        infiles = self.subtract_dark_current(infiles)

        # Ref Pix Step (1.12)
        infiles = self.apply_reference_pixel_correction(infiles)

        # NOTE: Persistence step is skipped for MIRI in official pipeline

        # Charge Migration Step (1.13)
        infiles = self.correct_charge_migration(infiles)

        # Jump Step (1.14)
        infiles = self.detect_and_flag_jumps(infiles)

        # Picture Frame Step (1.15)
        infiles = self.picture_frame_step(infiles)

        # Clean Flicker Noise Step (1.16)
        infiles = self.remove_flicker_noise(infiles)

        # Ramp Fit Step
        infiles = self.fit_signal_ramps(infiles)

        # Gain Scale Step
        infiles = self.apply_gain_scaling(infiles)
        # Save TSO-style integration product
        infiles = self.save_outputs('_rateints.fits', infiles)

        # =====================================================================
        # LEVEL 2: Spectroscopic Processing (calwebb_spec2 - MIRI LRS
        # common mode)
        # =====================================================================
        # Reference:
        # https://github.com/spacetelescope/jwst/blob/main/jwst/pipeline/
        # calwebb_spec2.py

        msg = ('Applying Level 2 (spectroscopic) calibration steps to '
               'MIRI LRS data')
        WLOG(self.params, 'info', msg)
        WLOG(self.params, 'info', msg)

        # Step 2.1: Assign WCS
        infiles = self.assign_wcs_solution(infiles)

        # Step 2.2: Source Type (srctype)
        # Convert to SlitModel type for LRS time-series data
        infiles = self.srctype_determination(infiles)

        # Step 2.3: Target Centroid (for TA verification image if present)
        # Typically skipped for LRS but included for completeness
        # infiles = self.measure_target_centroid(infiles)

        # Step 2.4: Stray Light Correction
        infiles = self.correct_stray_light(infiles)

        # Step 2.5: Flat Field
        infiles = self.apply_flat_field(infiles)

        # Step 2.6: Fringe Correction
        infiles = self.correct_fringe(infiles)

        # Step 2.7: Path Loss Correction
        # Note: Path loss is NOT applied to MIR_LRS in official pipeline
        # but step is included for completeness
        # infiles = self.correct_path_loss(infiles)
        # infiles = self.correct_path_loss(infiles)

        # Step 2.8: Bar Shadow Correction
        infiles = self.correct_bar_shadow(infiles)

        # Step 2.9: Photometric Calibration
        infiles = self.apply_photometric_calibration(infiles)
        # Save TSO-style calibrated product
        infiles = self.save_outputs('_calints.fits', infiles)

        # Step 2.10: Residual Fringe Correction (MIRI-specific)
        infiles = self.correct_residual_fringe(infiles)

        # Step 2.11: Extract 1D
        # For LRS: extract_1d for 1D spectrum
        x1d_files = self.extract_1d_spectrum(infiles)
        # Save 1D extracted spectra
        x1d_files = self.save_outputs('_x1dints.fits', x1d_files)


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # print 'Hello World!'
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================

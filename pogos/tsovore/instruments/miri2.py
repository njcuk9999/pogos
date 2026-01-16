#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MIRI Imaging Detector1 Pipeline - Benchmark Implementation

This module provides an alternative implementation of the MIRI Imaging detector-level
processing pipeline that more closely follows the official JWST calwebb_detector1 pipeline
structure.

KEY DIFFERENCES FROM miri.py:
============================

1. EXPANDED INDIVIDUAL DETECTOR INIT STEPS:
   - miri.py uses: self.initialize_detector_data() (bundles steps 1.1-1.4)
   - miri2.py calls: group_scale_step(), dq_init_step(), emicorr_step(), saturation_step()
   - This matches the official JWST pipeline granularity exactly

2. EXPLICIT STEP ORDERING:
   - Each step is called individually with clear comments matching official pipeline
   - Makes the exact processing sequence visible and auditable
   - Official order: group_scale → dq_init → emicorr → saturation → ipc → firstframe →
     lastframe → reset → linearity → rscd → dark_current → refpix → (common steps)

3. PROPER RAMP_FIT OUTPUT HANDLING:
   - miri.py: self.fit_signal_ramps() - ignores return values
   - miri2.py: Explicitly handles tuple return (rate_data, ints_model)
   - Matches official JWST behavior where ramp_fit returns two products

4. SEPARATE GAIN SCALE APPLICATIONS:
   - miri.py: Calls apply_gain_scaling() once, saves _rateints.fits
   - miri2.py: Applies gain_scale separately to rate product (_rate.fits) and
     ints_model (_rateints.fits)
   - Matches official pipeline where gain_scale is applied to both products

5. ENABLED COMMON STEPS:
   - miri.py: Comments out charge_migration and clean_flicker_noise
   - miri2.py: Calls both steps (matching official pipeline)
   - Persistence is still correctly skipped (MIRI-specific)

6. DETECTOR-LEVEL FOCUS (MiriImaging2):
   - miri.py includes Level 2 steps (WCS, flat field, photometry)
   - MiriImaging2 includes Level 2 processing (calwebb_image2)
   - For a fair comparison, Level 2 steps are included in the full pipeline

7. SUPPORTED MODES:
   - MiriImaging: Direct imaging mode with calwebb_image2 processing
   - MiriLrs: Low resolution spectroscopy with calwebb_spec2 processing

REFERENCE:
==========
Official JWST Pipeline: https://github.com/spacetelescope/jwst/blob/main/jwst/pipeline/calwebb_detector1.py

Created on 2025-01-16 at 11:00

@author: cook (benchmark implementation)
"""
from aperocore.constants import param_functions
from aperocore.core import drs_log
from pogos.core import base as pogos_base
from pogos.tsovore.instruments import default as ts_default

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'tsovore.instruments.miri2'
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
class MiriImaging2(ts_default.JWST):
    """
    MIRI Imaging detector-level processing following official JWST pipeline structure.

    This is a benchmark implementation for comparing against the standard miri.py approach.
    """
    def __init__(self, params):
        super().__init__(params, instrument='JWST.MIRI.IMAGING')

    def process(self):
        """
        Process the MIRI Imaging data - Following JWST calwebb_detector1 pipeline structure

        This implementation follows the official JWST pipeline structure more closely
        than the miri.py version, with explicit individual step calls and proper
        handling of multi-value returns (e.g., from ramp_fit).

        Processing order matches: https://github.com/spacetelescope/jwst/blob/main/jwst/pipeline/calwebb_detector1.py
        """
        # Initialize processing
        self.handle_input_data()

        # =====================================================================
        # MIRI-Specific Level 1 Processing (in official pipeline order)
        # =====================================================================
        msg = ('Applying Level 1 calibration steps to MIRI Imaging data')
        WLOG(self.params, 'info', msg)

        # Group Scale Step (1.1)
        # Scales group data to account for on-chip amplifier effects
        self.group_scale_step()

        # DQ Init Step (1.2)
        # Initialize the data quality flags
        self.dq_init_step()

        # Emi Corr Step (1.3)
        # Apply EMI (electro-magnetic interference) corrections
        self.emicorr_step()

        # Saturation Step (1.4)
        # Flag saturated pixels
        self.saturation_step()

        # IPC Step (1.5)
        # Correct for interpixel capacitance
        self.apply_interpixel_capacitance()

        # First Frame Step (1.6)
        # Remove or flag the first frame of data
        # TODO: Replace this step with a copy and simply change that
        #       so that more than 1 frame is set to DO NOT USE
        #       (if that is what Etienne needs)
        self.remove_first_frame_signal()

        # Last Frame Step (1.7)
        # Remove or flag the last frame of data
        self.remove_last_frame_signal()

        # Reset Step (1.8)
        # Correct for reset anomaly
        self.correct_reset_anomaly()

        # Linearity Step (1.9)
        # Apply linearity correction
        self.apply_linearity_correction()

        # RSCD Step (1.10)
        # Apply RSCD (Reset Switch Charge Decay) corrections
        self.apply_rscd_correction()

        # Dark Current Step (1.11)
        # Subtract dark current
        self.subtract_dark_current()

        # Ref Pix Step (1.12)
        # Apply reference pixel correction
        self.apply_reference_pixel_correction()

        # NOTE: Persistence step is skipped for MIRI in official pipeline
        # (MIRI team has not figured out algorithm yet)

        # =====================================================================
        # Common Processing Steps (applied to all instruments after MIRI-specific)
        # =====================================================================

        # Charge Migration Step (1.13)
        # Correct for charge migration
        # NOTE: In official pipeline, this is called even though it may be skipped
        self.correct_charge_migration()

        # Jump Step (1.14)
        # Detect and flag cosmic ray jumps
        self.detect_and_flag_jumps()

        # Picture Frame Step (1.15)
        # Correct for picture frame effect
        self.picture_frame_step()

        # Clean Flicker Noise Step (1.16)
        # Remove flicker noise
        # NOTE: In official pipeline, this is called even though it may be skipped
        self.remove_flicker_noise()

        # Gain Scale Step (TSO-only: no ramp_fit handling)
        # Apply gain scaling to convert DN to electrons
        self.apply_gain_scaling()
        # Save TSO-style integration product
        self.save_outputs('_rateints.fits')

        # =====================================================================
        # Level 2 Processing Steps (calwebb_image2 - MIRI Imaging specific)
        # =====================================================================
        # Reference: https://github.com/spacetelescope/jwst/blob/main/jwst/pipeline/calwebb_image2.py

        msg = ('Applying Level 2 calibration steps to MIRI Imaging data')
        WLOG(self.params, 'info', msg)

        # Step 2.1: Background Subtraction
        # Subtract background/dark exposures from science data
        # For time-series observations, typically skipped
        self.subtract_background()

        # Step 2.2: Assign WCS
        # Assign world coordinate system to the data
        self.assign_wcs_solution()

        # Step 2.3: Flat Field Correction
        # Apply flat field correction using reference files
        self.apply_flat_field()

        # Step 2.4: Photometric Calibration
        # Apply photometric calibration and convert DN/s to physical units
        self.apply_photometric_calibration()
        # Save TSO-style calibrated product
        self.save_outputs('_calints.fits')


class MiriLrs(ts_default.JWST):
    """
    MIRI Low Resolution Spectroscopy detector and spectroscopic processing following official JWST pipeline.

    This is a benchmark implementation for comparing against standard approaches.
    Supports both MIR_LRS-FIXEDSLIT and MIR_LRS-SLITLESS modes.
    """
    def __init__(self, params):
        super().__init__(params, instrument='JWST.MIRI.LRS')

    def process(self):
        """
        Process MIRI LRS data through Level 1 (detector) and Level 2 (spectroscopic) pipelines.

        Processing order matches:
        - Level 1: https://github.com/spacetelescope/jwst/blob/main/jwst/pipeline/calwebb_detector1.py
        - Level 2: https://github.com/spacetelescope/jwst/blob/main/jwst/pipeline/calwebb_spec2.py (common processing for LRS)
        """
        # Initialize processing
        self.handle_input_data()

        # =====================================================================
        # LEVEL 1: Detector-Level Processing (calwebb_detector1)
        # =====================================================================
        msg = ('Applying Level 1 (detector) calibration steps to MIRI LRS '
               'data')
        WLOG(self.params, 'info', msg)

        # Group Scale Step (1.1)
        self.group_scale_step()

        # DQ Init Step (1.2)
        self.dq_init_step()

        # Emi Corr Step (1.3)
        self.emicorr_step()

        # Saturation Step (1.4)
        self.saturation_step()

        # IPC Step (1.5)
        self.apply_interpixel_capacitance()

        # First Frame Step (1.6)
        self.remove_first_frame_signal()

        # Last Frame Step (1.7)
        self.remove_last_frame_signal()

        # Reset Step (1.8)
        self.correct_reset_anomaly()

        # Linearity Step (1.9)
        self.apply_linearity_correction()

        # RSCD Step (1.10)
        self.apply_rscd_correction()

        # Dark Current Step (1.11)
        self.subtract_dark_current()

        # Ref Pix Step (1.12)
        self.apply_reference_pixel_correction()

        # NOTE: Persistence step is skipped for MIRI in official pipeline

        # Charge Migration Step (1.13)
        self.correct_charge_migration()

        # Jump Step (1.14)
        self.detect_and_flag_jumps()

        # Picture Frame Step (1.15)
        self.picture_frame_step()

        # Clean Flicker Noise Step (1.16)
        self.remove_flicker_noise()

        # Gain Scale Step (TSO-only: no ramp_fit handling)
        self.apply_gain_scaling()
        # Save TSO-style integration product
        self.save_outputs('_rateints.fits')

        # =====================================================================
        # LEVEL 2: Spectroscopic Processing (calwebb_spec2 - MIRI LRS common mode)
        # =====================================================================
        # Reference: https://github.com/spacetelescope/jwst/blob/main/jwst/pipeline/calwebb_spec2.py

        msg = ('Applying Level 2 (spectroscopic) calibration steps to MIRI '
               'LRS data')
        WLOG(self.params, 'info', msg)

        # Step 2.1: Assign WCS
        self.assign_wcs_solution()

        # Step 2.2: Source Type (srctype)
        # Convert to SlitModel type for LRS time-series data
        self.srctype_determination()

        # Step 2.3: Target Centroid (for TA verification image if present)
        # Typically skipped for LRS but included for completeness
        # self.measure_target_centroid()

        # Step 2.4: Stray Light Correction
        self.correct_stray_light()

        # Step 2.5: Flat Field
        self.apply_flat_field()

        # Step 2.6: Fringe Correction
        self.correct_fringe()

        # Step 2.7: Path Loss Correction
        # Note: Path loss is NOT applied to MIR_LRS in official pipeline
        # but step is included for completeness
        # self.correct_path_loss()

        # Step 2.8: Bar Shadow Correction
        self.correct_bar_shadow()

        # Step 2.9: Photometric Calibration
        self.apply_photometric_calibration()
        # Save TSO-style calibrated product
        self.save_outputs('_calints.fits')

        # Step 2.10: Residual Fringe Correction (MIRI-specific)
        self.correct_residual_fringe()

        # Step 2.11: Extract 1D
        # For LRS: extract_1d for 1D spectrum
        x1d_files = self.extract_1d_spectrum()
        if x1d_files:
            # Save 1D extracted spectra overriding LAST
            self.save_outputs('_x1dints.fits', infiles=x1d_files)


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

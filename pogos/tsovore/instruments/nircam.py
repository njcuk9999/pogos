#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NIRCam Detector1 & Spec2/Image2 Pipeline - Benchmark Implementation

This module provides NIRCam detector-level and
imaging/spectroscopic processing pipelines that follow the official JWST
calwebb_detector1, calwebb_image2, and calwebb_spec2 pipeline structures.

SUPPORTED MODES:
================

1. NircamImaging (NRC_IMAGE)
   - Direct imaging mode
   - Level 1: calwebb_detector1
   - Level 2: calwebb_image2
   - Level 2 steps: bkg_subtract → assign_wcs → flat_field → photom → resample

2. NircamGrism (NRC_WFSS / NRC_GRISM)
   - Grism slitless spectroscopy / wide-field slitless spectroscopy
   - Level 1: calwebb_detector1
   - Level 2: calwebb_spec2 with Grism-specific processing
   - Level 2 steps: assign_wcs → flat_field (before extract_2d) → extract_2d
                    → srctype → straylight → fringe → pathloss → barshadow
                    → wfss_contam → photom

3. NircamMultistripe (NRC_MULTISTRIPE)
   - Multi-channel spectroscopic mode
   - Uses similar processing to Grism but optimized for multi-stripe
     configuration

REFERENCE:
==========
Official JWST Pipelines:
- Detector1:
  https://github.com/spacetelescope/jwst/blob/main/jwst/pipeline/
  calwebb_detector1.py
- Image2:
  https://github.com/spacetelescope/jwst/blob/main/jwst/pipeline/
  calwebb_image2.py
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
__NAME__ = 'tsovore.instruments.nircam'
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
class NircamImaging(ts_default.JWST):
    """
    NIRCam direct imaging detector and image processing following official
    JWST pipeline structure.

    This is a benchmark implementation for comparing against standard
    approaches.
    """
    def __init__(self, params):
        super().__init__(params, instrument='JWST.NIRCAM.IMAGING')

    def process(self):
        """
        Process NIRCam imaging data through Level 1 (detector) and Level 2
        (image) pipelines.

        Processing order matches:
        - Level 1:
          https://github.com/spacetelescope/jwst/blob/main/jwst/pipeline/
          calwebb_detector1.py
        - Level 2:
          https://github.com/spacetelescope/jwst/blob/main/jwst/pipeline/
          calwebb_image2.py
        """
        # Initialize processing
        infiles = self.handle_input_data()

        # =====================================================================
        # LEVEL 1: Detector-Level Processing (calwebb_detector1)
        # =====================================================================
        msg = ('Applying Level 1 (detector) calibration steps to NIRCam '
               'imaging data')
        WLOG(self.params, 'info', msg)

        # Initialize Detector Data (bundled: group_scale + dq_init + saturation)
        # Note: NIRCam doesn't use emicorr_step
        infiles = self.initialize_detector_data(infiles)

        # IPC Step
        infiles = self.apply_interpixel_capacitance(infiles)

        # Superbias Step
        infiles = self.subtract_superbias(infiles)

        # Refpix Step
        infiles = self.apply_reference_pixel_correction(infiles)

        # Linearity Step
        infiles = self.apply_linearity_correction(infiles)

        # Dark Current Step
        infiles = self.subtract_dark_current(infiles)

        # Persistence Step (skipped for NIRCam)
        # infiles = self.correct_persistence(infiles)

        # Charge Migration Step
        infiles = self.correct_charge_migration(infiles)

        # Jump Step
        infiles = self.detect_and_flag_jumps(infiles)

        # Picture Frame Step
        infiles = self.picture_frame_step(infiles)

        # Clean Flicker Noise Step
        infiles = self.remove_flicker_noise(infiles)

        # Ramp Fit Step
        infiles = self.fit_signal_ramps(infiles)

        # Gain Scale Step
        # infiles = self.apply_gain_scaling(infiles)
        # Save TSO-style integration product
        infiles = self.save_outputs('_rateints.fits', infiles)

        # =====================================================================
        # LEVEL 2: Image Processing (calwebb_image2)
        # =====================================================================
        msg = ('Applying Level 2 (image) calibration steps to NIRCam '
               'imaging data')
        WLOG(self.params, 'info', msg)

        # Step 2.1: Background Subtraction
        infiles = self.subtract_background(infiles)

        # Step 2.2: Assign WCS
        infiles = self.assign_wcs_solution(infiles)

        # Step 2.3: Flat Field
        infiles = self.apply_flat_field(infiles)

        # Step 2.4: Photometric Calibration
        infiles = self.apply_photometric_calibration(infiles)

        # Save the final calibrated product
        # Always TSO-style integration products
        infiles = self.save_outputs('_calints.fits', infiles)

        # Step 2.5: (Optional) Extract 1D for imaging-derived spectra
        x1d_files = self.extract_1d_spectrum(infiles)
        # Save 1D extracted spectra
        x1d_files = self.save_outputs('_x1dints.fits', x1d_files)
        # ---------------------------------------------------------------------
        # Last step is to save the outputs for return, do not remove this
        self.add_output(infiles)
        self.add_calib('X1D', x1d_files)


class NircamGrism(ts_default.JWST):
    """
    NIRCam Grism (wide-field slitless spectroscopy) detector and spectroscopic
    processing.

    Grism mode uses flat_field before extract_2d, and includes WFSS-specific
    steps.
    """
    def __init__(self, params):
        super().__init__(params, instrument='JWST.NIRCAM.GRISM')

    def process(self):
        """
        Process NIRCam Grism data through Level 1 (detector) and Level 2
        (spectroscopic) pipelines.

        Processing order matches:
        - Level 1:
          https://github.com/spacetelescope/jwst/blob/main/jwst/pipeline/
          calwebb_detector1.py
        - Level 2:
          https://github.com/spacetelescope/jwst/blob/main/jwst/pipeline/
          calwebb_spec2.py (grism processing)
        """
        # Initialize processing
        infiles = self.handle_input_data()

        # =====================================================================
        # LEVEL 1: Detector-Level Processing (calwebb_detector1)
        # =====================================================================
        msg = ('Applying Level 1 (detector) calibration steps to NIRCam '
               'Grism data')
        WLOG(self.params, 'info', msg)

        # Initialize Detector Data (bundled: group_scale + dq_init + saturation)
        infiles = self.initialize_detector_data(infiles)

        # IPC Step
        infiles = self.apply_interpixel_capacitance(infiles)

        # Superbias Step
        infiles = self.subtract_superbias(infiles)

        # Refpix Step
        infiles = self.apply_reference_pixel_correction(infiles)

        # Linearity Step
        infiles = self.apply_linearity_correction(infiles)

        # Dark Current Step
        infiles = self.subtract_dark_current(infiles)

        # Charge Migration Step
        infiles = self.correct_charge_migration(infiles)

        # Jump Step
        infiles = self.detect_and_flag_jumps(infiles)

        # Picture Frame Step
        infiles = self.picture_frame_step(infiles)

        # Clean Flicker Noise Step
        infiles = self.remove_flicker_noise(infiles)

        # Ramp Fit Step
        infiles = self.fit_signal_ramps(infiles)

        # Gain Scale Step
        # infiles = self.apply_gain_scaling(infiles)
        # Save TSO-style integration product
        infiles = self.save_outputs('_rateints.fits', infiles)

        # =====================================================================
        # LEVEL 2: Spectroscopic Processing (calwebb_spec2 - Grism specific)
        # =====================================================================
        msg = ('Applying Level 2 (spectroscopic) calibration steps to NIRCam '
               'Grism data')
        WLOG(self.params, 'info', msg)

        # Step 2.1: Assign WCS
        infiles = self.assign_wcs_solution(infiles)

        # Step 2.2: Flat Field (applied before extract_2d for Grism)
        infiles = self.apply_flat_field(infiles)

        # Step 2.3: Extract 2D
        infiles = self.extract_2d_spectrum(infiles)

        # Step 2.4: Source Type (srctype)
        infiles = self.srctype_determination(infiles)

        # Step 2.5: Stray Light Correction
        infiles = self.correct_stray_light(infiles)

        # Step 2.6: Fringe Correction
        infiles = self.correct_fringe(infiles)

        # Step 2.7: Path Loss Correction
        infiles = self.correct_path_loss(infiles)

        # Step 2.8: Bar Shadow Correction
        infiles = self.correct_bar_shadow(infiles)

        # Step 2.9: WFSS Contamination Correction
        infiles = self.correct_wfss_contamination(infiles)

        # Step 2.10: Photometric Calibration
        infiles = self.apply_photometric_calibration(infiles)

        # Save the final calibrated product
        # Always TSO-style integration products
        infiles = self.save_outputs('_calints.fits', infiles)

        # Step 2.11: Extract 1D (x1dints) after photom
        x1d_files = self.extract_1d_spectrum(infiles)
        # Save 1D extracted spectra
        x1d_files = self.save_outputs('_x1dints.fits', x1d_files)
        # ---------------------------------------------------------------------
        # Last step is to save the outputs for return, do not remove this
        self.add_output(infiles)
        self.add_calib('X1D', x1d_files)


class NircamMultistripe(NircamGrism):
    """
    NIRCam Multistripe spectroscopic mode processing.

    Multistripe is a multi-channel spectroscopic configuration.
    Processing is similar to Grism but optimized for multi-stripe setup.
    """
    def __init__(self, params):
        super().__init__(params)
        self.instrument = 'JWST.NIRCAM.MULTISTRIPE'


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================

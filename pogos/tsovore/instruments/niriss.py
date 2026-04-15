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
from pogos.tsovore.dev import loic_niriss
from pogos.tsovore.science import tso

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
class NirissSoss(ts_default.JWST, tso.Tso):
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
        infiles = self.handle_input_data()

        # =====================================================================
        # LEVEL 1: Detector-Level Processing (calwebb_detector1)
        # =====================================================================
        msg = ('Applying Level 1 (detector) calibration steps to NIRISS '
               'SOSS data')
        WLOG(self.params, 'info', msg)

        # Initialize Detector Data (bundled: group_scale + dq_init + saturation)
        infiles = self.initialize_detector_data(infiles)
        # This is an example for Loic
        # infiles = loic_niriss.loic_group_scale_step(self, infiles)

        # Get the dictionary for the pastasoss reference file (formerly spectrace)
        # spectracedict contains x_o1, y_o1, wave_o1 and throughput_o1
        # and for all 3 orders.
        infiles = self.get_spectrace(infiles)

        # Build a deep stack for each group of the TSO.
        infiles = self.stack_multisegments(infiles)
        # TODO: no need to return deepstack_grouplevel here but I will need a
        #       internal way of naming this kind of "calibration" files.
        # TODO: create more functions like it to create masks of
        #       different flavors

        # Refpix Step
        infiles = self.apply_reference_pixel_correction(infiles)

        # Linearity Step
        infiles = self.apply_linearity_correction(infiles)

        # Jump Step
        infiles = self.detect_and_flag_jumps(infiles)

        # Ramp Fit Step
        infiles = self.fit_signal_ramps(infiles)

        # Gain Scale Step → save _rateints.fits
        infiles = self.apply_gain_scaling(infiles)

        # Save RATEINTS
        infiles = self.save_outputs('_rateints.fits', infiles)

        # =====================================================================
        # LEVEL 2: Spectroscopic Processing (calwebb_spec2 - SOSS specific)
        # =====================================================================
        msg = ('Applying Level 2 (spectroscopic) calibration steps to NIRISS '
               'SOSS data')
        WLOG(self.params, 'info', msg)

        # Step 2.1: Assign WCS
        infiles = self.assign_wcs_solution(infiles)

        # Step 2.2: Flat Field
        infiles = self.apply_flat_field(infiles)

        # Step 2.3: Background Subtraction (usually skipped for TSO)
        # infiles = self.subtract_background(infiles)
        #TODO: Loic to implement a custom step for background subtraction
        # it will either call the current default step or the custom step.
        # and the yaml file will dictate which is used.

        # Loic's looooooooong method to flag and remove bad pixels
        infiles = self.soss_correct_badpix(infiles)

        # Step 2.4: Source Type (srctype)
        infiles = self.srctype_determination(infiles)

        # Save cal _calints.fits
        infiles = self.save_outputs('_calints.fits', infiles)

        # Step 2.5: Extract 1D Spectrum → save _x1dints.fits
        x1d_files = self.extract_1d_spectrum(infiles)

        # Step 2.6: Photometric Calibration on infiles
        x1d_files = self.apply_photometric_calibration(x1d_files)

        # Save 1D extracted spectra
        x1d_files = self.save_outputs('_x1dints.fits', x1d_files)

        # ---------------------------------------------------------------------
        # Last step is to save the outputs for return, do not remove this
        self.add_output(infiles)
        self.add_calib('X1D', x1d_files)


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
    print("To run, type at the command line in the proper conda environment, for example:")
    print("pogos_run --yamlfile DEMO_T1b.20220718.JWST.NIRISS.SOSS.TSOVORE.yaml")

# =============================================================================
# End of code
# =============================================================================

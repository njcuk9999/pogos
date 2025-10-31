#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2025-10-27 at 11:53

@author: cook
"""
from aperocore.constants import param_functions
from aperocore.core import drs_log
from pogos.core import base as pogos_base
from pogos.tsovore.instruments import default as ts_default

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'tsovore.instruments.default'
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
    def __init__(self, params):
        super().__init__(params, instrument='JWST.MIRI.IMAGING')

    def process(self):
        """
        Process the MIRI Imaging data
        """
        # Initialize processing
        self.handle_input_data()

        # ---------------------------------------------------------------------
        # Level 1 Processing Steps
        # ---------------------------------------------------------------------
        # Step 1.1 - 1.4:
        #         Load the input data
        #         GroupScaleStep
        #         DQInitStep
        #         EmiCorrStep
        #         SaturationStep
        self.initialize_detector_data()

        # Step 1.5: IPCSTep
        self.apply_interpixel_capacitance()

        # Step 1.6: FirstFrameStep
        # TODO: Replace this step with a copy and simply change that
        #       so that more than 1 frame is set to DO NOT USE
        #       (if that is what Etienne needs)
        self.remove_first_frame_signal()

        # Step 1.7: LastFrameStep
        self.remove_last_frame_signal()

        # Step 1.8: ResetStep
        self.correct_reset_anomaly()

        # Step 1.9: LinearityStep
        self.apply_linearity_correction()

        # Step 1.10: RscdStep
        self.apply_rscd_correction()

        # Step 1.11: DarkCurrentStep
        self.subtract_dark_current()

        # Step 1.12: RefPixStep
        self.apply_reference_pixel_correction()

        # Step 1.13: ChargeMigration Step
        # The ChargeMigrationStep is by default skipped when
        # executed on these data
        # self.correct_charge_migration()

        # Step 1.14: JumpStep
        self.detect_and_flag_jumps()

        # Step 1.15: CleanFlickerStep
        # The CleanFlickerStep is by default skipped when executed on these data
        # self.remove_flicker_noise()

        # Step 1.16: RampFitStep
        self.fit_signal_ramps()

        # Step 1.17: GainScaleStep
        self.apply_gain_scaling()

        # ---------------------------------------------------------------------
        # Level 2 Processing Steps
        # ---------------------------------------------------------------------
        # Step 2.1: BackgroundStep
        # The background step in order to work needs a list of *** dithered ***
        # exposures which we don't have with TSO. Skip that step.
        # self.subtract_background()

        # Step 2.2: AssignWcsStep
        self.assign_wcs_solution()

        # Step 2.3: FlatFieldStep
        self.apply_flat_field()

        # Step 2.4: PhotomStep
        self.apply_photometric_calibration()



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

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Default Instument Class for TSOVore

Created on 2025-10-27 at 11:39

@author: cook
"""
import os

from aperocore.constants import param_functions
from aperocore.core import drs_log
from pogos.core import base as pogos_base
from pogos.tsovore.core import base as tsovore_base

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
# Not implemented message
NOT_IMPLEMENTED_MSG = "Method {0} not implemented for instrument {1}"


# =============================================================================
# Define instrument class
# =============================================================================
class Instrument:
    """
    Base instrument class - must have all methods given in
    any child class
    """
    def __init__(self, params: ParamDict, instrument: str = 'None'):
        # set the instrument name
        self.instrument = instrument
        # push params into class
        self.params = params
        # store variables to be used throughout the code
        self.variables = ParamDict()

        pass

    def process(self):
        """
        Process TSOvore for this instrument

        :return:
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.process"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def handle_input_data(self):
        """
        Handle input data - this should work for all instruments/modes
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.handle_input_data"
        # get the input file directory
        input_dir = self.params['PATHS.INPUT_PATH']
        # Get the input files
        input_files = self.params['INPUTS.FILES']
        # Storage for absolute file paths
        input_absfiles = []
        input_prefixes = []
        # update with full paths
        for filename in input_files:
            # deal with filename existing (as absolute path from input)
            if os.path.isabs(filename):
                absfile = filename
            else:
                # construct absolute path
                absfile = os.path.join(input_dir, filename)
                # check that file is on disk
                if not os.path.isfile(absfile):
                    emsg = f'Input file {absfile} does not exist on disk'
                    raise tsovore_base.TSOvoreException(emsg)
            # append to list
            input_absfiles.append(absfile)
            # add basename to list
            basename = os.path.basename(filename)
            input_prefixes.append(basename.split('_uncal')[0])
        # get the number of segments
        nsegments = len(input_absfiles)
        # ----------------------------------------------------------------------
        # print progress
        msg = 'Found {0} input files'
        WLOG(self.params, 'info', msg.format(nsegments))
        # ----------------------------------------------------------------------
        # push into variables
        self.variables.set('ABSFILES', input_absfiles, source=func_name)
        self.variables.set('PREFIXES', input_prefixes, source=func_name)
        self.variables.set('NSEGMENTS', nsegments, source=func_name)
        self.variables.set('LAST', input_absfiles, source=func_name)

    def initialize_detector_data(self):
        """
        Handles data load and initial detector corrections
        (scaling, DQ flags, emission correction, saturation map).

        """
        # set function name
        func_name = f"{__NAME__}.Instrument.initialize_detector_data"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def apply_interpixel_capacitance(self):
        """
        Corrects for interpixel capacitance effects.
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.apply_interpixel_capacitance"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def remove_first_frame_signal(self):
        """
        Removes bias introduced in first frame of each integration.
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.remove_first_frame_signal"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def remove_last_frame_signal(self):
        """
        Removes last-frame pedestal effect.
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.remove_last_frame_signal"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def correct_reset_anomaly(self):
        """
        Fixes reset anomaly across integrations.
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.correct_reset_anomaly"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def apply_linearity_correction(self):
        """
        Corrects for detector nonlinearity.
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.apply_linearity_correction"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def apply_rscd_correction(self):
        """
        Applies reset switch charge decay correction.
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.apply_rscd_correction"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def subtract_dark_current(self):
        """
        Removes dark current signal using reference darks.
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.subtract_dark_current"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def apply_reference_pixel_correction(self):
        """
        Corrects readout noise using reference pixels.
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.apply_reference_pixel_correction"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def correct_charge_migration(self):
        """
        Mitigates charge migration between pixels.
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.correct_charge_migration"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def detect_and_flag_jumps(self):
        """
        Identifies and flags cosmic ray hits (jumps) in the data.
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.detect_and_flag_jumps"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def remove_flicker_noise(self):
        """
        Removes flicker noise from the data.
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.remove_flicker_noise"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def fit_signal_ramps(self):
        """
        Fits slopes to groups to derive count rates.
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.fit_signal_ramps"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def apply_gain_scaling(self):
        """
        Scales results to correct gain differences.
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.apply_gain_scaling"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def subtract_background(self):
        """
        Removes background using reference or modeled backgrounds.
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.subtract_background"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def assign_wcs_solution(self):
        """
        Adds WCS (world coordinate system) information.
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.assign_wcs_solution"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def apply_flat_field(self):
        """
        Corrects pixel-to-pixel sensitivity variations.
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.apply_flat_field"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def apply_photometric_calibration(self):
        """
        Converts data units to physical flux units.
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.apply_photometric_calibration"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)


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

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Default Instument Class for TSOVore

Created on 2025-10-27 at 11:39

@author: cook
"""
import os
import shutil
from typing import Any, Dict, Tuple

import numpy as np
from jwst import datamodels
from jwst.assign_wcs import AssignWcsStep
from jwst.background import BackgroundStep
from jwst.barshadow import BarShadowStep
from jwst.charge_migration import ChargeMigrationStep
from jwst.clean_flicker_noise import CleanFlickerNoiseStep
from jwst.dark_current import DarkCurrentStep
from jwst.dq_init import DQInitStep
from jwst.emicorr import EmiCorrStep
from jwst.extract_1d import Extract1dStep
from jwst.extract_2d import Extract2dStep
from jwst.firstframe import FirstFrameStep
from jwst.flatfield import FlatFieldStep
from jwst.fringe import FringeStep
from jwst.gain_scale import GainScaleStep
from jwst.group_scale import GroupScaleStep
from jwst.ipc import IPCStep
from jwst.jump import JumpStep
from jwst.lastframe import LastFrameStep
from jwst.linearity import LinearityStep
from jwst.master_background import MasterBackgroundStep
from jwst.pathloss import PathLossStep
from jwst.photom import PhotomStep
from jwst.ramp_fitting import RampFitStep
from jwst.refpix import RefPixStep
from jwst.resample import ResampleStep
from jwst.reset import ResetStep
from jwst.rscd import RscdStep
from jwst.saturation import SaturationStep
from jwst.srctype import SourceTypeStep
from jwst.straylight import StraylightStep
from jwst.superbias import SuperBiasStep
from jwst.wavecorr import WavecorrStep
from jwst.wfss_contam import WfssContamStep

from aperocore.constants import param_functions
from aperocore.core import drs_log
from pogos.core import base as pogos_base
from pogos.tsovore.core import base as ts_base

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
        # set function name
        func_name = f"{__NAME__}.Instrument.__init__"
        # set the instrument name
        self.instrument = instrument
        # push params into class
        self.params = params
        self.tparams = params.get('TSOVORE')
        # store variables to be used throughout the code
        self.variables = ParamDict()
        # push into variables
        self.variables.set('ABSFILES', [], source=func_name)
        self.variables.set('PREFIXES', [], source=func_name)
        self.variables.set('NSEGMENTS', 0, source=func_name)
        # lock variables to avoid misuse
        self.variables.lock()

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

    # -------------------------------------------------------------------------
    # Define science methods
    # -------------------------------------------------------------------------
    def handle_input_data(self) -> list:
        """
        Handle input data - this should work for all instruments/modes

        :return: list[str], list of input files
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.handle_input_data"
        # raise not implemented error (implemented in JWST)
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def initialize_detector_data(self, infiles: list) -> list:
        """
        Handles data load and initial detector corrections
        (scaling, DQ flags, emission correction, saturation map).

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.initialize_detector_data"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def apply_interpixel_capacitance(self, infiles: list) -> list:
        """
        Corrects for interpixel capacitance effects.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.apply_interpixel_capacitance"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def remove_first_frame_signal(self, infiles: list) -> list:
        """
        Removes bias introduced in first frame of each integration.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.remove_first_frame_signal"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def remove_last_frame_signal(self, infiles: list) -> list:
        """
        Removes last-frame pedestal effect.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.remove_last_frame_signal"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def correct_reset_anomaly(self, infiles: list) -> list:
        """
        Fixes reset anomaly across integrations.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.correct_reset_anomaly"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def apply_linearity_correction(self, infiles: list) -> list:
        """
        Corrects for detector nonlinearity.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.apply_linearity_correction"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def apply_rscd_correction(self, infiles: list) -> list:
        """
        Applies reset switch charge decay correction.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.apply_rscd_correction"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def subtract_dark_current(self, infiles: list) -> list:
        """
        Removes dark current signal using reference darks.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.subtract_dark_current"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def apply_reference_pixel_correction(self, infiles: list) -> list:
        """
        Corrects readout noise using reference pixels.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.apply_reference_pixel_correction"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def correct_charge_migration(self, infiles: list) -> list:
        """
        Mitigates charge migration between pixels.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.correct_charge_migration"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def detect_and_flag_jumps(self, infiles: list) -> list:
        """
        Identifies and flags cosmic ray hits (jumps) in the data.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.detect_and_flag_jumps"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def remove_flicker_noise(self, infiles: list) -> list:
        """
        Removes flicker noise from the data.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.remove_flicker_noise"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def fit_signal_ramps(self, infiles: list) -> list:
        """
        Fits slopes to groups to derive count rates.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.fit_signal_ramps"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def apply_gain_scaling(self, infiles: list) -> list:
        """
        Scales results to correct gain differences.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.apply_gain_scaling"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def subtract_background(self, infiles: list) -> list:
        """
        Removes background using reference or modeled backgrounds.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.subtract_background"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def assign_wcs_solution(self, infiles: list) -> list:
        """
        Adds WCS (world coordinate system) information.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.assign_wcs_solution"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def apply_flat_field(self, infiles: list) -> list:
        """
        Corrects pixel-to-pixel sensitivity variations.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.apply_flat_field"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def apply_photometric_calibration(self, infiles: list) -> list:
        """
        Converts data units to physical flux units.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.apply_photometric_calibration"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def group_scale_step(self, infiles: list) -> list:
        """
        Scale group data to account for on-chip amplifier effects.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.group_scale_step"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def dq_init_step(self, infiles: list) -> list:
        """
        Initialize data quality flags.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.dq_init_step"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def emicorr_step(self, infiles: list) -> list:
        """
        Apply EMI (electro-magnetic interference) corrections.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.emicorr_step"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def saturation_step(self, infiles: list) -> list:
        """
        Flag saturated pixels.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.saturation_step"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def subtract_superbias(self, infiles: list) -> list:
        """
        Subtract superbias reference for NIR instruments.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.subtract_superbias"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def picture_frame_step(self, infiles: list) -> list:
        """
        Correct for picture frame effect.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.picture_frame_step"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def correct_persistence(self, infiles: list) -> list:
        """
        Correct for charge persistence between integrations.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.correct_persistence"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def extract_2d_spectrum(self, infiles: list) -> list:
        """
        Extract 2D spectrum from detector image.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.extract_2d_spectrum"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def extract_1d_spectrum(self, infiles: list) -> list:
        """
        Extract 1D spectrum from 2D data.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.extract_1d_spectrum"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def srctype_determination(self, infiles: list) -> list:
        """
        Determine source type for photometric calibration.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.srctype_determination"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def correct_stray_light(self, infiles: list) -> list:
        """
        Remove stray light from the data.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.correct_stray_light"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def correct_fringe(self, infiles: list) -> list:
        """
        Remove fringe patterns from the data.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.correct_fringe"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def correct_path_loss(self, infiles: list) -> list:
        """
        Correct for path loss through the optical system.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.correct_path_loss"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def correct_bar_shadow(self, infiles: list) -> list:
        """
        Correct for bar shadow effect.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.correct_bar_shadow"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def correct_wfss_contamination(self, infiles: list) -> list:
        """
        Correct for WFSS contamination.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.correct_wfss_contamination"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def correct_wavelength(self, infiles: list) -> list:
        """
        Correct wavelength calibration.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.correct_wavelength"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def subtract_master_background(self, infiles: list) -> list:
        """
        Subtract master background for NIRSpec MOS data.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.subtract_master_background"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def measure_target_centroid(self, infiles: list) -> list:
        """
        Measure target centroid position.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.measure_target_centroid"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def correct_residual_fringe(self, infiles: list) -> list:
        """
        Correct for residual fringe patterns (MIRI-specific).

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.correct_residual_fringe"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def resample_images(self, infiles: list) -> list:
        """
        Resample images to a common grid.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.resample_images"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    # -------------------------------------------------------------------------
    # Define additional methods (worker functions)
    # -------------------------------------------------------------------------
    def get_output_path(self, it: int, output_dir: str,
                        output_filename: Any) -> str:
        """
        Construct the output file path

        :param it: int, the iteration number
        :param output_dir: str, the output directory
        :param output_filename: str, the output filename
        :return: str, the absolute path to the output file
        """
        # construct absolute path to filename
        absfile = os.path.join(output_dir, output_filename)
        return absfile

    def save_outputs(self, suffix: str, infiles: list):
        """
        Rename/copy the current files to have a given suffix.

        :param suffix: str, the suffix to add to the filename
        :param infiles: list[str], list of files to copy
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.rename_results"
        prefixes = self.variables['PREFIXES']
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # storage for OUT variable
        out_files = []
        # loop around files
        for it, filename in enumerate(infiles):
            # construct new filename
            new_base_name = prefixes[it] + suffix
            new_filename = str(os.path.join(datadir, new_base_name))
            # deal with files not existing (not allowed)
            if not os.path.exists(filename):
                wmsg = ('File {0} does not exist on disk. Cannot add to out. '
                        'This may crash future steps.').format(filename)
                WLOG(self.params, 'warning', wmsg)
                return out_files
            else:
                msg = ('Copying file {0} to {1}').format(filename,
                                                         new_filename)
                WLOG(self.params, 'info', msg)
            # copy the file
            shutil.copy(filename, new_filename)
            # save files to list
            out_files.append(new_filename)

        return out_files

    def remove_intermediate_files(self, filepath: str):
        """
        Remove intermediate files to save disk space

        :param filepath: str, the path to the file to remove
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.remove_intermediate_files"
        # get parameters from params
        remove_intermediates = self.tparams['INPUTS.REMOVE_INTERMEDIATES']
        # check if we need to remove intermediate files
        if remove_intermediates and os.path.exists(filepath):
            # remove the file
            os.remove(filepath)

    def from_step_args(self, func_name: str) -> Tuple[bool, str, Dict[str, Any], str]:
        """
        Get step arguments from params

        :param func_name: str, the function name calling this function

        :return: tuple, (run_step: bool, flavour: str, kwargs: dict,
                 suffix: str)
        """
        # get step name from function name
        step_name = func_name.split('.')[-1].upper()
        step_arg = f'STEP.{step_name}'
        # ---------------------------------------------------------------------
        # see if we have the step in params
        if step_arg not in self.tparams:
            emsg = ('"{0}" not found in parameters').format(step_arg)
            eargs = [step_name]
            raise ts_base.TSOvoreException(emsg.format(*eargs))
        # ---------------------------------------------------------------------
        # get run step
        run_step = self.tparams[f'{step_arg}'].get('RUN', True)
        # get flavour
        flavour = self.tparams[f'{step_arg}'].get('FLAVOUR', 'None')
        # get kwargs
        kwargs = self.tparams[f'{step_arg}'].get('KWARGS', dict())
        # get the suffix
        suffix = self.tparams[f'{step_arg}'].get('SUFFIX', None)
        # ---------------------------------------------------------------------
        # if we are running this step print message
        if run_step:
            msg = ('\n\nRunning {0} flavour={1}').format(
                step_name, flavour)
            mlevel = 'info'
        else:
            msg = ('\n\nSkipping "{0}" [{1}.RUN=False]').format(
                step_name, step_arg)
            mlevel = 'warning'
        sep = '*' * 50
        WLOG(self.params, mlevel, sep)
        WLOG(self.params, mlevel, msg)
        WLOG(self.params, mlevel, sep)
        # ---------------------------------------------------------------------
        # return values
        return run_step, flavour, kwargs, suffix

    def skip_step(self, run_step: bool, step_name: str,
                  suffix: str, infiles: list):
        """
        Decide whether to skip a step based on existing files and parameters

        :param run_step: bool, whether to run the step (from params)
        :param step_name: str, the name of the step
        :param suffix: str, the suffix expected for output files
        :param infiles: list[str], the input files
        :return: tuple (bool, list[str]), whether to skip and list of
                 expected files
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.skip_step"
        # if we are already not running step then we don't need to check skips
        if not run_step:
            return False, infiles
        # skip if we have no suffix
        if suffix is None:
            return run_step, infiles
        # skip if we are not skipping processed files
        if not self.tparams['INPUTS.SKIP_PROCESSED_FILES']:
            return run_step, infiles
        # get variables from self
        prefixes = self.variables['PREFIXES']
        # assume all files are found
        all_found = True
        expected_files = []
        # loop around all infiles and check if the expected output
        # file exists
        for it in range(len(infiles)):
            # construct expected output filename
            expected_base_name = prefixes[it] + suffix
            expected_filename = os.path.join(self.tparams['PATHS.TEMP_PATH'],
                                             expected_base_name)
            # store expected filename
            expected_files.append(expected_filename)
            # check if file exists
            if not os.path.isfile(expected_filename):
                all_found = False
        # if all found then run_step is False and we return expected files
        if all_found:
            # update run step
            run_step = False
            # print message to user
            msg = ('\tINPUTS.SKIP_PROCESSED_FILES=True\n\tAll expected '
                   'output files found with suffix "{0}".'
                   '\n\tSkipping step "{1}".').format(suffix, step_name)
            WLOG(self.params, '', msg)
            return run_step, expected_files

        return run_step, infiles

    def save_model_with_suffix(self, model, output_dir: str, suffix: str,
                               iteration: int) -> str:
        """
        Save a datamodel to disk with the given suffix.

        Must be implemented in subclasses for specific data formats.

        :param model: datamodel object to save
        :param output_dir: str, directory to save file to
        :param suffix: str, the suffix to add to the filename
        :param iteration: int, the iteration number
        :return: str, the path to the saved file
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.save_model_with_suffix"
        # raise not implemented error (implemented in JWST)
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def _force_float(self, result):
        """
        Force all uint16 arrays in datamodel to float32.

        Must be implemented in subclasses for specific data formats.

        :param result: datamodel with uint16 arrays
        :return: datamodel with float32 arrays
        """
        # set function name
        func_name = f"{__NAME__}.Instrument._force_float"
        # raise not implemented error (implemented in JWST)
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)


class JWST(Instrument):
    """
    JWST Instrument class
    """
    def __init__(self, params: ParamDict, instrument: str = 'JWST.NONE'):
        super().__init__(params, instrument)

    def handle_input_data(self) -> list:
        """
        Handle input data - this should work for all JWST instruments/modes

        :return: list[str], list of absolute paths to input files
        """
        # set function name
        func_name = f"{__NAME__}.JWST.handle_input_data"
        # get the input file directory
        input_dir = self.tparams['PATHS.INPUT_PATH']
        # Get the input files
        input_files = self.tparams['INPUTS.FILES']
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
                    emsg = 'Input file {0} does not exist on disk'.format(
                        absfile)
                    raise ts_base.TSOvoreException(emsg)
            # append to list
            input_absfiles.append(absfile)
            # add basename to list
            basename = os.path.basename(filename)
            input_prefixes.append(basename.split('_uncal')[0])
        # get the number of segments
        nsegments = len(input_absfiles)
        # ----------------------------------------------------------------------
        # print progress
        msg = 'Found {0} input files'.format(nsegments)
        WLOG(self.params, 'info', msg)
        # ----------------------------------------------------------------------
        # push into variables
        self.variables.set('ABSFILES', input_absfiles, source=func_name)
        self.variables.set('PREFIXES', input_prefixes, source=func_name)
        self.variables.set('NSEGMENTS', nsegments, source=func_name)

        return input_absfiles

    def process(self):
        """
        Process the data

        Must be implemented in child classes
        """
        # set function name
        func_name = f"{__NAME__}.JWST.process"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    # =========================================================================
    # Level 1 detector processing steps (individual step callers)
    # =========================================================================
    def initialize_detector_data(self, infiles: list) -> list:
        """
        Initialize detector data models.
        (group scale step + dq init step + emicorr step + saturation step)

        These are bundled to avoid problems with steps that are skipped
        (and going between int arrays to float arrays).

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.JWST.initialize_detector_data"
        # get params from step constant
        run_step, flavour, kwargs, suffix = self.from_step_args(func_name)
        # deal with skipping step
        run_step, infiles = self.skip_step(run_step, 'INITIALIZE_DETECTOR_DATA',
                                           suffix, infiles)
        # deal with not running this step
        if not run_step:
            return infiles
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # storage for output files
        outfiles = []
        # loop around infiles
        for it, filename in enumerate(infiles):
            # Read input segments files from disk
            input_data = datamodels.open(filename)
            # Execute the bundled steps in sequence
            # Step 1: Group Scale (even if skipped converts ints --> floats)
            result = GroupScaleStep.call(input_data, save_results=False)
            # Step 2: DQ Init
            result = DQInitStep.call(result, save_results=False)
            # Step 3: EMI Correction
            result = EmiCorrStep.call(result, save_results=False)
            # Step 4: Saturation (save to disk)
            result = SaturationStep.call(result, output_dir=datadir,
                                         save_results=True)
            # To limit disk usage, erase the file from the previous step
            self.remove_intermediate_files(filename)
            # get output path
            outfile = self.get_output_path(it, datadir, result.meta.filename)
            outfiles.append(outfile)

        return outfiles

    def group_scale_step(self, infiles: list) -> list:
        """
        Scale group data to account for on-chip amplifier effects.

        DEPRECATED: This step is now bundled in initialize_detector_data()
        along with dq_init_step, emicorr_step, and saturation_step.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # Raise error - this step should not be called directly anymore
        emsg = ('group_scale_step is deprecated. Use initialize_detector_data() '
                'instead, which bundles group_scale + dq_init + emicorr + saturation.')
        raise ts_base.TSOvoreException(emsg)

    def dq_init_step(self, infiles: list) -> list:
        """
        Initialize data quality flags.

        DEPRECATED: This step is now bundled in initialize_detector_data()
        along with group_scale_step, emicorr_step, and saturation_step.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # Raise error - this step should not be called directly anymore
        emsg = ('dq_init_step is deprecated. Use initialize_detector_data() '
                'instead, which bundles group_scale + dq_init + emicorr + saturation.')
        raise ts_base.TSOvoreException(emsg)

    def emicorr_step(self, infiles: list) -> list:
        """
        Apply EMI (electro-magnetic interference) corrections.

        DEPRECATED: This step is now bundled in initialize_detector_data()
        along with group_scale_step, dq_init_step, and saturation_step.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # Raise error - this step should not be called directly anymore
        emsg = ('emicorr_step is deprecated. Use initialize_detector_data() '
                'instead, which bundles group_scale + dq_init + emicorr + saturation.')
        raise ts_base.TSOvoreException(emsg)

    def saturation_step(self, infiles: list) -> list:
        """
        Flag saturated pixels.

        DEPRECATED: This step is now bundled in initialize_detector_data()
        along with group_scale_step, dq_init_step, and emicorr_step.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # Raise error - this step should not be called directly anymore
        emsg = ('saturation_step is deprecated. Use initialize_detector_data() '
                'instead, which bundles group_scale + dq_init + emicorr + saturation.')
        raise ts_base.TSOvoreException(emsg)

    def apply_interpixel_capacitance(self, infiles: list) -> list:
        """
        Corrects for interpixel capacitance effects.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.JWST.apply_interpixel_capacitance"
        # ---------------------------------------------------------------------
        # get params from step constant
        run_step, flavour, kwargs, suffix = self.from_step_args(func_name)
        # deal with skipping step
        run_step, infiles = self.skip_step(
            run_step, 'APPLY_INTERPIXEL_CAPACITANCE', suffix, infiles)
        # deal with not running this step
        if not run_step:
            return infiles
        # ---------------------------------------------------------------------
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # storage for output files
        outfiles = []
        # loop around infiles
        for it, filename in enumerate(infiles):
            # Read input segments files from disk
            input_data = datamodels.open(filename)
            result = IPCStep.call(input_data, output_dir=datadir,
                                  save_results=True, **kwargs)
            # To limit disk usage, erase the file from the previously saved step
            self.remove_intermediate_files(filename)
            # get output path
            outfile = self.get_output_path(it, datadir, result.meta.filename)
            outfiles.append(outfile)

        return outfiles

    def remove_first_frame_signal(self, infiles: list) -> list:
        """
        Removes bias introduced in first frame of each integration.

        All this does is set the DQflag of the first frame of every integration
        to DO NOT USE provided that the integrations have more than 3 usable 
        (non-saturated group).

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.JWST.remove_first_frame_signal"
        # ---------------------------------------------------------------------
        # get params from step constant
        run_step, flavour, kwargs, suffix = self.from_step_args(func_name)
        # deal with skipping step
        run_step, infiles = self.skip_step(
            run_step, 'REMOVE_FIRST_FRAME_SIGNAL', suffix, infiles)
        # deal with not running this step
        if not run_step:
            return infiles
        # ---------------------------------------------------------------------
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # storage for output files
        outfiles = []
        # loop around infiles
        for it, filename in enumerate(infiles):
            # Read input segments files from disk
            input_data = datamodels.open(filename)
            result = FirstFrameStep.call(input_data, output_dir=datadir,
                                         save_results=True, **kwargs)
            # To limit disk usage, erase the file from the previously saved step
            self.remove_intermediate_files(filename)
            # get output path
            outfile = self.get_output_path(it, datadir, result.meta.filename)
            outfiles.append(outfile)

        return outfiles

    def remove_last_frame_signal(self, infiles: list) -> list:
        """
        Removes last-frame pedestal effect.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.JWST.remove_last_frame_signal"
        # ---------------------------------------------------------------------
        # get params from step constant
        run_step, flavour, kwargs, suffix = self.from_step_args(func_name)
        # deal with skipping step
        run_step, infiles = self.skip_step(
            run_step, 'REMOVE_LAST_FRAME_SIGNAL', suffix, infiles)
        # deal with not running this step
        if not run_step:
            return infiles
        # ---------------------------------------------------------------------
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # storage for output files
        outfiles = []
        # loop around infiles
        for it, filename in enumerate(infiles):
            # Read input segments files from disk
            input_data = datamodels.open(filename)
            result = LastFrameStep.call(input_data, output_dir=datadir,
                                        save_results=True, **kwargs)
            # To limit disk usage, erase the file from the previously saved step
            self.remove_intermediate_files(filename)
            # get output path
            outfile = self.get_output_path(it, datadir, result.meta.filename)
            outfiles.append(outfile)

        return outfiles

    def correct_reset_anomaly(self, infiles: list) -> list:
        """
        Fixes reset anomaly across integrations.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.JWST.correct_reset_anomaly"
        # ---------------------------------------------------------------------
        # get params from step constant
        run_step, flavour, kwargs, suffix = self.from_step_args(func_name)
        # deal with skipping step
        run_step, infiles = self.skip_step(
            run_step, 'CORRECT_RESET_ANOMALY', suffix, infiles)
        # deal with not running this step
        if not run_step:
            return infiles
        # ---------------------------------------------------------------------
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # storage for output files
        outfiles = []
        # loop around infiles
        for it, filename in enumerate(infiles):
            # Read input segments files from disk
            input_data = datamodels.open(filename)
            result = ResetStep.call(input_data, output_dir=datadir,
                                    save_results=True, **kwargs)
            # To limit disk usage, erase the file from the previously saved step
            self.remove_intermediate_files(filename)
            # get output path
            outfile = self.get_output_path(it, datadir, result.meta.filename)
            outfiles.append(outfile)

        return outfiles

    def apply_linearity_correction(self, infiles: list) -> list:
        """
        Corrects for detector nonlinearity.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.JWST.apply_linearity_correction"
        # ---------------------------------------------------------------------
        # get params from step constant
        run_step, flavour, kwargs, suffix = self.from_step_args(func_name)
        # deal with skipping step
        run_step, infiles = self.skip_step(
            run_step, 'APPLY_LINEARITY_CORRECTION', suffix, infiles)
        # deal with not running this step
        if not run_step:
            return infiles
        # ---------------------------------------------------------------------
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # storage for output files
        outfiles = []
        # loop around infiles
        for it, filename in enumerate(infiles):
            # Read input segments files from disk
            input_data = datamodels.open(filename)
            result = LinearityStep.call(input_data, output_dir=datadir,
                                        save_results=True, **kwargs)
            # To limit disk usage, erase the file from the previously saved step
            self.remove_intermediate_files(filename)
            # get output path
            outfile = self.get_output_path(it, datadir, result.meta.filename)
            outfiles.append(outfile)

        return outfiles

    def apply_rscd_correction(self, infiles: list) -> list:
        """
        Applies reset switch charge decay correction.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.JWST.apply_rscd_correction"
        # ---------------------------------------------------------------------
        # get params from step constant
        run_step, flavour, kwargs, suffix = self.from_step_args(func_name)
        # deal with skipping step
        run_step, infiles = self.skip_step(
            run_step, 'APPLY_RSCD_CORRECTION', suffix, infiles)
        # deal with not running this step
        if not run_step:
            return infiles
        # ---------------------------------------------------------------------
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # storage for output files
        outfiles = []
        # loop around infiles
        for it, filename in enumerate(infiles):
            # Read input segments files from disk
            input_data = datamodels.open(filename)
            result = RscdStep.call(input_data, output_dir=datadir,
                                   save_results=True, **kwargs)
            # To limit disk usage, erase the file from the previously saved step
            self.remove_intermediate_files(filename)
            # get output path
            outfile = self.get_output_path(it, datadir, result.meta.filename)
            outfiles.append(outfile)

        return outfiles

    def subtract_dark_current(self, infiles: list) -> list:
        """
        Removes dark current signal using reference darks.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.JWST.subtract_dark_current"
        # ---------------------------------------------------------------------
        # get params from step constant
        run_step, flavour, kwargs, suffix = self.from_step_args(func_name)
        # deal with skipping step
        run_step, infiles = self.skip_step(
            run_step, 'SUBTRACT_DARK_CURRENT', suffix, infiles)
        # deal with not running this step
        if not run_step:
            return infiles
        # ---------------------------------------------------------------------
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # storage for output files
        outfiles = []
        # loop around infiles
        for it, filename in enumerate(infiles):
            # Read input segments files from disk
            input_data = datamodels.open(filename)
            result = DarkCurrentStep.call(input_data, output_dir=datadir,
                                          save_results=True, **kwargs)
            # To limit disk usage, erase the file from the previously saved step
            self.remove_intermediate_files(filename)
            # get output path
            outfile = self.get_output_path(it, datadir, result.meta.filename)
            outfiles.append(outfile)

        return outfiles

    def apply_reference_pixel_correction(self, infiles: list) -> list:
        """
        Corrects readout noise using reference pixels.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.JWST.apply_reference_pixel_correction"
        # ---------------------------------------------------------------------
        # get params from step constant
        run_step, flavour, kwargs, suffix = self.from_step_args(func_name)
        # deal with skipping step
        run_step, infiles = self.skip_step(
            run_step, 'APPLY_REFERENCE_PIXEL_CORRECTION', suffix, infiles)
        # deal with not running this step
        if not run_step:
            return infiles
        # ---------------------------------------------------------------------
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # storage for output files
        outfiles = []
        # loop around infiles
        for it, filename in enumerate(infiles):
            # Read input segments files from disk
            input_data = datamodels.open(filename)
            result = RefPixStep.call(input_data, output_dir=datadir,
                                     save_results=True, **kwargs)
            # To limit disk usage, erase the file from the previously saved step
            self.remove_intermediate_files(filename)
            # get output path
            outfile = self.get_output_path(it, datadir, result.meta.filename)
            outfiles.append(outfile)

        return outfiles

    def correct_charge_migration(self, infiles: list) -> list:
        """
        Mitigates charge migration between pixels.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.JWST.correct_charge_migration"
        # ---------------------------------------------------------------------
        # get params from step constant
        run_step, flavour, kwargs, suffix = self.from_step_args(func_name)
        # deal with skipping step
        run_step, infiles = self.skip_step(
            run_step, 'CORRECT_CHARGE_MIGRATION', suffix, infiles)
        # deal with not running this step
        if not run_step:
            return infiles
        # ---------------------------------------------------------------------
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # storage for output files
        outfiles = []
        # loop around infiles
        for it, filename in enumerate(infiles):
            # Read input segments files from disk
            input_data = datamodels.open(filename)
            result = ChargeMigrationStep.call(input_data, output_dir=datadir,
                                              save_results=True, **kwargs)
            # To limit disk usage, erase the file from the previously saved step
            self.remove_intermediate_files(filename)
            # get output path
            outfile = self.get_output_path(it, datadir, result.meta.filename)
            outfiles.append(outfile)

        return outfiles

    def detect_and_flag_jumps(self, infiles: list) -> list:
        """
        Identifies and flags cosmic ray hits (jumps) in the data.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.JWST.detect_and_flag_jumps"
        # ---------------------------------------------------------------------
        # get params from step constant
        run_step, flavour, kwargs, suffix = self.from_step_args(func_name)
        # deal with skipping step
        run_step, infiles = self.skip_step(
            run_step, 'DETECT_AND_FLAG_JUMPS', suffix, infiles)
        # deal with not running this step
        if not run_step:
            return infiles
        # ---------------------------------------------------------------------
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # storage for output files
        outfiles = []
        # loop around infiles
        for it, filename in enumerate(infiles):
            # Read input segments files from disk
            input_data = datamodels.open(filename)
            result = JumpStep.call(input_data, output_dir=datadir,
                                   save_results=True, **kwargs)
            # Note: JumpStep may modify the input file instead of creating
            # new file
            # get output path
            outfile = self.get_output_path(it, datadir, result.meta.filename)
            outfiles.append(outfile)

        return outfiles

    def remove_flicker_noise(self, infiles: list) -> list:
        """
        Removes flicker noise from the data.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.JWST.remove_flicker_noise"
        # ---------------------------------------------------------------------
        # get params from step constant
        run_step, flavour, kwargs, suffix = self.from_step_args(func_name)
        # deal with skipping step
        run_step, infiles = self.skip_step(
            run_step, 'REMOVE_FLICKER_NOISE', suffix, infiles)
        # deal with not running this step
        if not run_step:
            return infiles
        # ---------------------------------------------------------------------
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # storage for output files
        outfiles = []
        # loop around infiles
        for it, filename in enumerate(infiles):
            # Read input segments files from disk
            input_data = datamodels.open(filename)
            result = CleanFlickerNoiseStep.call(input_data, output_dir=datadir,
                                                save_results=True, **kwargs)
            # To limit disk usage, erase the file from the previously saved step
            self.remove_intermediate_files(filename)
            # get output path
            outfile = self.get_output_path(it, datadir, result.meta.filename)
            outfiles.append(outfile)

        return outfiles

    def fit_signal_ramps(self, infiles: list) -> list:
        """
        Fits slopes to groups to derive count rates.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.JWST.fit_signal_ramps"
        # ---------------------------------------------------------------------
        # get params from step constant
        run_step, flavour, kwargs, suffix = self.from_step_args(func_name)
        # deal with skipping step
        run_step, infiles = self.skip_step(
            run_step, 'FIT_SIGNAL_RAMPS', suffix, infiles)
        # deal with not running this step
        if not run_step:
            return infiles
        # ---------------------------------------------------------------------
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # storage for output files
        outfiles = []
        # loop around infiles
        for it, filename in enumerate(infiles):
            # Read input segments files from disk
            input_data = datamodels.open(filename)
            rate, result = RampFitStep.call(input_data, output_dir=datadir,
                                            save_results=True, **kwargs)
            # To limit disk usage, erase the file from the previously saved step
            self.remove_intermediate_files(filename)
            # get output path
            outfile = self.get_output_path(it, datadir, result.meta.filename)
            outfiles.append(outfile)

        return outfiles

    def apply_gain_scaling(self, infiles: list) -> list:
        """
        Scales results to correct gain differences.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.JWST.apply_gain_scaling"
        # ---------------------------------------------------------------------
        # get params from step constant
        run_step, flavour, kwargs, suffix = self.from_step_args(func_name)
        # deal with skipping step
        run_step, infiles = self.skip_step(
            run_step, 'APPLY_GAIN_SCALING', suffix, infiles)
        # deal with not running this step
        if not run_step:
            return infiles
        # ---------------------------------------------------------------------
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # storage for output files
        outfiles = []
        # loop around infiles
        for it, filename in enumerate(infiles):
            # Read input segments files from disk
            input_data = datamodels.open(filename)
            result = GainScaleStep.call(input_data, output_dir=datadir,
                                        save_results=True, **kwargs)
            # To limit disk usage, erase the file from the previously saved step
            self.remove_intermediate_files(filename)
            # get output path
            outfile = self.get_output_path(it, datadir, result.meta.filename)
            outfiles.append(outfile)

        return outfiles

    def subtract_background(self, infiles: list) -> list:
        """
        Removes background using reference or modeled backgrounds.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.JWST.subtract_background"
        # ---------------------------------------------------------------------
        # get params from step constant
        run_step, flavour, kwargs, suffix = self.from_step_args(func_name)
        # deal with skipping step
        run_step, infiles = self.skip_step(
            run_step, 'SUBTRACT_BACKGROUND', suffix, infiles)
        # deal with not running this step
        if not run_step:
            return infiles
        # ---------------------------------------------------------------------
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # storage for output files
        outfiles = []
        # loop around infiles
        for it, filename in enumerate(infiles):
            # Read input segments files from disk
            input_data = datamodels.open(filename)
            result = BackgroundStep.call(input_data, output_dir=datadir,
                                         save_results=True, **kwargs)
            # To limit disk usage, erase the file from the previously saved step
            self.remove_intermediate_files(filename)
            # get output path
            outfile = self.get_output_path(it, datadir, result.meta.filename)
            outfiles.append(outfile)

        return outfiles

    def assign_wcs_solution(self, infiles: list) -> list:
        """
        Adds WCS (world coordinate system) information.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.JWST.assign_wcs_solution"
        # ---------------------------------------------------------------------
        # get params from step constant
        run_step, flavour, kwargs, suffix = self.from_step_args(func_name)
        # deal with skipping step
        run_step, infiles = self.skip_step(
            run_step, 'ASSIGN_WCS_SOLUTION', suffix, infiles)
        # deal with not running this step
        if not run_step:
            return infiles
        # ---------------------------------------------------------------------
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # storage for output files
        outfiles = []
        # loop around infiles
        for it, filename in enumerate(infiles):
            # Read input segments files from disk
            input_data = datamodels.open(filename)
            result = AssignWcsStep.call(input_data, output_dir=datadir,
                                        save_results=True, **kwargs)
            # To limit disk usage, erase the file from the previously saved step
            self.remove_intermediate_files(filename)
            # get output path
            outfile = self.get_output_path(it, datadir, result.meta.filename)
            outfiles.append(outfile)

        return outfiles

    def apply_flat_field(self, infiles: list) -> list:
        """
        Corrects pixel-to-pixel sensitivity variations.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.JWST.apply_flat_field"
        # ---------------------------------------------------------------------
        # get params from step constant
        run_step, flavour, kwargs, suffix = self.from_step_args(func_name)
        # deal with skipping step
        run_step, infiles = self.skip_step(
            run_step, 'APPLY_FLAT_FIELD', suffix, infiles)
        # deal with not running this step
        if not run_step:
            # save output files to {PREFIX}_rateints.fits
            return self.save_outputs('_rateints.fits', infiles)
        # ---------------------------------------------------------------------
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # storage for output files
        outfiles = []
        # loop around infiles
        for it, filename in enumerate(infiles):
            # Read input segments files from disk
            input_data = datamodels.open(filename)
            result = FlatFieldStep.call(input_data, output_dir=datadir,
                                        save_results=True, **kwargs)
            # To limit disk usage, erase the file from the previously saved step
            self.remove_intermediate_files(filename)
            # get output path
            outfile = self.get_output_path(it, datadir, result.meta.filename)
            outfiles.append(outfile)

        return outfiles

    def apply_photometric_calibration(self, infiles: list) -> list:
        """
        Converts data units to physical flux units.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.JWST.apply_photometric_calibration"
        # ---------------------------------------------------------------------
        # get params from step constant
        run_step, flavour, kwargs, suffix = self.from_step_args(func_name)
        # deal with skipping step
        run_step, infiles = self.skip_step(
            run_step, 'APPLY_PHOTOMETRIC_CALIBRATION', suffix, infiles)
        # deal with not running this step
        if not run_step:
            # save output files to {PREFIX}_calints.fits
            return self.save_outputs('_calints.fits', infiles)
        # ---------------------------------------------------------------------
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # storage for output files
        outfiles = []
        # loop around infiles
        for it, filename in enumerate(infiles):
            # Read input segments files from disk
            input_data = datamodels.open(filename)
            result = PhotomStep.call(input_data, output_dir=datadir,
                                     save_results=True, **kwargs)
            # To limit disk usage, erase the file from the previously saved step
            self.remove_intermediate_files(filename)
            # get output path
            outfile = self.get_output_path(it, datadir, result.meta.filename)
            outfiles.append(outfile)

        return outfiles

    def subtract_superbias(self, infiles: list) -> list:
        """
        Subtract superbias reference for NIR instruments.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.JWST.subtract_superbias"
        # get params from step constant
        run_step, flavour, kwargs, suffix = self.from_step_args(func_name)
        # deal with skipping step
        run_step, infiles = self.skip_step(
            run_step, 'SUBTRACT_SUPERBIAS', suffix, infiles)
        # deal with not running this step
        if not run_step:
            return infiles
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # storage for output files
        outfiles = []
        # loop around infiles
        for it, filename in enumerate(infiles):
            # Read input segments files from disk
            input_data = datamodels.open(filename)
            result = SuperBiasStep.call(input_data, output_dir=datadir,
                                        save_results=True, **kwargs)
            # To limit disk usage, erase the file from the previously saved step
            self.remove_intermediate_files(filename)
            # get output path
            outfile = self.get_output_path(it, datadir, result.meta.filename)
            outfiles.append(outfile)

        return outfiles

    def picture_frame_step(self, infiles: list) -> list:
        """
        Correct for picture frame effect.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.JWST.picture_frame_step"
        # get params from step constant
        run_step, flavour, kwargs, suffix = self.from_step_args(func_name)
        # deal with not running this step
        if not run_step:
            return infiles
        # NOTE: Picture frame step is not a standard step in JWST pipeline
        msg = 'Picture frame step not implemented in standard JWST pipeline'
        WLOG(self.params, 'warning', msg)
        return infiles

    def correct_persistence(self, infiles: list) -> list:
        """
        Correct for charge persistence between integrations.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.JWST.correct_persistence"
        # get params from step constant
        run_step, flavour, kwargs, suffix = self.from_step_args(func_name)
        # deal with not running this step
        if not run_step:
            return infiles
        # NOTE: Persistence step is not implemented in standard JWST pipeline
        msg = 'Persistence correction not available in standard JWST pipeline'
        WLOG(self.params, 'warning', msg)
        return infiles

    # =========================================================================
    # Level 2 spectroscopic and imaging processing steps
    # =========================================================================
    def extract_2d_spectrum(self, infiles: list) -> list:
        """
        Extract 2D spectrum from detector image.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.JWST.extract_2d_spectrum"
        # get params from step constant
        run_step, flavour, kwargs, suffix = self.from_step_args(func_name)
        # deal with skipping step
        run_step, infiles = self.skip_step(
            run_step, 'EXTRACT_2D_SPECTRUM', suffix, infiles)
        # deal with not running this step
        if not run_step:
            return infiles
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # storage for output files
        outfiles = []
        # loop around infiles
        for it, filename in enumerate(infiles):
            # Read input segments files from disk
            input_data = datamodels.open(filename)
            result = Extract2dStep.call(input_data, output_dir=datadir,
                                        save_results=True, **kwargs)
            # To limit disk usage, erase the file from the previously saved step
            self.remove_intermediate_files(filename)
            # get output path
            outfile = self.get_output_path(it, datadir, result.meta.filename)
            outfiles.append(outfile)

        return outfiles

    def extract_1d_spectrum(self, infiles: list) -> list:
        """
        Extract 1D spectrum from 2D data.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.JWST.extract_1d_spectrum"
        # get params from step constant
        run_step, flavour, kwargs, suffix = self.from_step_args(func_name)
        # deal with skipping step
        run_step, infiles = self.skip_step(
            run_step, 'EXTRACT_1D_SPECTRUM', suffix, infiles)
        # deal with not running this step
        if not run_step:
            return infiles
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # storage for output files
        outfiles = []
        # loop around infiles
        for it, filename in enumerate(infiles):
            # Read input segments files from disk
            input_data = datamodels.open(filename)
            result = Extract1dStep.call(input_data, output_dir=datadir,
                                        save_results=True, **kwargs)
            # erase previous step file to limit disk usage
            self.remove_intermediate_files(filename)
            # get output path
            outfile = self.get_output_path(it, datadir, result.meta.filename)
            outfiles.append(outfile)

        return outfiles

    def srctype_determination(self, infiles: list) -> list:
        """
        Determine source type for photometric calibration.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.JWST.srctype_determination"
        # get params from step constant
        run_step, flavour, kwargs, suffix = self.from_step_args(func_name)
        # deal with skipping step
        run_step, infiles = self.skip_step(
            run_step, 'SRCTYPE_DETERMINATION', suffix, infiles)
        # deal with not running this step
        if not run_step:
            return infiles
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # storage for output files
        outfiles = []
        # loop around infiles
        for it, filename in enumerate(infiles):
            # Read input segments files from disk
            input_data = datamodels.open(filename)
            result = SourceTypeStep.call(input_data, output_dir=datadir,
                                         save_results=True, **kwargs)
            # To limit disk usage, erase the file from the previously saved step
            self.remove_intermediate_files(filename)
            # get output path
            outfile = self.get_output_path(it, datadir, result.meta.filename)
            outfiles.append(outfile)

        return outfiles

    def correct_stray_light(self, infiles: list) -> list:
        """
        Remove stray light from the data.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.JWST.correct_stray_light"
        # get params from step constant
        run_step, flavour, kwargs, suffix = self.from_step_args(func_name)
        # deal with skipping step
        run_step, infiles = self.skip_step(
            run_step, 'CORRECT_STRAY_LIGHT', suffix, infiles)
        # deal with not running this step
        if not run_step:
            return infiles
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # storage for output files
        outfiles = []
        # loop around infiles
        for it, filename in enumerate(infiles):
            # Read input segments files from disk
            input_data = datamodels.open(filename)
            result = StraylightStep.call(input_data, output_dir=datadir,
                                         save_results=True, **kwargs)
            # To limit disk usage, erase the file from the previously saved step
            self.remove_intermediate_files(filename)
            # get output path
            outfile = self.get_output_path(it, datadir, result.meta.filename)
            outfiles.append(outfile)

        return outfiles

    def correct_fringe(self, infiles: list) -> list:
        """
        Remove fringe patterns from the data.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.JWST.correct_fringe"
        # get params from step constant
        run_step, flavour, kwargs, suffix = self.from_step_args(func_name)
        # deal with skipping step
        run_step, infiles = self.skip_step(
            run_step, 'CORRECT_FRINGE', suffix, infiles)
        # deal with not running this step
        if not run_step:
            return infiles
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # storage for output files
        outfiles = []
        # loop around infiles
        for it, filename in enumerate(infiles):
            # Read input segments files from disk
            input_data = datamodels.open(filename)
            result = FringeStep.call(input_data, output_dir=datadir,
                                     save_results=True, **kwargs)
            # To limit disk usage, erase the file from the previously saved step
            self.remove_intermediate_files(filename)
            # get output path
            outfile = self.get_output_path(it, datadir, result.meta.filename)
            outfiles.append(outfile)

        return outfiles

    def correct_path_loss(self, infiles: list) -> list:
        """
        Correct for path loss through the optical system.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.JWST.correct_path_loss"
        # get params from step constant
        run_step, flavour, kwargs, suffix = self.from_step_args(func_name)
        # deal with skipping step
        run_step, infiles = self.skip_step(
            run_step, 'CORRECT_PATH_LOSS', suffix, infiles)
        # deal with not running this step
        if not run_step:
            return infiles
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # storage for output files
        outfiles = []
        # loop around infiles
        for it, filename in enumerate(infiles):
            # Read input segments files from disk
            input_data = datamodels.open(filename)
            result = PathLossStep.call(input_data, output_dir=datadir,
                                       save_results=True, **kwargs)
            # To limit disk usage, erase the file from the previously saved step
            self.remove_intermediate_files(filename)
            # get output path
            outfile = self.get_output_path(it, datadir, result.meta.filename)
            outfiles.append(outfile)

        return outfiles

    def correct_bar_shadow(self, infiles: list) -> list:
        """
        Correct for bar shadow effect.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.JWST.correct_bar_shadow"
        # get params from step constant
        run_step, flavour, kwargs, suffix = self.from_step_args(func_name)
        # deal with skipping step
        run_step, infiles = self.skip_step(
            run_step, 'CORRECT_BAR_SHADOW', suffix, infiles)
        # deal with not running this step
        if not run_step:
            return infiles
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # storage for output files
        outfiles = []
        # loop around infiles
        for it, filename in enumerate(infiles):
            # Read input segments files from disk
            input_data = datamodels.open(filename)
            result = BarShadowStep.call(input_data, output_dir=datadir,
                                        save_results=True, **kwargs)
            # To limit disk usage, erase the file from the previously saved step
            self.remove_intermediate_files(filename)
            # get output path
            outfile = self.get_output_path(it, datadir, result.meta.filename)
            outfiles.append(outfile)

        return outfiles

    def correct_wfss_contamination(self, infiles: list) -> list:
        """
        Correct for WFSS contamination.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.JWST.correct_wfss_contamination"
        # get params from step constant
        run_step, flavour, kwargs, suffix = self.from_step_args(func_name)
        # deal with skipping step
        run_step, infiles = self.skip_step(
            run_step, 'CORRECT_WFSS_CONTAMINATION', suffix, infiles)
        # deal with not running this step
        if not run_step:
            return infiles
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # storage for output files
        outfiles = []
        # loop around infiles
        for it, filename in enumerate(infiles):
            # Read input segments files from disk
            input_data = datamodels.open(filename)
            result = WfssContamStep.call(input_data, output_dir=datadir,
                                         save_results=True, **kwargs)
            # To limit disk usage, erase the file from the previously saved step
            self.remove_intermediate_files(filename)
            # get output path
            outfile = self.get_output_path(it, datadir, result.meta.filename)
            outfiles.append(outfile)

        return outfiles

    def correct_wavelength(self, infiles: list) -> list:
        """
        Correct wavelength calibration.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.JWST.correct_wavelength"
        # get params from step constant
        run_step, flavour, kwargs, suffix = self.from_step_args(func_name)
        # deal with skipping step
        run_step, infiles = self.skip_step(
            run_step, 'CORRECT_WAVELENGTH', suffix, infiles)
        # deal with not running this step
        if not run_step:
            return infiles
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # storage for output files
        outfiles = []
        # loop around infiles
        for it, filename in enumerate(infiles):
            # Read input segments files from disk
            input_data = datamodels.open(filename)
            result = WavecorrStep.call(input_data, output_dir=datadir,
                                       save_results=True, **kwargs)
            # To limit disk usage, erase the file from the previously saved step
            self.remove_intermediate_files(filename)
            # get output path
            outfile = self.get_output_path(it, datadir, result.meta.filename)
            outfiles.append(outfile)

        return outfiles

    def subtract_master_background(self, infiles: list) -> list:
        """
        Subtract master background for NIRSpec MOS data.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.JWST.subtract_master_background"
        # get params from step constant
        run_step, flavour, kwargs, suffix = self.from_step_args(func_name)
        # deal with skipping step
        run_step, infiles = self.skip_step(
            run_step, 'SUBTRACT_MASTER_BACKGROUND', suffix, infiles)
        # deal with not running this step
        if not run_step:
            return infiles
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # storage for output files
        outfiles = []
        # loop around infiles
        for it, filename in enumerate(infiles):
            # Read input segments files from disk
            input_data = datamodels.open(filename)
            result = MasterBackgroundStep.call(input_data, output_dir=datadir,
                                               save_results=True, **kwargs)
            # To limit disk usage, erase the file from the previously saved step
            self.remove_intermediate_files(filename)
            # get output path
            outfile = self.get_output_path(it, datadir, result.meta.filename)
            outfiles.append(outfile)

        return outfiles

    def measure_target_centroid(self, infiles: list) -> list:
        """
        Measure target centroid position.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.JWST.measure_target_centroid"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def correct_residual_fringe(self, infiles: list) -> list:
        """
        Correct for residual fringe patterns (MIRI-specific).

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.JWST.correct_residual_fringe"
        # NOTE: Residual fringe correction is MIRI-specific and not in standard
        msg = 'Residual fringe correction not in standard JWST pipeline'
        WLOG(self.params, 'warning', msg)
        return infiles

    def resample_images(self, infiles: list) -> list:
        """
        Resample images to a common grid.

        :param infiles: list[str], list of input files
        :return: list[str], list of output files
        """
        # set function name
        func_name = f"{__NAME__}.JWST.resample_images"
        # get params from step constant
        run_step, flavour, kwargs, suffix = self.from_step_args(func_name)
        # deal with skipping step
        run_step, infiles = self.skip_step(
            run_step, 'RESAMPLE_IMAGES', suffix, infiles)
        # deal with not running this step
        if not run_step:
            return infiles
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # storage for output files
        outfiles = []
        # loop around infiles
        for it, filename in enumerate(infiles):
            # Read input segments files from disk
            input_data = datamodels.open(filename)
            result = ResampleStep.call(input_data, output_dir=datadir,
                                       save_results=True, **kwargs)
            # To limit disk usage, erase the file from the previously saved step
            self.remove_intermediate_files(filename)
            # get output path
            outfile = self.get_output_path(it, datadir, result.meta.filename)
            outfiles.append(outfile)

        return outfiles

    # =========================================================================
    # JWST specific helper functions
    # =========================================================================
    def save_model_with_suffix(self, model, output_dir: str, suffix: str,
                               iteration: int) -> str:
        """
        Save a JWST datamodel to disk with the given suffix.

        Uses the prefix + suffix naming convention.

        :param model: JWST datamodel object to save
        :param output_dir: str, directory to save file to
        :param suffix: str, the suffix to add to the filename
        :param iteration: int, the iteration number
        :return: str, the path to the saved file
        """
        # Get the prefix for this iteration
        prefixes = self.variables['PREFIXES']
        prefix = prefixes[iteration]
        # Construct the output filename
        new_base_name = prefix + suffix
        outfile = os.path.join(output_dir, new_base_name)
        # Save the model
        model.save(outfile)
        return outfile

    def _force_float(self, result):
        """
        Force all uint16 arrays in JWST data model to float32.

        Group scale should do this, but if skipped it might not convert
        all arrays. This ensures data, err, refout, zeroframe, etc.
        are all float32.

        :param result: JWST datamodel
        :return: JWST datamodel with float32 arrays
        """
        # Convert data array
        if result.data.dtype != np.float32:
            result.data = result.data.astype(np.float32, copy=True)
        # Convert err array
        if hasattr(result, 'err') and result.err is not None:
            if result.err.dtype != np.float32:
                result.err = result.err.astype(np.float32, copy=True)
        # Convert refout array (MIRI specific)
        if hasattr(result, 'refout') and result.refout is not None:
            if result.refout.dtype != np.float32:
                result.refout = result.refout.astype(np.float32,
                                                     copy=True)
        # Convert zeroframe array if present
        if hasattr(result, 'zeroframe') and result.zeroframe is not None:
            if result.zeroframe.dtype != np.float32:
                result.zeroframe = result.zeroframe.astype(np.float32,
                                                            copy=True)
        return result


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

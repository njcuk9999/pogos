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
        self.variables.set('LAST', [], source=func_name)
        self.variables.set('OUT', [], source=func_name)
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
    def handle_input_data(self):
        """
        Handle input data - this should work for all instruments/modes
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.handle_input_data"
        # raise not implemented error (implemented in JWST)
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

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

    def group_scale_step(self):
        """
        Scale group data to account for on-chip amplifier effects.
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.group_scale_step"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def dq_init_step(self):
        """
        Initialize data quality flags.
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.dq_init_step"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def emicorr_step(self):
        """
        Apply EMI (electro-magnetic interference) corrections.
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.emicorr_step"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def saturation_step(self):
        """
        Flag saturated pixels.
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.saturation_step"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def subtract_superbias(self):
        """
        Subtract superbias reference for NIR instruments.
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.subtract_superbias"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def picture_frame_step(self):
        """
        Correct for picture frame effect.
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.picture_frame_step"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def correct_persistence(self):
        """
        Correct for charge persistence between integrations.
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.correct_persistence"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def extract_2d_spectrum(self):
        """
        Extract 2D spectrum from detector image.
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.extract_2d_spectrum"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def extract_1d_spectrum(self):
        """
        Extract 1D spectrum from 2D data.

        Returns
        -------
        list[str]
            Absolute paths to the produced 1D spectrum files.
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.extract_1d_spectrum"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def srctype_determination(self):
        """
        Determine source type for photometric calibration.
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.srctype_determination"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def correct_stray_light(self):
        """
        Remove stray light from the data.
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.correct_stray_light"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def correct_fringe(self):
        """
        Remove fringe patterns from the data.
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.correct_fringe"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def correct_path_loss(self):
        """
        Correct for path loss through the optical system.
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.correct_path_loss"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def correct_bar_shadow(self):
        """
        Correct for bar shadow effect.
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.correct_bar_shadow"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def correct_wfss_contamination(self):
        """
        Correct for WFSS contamination.
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.correct_wfss_contamination"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def correct_wavelength(self):
        """
        Correct wavelength calibration.
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.correct_wavelength"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def subtract_master_background(self):
        """
        Subtract master background for NIRSpec MOS data.
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.subtract_master_background"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def measure_target_centroid(self):
        """
        Measure target centroid position.
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.measure_target_centroid"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def correct_residual_fringe(self):
        """
        Correct for residual fringe patterns (MIRI-specific).
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.correct_residual_fringe"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    def resample_images(self):
        """
        Resample images to a common grid.
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.resample_images"
        # raise not implemented error
        nmsg = NOT_IMPLEMENTED_MSG.format(func_name, self.instrument)
        raise NotImplemented(nmsg)

    # -------------------------------------------------------------------------
    # Define additional methods (worker functions)
    # -------------------------------------------------------------------------
    def update_last(self, it: int, output_dir: str, output_filename: Any,
                       func_name: str):
        """
        Update the LAST variable in the variables dictionary

        :param variables: ParamDict, the variables dictionary
        :param it: int, the iteration number
        :param output_dir: str, the output directory
        :param result: The JWST data result to store
        :param func_name: str, the function name calling this function

        :return: ParamDict, the updated variables dictionary
        """
        # construct absolute path to filename
        absfile = os.path.join(output_dir, output_filename)
        # deal with bad iteration number
        if it < 0 or it >= len(self.variables['LAST']):
            emsg = ('Iteration number {} is out of bounds for LAST variable of '
                    'length {}')
            eargs = [it, len(self.variables['LAST'])]
            raise ts_base.TSOvoreException(emsg.format(*eargs))
        # update the LAST variable
        self.variables.unlock()
        self.variables['LAST'][it] = absfile
        # update the source of the LAST variable
        self.variables.set_source('LAST', func_name)
        self.variables.lock()

    def save_outputs(self, suffix: str, infiles: Any = None):
        """
        Rename/copy the current files to have a given suffix.

        :param suffix: str, the suffix to add to the filename
        :param infiles: list[str] or None, optional override for files to copy.
                        If None, uses self.variables['LAST'].
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.rename_results"
        # choose input files: override or LAST
        if infiles is None:
            in_files = self.variables['LAST']
        else:
            in_files = infiles
        prefixes = self.variables['PREFIXES']
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # storage for OUT variable
        out_files = []
        # loop around files
        for it, filename in enumerate(in_files):
            # construct new filename
            new_base_name = prefixes[it] + suffix
            new_filename = str(os.path.join(datadir, new_base_name))
            # deal with files not existing (not allowed)
            if not os.path.exists(filename):
                wmsg = ('File {0} does not exist on disk. Cannot add to out. '
                        'This may crash future steps.').format(filename)
                WLOG(self.params, 'warning', wmsg)
                return
            else:
                msg = ('Copying file {0} to {1}').format(filename,
                                                          new_filename)
                WLOG(self.params, 'info', msg)
            # copy the file
            shutil.copy(filename, new_filename)
            # save files to list
            out_files.append(new_filename)
        # update the OUT variable
        self.variables.unlock()
        self.variables['OUT'] = out_files
        self.variables.set_source('OUT', func_name)
        self.variables.lock()

    def remove_intermediate_files(self, it: int):
        """
        Remove intermediate files to save disk space
        
        :param it: int, the iteration number
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.remove_intermediate_files"
        # get parameters from params
        remove_intermediates = self.tparams['INPUTS.REMOVE_INTERMEDIATES']
        # get variables from self
        infiles = self.variables['LAST']
        # check if we need to remove intermediate files
        if remove_intermediates:
            # remove the file
            os.remove(infiles[it])

    def from_step_args(self, func_name: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Get step arguments from params

        :param func_name: str, the function name calling this function

        :return: tuple, (run_step: bool, mode: str, kwargs: dict)
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
        # get mode
        mode = self.tparams[f'{step_arg}'].get('MODE', 'None')
        # get kwargs
        kwargs = self.tparams[f'{step_arg}'].get('KWARGS', dict())
        # get the suffix
        suffix = self.tparams[f'{step_arg}'].get('SUFFIX', None)
        # ---------------------------------------------------------------------
        # if we are running this step print message
        if run_step:
            msg = ('\n\nRunning {0} mode={1}').format(step_name, mode)
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
        # deal with skipping step
        run_step = self.skip_step(run_step, step_name, suffix)
        # ---------------------------------------------------------------------
        # return values
        return run_step, mode, kwargs

    def skip_step(self, run_step: bool, step_name: str, suffix: str):
        """
        Decide whether to skip a step based on existing files and parameters

        :param run_step: bool, whether to run the step (from params)
        :param step_name: str, the name of the step
        :param suffix: str, the suffix expected for output files
        :return:
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.skip_step"
        # if we are already not running step then we don't need to check skips
        if not run_step:
            return False
        # skip if we have no suffix
        if suffix is None:
            return run_step
        # skip if we are not skipping processed files
        if not self.tparams['INPUTS.SKIP_PROCESSED_FILES']:
            return run_step
        # get variables from self
        infiles = self.variables['LAST']
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
        # if all found then run_step is False and we update variables
        if all_found:
            # update run step
            run_step = False
            # print message to user
            msg = ('\tINPUTS.SKIP_PROCESSED_FILES=True\n\tAll expected '
                   'output files found with suffix "{0}".'
                   '\n\tSkipping step "{1}".').format(suffix, step_name)
            WLOG(self.params, '', msg)
            # update LAST variable to point to expected file
            for it in range(len(expected_files)):
                self.variables.unlock()
                self.variables['LAST'][it] = expected_files[it]
                self.variables.set_source('LAST', func_name)
                self.variables.lock()

        return run_step


class JWST(Instrument):
    """
    JWST Instrument class
    """
    def __init__(self, params: ParamDict, instrument: str = 'JWST.NONE'):
        super().__init__(params, instrument)

    def handle_input_data(self):
        """
        Handle input data - this should work for all JWST instruments/modes
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
        self.variables.set('LAST', input_absfiles, source=func_name)

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

    def initialize_detector_data(self):
        """
        Handles data load and initial detector corrections
        (scaling, DQ flags, emission correction, saturation map).

        """
        # set function name
        func_name = f"{__NAME__}.JWST.initialize_detector_data"
        # ---------------------------------------------------------------------
        # get params from step constant
        run_step, mode, kwargs = self.from_step_args(func_name)
        # deal with not running this step
        if not run_step: return
        # ---------------------------------------------------------------------
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # get variables from self
        infiles = self.variables['LAST']
        # loop around infiles
        for it, filename in enumerate(infiles):
            # Read input segments files from disk
            input_data = datamodels.open(filename, output_dir=datadir,
                                         save_results=False)
            # Execute the first step
            result = GroupScaleStep.call(input_data)
            # Execute the second step
            result = DQInitStep.call(result, output_dir=datadir,
                                     save_results=False)
            # Execute the third step
            # The EmiCorrStep is by default skipped when executed on these data
            # result = EmiCorrStep.call(input_data, save_results=False)
            # Execute the fourth step
            # this time saving files on disk
            result = SaturationStep.call(result, output_dir=datadir,
                                         save_results=True)
            # update the LAST and RESULT variables
            self.update_last(it, datadir, result.meta.filename, func_name)

    def apply_interpixel_capacitance(self):
        """
        Corrects for interpixel capacitance effects.
        """
        # set function name
        func_name = f"{__NAME__}.JWST.apply_interpixel_capacitance"
        # ---------------------------------------------------------------------
        # get params from step constant
        run_step, mode, kwargs = self.from_step_args(func_name)
        # deal with not running this step
        if not run_step: return
        # ---------------------------------------------------------------------
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # get variables from self
        infiles = self.variables['LAST']
        # loop around infiles
        for it, filename in enumerate(infiles):
            # Read input segments files from disk
            input_data = datamodels.open(filename)
            result = IPCStep.call(input_data, output_dir=datadir, 
                                  save_results=True, **kwargs)
            # To limit disk usage, erase the file from the previously saved step
            self.remove_intermediate_files(it)
            # update the LAST and RESULT variables
            self.update_last(it, datadir, result.meta.filename, func_name)

    def remove_first_frame_signal(self):
        """
        Removes bias introduced in first frame of each integration.
        
        All this does is set the DQflag of the first frame of every integration
        to DO NOT USE provided that the integrations have more than 3 usable 
        (non-saturated group).
        """
        # set function name
        func_name = f"{__NAME__}.JWST.remove_first_frame_signal"
        # ---------------------------------------------------------------------
        # get params from step constant
        run_step, mode, kwargs = self.from_step_args(func_name)
        # deal with not running this step
        if not run_step: return
        # ---------------------------------------------------------------------
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # get variables from self
        infiles = self.variables['LAST']
        # loop around infiles
        for it, filename in enumerate(infiles):
            # Read input segments files from disk
            input_data = datamodels.open(filename)
            result = FirstFrameStep.call(input_data, output_dir=datadir,
                                         save_results=True, **kwargs)
            # To limit disk usage, erase the file from the previously saved step
            self.remove_intermediate_files(it)
            # update the LAST and RESULT variables
            self.update_last(it, datadir, result.meta.filename, func_name)

    def remove_last_frame_signal(self):
        """
        Removes last-frame pedestal effect.
        """
        # set function name
        func_name = f"{__NAME__}.JWST.remove_last_frame_signal"
        # ---------------------------------------------------------------------
        # get params from step constant
        run_step, mode, kwargs = self.from_step_args(func_name)
        # deal with not running this step
        if not run_step: return
        # ---------------------------------------------------------------------
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # get variables from self
        infiles = self.variables['LAST']
        # loop around infiles
        for it, filename in enumerate(infiles):
            # Read input segments files from disk
            input_data = datamodels.open(filename)
            result = LastFrameStep.call(input_data, output_dir=datadir,
                                        save_results=True, **kwargs)
            # To limit disk usage, erase the file from the previously saved step
            self.remove_intermediate_files(it)
            # update the LAST and RESULT variables
            self.update_last(it, datadir, result.meta.filename, func_name)
            
    def correct_reset_anomaly(self):
        """
        Fixes reset anomaly across integrations.
        """
        # set function name
        func_name = f"{__NAME__}.JWST.correct_reset_anomaly"
        # ---------------------------------------------------------------------
        # get params from step constant
        run_step, mode, kwargs = self.from_step_args(func_name)
        # deal with not running this step
        if not run_step: return
        # ---------------------------------------------------------------------
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # get variables from self
        infiles = self.variables['LAST']
        # loop around infiles
        for it, filename in enumerate(infiles):
            # Read input segments files from disk
            input_data = datamodels.open(filename)
            result = ResetStep.call(input_data, output_dir=datadir,
                                    save_results=True, **kwargs)
            # To limit disk usage, erase the file from the previously saved step
            self.remove_intermediate_files(it)
            # update the LAST and RESULT variables
            self.update_last(it, datadir, result.meta.filename, func_name)
        
    def apply_linearity_correction(self):
        """
        Corrects for detector nonlinearity.
        """
        # set function name
        func_name = f"{__NAME__}.JWST.apply_linearity_correction"
        # ---------------------------------------------------------------------
        # get params from step constant
        run_step, mode, kwargs = self.from_step_args(func_name)
        # deal with not running this step
        if not run_step: return
        # ---------------------------------------------------------------------
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # get variables from self
        infiles = self.variables['LAST']
        # loop around infiles
        for it, filename in enumerate(infiles):
            # Read input segments files from disk
            input_data = datamodels.open(filename)
            result = LinearityStep.call(input_data, output_dir=datadir,
                                        save_results=True, **kwargs)
            # To limit disk usage, erase the file from the previously saved step
            self.remove_intermediate_files(it)
            # update the LAST and RESULT variables
            self.update_last(it, datadir, result.meta.filename, func_name)

    def apply_rscd_correction(self):
        """
        Applies reset switch charge decay correction.
        """
        # set function name
        func_name = f"{__NAME__}.JWST.apply_rscd_correction"
        # ---------------------------------------------------------------------
        # get params from step constant
        run_step, mode, kwargs = self.from_step_args(func_name)
        # deal with not running this step
        if not run_step: return
        # ---------------------------------------------------------------------
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # get variables from self
        infiles = self.variables['LAST']
        # loop around infiles
        for it, filename in enumerate(infiles):
            # Read input segments files from disk
            input_data = datamodels.open(filename)
            result = RscdStep.call(input_data, output_dir=datadir,
                                   save_results=True, **kwargs)
            # To limit disk usage, erase the file from the previously saved step
            self.remove_intermediate_files(it)
            # update the LAST and RESULT variables
            self.update_last(it, datadir, result.meta.filename, func_name)
            
    def subtract_dark_current(self):
        """
        Removes dark current signal using reference darks.
        """
        # set function name
        func_name = f"{__NAME__}.JWST.subtract_dark_current"
        # ---------------------------------------------------------------------
        # get params from step constant
        run_step, mode, kwargs = self.from_step_args(func_name)
        # deal with not running this step
        if not run_step: return
        # ---------------------------------------------------------------------
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # get variables from self
        infiles = self.variables['LAST']
        # loop around infiles
        for it, filename in enumerate(infiles):
            # Read input segments files from disk
            input_data = datamodels.open(filename)
            result = DarkCurrentStep.call(input_data, output_dir=datadir,
                                          save_results=True, **kwargs)
            # To limit disk usage, erase the file from the previously saved step
            self.remove_intermediate_files(it)
            # update the LAST and RESULT variables
            self.update_last(it, datadir, result.meta.filename, func_name)
            
    def apply_reference_pixel_correction(self):
        """
        Corrects readout noise using reference pixels.
        """
        # set function name
        func_name = f"{__NAME__}.JWST.apply_reference_pixel_correction"
        # ---------------------------------------------------------------------
        # get params from step constant
        run_step, mode, kwargs = self.from_step_args(func_name)
        # deal with not running this step
        if not run_step: return
        # ---------------------------------------------------------------------
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # get variables from self
        infiles = self.variables['LAST']
        # loop around infiles
        for it, filename in enumerate(infiles):
            # Read input segments files from disk
            input_data = datamodels.open(filename)
            result = RefPixStep.call(input_data, output_dir=datadir,
                                     save_results=True, **kwargs)
            # To limit disk usage, erase the file from the previously saved step
            self.remove_intermediate_files(it)
            # update the LAST and RESULT variables
            self.update_last(it, datadir, result.meta.filename, func_name)
            
    def correct_charge_migration(self):
        """
        Mitigates charge migration between pixels.
        """
        # set function name
        func_name = f"{__NAME__}.JWST.correct_charge_migration"
        # ---------------------------------------------------------------------
        # get params from step constant
        run_step, mode, kwargs = self.from_step_args(func_name)
        # deal with not running this step
        if not run_step: return
        # ---------------------------------------------------------------------
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # get variables from self
        infiles = self.variables['LAST']
        # loop around infiles
        for it, filename in enumerate(infiles):
            # Read input segments files from disk
            input_data = datamodels.open(filename)
            result = ChargeMigrationStep.call(input_data, output_dir=datadir,
                                             save_results=True, **kwargs)
            # To limit disk usage, erase the file from the previously saved step
            self.remove_intermediate_files(it)
            # update the LAST and RESULT variables
            self.update_last(it, datadir, result.meta.filename, func_name)
            
    def detect_and_flag_jumps(self):
        """
        Identifies and flags cosmic ray hits (jumps) in the data.
        """
        # set function name
        func_name = f"{__NAME__}.JWST.detect_and_flag_jumps"
        # ---------------------------------------------------------------------
        # get params from step constant
        run_step, mode, kwargs = self.from_step_args(func_name)
        # deal with not running this step
        if not run_step: return
        # ---------------------------------------------------------------------
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # get variables from self
        infiles = self.variables['LAST']
        # loop around infiles
        for it, filename in enumerate(infiles):
            # Read input segments files from disk
            input_data = datamodels.open(filename)
            result = JumpStep.call(input_data, output_dir=datadir,
                                   save_results=True, **kwargs)
            # Fot the JumpStep, no new outfile file is created, instead,
            # the previous step's file is modified when running the JumpStep.
            # I don't know why.
            # update the LAST and RESULT variables
            self.update_last(it, datadir, result.meta.filename, func_name)

    def remove_flicker_noise(self):
        """
        Removes flicker noise from the data.
        """
        # set function name
        func_name = f"{__NAME__}.JWST.remove_flicker_noise"
        # ---------------------------------------------------------------------
        # get params from step constant
        run_step, mode, kwargs = self.from_step_args(func_name)
        # deal with not running this step
        if not run_step: return
        # ---------------------------------------------------------------------
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # get variables from self
        infiles = self.variables['LAST']
        # loop around infiles
        for it, filename in enumerate(infiles):
            # Read input segments files from disk
            input_data = datamodels.open(filename)
            result = CleanFlickerNoiseStep.call(input_data, output_dir=datadir,
                                               save_results=True, **kwargs)
            # To limit disk usage, erase the file from the previously saved step
            self.remove_intermediate_files(it)
            # update the LAST and RESULT variables
            self.update_last(it, datadir, result.meta.filename, func_name)

    def fit_signal_ramps(self):
        """
        Fits slopes to groups to derive count rates.
        """
        # set function name
        func_name = f"{__NAME__}.JWST.fit_signal_ramps"
        # ---------------------------------------------------------------------
        # get params from step constant
        run_step, mode, kwargs = self.from_step_args(func_name)
        # deal with not running this step
        if not run_step: return
        # ---------------------------------------------------------------------
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # get variables from self
        infiles = self.variables['LAST']
        # loop around infiles
        for it, filename in enumerate(infiles):
            # Read input segments files from disk
            input_data = datamodels.open(filename)
            rate, result = RampFitStep.call(input_data, output_dir=datadir,
                                            save_results=True, **kwargs)
            # To limit disk usage, erase the file from the previously saved step
            self.remove_intermediate_files(it)
            # update the LAST and RESULT variables
            self.update_last(it, datadir, result.meta.filename, func_name)
            
    def apply_gain_scaling(self):
        """
        Scales results to correct gain differences.
        """
        # set function name
        func_name = f"{__NAME__}.JWST.apply_gain_scaling"
        # ---------------------------------------------------------------------
        # get params from step constant
        run_step, mode, kwargs = self.from_step_args(func_name)
        # deal with not running this step
        if not run_step: return
        # ---------------------------------------------------------------------
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # get variables from self
        infiles = self.variables['LAST']
        # loop around infiles
        for it, filename in enumerate(infiles):
            # Read input segments files from disk
            input_data = datamodels.open(filename)
            result = GainScaleStep.call(input_data, output_dir=datadir,
                                        save_results=True, **kwargs)
            # To limit disk usage, erase the file from the previously saved step
            self.remove_intermediate_files(it)
            # update the LAST and RESULT variables
            self.update_last(it, datadir, result.meta.filename, func_name)
    
    def subtract_background(self):
        """
        Removes background using reference or modeled backgrounds.
        """
        # set function name
        func_name = f"{__NAME__}.JWST.subtract_background"
        # ---------------------------------------------------------------------
        # get params from step constant
        run_step, mode, kwargs = self.from_step_args(func_name)
        # deal with not running this step
        if not run_step: return
        # ---------------------------------------------------------------------
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # get variables from self
        infiles = self.variables['LAST']
        # loop around infiles
        for it, filename in enumerate(infiles):
            # Read input segments files from disk
            input_data = datamodels.open(filename)
            result = BackgroundStep.call(input_data, output_dir=datadir,
                                         save_results=True, **kwargs)
            # To limit disk usage, erase the file from the previously saved step
            self.remove_intermediate_files(it)
            # update the LAST and RESULT variables
            self.update_last(it, datadir, result.meta.filename, func_name)
    
    def assign_wcs_solution(self):
        """
        Adds WCS (world coordinate system) information.
        """
        # set function name
        func_name = f"{__NAME__}.JWST.assign_wcs_solution"
        # ---------------------------------------------------------------------
        # get params from step constant
        run_step, mode, kwargs = self.from_step_args(func_name)
        # deal with not running this step
        if not run_step: return
        # ---------------------------------------------------------------------
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # get variables from self
        infiles = self.variables['LAST']
        # loop around infiles
        for it, filename in enumerate(infiles):
            # Read input segments files from disk
            input_data = datamodels.open(filename)
            result = AssignWcsStep.call(input_data, output_dir=datadir,
                                        save_results=True, **kwargs)
            # To limit disk usage, erase the file from the previously saved step
            self.remove_intermediate_files(it)
            # update the LAST and RESULT variables
            self.update_last(it, datadir, result.meta.filename, func_name)

    def apply_flat_field(self):
        """
        Corrects pixel-to-pixel sensitivity variations.
        """
        # set function name
        func_name = f"{__NAME__}.JWST.apply_flat_field"
        # ---------------------------------------------------------------------
        # get params from step constant
        run_step, mode, kwargs = self.from_step_args(func_name)
        # deal with not running this step
        if not run_step:
            # save output files to {PREFIX}_rateints.fits
            self.save_outputs('_rateints.fits')
            return
        # ---------------------------------------------------------------------
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # get variables from self
        infiles = self.variables['LAST']
        # loop around infiles
        for it, filename in enumerate(infiles):
            # Read input segments files from disk
            input_data = datamodels.open(filename)
            result = FlatFieldStep.call(input_data, output_dir=datadir,
                                        save_results=True, **kwargs)
            # To limit disk usage, erase the file from the previously saved step
            self.remove_intermediate_files(it)
            # update the LAST and RESULT variables
            self.update_last(it, datadir, result.meta.filename, func_name)
        
    def apply_photometric_calibration(self):
        """
        Converts data units to physical flux units.
        """
        # set function name
        func_name = f"{__NAME__}.JWST.apply_photometric_calibration"
        # ---------------------------------------------------------------------
        # get params from step constant
        run_step, mode, kwargs = self.from_step_args(func_name)
        # deal with not running this step
        if not run_step:
            # save output files to {PREFIX}_rateints.fits
            self.save_outputs('_calints.fits')
            return
        # ---------------------------------------------------------------------
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # get variables from self
        infiles = self.variables['LAST']
        # loop around infiles
        for it, filename in enumerate(infiles):
            # Read input segments files from disk
            input_data = datamodels.open(filename)
            result = PhotomStep.call(input_data, output_dir=datadir,
                                     save_results=True, **kwargs)
            # To limit disk usage, erase the file from the previously saved step
            self.remove_intermediate_files(it)
            # update the LAST and RESULT variables
            self.update_last(it, datadir, result.meta.filename, func_name)

    # =========================================================================
    # Additional Level 1 detector processing steps (individual step callers)
    # =========================================================================
    # These methods are called by benchmark implementations to run individual
    # steps rather than bundled into initialize_detector_data()

    def group_scale_step(self):
        """
        Scale group data to account for on-chip amplifier effects.
        """
        # set function name
        func_name = f"{__NAME__}.JWST.group_scale_step"
        # get params from step constant
        run_step, mode, kwargs = self.from_step_args(func_name)
        # deal with not running this step
        if not run_step: return
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # get variables from self
        infiles = self.variables['LAST']
        # loop around infiles
        for it, filename in enumerate(infiles):
            # Read input segments files from disk
            input_data = datamodels.open(filename)
            result = GroupScaleStep.call(input_data, output_dir=datadir,
                                         save_results=True, **kwargs)
            # To limit disk usage, erase the file from the previously saved step
            self.remove_intermediate_files(it)
            # update the LAST and RESULT variables
            self.update_last(it, datadir, result.meta.filename, func_name)

    def dq_init_step(self):
        """
        Initialize data quality flags.
        """
        # set function name
        func_name = f"{__NAME__}.JWST.dq_init_step"
        # get params from step constant
        run_step, mode, kwargs = self.from_step_args(func_name)
        # deal with not running this step
        if not run_step: return
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # get variables from self
        infiles = self.variables['LAST']
        # loop around infiles
        for it, filename in enumerate(infiles):
            # Read input segments files from disk
            input_data = datamodels.open(filename)
            result = DQInitStep.call(input_data, output_dir=datadir,
                                     save_results=True, **kwargs)
            # To limit disk usage, erase the file from the previously saved step
            self.remove_intermediate_files(it)
            # update the LAST and RESULT variables
            self.update_last(it, datadir, result.meta.filename, func_name)

    def emicorr_step(self):
        """
        Apply EMI (electro-magnetic interference) corrections.
        """
        # set function name
        func_name = f"{__NAME__}.JWST.emicorr_step"
        # get params from step constant
        run_step, mode, kwargs = self.from_step_args(func_name)
        # deal with not running this step
        if not run_step: return
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # get variables from self
        infiles = self.variables['LAST']
        # loop around infiles
        for it, filename in enumerate(infiles):
            # Read input segments files from disk
            input_data = datamodels.open(filename)
            result = EmiCorrStep.call(input_data, output_dir=datadir,
                                      save_results=True, **kwargs)
            # To limit disk usage, erase the file from the previously saved step
            self.remove_intermediate_files(it)
            # update the LAST and RESULT variables
            self.update_last(it, datadir, result.meta.filename, func_name)

    def saturation_step(self):
        """
        Flag saturated pixels.
        """
        # set function name
        func_name = f"{__NAME__}.JWST.saturation_step"
        # get params from step constant
        run_step, mode, kwargs = self.from_step_args(func_name)
        # deal with not running this step
        if not run_step: return
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # get variables from self
        infiles = self.variables['LAST']
        # loop around infiles
        for it, filename in enumerate(infiles):
            # Read input segments files from disk
            input_data = datamodels.open(filename)
            result = SaturationStep.call(input_data, output_dir=datadir,
                                         save_results=True, **kwargs)
            # To limit disk usage, erase the file from the previously saved step
            self.remove_intermediate_files(it)
            # update the LAST and RESULT variables
            self.update_last(it, datadir, result.meta.filename, func_name)

    def subtract_superbias(self):
        """
        Subtract superbias reference for NIR instruments.
        """
        # set function name
        func_name = f"{__NAME__}.JWST.subtract_superbias"
        # get params from step constant
        run_step, mode, kwargs = self.from_step_args(func_name)
        # deal with not running this step
        if not run_step: return
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # get variables from self
        infiles = self.variables['LAST']
        # loop around infiles
        for it, filename in enumerate(infiles):
            # Read input segments files from disk
            input_data = datamodels.open(filename)
            result = SuperBiasStep.call(input_data, output_dir=datadir,
                                        save_results=True, **kwargs)
            # To limit disk usage, erase the file from the previously saved step
            self.remove_intermediate_files(it)
            # update the LAST and RESULT variables
            self.update_last(it, datadir, result.meta.filename, func_name)

    def picture_frame_step(self):
        """
        Correct for picture frame effect.
        """
        # set function name
        func_name = f"{__NAME__}.JWST.picture_frame_step"
        # get params from step constant
        run_step, mode, kwargs = self.from_step_args(func_name)
        # deal with not running this step
        if not run_step: return
        # NOTE: Picture frame step is not a standard step in JWST pipeline
        msg = 'Picture frame step not implemented in standard JWST pipeline'
        WLOG(self.params, 'warning', msg)
        return

    def correct_persistence(self):
        """
        Correct for charge persistence between integrations.
        """
        # set function name
        func_name = f"{__NAME__}.JWST.correct_persistence"
        # get params from step constant
        run_step, mode, kwargs = self.from_step_args(func_name)
        # deal with not running this step
        if not run_step: return
        # NOTE: Persistence step is not implemented in standard JWST pipeline
        msg = 'Persistence correction not available in standard JWST pipeline'
        WLOG(self.params, 'warning', msg)
        return

    # =========================================================================
    # Level 2 spectroscopic and imaging processing steps
    # =========================================================================

    def extract_2d_spectrum(self):
        """
        Extract 2D spectrum from detector image.
        """
        # set function name
        func_name = f"{__NAME__}.JWST.extract_2d_spectrum"
        # get params from step constant
        run_step, mode, kwargs = self.from_step_args(func_name)
        # deal with not running this step
        if not run_step: return
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # get variables from self
        infiles = self.variables['LAST']
        # loop around infiles
        for it, filename in enumerate(infiles):
            # Read input segments files from disk
            input_data = datamodels.open(filename)
            result = Extract2dStep.call(input_data, output_dir=datadir,
                                        save_results=True, **kwargs)
            # To limit disk usage, erase the file from the previously saved step
            self.remove_intermediate_files(it)
            # update the LAST and RESULT variables
            self.update_last(it, datadir, result.meta.filename, func_name)

    def extract_1d_spectrum(self):
        """
        Extract 1D spectrum from 2D data.

        Returns
        -------
        list[str]
            Absolute paths to the produced 1D spectrum files.
        """
        # set function name
        func_name = f"{__NAME__}.JWST.extract_1d_spectrum"
        # get params from step constant
        run_step, mode, kwargs = self.from_step_args(func_name)
        # deal with not running this step
        if not run_step:
            return []
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # get variables from self
        infiles = self.variables['LAST']
        outlist = []
        # loop around infiles
        for it, filename in enumerate(infiles):
            # Read input segments files from disk
            input_data = datamodels.open(filename)
            result = Extract1dStep.call(input_data, output_dir=datadir,
                                        save_results=True, **kwargs)
            # erase previous step file to limit disk usage
            self.remove_intermediate_files(it)
            # update LAST and RESULT
            self.update_last(it, datadir, result.meta.filename, func_name)
            # add absolute path to list
            outlist.append(self.variables['LAST'][it])
        return outlist

    def srctype_determination(self):
        """
        Determine source type for photometric calibration.
        """
        # set function name
        func_name = f"{__NAME__}.JWST.srctype_determination"
        # get params from step constant
        run_step, mode, kwargs = self.from_step_args(func_name)
        # deal with not running this step
        if not run_step: return
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # get variables from self
        infiles = self.variables['LAST']
        # loop around infiles
        for it, filename in enumerate(infiles):
            # Read input segments files from disk
            input_data = datamodels.open(filename)
            result = SourceTypeStep.call(input_data, output_dir=datadir,
                                         save_results=True, **kwargs)
            # To limit disk usage, erase the file from the previously saved step
            self.remove_intermediate_files(it)
            # update the LAST and RESULT variables
            self.update_last(it, datadir, result.meta.filename, func_name)

    def correct_stray_light(self):
        """
        Remove stray light from the data.
        """
        # set function name
        func_name = f"{__NAME__}.JWST.correct_stray_light"
        # get params from step constant
        run_step, mode, kwargs = self.from_step_args(func_name)
        # deal with not running this step
        if not run_step: return
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # get variables from self
        infiles = self.variables['LAST']
        # loop around infiles
        for it, filename in enumerate(infiles):
            # Read input segments files from disk
            input_data = datamodels.open(filename)
            result = StraylightStep.call(input_data, output_dir=datadir,
                                         save_results=True, **kwargs)
            # To limit disk usage, erase the file from the previously saved step
            self.remove_intermediate_files(it)
            # update the LAST and RESULT variables
            self.update_last(it, datadir, result.meta.filename, func_name)

    def correct_fringe(self):
        """
        Remove fringe patterns from the data.
        """
        # set function name
        func_name = f"{__NAME__}.JWST.correct_fringe"
        # get params from step constant
        run_step, mode, kwargs = self.from_step_args(func_name)
        # deal with not running this step
        if not run_step: return
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # get variables from self
        infiles = self.variables['LAST']
        # loop around infiles
        for it, filename in enumerate(infiles):
            # Read input segments files from disk
            input_data = datamodels.open(filename)
            result = FringeStep.call(input_data, output_dir=datadir,
                                     save_results=True, **kwargs)
            # To limit disk usage, erase the file from the previously saved step
            self.remove_intermediate_files(it)
            # update the LAST and RESULT variables
            self.update_last(it, datadir, result.meta.filename, func_name)

    def correct_path_loss(self):
        """
        Correct for path loss through the optical system.
        """
        # set function name
        func_name = f"{__NAME__}.JWST.correct_path_loss"
        # get params from step constant
        run_step, mode, kwargs = self.from_step_args(func_name)
        # deal with not running this step
        if not run_step: return
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # get variables from self
        infiles = self.variables['LAST']
        # loop around infiles
        for it, filename in enumerate(infiles):
            # Read input segments files from disk
            input_data = datamodels.open(filename)
            result = PathLossStep.call(input_data, output_dir=datadir,
                                       save_results=True, **kwargs)
            # To limit disk usage, erase the file from the previously saved step
            self.remove_intermediate_files(it)
            # update the LAST and RESULT variables
            self.update_last(it, datadir, result.meta.filename, func_name)

    def correct_bar_shadow(self):
        """
        Correct for bar shadow effect.
        """
        # set function name
        func_name = f"{__NAME__}.JWST.correct_bar_shadow"
        # get params from step constant
        run_step, mode, kwargs = self.from_step_args(func_name)
        # deal with not running this step
        if not run_step: return
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # get variables from self
        infiles = self.variables['LAST']
        # loop around infiles
        for it, filename in enumerate(infiles):
            # Read input segments files from disk
            input_data = datamodels.open(filename)
            result = BarShadowStep.call(input_data, output_dir=datadir,
                                        save_results=True, **kwargs)
            # To limit disk usage, erase the file from the previously saved step
            self.remove_intermediate_files(it)
            # update the LAST and RESULT variables
            self.update_last(it, datadir, result.meta.filename, func_name)

    def correct_wfss_contamination(self):
        """
        Correct for WFSS contamination.
        """
        # set function name
        func_name = f"{__NAME__}.JWST.correct_wfss_contamination"
        # get params from step constant
        run_step, mode, kwargs = self.from_step_args(func_name)
        # deal with not running this step
        if not run_step: return
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # get variables from self
        infiles = self.variables['LAST']
        # loop around infiles
        for it, filename in enumerate(infiles):
            # Read input segments files from disk
            input_data = datamodels.open(filename)
            result = WfssContamStep.call(input_data, output_dir=datadir,
                                         save_results=True, **kwargs)
            # To limit disk usage, erase the file from the previously saved step
            self.remove_intermediate_files(it)
            # update the LAST and RESULT variables
            self.update_last(it, datadir, result.meta.filename, func_name)

    def correct_wavelength(self):
        """
        Correct wavelength calibration.
        """
        # set function name
        func_name = f"{__NAME__}.JWST.correct_wavelength"
        # get params from step constant
        run_step, mode, kwargs = self.from_step_args(func_name)
        # deal with not running this step
        if not run_step: return
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # get variables from self
        infiles = self.variables['LAST']
        # loop around infiles
        for it, filename in enumerate(infiles):
            # Read input segments files from disk
            input_data = datamodels.open(filename)
            result = WavecorrStep.call(input_data, output_dir=datadir,
                                       save_results=True, **kwargs)
            # To limit disk usage, erase the file from the previously saved step
            self.remove_intermediate_files(it)
            # update the LAST and RESULT variables
            self.update_last(it, datadir, result.meta.filename, func_name)

    def subtract_master_background(self):
        """
        Subtract master background for NIRSpec MOS data.
        """
        # set function name
        func_name = f"{__NAME__}.JWST.subtract_master_background"
        # get params from step constant
        run_step, mode, kwargs = self.from_step_args(func_name)
        # deal with not running this step
        if not run_step: return
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # get variables from self
        infiles = self.variables['LAST']
        # loop around infiles
        for it, filename in enumerate(infiles):
            # Read input segments files from disk
            input_data = datamodels.open(filename)
            result = MasterBackgroundStep.call(input_data, output_dir=datadir,
                                               save_results=True, **kwargs)
            # To limit disk usage, erase the file from the previously saved step
            self.remove_intermediate_files(it)
            # update the LAST and RESULT variables
            self.update_last(it, datadir, result.meta.filename, func_name)

    def measure_target_centroid(self):
        """
        Measure target centroid position.
        """
        # set function name
        func_name = f"{__NAME__}.JWST.measure_target_centroid"
        # NOTE: Target centroid is rarely used
        msg = 'Target centroid measurement not commonly used'
        WLOG(self.params, 'warning', msg)
        return

    def correct_residual_fringe(self):
        """
        Correct for residual fringe patterns (MIRI-specific).
        """
        # set function name
        func_name = f"{__NAME__}.JWST.correct_residual_fringe"
        # NOTE: Residual fringe correction is MIRI-specific and not in standard
        msg = 'Residual fringe correction not in standard JWST pipeline'
        WLOG(self.params, 'warning', msg)
        return

    def resample_images(self):
        """
        Resample images to a common grid.
        """
        # set function name
        func_name = f"{__NAME__}.JWST.resample_images"
        # get params from step constant
        run_step, mode, kwargs = self.from_step_args(func_name)
        # deal with not running this step
        if not run_step: return
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # get variables from self
        infiles = self.variables['LAST']
        # loop around infiles
        for it, filename in enumerate(infiles):
            # Read input segments files from disk
            input_data = datamodels.open(filename)
            result = ResampleStep.call(input_data, output_dir=datadir,
                                       save_results=True, **kwargs)
            # To limit disk usage, erase the file from the previously saved step
            self.remove_intermediate_files(it)
            # update the LAST and RESULT variables
            self.update_last(it, datadir, result.meta.filename, func_name)


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

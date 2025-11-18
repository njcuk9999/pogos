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
from jwst.charge_migration import ChargeMigrationStep
from jwst.clean_flicker_noise import CleanFlickerNoiseStep
from jwst.dark_current import DarkCurrentStep
from jwst.dq_init import DQInitStep
from jwst.firstframe import FirstFrameStep
from jwst.flatfield import FlatFieldStep
from jwst.gain_scale import GainScaleStep
from jwst.group_scale import GroupScaleStep
from jwst.ipc import IPCStep
from jwst.jump import JumpStep
from jwst.lastframe import LastFrameStep
from jwst.linearity import LinearityStep
from jwst.photom import PhotomStep
from jwst.ramp_fitting import RampFitStep
from jwst.refpix import RefPixStep
from jwst.reset import ResetStep
from jwst.rscd import RscdStep
from jwst.saturation import SaturationStep

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
                    emsg = f'Input file {absfile} does not exist on disk'
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

    def save_outputs(self, suffix: str):
        """
        Rename the last file to have a given suffix

        :param suffix: str, the suffix to add to the filename
        """
        # set function name
        func_name = f"{__NAME__}.Instrument.rename_results"
        # get variables from self
        infiles = self.variables['LAST']
        prefixes = self.variables['PREFIXES']
        # get parameters from params
        datadir = self.tparams['PATHS.TEMP_PATH']
        # storage for OUT variable
        out_files = []
        # loop around infiles
        for it, filename in enumerate(infiles):
            # construct new filename
            new_base_name = prefixes[it] + suffix
            new_filename = str(os.path.join(datadir, new_base_name))
            # deal with files not existing (not allowed)
            if not os.path.exists(infiles[it]):
                wmsg = (f'File {infiles[it]} does not exist on disk. '
                        f'Cannot add to out. This may crash future steps.')
                WLOG(self.params, 'warning', wmsg)
                return
            else:
                wmsg = (f'Copying file {infiles[it]} to {new_filename}')
                WLOG(self.params, 'info', wmsg)
            # copy the file
            shutil.copy(infiles[it], new_filename)
            # save files to list
            out_files.append(new_filename)
        # update the LAST variable
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
            emsg = f'"{step_arg}" not found in parameters'
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
            msg = f'\n\nRunning {step_name} mode={mode}'
            mlevel = 'info'
        else:
            # print message
            msg = f'\n\nSkipping "{step_name}" [{step_arg}.RUN=False]'
            mlevel = 'warning'
        WLOG(self.params, mlevel, '*'*50)
        WLOG(self.params, mlevel, msg)
        WLOG(self.params, mlevel, '*' * 50)
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
            msg = (f'\tINPUTS.SKIP_PROCESSED_FILES=True\n\tAll expected '
                   f'output files found with suffix '
                   f'"{suffix}".\n\tSkipping step "{step_name}".')
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
        self.correct_charge_migration()

        # Step 1.14: JumpStep
        self.detect_and_flag_jumps()

        # Step 1.15: CleanFlickerStep
        self.remove_flicker_noise()

        # Step 1.16: RampFitStep
        self.fit_signal_ramps()

        # Step 1.17: GainScaleStep
        self.apply_gain_scaling()

        # This is where the _rateints files are created
        # save LAST to output file with {PREFIX}_rateints.fits
        self.save_outputs('_rateints.fits')

        # ---------------------------------------------------------------------
        # Level 2 Processing Steps
        # ---------------------------------------------------------------------
        # Step 2.1: BackgroundStep
        self.subtract_background()

        # Step 2.2: AssignWcsStep
        self.assign_wcs_solution()

        # Step 2.3: FlatFieldStep
        self.apply_flat_field()

        # Step 2.4: PhotomStep
        self.apply_photometric_calibration()

        # This is where the calints files are created
        # save LAST to output file with {PREFIX}_calints.fits
        self.save_outputs('_calints.fits')

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
            #     the previous step's file is modified when running the 
            #     JumpStep. I don't know why.
            # To limit disk usage, erase the file from the previously saved step
            # self.remove_intermediate_files(it)
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

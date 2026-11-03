#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2025-10-16 at 13:39

@author: cook
"""
import shutil
import string
import os
from copy import deepcopy
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from aperocore.constants.param_functions import ParamDict
from aperocore.constants import load_functions
from aperocore.core import drs_log
from aperocore.core import drs_misc
from pogos.core import base as pogos_base
from pogos.core import definitions
from pogos.core import general as pogos_general
from pogos.core import io as pogos_io
from pogos.sorbet.core import base as sorbet_base
from pogos.sorbet.core import core as sorbet_core
from sossisse.core import misc
from sossisse.instruments import default as sdefault


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'pogos.sorbet.core.core'
__PACKAGE__ = pogos_base.__PACKAGE__
__version__ = pogos_base.__version__
__authors__ = pogos_base.__authors__
__date__ = pogos_base.__date__
__release__ = pogos_base.__release__
# get the Drs Exceptions
AperoCodedException = drs_log.AperoCodedException
AperoCodedWarning = drs_log.AperoCodedWarning
# get display func
display_func = drs_misc.display_func
# Get Logging function
WLOG = drs_log.wlog
# Define the SORBET run constants
RUN_CONSTANTS = ['RUN.SORBET.WLCA', 'RUN.SORBET.SLCA']  # , 'SORBET.TFIT.RUN', 'SORBET.RV.RUN']
# get all chars
CHARS = string.ascii_uppercase + string.digits


def _load_sorbet_runtime_modules():
    from pogos.sorbet.general import science as sorbet_science
    from pogos.sorbet.general import plots as sorbet_plots
    return sorbet_science, sorbet_plots


# =============================================================================
# Define functions
# =============================================================================
def setup_sorbet_module(params: ParamDict):
    """
    Setup the SORBET module

    :param params: ParamDict, the parameter dictionary of constants

    :return: Updated params, sets up sorbet module
    """
    # deal with no requiring to run sorbet
    if not any_sorbet_run(params):
        return params
    run_wlca = params.rget('RUN.SORBET.WLCA', required=True)
    run_slca = params.rget('RUN.SORBET.SLCA', required=True)
    # ----------------------------------------------------------------------
    # setup the wlca  input and output directories
    if run_wlca:
        # prepare directories
        prepare_directories(params, method='WLCA')
    # ----------------------------------------------------------------------
    # setup the slca  input and output directories
    if run_slca:
        # prepare directories
        prepare_directories(params, method='SLCA')

    return params


def any_sorbet_run(params: ParamDict) -> bool:
    """
    Loop through SORBET sub modules and see if any have RUN.XXXX as True

    :param params: ParamDict, the parameter dictionary of constants

    :return: bool, True if any SORBET sub module has RUN.XXX = True,
                   False otherwise
    """
    # loop around all sorbet modules and check for any to be True to run
    # them
    sorbet_steps = (definitions.SORBET_WLCA, definitions.SORBET_SLCA)
    for step in sorbet_steps:
        if step.run_key in params:
            run_step = params.rget(step.run_key, required=True)
            if run_step:
                return True
    # if we get here then nothing is set to run
    return False


def run_sorbet_module(params: ParamDict, ext_inst: Dict[str, Any]):
    """
    Run the sorbet recipes

    :param params: ParamDict, the parameter dictionary of constants

    :return: Updated params, runs sorbet recipes
    """
    # set the function name
    func_name = f'{__NAME__}.run_sorbet_module'
    # -------------------------------------------------------------------------
    # get the instances from the pre-extraction step
    sossisse_inst = ext_inst.get('sossisse', None)
    miriam_params = ext_inst.get('miriam', None)
    # -------------------------------------------------------------------------
    # Check at least one recipe is set to run
    run_any = False
    for key in RUN_CONSTANTS:
        run_step = params.rget(key, required=True, func=func_name)
        if run_step:
            run_any = True
            break
    # if not running any then skip SORBET
    if not run_any:
        WLOG(params, 'warning', 'No SORBET recipes set to run - skipping.')
        return params

    # ----------------------------------------------------------------------
    # Deal with input from SOSSISSE and MIRIAM if available
    # ----------------------------------------------------------------------
    if sossisse_inst is not None:
        params = sossisse_input(params, sossisse_inst)
    if miriam_params is not None:
        params = miriam_input(params, miriam_params)

    # ----------------------------------------------------------------------
    # White Light Curve Transit Analysis
    # ----------------------------------------------------------------------
    run_wlca = params.rget('RUN.SORBET.WLCA', required=True, func=func_name)
    if run_wlca:
        params = run_sorbet_wlcta(params)

    # ----------------------------------------------------------------------
    # Spectral Light Curve Transit Analysis
    # ----------------------------------------------------------------------
    run_slca = params.rget('RUN.SORBET.SLCA', required=True, func=func_name)
    if run_slca:
        params = run_sorbet_slcta(params)

    # ----------------------------------------------------------------------
    # TFIT
    # ----------------------------------------------------------------------
    # if params['SORBET.TFIT.RUN']:
    #    params = run_sorbet_tfit(params)

    # ----------------------------------------------------------------------
    # RV Module
    # ----------------------------------------------------------------------
    # if params['SORBET.RV.RUN']:
    #    params = run_sorbet_rv(params)

    return params


def sossisse_input(params: ParamDict,
                  sossisse_inst: Optional[sdefault.Instrument] = None
                  ) -> ParamDict:
    """
    Copy SOSSISSE light curves and forward its selected traces to SORBET.

    A trace is a SOSS diffraction order or a NIRSpec detector (1=NRS1,
    2=NRS2). Other instruments may use one unnumbered trace. A combined
    spectral file is repeated once per selection; SOSS white-light tables
    may still contain shared reconstruction amplitudes rather than
    independently measured order light curves.

    :param params: POGOS parameters, updated in place with input basenames
        and user-facing WLCA/SLCA trace selections.
    :param sossisse_inst: Completed instance owning the output paths,
        filename prefix, and GENERAL.TRACES selection.
    :return: Updated params after copying products for enabled analyses.
    :raises sorbet_base.SorbetException: Invalid trace selection.
    """
    # set function name
    func_name = f'{__NAME__}.sossisse_input'
    # -------------------------------------------------------------------------
    # after sossisse run we may need to copy files to SORBET input location
    sossisse_output_dir = sossisse_inst.params['PATHS.OUT_PATH']
    run_wlca = params.rget('RUN.SORBET.WLCA', required=True, func=func_name)
    run_slca = params.rget('RUN.SORBET.SLCA', required=True, func=func_name)
    # get sorbet parameters
    sb_params = params.get('SORBET')
    # get sossisse parameters
    sossisse_params = sossisse_inst.params
    # get sossisse files to copy
    sossisse_wlc_file = sossisse_inst.get_variable('OUT_WLC_FILE',
                                                   func_name)
    sossisse_spec_lc_file = sossisse_inst.get_variable('OUT_SPEC_LC_FILE',
                                                       func_name)
    # -------------------------------------------------------------------------
    # get the prefix used for the sossisse files
    sossisse_prefix = sossisse_params['GENERAL.PREFIX']
    if sossisse_prefix is None:
        sossisse_files = sossisse_params.rget('GENERAL.FILES', required=True,
                                             func=func_name)
        sossisse_prefix = load_functions.common_prefix(sossisse_files)
    # add the prefix to wlc and spec file
    sossisse_wlc_file = sossisse_wlc_file.format(prefix=sossisse_prefix)
    sossisse_spec_lc_file = sossisse_spec_lc_file.format(prefix=sossisse_prefix)
    # Use the completed instance's selection, not stale wrapper parameters.
    traces = sossisse_params.get('GENERAL.TRACES')
    _validate_traces(traces, 'GENERAL.TRACES')
    # Give both analyses independent copies of the user-facing selection.
    for method in ('WLCA', 'SLCA'):
        trace_key = f'SORBET.{method}.TRACES'
        params[trace_key] = list(traces) if traces is not None else None
        # Record that the selection came from this completed backend run.
        params.set_source(trace_key, func_name)

    # ---------------------------------------------------------------------
    # deal with WLCA files
    if run_wlca:
        # prepare input directory
        prepare_directories(params, method='WLCA', verbose=False)
        # get the sorbet input directory for WLCA
        sorbet_wlcta_indir = sb_params.rget('WLCA.INPUT_PATH', required=True,
                           func=func_name)
        sorbet_wlcta_indir = str(sorbet_wlcta_indir)
        sossisse_wlc_base = str(os.path.basename(sossisse_wlc_file))
        # get absolute path to
        sorbet_file = str(os.path.join(sorbet_wlcta_indir, sossisse_wlc_base))
        # copy linear recon coeffs csv file
        shutil.copy(sossisse_wlc_file, sorbet_file)
        # update params
        params['SORBET.WLCA.INPUT_FILE'] = os.path.basename(sorbet_file)
        params.set_source('SORBET.WLCA.INPUT_FILE', func_name)
    # ---------------------------------------------------------------------
    # deal with SLCA files
    if run_slca:
        # prepare input directory
        prepare_directories(params, method='SLCA', verbose=False)
        # get the sorbet input directory for SLCA
        sorbet_slcta_indir = sb_params.rget('SLCA.INPUT_PATH', required=True,
                           func=func_name)
        sorbet_slcta_indir = str(sorbet_slcta_indir)
        sossisse_spec_lc_base = str(os.path.basename(sossisse_spec_lc_file))
        # get absolute path to
        sorbet_file = str(os.path.join(sorbet_slcta_indir, sossisse_spec_lc_base))
        # copy linear recon coeffs csv file
        shutil.copy(sossisse_spec_lc_file, sorbet_file)
        # Pair each selected trace with the same combined spectral product.
        trace_count = len(traces) if traces is not None else 1
        params['SORBET.SLCA.INPUT_FILE'] = (
            [os.path.basename(sorbet_file)] * trace_count)
        params.set_source('SORBET.SLCA.INPUT_FILE', func_name)
    # return params
    return params


def miriam_input(params: ParamDict,
                 miriam_params: Optional[ParamDict] = None
                 ) -> ParamDict:
    func_name = f'{__NAME__}.miriam_input'
    # -------------------------------------------------------------------------
    # get sorbet parameters
    sb_params = params.get('SORBET')
    # get MIRIAM file to copy
    miriam_wlc_file = miriam_params.get('WLC_FILE', None)
    # deal with no MIRIAM WLC file
    if miriam_wlc_file is None:
        return params
    run_wlca = sb_params.rget('WLCA.RUN', required=True, func=func_name)
    miriam_wlc_file = str(miriam_wlc_file)
    # ---------------------------------------------------------------------
    # deal with WLCA files
    if run_wlca:
        # prepare input directory
        prepare_directories(params, method='WLCA', verbose=False)
        # get the sorbet input directory for WLCA
        sorbet_wlcta_input_dir = sb_params.rget('WLCA.INPUT_PATH',
                               required=True, func=func_name)
        sorbet_wlcta_input_dir = str(sorbet_wlcta_input_dir)
        # get absolute path to
        sorbet_file = str(os.path.join(sorbet_wlcta_input_dir,
                                       os.path.basename(miriam_wlc_file)))
        # copy linear recon coeffs csv file
        shutil.copy(miriam_wlc_file, sorbet_file)
        # update params
        params['SORBET.WLCA.INPUT_FILE'] = os.path.basename(sorbet_file)
        params.set_source('SORBET.WLCA.INPUT_FILE', func_name)
    # return params
    return params


def _validate_traces(traces, parameter: str):
    """
    Validate a user-facing trace selection without coercing identifiers.

    :param traces: None for one unnumbered trace, or a nonempty list of
        unique positive integers. Booleans are not trace identifiers.
    :param parameter: Parameter name included in validation errors.
    :return: None; the selection is not modified.
    :raises sorbet_base.SorbetException: Invalid container or identifier.
    """
    # None deliberately preserves the single unnumbered-product workflow.
    if traces is None:
        return
    # Reject containers before iterating or attempting duplicate detection.
    invalid_selection = not isinstance(traces, list) or not traces
    if not invalid_selection:
        # Check types first so malformed entries never reach set().
        invalid_identifiers = any(
            isinstance(trace, bool) or not isinstance(trace, int) or trace < 1
            for trace in traces)
        invalid_selection = (
            invalid_identifiers or len(set(traces)) != len(traces))
    # Keep one diagnostic for invalid containers, entries, and duplicates.
    if invalid_selection:
        raise sorbet_base.SorbetException(
            f'{parameter} must be None or a nonempty list of unique positive '
            'integer trace identifiers.')


def run_sorbet_wlcta(params: ParamDict):
    """
    Fit selected traces separately, or run once for an unnumbered product.

    :param params: POGOS parameters with optional user-facing WLCA.TRACES.
        Mutated with the runtime-only TRACE_FIT_PARAMS mapping after fits.
    :return: Updated params, or the single unnumbered runner's result.
    :raises sorbet_base.SorbetException: Invalid trace selection.
    """
    # Validate before resetting fit state or invoking a scientific runner.
    traces = params.get('SORBET.WLCA.TRACES')
    _validate_traces(traces, 'SORBET.WLCA.TRACES')
    # Do not reuse fitted state from an earlier invocation.
    params['SORBET.WLCA.TRACE_FIT_PARAMS'] = None
    if traces is None:
        # Preserve the legacy runner's in-place parameter updates.
        params['SORBET.WLCA.TRACE'] = None
        return _run_sorbet_wlcta(params)
    # Resolve common paths before deriving isolated per-trace directories.
    prepare_directories(params, method='WLCA')
    trace_fit_params = dict()
    # Deep copies keep priors and fitted parameters independent per trace.
    for trace in traces:
        fit_params = _trace_fit_params(params, trace)
        trace_fit_params[trace] = _run_sorbet_wlcta(fit_params)
    # SLCA will retrieve only the fit corresponding to its selected trace.
    params['SORBET.WLCA.TRACE_FIT_PARAMS'] = trace_fit_params
    return params


def _trace_fit_params(params: ParamDict, trace: Optional[int]):
    """
    Copy fit configuration and isolate a numbered trace's WLCA locations.

    :param params: POGOS parameters, including resolved WLCA paths when a
        numbered trace is selected. Nested fit state is copied, not shared.
    :param trace: Positive trace identifier, or None for unnumbered data.
    :return: Independent parameters with runtime-only TRACE set and any
        cached trace fits cleared. Numbered paths end in trace<identifier>.
    """
    # Include nested priors in the copy to prevent cross-trace mutations.
    fit_params = deepcopy(params)
    # A trace's configuration must not retain the parent cache of fits.
    fit_params['SORBET.WLCA.TRACE_FIT_PARAMS'] = None
    fit_params['SORBET.WLCA.TRACE'] = trace
    # Unnumbered products keep their original output locations.
    if trace is None:
        return fit_params
    # Isolate both saved results and diagnostics without changing the parent.
    for path_kind in ('OUTPUT_PATH', 'PLOT_PATH'):
        path_key = f'SORBET.WLCA.{path_kind}'
        base_path = params.rget(path_key, required=True)
        fit_params[path_key] = os.path.join(base_path, f'trace{trace}')
    return fit_params


def _run_sorbet_wlcta(params: ParamDict):
    """
    Run the SORBET White Light Curve Transit Analysis recipe

    :param params: ParamDict, the parameter dictionary of constants

    :return: Updated params, runs sorbet recipes
    """
    # set the function name
    func_name = f'{__NAME__}.run_sorbet_wlca'
    sorbet_science, sorbet_plots = _load_sorbet_runtime_modules()
    # print the white light curve splash
    print(misc.art('SORBET WLC Transit Analysis', 'yellow', 'CYAN'))
    # --------------------------------------------------------------------------
    # prepare input directories
    prepare_directories(params, method='WLCA')
    # load the dataset
    data_table = sorbet_science.load_wlc(params)
    # -----------------------------------------------------------------
    # print progress
    msg = f'Finding outliers for white light curve...'
    WLOG(params, '', msg)
    # find outliers
    medfilt_model, outlier_mask = sorbet_science.find_outliers(params,
                                                               data_table,
                                                               method='WLCA')
    # diagnostic plot for outlier removal
    sorbet_plots.plot_outlier(params, data_table, medfilt_model, outlier_mask,
                              method='WLCA')
    # -------------------------------------------------------------------------
    # prepare the dataset for juliet
    dataset = sorbet_science.prepare_dataset(params, data_table, method='WLCA',
                                             outlier_mask=outlier_mask)
    # -------------------------------------------------------------------------
    # print progress
    msg = f'Fitting white light curve...'
    WLOG(params, '', msg)
    # fit the dataset with juliet/batman
    results = sorbet_science.fit_transit(params, dataset, method='WLCA')
    # -------------------------------------------------------------------------
    # save the model components to disk
    sorbet_science.save_transit_model(params, dataset, results, method='WLCA')
    # -------------------------------------------------------------------------
    # plot the results (corner plot)
    sorbet_plots.plot_corner(params, dataset, results, method='WLCA')
    # -------------------------------------------------------------------------
    # plot the best-fit model
    sorbet_plots.plot_transit(params, dataset, results, method='WLCA')
    # -------------------------------------------------------------------------
    # produce summary html
    stitle = params.get('SORBET.GENERAL.DESCRIPTION', '')
    pogos_io.summary_html(params, 'SORBET:WLCA', 'SORBET.WLCA.PLOT_PATH',
                          'GLOBAL.PROJECT_NAME',
                          'SORBET.WLCA.OUTPUT_PATH',
                          stitle)
    # return params
    return params


def _deal_with_slcta_input_file(params) -> Tuple[List[str], List[int | None]]:
    """
    Pair spectral filenames with explicit traces or one unnumbered trace.

    :param params: POGOS parameters containing SLCA.INPUT_FILE and optional
        user-facing SLCA.TRACES. A string filename is accepted as one file.
    :return: Input-file list and equally sized trace list; [None] denotes
        the single unnumbered case. The parameter dictionary is not mutated.
    :raises sorbet_base.SorbetException: Invalid traces, empty input, or
        ambiguous pairing between input files and trace identifiers.
    """
    func_name = f'{__NAME__}._deal_with_slcta_input_file'
    # get the sorbet parameters
    slcta_params = params.get('SORBET.SLCA')
    # check the dataset (multiple channels/traces?)
    input_files = slcta_params.rget('INPUT_FILE', required=True, func=func_name)
    # None is meaningful here and must not become a required setting.
    traces = slcta_params.get('TRACES')
    _validate_traces(traces, 'SORBET.SLCA.TRACES')
    # Normalize a single filename locally without mutating its stored value.
    if isinstance(input_files, str):
        input_files = [input_files]
    # An empty file list cannot describe even an unnumbered trace.
    if not input_files:
        raise sorbet_base.SorbetException(
            'SORBET.SLCA.INPUT_FILE must contain at least one file.')
    # Multiple files require an explicit one-to-one trace selection.
    if traces is None:
        if len(input_files) != 1:
            raise sorbet_base.SorbetException(
                'SORBET.SLCA.TRACES must be provided '
                'for multiple input files.')
        return input_files, [None]
    # Repeated combined filenames are allowed, but every trace needs a file.
    if len(traces) != len(input_files):
        emsg = (f'The number of traces ({len(traces)}) must match '
                f'the number of input files ({len(input_files)}).')
        raise sorbet_base.SorbetException(emsg)

    return input_files, traces


def run_sorbet_slcta(params: ParamDict):
    """
    Run spectral fits with the matching trace's independent WLCA state.

    :param params: POGOS parameters with spectral files, optional selected
        traces, and any runtime-only WLCA.TRACE_FIT_PARAMS cache.
    :return: Parent params, or the unnumbered runner's result. Numbered
        fits use copies and do not mutate cached WLCA fits or other traces.
    :raises sorbet_base.SorbetException: Invalid spectral file/trace pairing.
    """
    # Resolve and validate selection before preparing paths or running fits.
    input_files, traces = _deal_with_slcta_input_file(params)
    if traces == [None]:
        # Preserve the existing single-run behavior and parameter identity.
        return _run_sorbet_slcta(params)
    # Resolve shared paths before deriving trace-specific fit configurations.
    prepare_directories(params, method='WLCA', verbose=False)
    prepare_directories(params, method='SLCA')
    # A standalone SLCA run may not have a previous WLCA fit cache.
    trace_fit_params = params.get('SORBET.WLCA.TRACE_FIT_PARAMS') or dict()
    # Pair traces by identifier, never by another trace's fitted state.
    for input_file, trace in zip(input_files, traces):
        if trace in trace_fit_params:
            # SLCA may mutate fit parameters without changing the stored fit.
            fit_params = deepcopy(trace_fit_params[trace])
        else:
            # Standalone fits still need independent priors and locations.
            fit_params = _trace_fit_params(params, trace)
        # Restrict the delegated runner to this one file/trace pair.
        fit_params['SORBET.SLCA.INPUT_FILE'] = [input_file]
        fit_params['SORBET.SLCA.TRACES'] = [trace]
        # Keep scientific fitting within the existing runtime boundary.
        _run_sorbet_slcta(fit_params)
    return params


def _run_sorbet_slcta(params: ParamDict):
    """
    Run the SORBET Spectral Light Curves Transit Analysis recipe

    :param params: ParamDict, the parameter dictionary of constants

    :return: Updated params, runs sorbet recipes
    """
    # set the function name
    func_name = f'{__NAME__}.run_sorbet_slca'
    sorbet_science, sorbet_plots = _load_sorbet_runtime_modules()
    # print the spectral light curve splash
    print(misc.art('SORBET SLC Transit Analysis', 'blue', 'CYAN'))
    # --------------------------------------------------------------------------
    # prepare directories
    prepare_directories(params, method='SLCA')
    # get input files and traces
    input_files, traces = _deal_with_slcta_input_file(params)
    # --------------------------------------------------------------------------
    # loop around channels
    for chl in range(len(input_files)):
        # load the dataset
        spectral_outputs = sorbet_science.load_slc(params, input_files[chl],
                               traces[chl])
        bjd, wave_tuple, flux_bin, eflux_bin, channel = spectral_outputs
        # eflux_bin = np.ones_like(flux_bin) * 10e-6
        # initiate transmission spectrum table
        tout = sorbet_science.initiate_transmission_spectrum(wave_tuple)
        spec_tbl, nbin = tout
        # looping through spectral bins
        for wb in range(nbin):
            # store bin parameters
            bin_params = dict()
            # print the wavelength bin
            msg = f'Spectral bin {wb + 1}/{nbin}'
            # print the message
            WLOG(params, 'info', msg)
            # set the wavelength bin limits
            bin_params['WAVE_BIN_LOW'] = wave_tuple[1][0, wb]
            bin_params['WAVE_BIN_HIGH'] = wave_tuple[2][0, wb]
            # set the bin suffix
            bin_params['CHANNEL'] = channel
            bin_params['BIN'] = wb
            bin_params['SUFFIX'] = f'ord{channel}bin{wb}'
            # -----------------------------------------------------------------
            # prepare the dataset
            data_table = sorbet_science.create_dataset_table(bjd,
                                                             flux_bin[:, wb],
                                                             eflux_bin[:, wb])
            # make sure we don't have a whole row of nans
            if np.isnan(data_table['RelFlux']).all():
                msg = f'Wavelength bin {wb + 1}/{nbin} is empty, skipping...'
                misc.printc(msg, msg_type='warning')
                continue
            # -----------------------------------------------------------------
            # print progress
            msg = f'Finding outliers for spectral bin {wb + 1}/{nbin}...'
            WLOG(params, '', msg)
            # find outliers
            fout = sorbet_science.find_outliers(params, data_table,
                                                method='SLCA')
            medfilt_model, outlier_mask = fout
            # -----------------------------------------------------------------
            # diagnostic plot for outlier removal
            sorbet_plots.plot_outlier(params, data_table, medfilt_model,
                                      outlier_mask, method='SLCA',
                                      bin_params=bin_params)
            # prepare the dataset for juliet
            dataset = sorbet_science.prepare_dataset(params, data_table,
                                                     method='SLCA',
                                                     outlier_mask=outlier_mask,
                                                     bin_params=bin_params)
            # -----------------------------------------------------------------
            # print progress
            msg = f'Fitting spectral bin {wb + 1}/{nbin}...'
            WLOG(params, '', msg)
            # fit the dataset with juliet/batman
            results = sorbet_science.fit_transit(params, dataset, method='SLCA')
            # -----------------------------------------------------------------
            # save the model components to disk
            sorbet_science.save_transit_model(params, dataset, results,
                                              method='SLCA')
            # -----------------------------------------------------------------
            # plot the results (corner plot)
            sorbet_plots.plot_corner(params, dataset, results, method='SLCA',
                                     bin_params=bin_params)
            # -----------------------------------------------------------------
            # plot the best-fit model
            sorbet_plots.plot_transit(params, dataset, results, method='SLCA',
                                     bin_params=bin_params)
            # -----------------------------------------------------------------
            # append to transmission spectrum table
            spec_tbl = sorbet_science.append_transmission_spec(params, results,
                                                               spec_tbl, wb)
        # ---------------------------------------------------------------------
        # save the transmission spectrum table
        sorbet_science.save_transmission_spectrum(params, spec_tbl, channel)
        # plot the transmission spectrum
        sorbet_plots.plot_transmission_spectrum(params, method='SLCA')
    # -------------------------------------------------------------------------
    # produce summary html
    stitle = params.get('SORBET.GENERAL.DESCRIPTION', '')
    pogos_io.summary_html(params, 'SORBET:SLCA', 'SORBET.SLCA.PLOT_PATH',
                          'GLOBAL.PROJECT_NAME',
                          'SORBET.SLCA.OUTPUT_PATH',
                          stitle)

    # return params
    return params


def prepare_directories(params: ParamDict, method: str, verbose: bool = True):

    mode = f'sorbet'
    # -------------------------------------------------------------------------
    # set parameters for preparing directory
    pkind = 'input'
    file_path = f'SORBET.{method}.INPUT_PATH'
    # run the prepare directory function
    pogos_general.prepare_directory(params, pkind, file_path, mode,
                                    verbose=verbose)
    # -------------------------------------------------------------------------
    # prepare the plots directory
    pkind = 'plot'
    file_path = f'SORBET.{method}.PLOT_PATH'
    # run the prepare directory function
    pogos_general.prepare_directory(params, pkind, file_path, mode,
                                    verbose=verbose)
    # -------------------------------------------------------------------------
    # set parameters for preparing directory
    pkind = 'output'
    file_path = f'SORBET.{method}.OUTPUT_PATH'
    # runt the prepare directory function
    pogos_general.prepare_directory(params, pkind, file_path, mode, verbose)


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

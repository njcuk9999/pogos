#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Verify trace selection, independent fit state, and legacy SOSS products."""

import ast
from copy import deepcopy
import importlib
import os
import shutil
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

import numpy as np
import pytest

from aperocore.constants.param_functions import ParamDict


def load_functions(relative_path, names, **namespace):
    """
    Compile selected functions without importing optional fitting backends.

    :param relative_path: Source path relative to the pogos package.
    :param names: Top-level function names to compile together.
    :param namespace: Dependencies injected into the compiled functions.
    :return: Namespace exposing functions with lightweight runtime globals.
    """
    # Read actual implementation bodies rather than duplicating their logic.
    source_path = Path(__file__).parents[1] / 'pogos' / relative_path
    tree = ast.parse(source_path.read_text())
    # Keep source order so helpers share the same execution namespace.
    functions: list[ast.stmt] = [
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in names]
    # Supply only the framework types and dependencies used by these bodies.
    namespace.update(ParamDict=ParamDict, np=np, os=os,
                     Union=Union, Dict=Dict, Any=Any, List=List,
                     Optional=Optional, Tuple=Tuple, deepcopy=deepcopy,
                     __NAME__='test_sorbet',
                     sorbet_base=SimpleNamespace(SorbetException=ValueError))
    # Retain the source filename in tracebacks from the compiled functions.
    function_module = ast.Module(body=functions, type_ignores=[])
    compiled_functions = compile(function_module, str(source_path), 'exec')
    exec(compiled_functions, namespace)
    return SimpleNamespace(**namespace)


@pytest.fixture(scope='module')
def fits():
    """
    Temporarily replace suite-level Astropy stubs with real FITS support.

    :return: Astropy FITS module; previous sys.modules entries are restored
        when this module-scoped fixture finishes.
    """
    # Keep real FITS I/O local to this module's scientific product tests.
    with pytest.MonkeyPatch.context() as patch:
        for name in list(sys.modules):
            if name == 'astropy' or name.startswith('astropy.'):
                patch.delitem(sys.modules, name)
        # Import only after removing any inherited dependency stubs.
        yield importlib.import_module('astropy.io.fits')


@pytest.mark.parametrize('trace', [1, 2, 3])
@pytest.mark.parametrize('numbered', [False, True])
@pytest.mark.parametrize('mode', ['JWST.NIRSPEC.G395H', 'GENERIC.MODE'])
def test_spectral_traces_keep_channel_and_all_wavelengths(
        tmp_path, trace, numbered, mode, fits):
    """Keep selected channels and all wavelengths outside SOSS order 2."""
    # Exercise the real loader with only its FITS dependency injected.
    science = load_functions('sorbet/general/science.py', ['load_slc'],
                             fits=fits)
    # Distinct lengths and time offsets expose accidental trace substitution.
    times = np.arange(trace + 2, dtype=float) + trace * 100
    wavelength = np.tile([0.5, 0.7, 0.9, 1.1], (len(times), 1))
    flux = np.ones_like(wavelength) * trace
    # Cover both numbered products and legacy unnumbered extension names.
    suffix = f'_{trace}' if numbered else ''
    products = dict(WAVELENGTH=wavelength, RELFLUX=flux,
                    RELFLUX_ERROR=flux / 100, BJD=times)
    filename = tmp_path / 'spectra.fits'
    hdus = [fits.PrimaryHDU()]
    # Every array in a product must share its trace suffix.
    hdus.extend(fits.ImageHDU(data=data, name=name + suffix)
                for name, data in products.items())
    fits.HDUList(hdus).writeto(filename)
    # Disable spectral rebinning so equality checks test extension selection.
    spectral_params = ParamDict()
    spectral_params['RESOLUTION_BIN'] = 1
    params = ParamDict()
    params['RUN.SORBET.SLCA'] = True
    params['GLOBAL.INSTRUMENTMODE'] = mode
    params['SORBET.SLCA'] = spectral_params

    # Keep the delegated call separate from unpacking its scientific arrays.
    spectral_outputs = science.load_slc(params, str(filename), trace)
    bjd, wave_tuple, actual_flux, errors, channel = spectral_outputs

    # Neither generic nor NIRSpec products should receive a SOSS order cut.
    np.testing.assert_array_equal(bjd, times)
    np.testing.assert_array_equal(wave_tuple[0], wavelength)
    np.testing.assert_array_equal(actual_flux, flux)
    np.testing.assert_array_equal(errors, flux / 100)
    assert channel == trace


@pytest.mark.parametrize('traces', [[1, 2], [2], [3]])
def test_combined_wlc_tables_have_independent_times(tmp_path, fits, traces):
    """Read each selected numbered white-light table's own time samples."""
    # Use real tables so FITS extension selection is exercised end to end.
    table_module = importlib.import_module('astropy.table')
    science = load_functions('sorbet/general/science.py', ['load_wlc'],
                             fits=fits, Table=table_module.Table)
    filename = tmp_path / 'combined.fits'
    hdus = [fits.PrimaryHDU()]
    # Unequal lengths ensure tables cannot accidentally share timestamps.
    for trace in traces:
        table = table_module.Table()
        table['Time'] = np.arange(trace + 2) + 100 * trace
        table['RelFlux'] = np.ones(trace + 2)
        table['RelFlux_Err'] = np.ones(trace + 2) / 100
        hdus.append(fits.BinTableHDU(table, name=f'WLC_TABLE_{trace}'))
    fits.HDUList(hdus).writeto(filename)
    # Select each table independently from the same combined file.
    for trace in traces:
        params = ParamDict()
        params['RUN.SORBET.WLCA'] = True
        params['SORBET.WLCA.INPUT_FILE'] = str(filename)
        params['SORBET.WLCA.TRACE'] = trace
        table = science.load_wlc(params)
        # Verify values as well as length to detect a wrong detector table.
        np.testing.assert_array_equal(table['Time'],
                                      np.arange(trace + 2) + 100 * trace)


class TraceParams(ParamDict):
    """Provide flat-key parameter views for isolated orchestration tests."""

    def get(self, key, default=None):
        """
        Return an exact value or a relative-key view of a dotted prefix.

        :param key: Exact parameter name or prefix without a trailing dot.
        :param default: Value returned if neither a value nor a view exists.
        :return: Stored value, independent TraceParams view, or default.
        """
        # Exact values, including None, take precedence over prefix views.
        if key in self:
            return self[key]
        # Copy relative keys to mimic the views consumed by the wrappers.
        if any(name.startswith(key + '.') for name in self):
            relative_values = dict()
            for name, value in self.items():
                if name.startswith(key + '.'):
                    relative_values[name[len(key) + 1:]] = value
            return TraceParams(relative_values)
        return default

    def set_source(self, key, source):
        """Accept key/source provenance without recording it in this stub."""
        pass


def orchestration_functions(**namespace):
    """
    Load trace orchestration with caller-provided scientific runner stubs.

    :param namespace: Dependencies injected into the compiled functions.
    :return: Namespace containing input transfer and trace runner helpers.
    """
    # Only an annotation needs the instrument class during compilation.
    namespace.setdefault('sdefault', SimpleNamespace(Instrument=object))
    names = ['sossisse_input', 'run_sorbet_wlcta', '_trace_fit_params',
             '_validate_traces',
             'run_sorbet_slcta', '_deal_with_slcta_input_file']
    return load_functions('sorbet/general/general.py', names, **namespace)


@pytest.mark.parametrize('traces', [[1, 2], [2], None])
@pytest.mark.parametrize('mode', ['JWST.NIRSPEC.G395H', 'JWST.NIRISS.SOSS',
                                 'GENERIC.MODE'])
def test_sossisse_input_uses_parent_prefix_and_selected_traces(tmp_path,
                                                            traces, mode):
    """Forward the completed backend's prefix and selection in every mode."""
    # Create minimal source products to verify copying rather than just paths.
    source = tmp_path / 'source'
    source.mkdir()
    for product in ('wlc', 'spectra'):
        (source / f'parent_{product}.fits').write_bytes(product.encode())
    # Stale wrapper values must not override the completed backend instance.
    params = TraceParams()
    params['GLOBAL.INSTRUMENTMODE'] = mode
    params['RUN.SORBET.WLCA'] = True
    params['RUN.SORBET.SLCA'] = True
    params['SOSSISSE.GENERAL.PREFIX'] = 'wrong'
    params['SOSSISSE.GENERAL.TRACES'] = [99]
    params['SORBET.WLCA.INPUT_PATH'] = str(tmp_path / 'wlca')
    params['SORBET.SLCA.INPUT_PATH'] = str(tmp_path / 'slca')
    # The instance owns the actual output location and trace selection.
    instance_params = TraceParams()
    instance_params['PATHS.OUT_PATH'] = str(source)
    instance_params['GENERAL.PREFIX'] = 'parent'
    instance_params['GENERAL.TRACES'] = traces
    templates = dict()
    templates['OUT_WLC_FILE'] = str(source / '{prefix}_wlc.fits')
    templates['OUT_SPEC_LC_FILE'] = str(source / '{prefix}_spectra.fits')
    instance = SimpleNamespace(params=instance_params,
                               get_variable=lambda name, func: templates[name])

    def prepare(params, method, **options):
        """Create only the requested input directory for the copy workflow."""
        Path(params[f'SORBET.{method}.INPUT_PATH']).mkdir(exist_ok=True)

    # Keep directory setup lightweight while executing the real copy helper.
    general = orchestration_functions(
        sdefault=SimpleNamespace(Instrument=object), shutil=shutil,
        prepare_directories=prepare)
    general.sossisse_input(params, instance)

    # A combined spectral filename must appear once for every selected trace.
    assert params['SORBET.WLCA.INPUT_FILE'] == 'parent_wlc.fits'
    assert params['SORBET.WLCA.TRACES'] == traces
    assert params['SORBET.SLCA.TRACES'] == traces
    trace_count = len(traces) if traces is not None else 1
    expected_files = ['parent_spectra.fits'] * trace_count
    assert params['SORBET.SLCA.INPUT_FILE'] == expected_files
    # Both enabled analyses receive the original product bytes.
    assert (tmp_path / 'wlca' / 'parent_wlc.fits').read_bytes() == b'wlc'
    spectral_file = tmp_path / 'slca' / 'parent_spectra.fits'
    assert spectral_file.read_bytes() == b'spectra'


@pytest.mark.parametrize('traces', [[1, 2], [2]])
@pytest.mark.parametrize('mode', ['JWST.NIRSPEC.G395H', 'JWST.NIRISS.SOSS',
                                 'GENERIC.MODE'])
def test_selected_trace_fitted_states_and_paths_are_isolated(tmp_path, traces,
                                                           mode):
    """Isolate mutable priors, fitted state, and output paths per trace."""
    # A nested mutable prior detects shallow copies between trace fits.
    params = TraceParams()
    params['GLOBAL.INSTRUMENTMODE'] = mode
    params['SORBET.WLCA.TRACES'] = traces
    params['SORBET.WLCA.OUTPUT_PATH'] = str(tmp_path / 'outputs')
    params['SORBET.WLCA.PLOT_PATH'] = str(tmp_path / 'plots')
    params['SORBET.WLCA.JULIET_PRIOR_VALS'] = dict(shared=[1, 2])
    params['SORBET.SLCA.INPUT_FILE'] = ['combined.fits'] * len(traces)
    params['SORBET.SLCA.TRACES'] = traces
    # Capture the actual parameter objects passed to each scientific runner.
    fitted = []
    spectral = []

    def fit(fit_params):
        """Mutate one trace's nested prior and stamp its fitted state."""
        trace = fit_params['SORBET.WLCA.TRACE']
        assert fit_params['SORBET.WLCA.JULIET_PRIOR_VALS']['shared'] == [1, 2]
        fit_params['SORBET.WLCA.JULIET_PRIOR_VALS']['shared'][0] = trace * 10
        fit_params['FITTED_STATE'] = trace
        fitted.append(fit_params)
        return fit_params

    # Directory effects are irrelevant to state and path isolation here.
    general = orchestration_functions(
        _run_sorbet_wlcta=fit, _run_sorbet_slcta=spectral.append,
        prepare_directories=lambda *inputs, **options: None)
    general.run_sorbet_wlcta(params)
    general.run_sorbet_slcta(params)

    # The parent prior remains intact and every selected fit is cached.
    assert params['SORBET.WLCA.JULIET_PRIOR_VALS']['shared'] == [1, 2]
    assert list(params['SORBET.WLCA.TRACE_FIT_PARAMS']) == traces
    # SLCA gets a further copy of the matching fit, not a shared fit object.
    for trace, white_params, spectral_params in zip(traces, fitted, spectral):
        assert spectral_params['FITTED_STATE'] == trace
        assert spectral_params is not white_params
        assert spectral_params['SORBET.SLCA.TRACES'] == [trace]
        assert spectral_params['SORBET.WLCA.OUTPUT_PATH'] == str(
            tmp_path / 'outputs' / f'trace{trace}')
        assert spectral_params['SORBET.WLCA.PLOT_PATH'] == str(
            tmp_path / 'plots' / f'trace{trace}')


def test_unselected_wlca_uses_one_unlabelled_runner():
    """Keep the parent's parameter identity for a single unnumbered fit."""
    calls = []
    general = orchestration_functions(_run_sorbet_wlcta=calls.append)
    # Unnumbered behavior must remain instrument-neutral.
    for mode in ('JWST.NIRISS.SOSS', 'JWST.NIRSPEC.PRISM', 'GENERIC.MODE'):
        params = TraceParams()
        params['GLOBAL.INSTRUMENTMODE'] = mode
        general.run_sorbet_wlcta(params)
        assert calls[-1] is params


def test_combined_spectra_keep_independent_detector_times(tmp_path, fits):
    """Keep detector timestamps separate when spectra share one FITS file."""
    science = load_functions('sorbet/general/science.py', ['load_slc'],
                             fits=fits)
    filename = tmp_path / 'combined_spectra.fits'
    hdus = [fits.PrimaryHDU()]
    # Distinct detector lengths and times catch positional trace substitution.
    for trace in (1, 2):
        times = np.arange(trace + 2, dtype=float) + 100 * trace
        wavelength = np.tile([0.5, 0.7, 0.9, 1.1], (len(times), 1))
        products = dict(WAVELENGTH=wavelength,
                        RELFLUX=np.ones_like(wavelength),
                        RELFLUX_ERROR=np.ones_like(wavelength) / 100,
                        BJD=times)
        # All extensions for a detector use the same numbered suffix.
        hdus.extend(fits.ImageHDU(data=data, name=f'{name}_{trace}')
                    for name, data in products.items())
    fits.HDUList(hdus).writeto(filename)
    # Native resolution permits exact shape and timestamp comparisons.
    spectral_params = ParamDict()
    spectral_params['RESOLUTION_BIN'] = 1
    params = ParamDict()
    params['RUN.SORBET.SLCA'] = True
    params['GLOBAL.INSTRUMENTMODE'] = 'JWST.NIRSPEC.G395H'
    params['SORBET.SLCA'] = spectral_params
    # Read each selection independently from the combined product.
    for trace in (1, 2):
        spectral_outputs = science.load_slc(params, str(filename), trace)
        times, wave_tuple, flux, errors, channel = spectral_outputs
        expected_times = np.arange(trace + 2) + 100 * trace
        np.testing.assert_array_equal(times, expected_times)
        # Flux, uncertainty, and wavelength must retain the detector's shape.
        expected_shape = (trace + 2, 4)
        assert (flux.shape == errors.shape
            == wave_tuple[0].shape == expected_shape)
        assert channel == trace
    # A missing detector must fail rather than fall back to another detector.
    with pytest.raises(ValueError, match='Could not find WAVELENGTH_3'):
        science.load_slc(params, str(filename), 3)


def test_missing_numbered_wlc_trace_does_not_read_another_trace(tmp_path,
                                                             fits):
    """Reject an absent detector even if another numbered WLC is present."""
    table_module = importlib.import_module('astropy.table')
    # Only NRS1 is written; selecting NRS2 must not read its data.
    table_columns = dict(Time=[1.0], RelFlux=[1.0], RelFlux_Err=[0.01])
    table = table_module.Table(table_columns)
    filename = tmp_path / 'nrs1_only.fits'
    hdus = [fits.PrimaryHDU(), fits.BinTableHDU(table, name='WLC_TABLE_1')]
    fits.HDUList(hdus).writeto(filename)
    science = load_functions('sorbet/general/science.py', ['load_wlc'],
                             fits=fits, Table=table_module.Table)
    # The runtime-only selector names the absent detector explicitly.
    params = ParamDict()
    params['RUN.SORBET.WLCA'] = True
    params['SORBET.WLCA.INPUT_FILE'] = str(filename)
    params['SORBET.WLCA.TRACE'] = 2
    with pytest.raises(ValueError, match='Could not find WLC_TABLE_2'):
        science.load_wlc(params)


def test_rejects_missing_identifier_in_trace_list():
    """Reject partial numbering before invoking a spectral fit."""
    general = orchestration_functions(
        prepare_directories=lambda *inputs, **options: None)
    # Mixing numbered and unnumbered traces is an invalid user selection.
    params = TraceParams()
    params['GLOBAL.INSTRUMENTMODE'] = 'JWST.NIRSPEC.G395H'
    params['SORBET.SLCA.INPUT_FILE'] = ['combined.fits', 'combined.fits']
    params['SORBET.SLCA.TRACES'] = [1, None]
    params['SORBET.WLCA.OUTPUT_PATH'] = '/tmp/wlca/outputs'
    params['SORBET.WLCA.PLOT_PATH'] = '/tmp/wlca/plots'
    # The scientific runner remains a no-op if validation were to reach it.
    runner_globals = general.run_sorbet_slcta.__globals__
    runner_globals['_run_sorbet_slcta'] = lambda params: params
    with pytest.raises(ValueError, match='unique positive integer'):
        general.run_sorbet_slcta(params)


@pytest.mark.parametrize('traces', [[], [0], [-1], [1, 1], [1, None],
                                  [None], [True], [1.5], ['1'], 1, (1, 2)])
@pytest.mark.parametrize('method', ['WLCA', 'SLCA'])
def test_standalone_trace_selection_is_validated(traces, method):
    """Validate both entry points before any scientific runner is called."""
    # Capture calls to ensure malformed selections fail before execution.
    calls = []
    general = orchestration_functions(_run_sorbet_wlcta=calls.append,
                                      _run_sorbet_slcta=calls.append)
    params = TraceParams()
    params[f'SORBET.{method}.TRACES'] = traces
    params['SORBET.SLCA.INPUT_FILE'] = ['spectra.fits']
    # Both standalone analyses must enforce the same identifier contract.
    runner = (general.run_sorbet_wlcta if method == 'WLCA'
              else general.run_sorbet_slcta)

    with pytest.raises(ValueError, match='unique positive integer'):
        runner(params)

    assert calls == []


@pytest.mark.parametrize('mode', ['JWST.NIRISS.SOSS', 'JWST.NIRSPEC.PRISM',
                                 'GENERIC.MODE'])
@pytest.mark.parametrize('input_files', ['spectra.fits', ['spectra.fits']])
def test_unselected_slca_uses_one_unlabelled_runner(mode, input_files):
    """Accept a single unnumbered filename in string or list form."""
    calls = []
    general = orchestration_functions(_run_sorbet_slcta=calls.append)
    # No explicit selection is necessary for one unnumbered product.
    params = TraceParams()
    params['GLOBAL.INSTRUMENTMODE'] = mode
    params['SORBET.SLCA.INPUT_FILE'] = input_files

    general.run_sorbet_slcta(params)

    # The runner keeps the parent object; normalization is local to the helper.
    assert calls == [params]
    normalized_inputs = general._deal_with_slcta_input_file(params)
    assert normalized_inputs == (['spectra.fits'], [None])


@pytest.mark.parametrize('traces, input_files, message', [
    (None, [], 'at least one file'),
    (None, ['first.fits', 'second.fits'], 'must be provided'),
    ([1, 2], ['combined.fits'], 'must match'),
])
def test_standalone_slca_rejects_ambiguous_file_selection(traces, input_files,
                                                        message):
    """Reject empty inputs and mismatches between filenames and traces."""
    general = orchestration_functions()
    # Validation must happen without opening files or launching a fit.
    params = TraceParams()
    params['SORBET.SLCA.INPUT_FILE'] = input_files
    params['SORBET.SLCA.TRACES'] = traces

    with pytest.raises(ValueError, match=message):
        general._deal_with_slcta_input_file(params)


@pytest.mark.parametrize('trace', [None, 1, 2])
def test_soss_channel_is_explicit_and_only_trace_two_is_cut(tmp_path, fits,
                                                          trace):
    """Restrict only explicitly selected SOSS order 2 to its valid band."""
    science = load_functions('sorbet/general/science.py', ['load_slc'],
                             fits=fits)
    # Sample both sides of the order-2 cut, expressed in microns.
    wavelength = np.tile([0.5, 0.65, 0.7, 0.8, 0.9], (3, 1))
    flux = np.ones_like(wavelength)
    suffix = '' if trace is None else f'_{trace}'
    products = dict(WAVELENGTH=wavelength, RELFLUX=flux,
                    RELFLUX_ERROR=flux / 100, BJD=np.arange(3, dtype=float))
    filename = tmp_path / 'soss_spectra.fits'
    hdus = [fits.PrimaryHDU()]
    # Preserve the selected extension suffix across all scientific arrays.
    hdus.extend(fits.ImageHDU(data=data, name=name + suffix)
                for name, data in products.items())
    fits.HDUList(hdus).writeto(filename)
    # Disable rebinning so only the established wavelength cut is tested.
    params = TraceParams()
    params['RUN.SORBET.SLCA'] = True
    params['GLOBAL.INSTRUMENTMODE'] = 'JWST.NIRISS.SOSS'
    params['SORBET.SLCA.RESOLUTION_BIN'] = 1

    spectral_outputs = science.load_slc(params, str(filename), trace=trace)
    times, wave_tuple, actual_flux, errors, channel = spectral_outputs

    # Wavelength coverage alone must not relabel an unnumbered or order-1 file.
    assert channel == trace
    expected_wavelength = wavelength[:, 1:4] if trace == 2 else wavelength
    np.testing.assert_array_equal(wave_tuple[0], expected_wavelength)
    assert actual_flux.shape == errors.shape == expected_wavelength.shape
    np.testing.assert_array_equal(times, np.arange(3))


def test_legacy_shared_wlc_is_fitted_separately_for_selected_traces(tmp_path,
                                                                 fits):
    """Fit shared SOSS amplitudes separately without inventing order WLCs."""
    table_module = importlib.import_module('astropy.table')
    # A legacy producer writes one shared table, not independent order data.
    table_columns = dict(Time=[100.0, 101.0], RelFlux=[1.0, 1.01],
                         RelFlux_Err=[0.01, 0.01])
    table = table_module.Table(table_columns)
    filename = tmp_path / 'legacy_shared_wlc.fits'
    fits.HDUList([fits.PrimaryHDU(),
                  fits.BinTableHDU(table, name='WLC_TABLE')]).writeto(filename)
    science = load_functions('sorbet/general/science.py', ['load_wlc'],
                             fits=fits, Table=table_module.Table)
    fitted_tables = []

    def fit(fit_params):
        """Capture the table actually loaded for each selected trace fit."""
        fitted_tables.append(science.load_wlc(fit_params))
        return fit_params

    # Keep real table loading but omit costly transit fitting and path setup.
    general = orchestration_functions(
        _run_sorbet_wlcta=fit,
        prepare_directories=lambda *inputs, **options: None)
    params = TraceParams()
    params['GLOBAL.INSTRUMENTMODE'] = 'JWST.NIRISS.SOSS'
    params['RUN.SORBET.WLCA'] = True
    params['SORBET.WLCA.INPUT_FILE'] = str(filename)
    params['SORBET.WLCA.TRACES'] = [1, 2]
    params['SORBET.WLCA.OUTPUT_PATH'] = str(tmp_path / 'outputs')
    params['SORBET.WLCA.PLOT_PATH'] = str(tmp_path / 'plots')

    general.run_sorbet_wlcta(params)

    # Both fits see identical shared samples but retain independent fit state.
    assert len(fitted_tables) == 2
    for fitted_table in fitted_tables:
        np.testing.assert_array_equal(fitted_table['Time'], table['Time'])
        shared_flux = table['RelFlux']
        np.testing.assert_array_equal(fitted_table['RelFlux'], shared_flux)
    # Separate output locations prevent order fits from overwriting each other.
    trace_fit_params = params['SORBET.WLCA.TRACE_FIT_PARAMS']
    assert isinstance(trace_fit_params[1], ParamDict)
    assert trace_fit_params[1] is not trace_fit_params[2]
    assert trace_fit_params[1]['SORBET.WLCA.OUTPUT_PATH'].endswith('/trace1')
    assert trace_fit_params[2]['SORBET.WLCA.OUTPUT_PATH'].endswith('/trace2')


@pytest.mark.parametrize('method', ['WLCA', 'SLCA'])
def test_numbered_products_require_explicit_trace_selection(tmp_path, fits,
                                                          method):
    """Reject implicit selection even when only one numbered trace exists."""
    table_module = importlib.import_module('astropy.table')
    filename = tmp_path / 'numbered.fits'
    # Cover both white-light tables and spectral wavelength extensions.
    if method == 'WLCA':
        table_columns = dict(Time=[100.0], RelFlux=[1.0], RelFlux_Err=[0.01])
        table = table_module.Table(table_columns)
        extensions = [fits.BinTableHDU(table, name='WLC_TABLE_3')]
    else:
        extensions = [fits.ImageHDU(data=np.ones((2, 3)), name='WAVELENGTH_3')]
    fits.HDUList([fits.PrimaryHDU(), *extensions]).writeto(filename)
    # Compile both readers with the same FITS and table dependencies.
    loader_args = ['sorbet/general/science.py', ['load_wlc', 'load_slc']]
    loader_kwargs = dict(fits=fits, Table=table_module.Table)
    science = load_functions(*loader_args, **loader_kwargs)
    params = TraceParams()
    params[f'RUN.SORBET.{method}'] = True
    params['GLOBAL.INSTRUMENTMODE'] = 'GENERIC.MODE'
    params['SORBET.WLCA.INPUT_FILE'] = str(filename)
    params['SORBET.SLCA.RESOLUTION_BIN'] = 1

    # The diagnostic must direct users to the appropriate selection setting.
    with pytest.raises(ValueError, match=f'SORBET.{method}.TRACES'):
        if method == 'WLCA':
            science.load_wlc(params)
        else:
            science.load_slc(params, str(filename))


@pytest.mark.parametrize('trace', [1, 2])
def test_soss_limb_darkening_profiles_remain_trace_specific(trace):
    """Choose the selected SOSS order's limb-darkening throughput profile."""
    profiles = []

    def compute(wave_range, profile):
        """Record the selected profile and validate the Angstrom bandpass."""
        profiles.append(profile)
        np.testing.assert_array_equal(wave_range, [6500, 8000])
        return 0.1, 0.2

    # Replace the atmosphere backend while preserving the real profile choice.
    loader_args = ['sorbet/general/science.py', ['get_model_ld_coeffs']]
    loader_kwargs = dict(
        StellarLimbDarkening=lambda *inputs: SimpleNamespace(
            compute_quadratic_ld_coeffs=compute),
        core=SimpleNamespace(
            sorbet_inst_mode=lambda params: 'JWST.NIRISS.SOSS'))
    science = load_functions(*loader_args, **loader_kwargs)
    # Stellar values are arbitrary; the selected channel controls throughput.
    params = TraceParams()
    params['SORBET.SLCA.CHANNEL'] = trace
    params['SORBET.SLCA.EXOTIC-LD.MODEL_PATH'] = '/unused'
    params['SORBET.SLCA.EXOTIC-LD.LD_LAW'] = 'quadratic'
    params['SORBET.SLCA.EXOTIC-LD.MODEL_GRID'] = 'test'
    params['SORBET.SLCA.EXOTIC-LD.STELLAR_MET'] = 0.0
    params['SORBET.SLCA.EXOTIC-LD.STELLAR_TEFF'] = 5000
    params['SORBET.SLCA.EXOTIC-LD.STELLAR_LOGG'] = 4.5

    # SORBET passes micron bounds and converts them for the atmosphere model.
    bin_params = dict(WAVE_BIN_LOW=0.65, WAVE_BIN_HIGH=0.8)
    assert science.get_model_ld_coeffs(params, bin_params) == (0.1, 0.2)
    assert profiles == [f'JWST_NIRISS_SOSSo{trace}']
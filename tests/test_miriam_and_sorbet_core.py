import ast
from pathlib import Path

import pytest

from aperocore.constants.param_functions import ParamDict

from pogos.core import general as pogos_general
from pogos.miriam.core import general as miriam_general
from pogos.sorbet.core import core as sorbet_core


def _load_directory_function(module_path):
    """Load directory orchestration without optional science dependencies."""
    source_path = Path(__file__).parents[1] / 'pogos' / module_path
    source_tree = ast.parse(source_path.read_text())
    function = next(node for node in source_tree.body
                    if isinstance(node, ast.FunctionDef)
                    and node.name == 'prepare_directories')
    function_tree = ast.Module(body=[function], type_ignores=[])
    namespace = {'ParamDict': ParamDict, 'pogos_general': pogos_general}
    exec(compile(function_tree, str(source_path), 'exec'), namespace)
    return namespace['prepare_directories']


@pytest.mark.parametrize('module, module_path, method', [
    ('tsovore', 'tsovore/core/general.py', None),
    ('miriam', 'miriam/general/general.py', None),
    ('sorbet', 'sorbet/general/general.py', 'WLCA'),
    ('sorbet', 'sorbet/general/general.py', 'SLCA'),
])
def test_module_directories_use_global_project_and_absolute_override(
        tmp_path, module, module_path, method):
    prepare_directories = _load_directory_function(module_path)
    group = f'{module.upper()}.{method or "PATHS"}'
    params = ParamDict({
        'GLOBAL.DATA_PATH': str(tmp_path),
        'GLOBAL.PROJECT_NAME': 'shared-project',
        f'{group}.INPUT_PATH': 'custom-input',
        f'{group}.PLOT_PATH': None,
        f'{group}.OUTPUT_PATH': str(tmp_path / 'external-output'),
    })
    if method is None:
        params[f'{group}.TEMP_PATH'] = None
        prepare_directories(params)
    else:
        prepare_directories(params, method=method, verbose=False)

    topdir = tmp_path / 'projects' / 'shared-project' / module
    assert params[f'{group}.INPUT_PATH'] == str(topdir / 'custom-input')
    assert params[f'{group}.PLOT_PATH'] == str(topdir / 'plot')
    assert params[f'{group}.OUTPUT_PATH'] == str(tmp_path / 'external-output')
    assert (topdir / 'custom-input').is_dir()
    assert (topdir / 'plot').is_dir()
    assert (tmp_path / 'external-output').is_dir()
    if method is None:
        assert params[f'{group}.TEMP_PATH'] == str(topdir / 'temp')
        assert (topdir / 'temp').is_dir()
    assert params['GLOBAL.PROJECT_NAME'] == 'shared-project'


def test_miriam_unique_id_format(monkeypatch):
    monkeypatch.setattr(
        miriam_general.pogos_general,
        "unix_char_code",
        lambda: (42, "ignored", "ABCD"),
    )

    uid = miriam_general.miriam_unique_id()

    assert uid == "MID-00000000000000000042-ABCD"


def test_sorbet_unique_id_format(monkeypatch):
    monkeypatch.setattr(
        sorbet_core.pogos_general,
        "unix_char_code",
        lambda: (31415, "ignored", "WXYZ"),
    )

    uid = sorbet_core.sorbet_unique_id()

    assert uid == "SBID-00000000000000031415-WXYZ"


def test_sorbet_inst_mode_normalizes_underscores():
    params = ParamDict({"GLOBAL.INSTRUMENTMODE": "jwst_niriss_soss"})

    assert sorbet_core.sorbet_inst_mode(params) == "JWST.NIRISS.SOSS"


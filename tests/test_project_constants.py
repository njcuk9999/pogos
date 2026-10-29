import ast
import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

PACKAGE = Path(__file__).resolve().parents[1] / 'pogos'
RESOURCES = PACKAGE / 'resources'
MODULE_SCHEMAS = [
    'constants/tsovore.py',
    'constants/miriam.py',
    'constants/sorbet.py',
    'eureka_wrap/constants/eureka_constants.py',
    'jwst_wrap/constants/jwst_constants.py',
    'nameless_wrap/constants/nameless_constants.py',
]
DEMO_PROJECTS = {
    'soss_demo.py': 'DEMO_T1b.20220718.JWST.NIRISS.SOSS',
    'miri_demo.py': 'DEMO_LHS1140.20240707.JWST.MIRI.IM',
    'bots_g395_demo.py': 'DEMO_WASP39b.20220710.JWST.NIRSPEC.BOTS.G395',
    'bots_prism_demo.py': 'DEMO_WASP39b.20220710.JWST.NIRSPEC.BOTS.PRISM',
}
ARCHIVED_DEMOS = sorted((RESOURCES / 'old_format_demos').glob('*.py'))
YAML_DEMOS = sorted((RESOURCES / 'yamls').glob('*.yaml'))


def test_global_project_schema():
    code = """
from pogos.constants.constants import CDict
project = CDict.get('GLOBAL.PROJECT_NAME')
assert project.value is None
assert project.dtype is str
assert project.not_none and project.user and project.active
assert project.cmd_arg == 'project_name'
"""
    subprocess.run([sys.executable, '-c', code], cwd='/tmp', check=True)


@pytest.mark.parametrize('relative_path', MODULE_SCHEMAS)
def test_modules_have_no_project_or_subdirectory_constants(relative_path):
    source = (PACKAGE / relative_path).read_text()
    tree = ast.parse(source)
    assert 'SUBDIRECTORY' not in source
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if not isinstance(node.func, ast.Attribute) or node.func.attr != 'add':
            continue
        if node.args and isinstance(node.args[0], ast.Constant):
            assert node.args[0].value != 'PROJECT_NAME'


@pytest.mark.parametrize('filename, expected', DEMO_PROJECTS.items())
def test_active_demo_startup_sets_one_global_project(filename, expected):
    source = (RESOURCES / 'demos' / filename).read_text()
    tree = ast.parse(source)
    startup = next(node for node in ast.walk(tree)
                   if isinstance(node, ast.FunctionDef)
                   and node.name == 'startup')
    code = f"""
from types import SimpleNamespace
from pogos.constants.constants import CDict
__NAME__ = 'test_project_constants'
definitions = SimpleNamespace(RED_STEPS=[])
demo = SimpleNamespace(cdict=CDict.copy(source=__NAME__),
                       instrument='JWST.NIRISS.SOSS')
{ast.unparse(startup)}
startup(demo)
assert demo.cdict['GLOBAL.PROJECT_NAME'] == {expected!r}
"""
    subprocess.run([sys.executable, '-c', code], cwd='/tmp', check=True)
    assert source.count("set('PROJECT_NAME'") == 1
    assert 'SUBDIRECTORY' not in source


@pytest.mark.parametrize('path', ARCHIVED_DEMOS, ids=lambda path: path.name)
def test_archived_demo_sets_one_global_project(path):
    source = path.read_text()
    tree = ast.parse(source)
    project_calls = [node for node in ast.walk(tree)
                     if isinstance(node, ast.Call)
                     and isinstance(node.func, ast.Attribute)
                     and node.func.attr == 'set'
                     and node.args
                     and isinstance(node.args[0], ast.Constant)
                     and node.args[0].value == 'PROJECT_NAME']
    assert len(project_calls) == 1
    call = project_calls[0]
    project = ast.literal_eval(next(keyword.value for keyword in call.keywords
                                  if keyword.arg == 'value'))
    assert project
    assert not any(module in project for module in
                   ['TSOVORE', 'MIRIAM', 'SORBET', 'SOSSISSE'])
    assert 'SUBDIRECTORY' not in source
    assert "cgroup = 'GLOBAL'\nCdict.set('PROJECT_NAME'" in source


@pytest.mark.parametrize('path', YAML_DEMOS, ids=lambda path: path.name)
def test_yaml_demo_uses_global_project_and_root(path):
    source = path.read_text()
    config = yaml.safe_load(source)
    assert isinstance(config['GLOBAL']['PROJECT_NAME'], str)
    assert config['GLOBAL']['PROJECT_NAME']
    assert 'SUBDIRECTORY' not in source
    assert source.count('PROJECT_NAME:') == 1
    if 'SOSSISSE' in config:
        assert (config['SOSSISSE']['INPUTS']['SOSSIOPATH']
                == config['GLOBAL']['DATA_PATH'])


def test_notebook_summaries_use_sossisse_project_and_run_path():
    path = RESOURCES / 'notebooks' / 'pogos_sossisse_demo.ipynb'
    notebook = json.loads(path.read_text())
    summary_cells = [''.join(cell['source']) for cell in notebook['cells']
                     if cell['cell_type'] == 'code'
                     and 'summary_html' in ''.join(cell['source'])]
    assert len(summary_cells) == 2
    for source in summary_cells:
        ast.parse(source)
        assert "'INPUTS.PROJECT_NAME', 'PATHS.RUN_PATH'" in source
        assert 'SUBDIRECTORY' not in source


def test_notebook_initialization_forwards_global_project(tmp_path):
    code = """
from types import SimpleNamespace
from unittest.mock import patch
from aperocore.constants.param_functions import ParamDict
from pogos.resources.nb_funcs import nb_sossisse

params = ParamDict()
params['GLOBAL.PROJECT_NAME'] = 'demo-project'
params['GLOBAL.DATA_PATH'] = '/observations'
params['GLOBAL.YAML_FILE'] = '/observations/yamls/demo.yaml'
params['SOSSISSE.INPUTS.PROJECT_NAME'] = None
params['SOSSISSE.INPUTS.SOSSIOPATH'] = '/obsolete-root'
instrument = SimpleNamespace(params=ParamDict())
with patch.object(nb_sossisse.startup, 'initial_setup',
                  return_value={'SOSSISSE': 'merged-config'}) as setup:
    with patch.object(nb_sossisse.load_functions, 'get_all_params',
                      return_value=params) as load:
        with patch.object(nb_sossisse.sossisse, 'get_parameters',
                          return_value=instrument) as initialize:
            assert nb_sossisse.sossisse_init('demo.yaml') is instrument
setup.assert_called_once_with()
assert load.call_args.kwargs['external_const'] == {'SOSSISSE': 'merged-config'}
forwarded = initialize.call_args.kwargs['__YAML_DICT__']
assert forwarded['INPUTS.PROJECT_NAME'] == 'demo-project'
assert forwarded['INPUTS.SOSSIOPATH'] == '/observations'
assert forwarded['INPUTS.PARAM_FILE'] == '/observations/yamls/demo.yaml'
assert instrument.params['PLOTS.SHOW'] is True
"""
    result = subprocess.run([sys.executable, '-c', code], cwd=tmp_path,
                            capture_output=True, text=True, timeout=90)
    assert result.returncode == 0, result.stdout + result.stderr
import subprocess
import sys
import textwrap

import pytest


def run_startup_check(tmp_path, code):
    preamble = (
        'from unittest.mock import patch\n'
        'from pathlib import Path\n'
        'from aperocore.constants.param_functions import ParamDict\n'
        'from pogos.core import base, startup\n'
    )
    result = subprocess.run(
        [sys.executable, '-c', preamble + textwrap.dedent(code)],
        cwd=tmp_path, capture_output=True, text=True, timeout=90)
    assert result.returncode == 0, result.stdout + result.stderr


def test_missing_project_prompts_once(tmp_path):
    run_startup_check(tmp_path, """
        params = ParamDict()
        params['GLOBAL.PROJECT_NAME'] = None
        with patch.object(startup.drs_text, 'user_input',
                          return_value='target-1+visit.2_a') as prompt:
            assert startup.ask_project_name(params) is params
            startup.ask_project_name(params)
        assert params['GLOBAL.PROJECT_NAME'] == 'target-1+visit.2_a'
        assert prompt.call_count == 1
    """)


def test_preset_project_does_not_prompt(tmp_path):
    run_startup_check(tmp_path, """
        params = ParamDict()
        params['GLOBAL.PROJECT_NAME'] = 'target'
        with patch.object(startup.drs_text, 'user_input') as prompt:
            assert startup.ask_project_name(params) is params
        prompt.assert_not_called()
    """)


@pytest.mark.parametrize('name', ['', '.', '..', 'a b', 'a\tb', 'a\nb',
                                  '/tmp/target', 'a/b', 'a\\b', 'a:b',
                                  'a*', False, 123])
def test_invalid_project_name(tmp_path, name):
    run_startup_check(tmp_path, f"""
        params = ParamDict()
        params['GLOBAL.PROJECT_NAME'] = {name!r}
        try:
            startup.ask_project_name(params)
        except base.PogosException as error:
            assert 'GLOBAL.PROJECT_NAME' in str(error)
        else:
            raise AssertionError('Invalid project was accepted')
    """)


def test_missing_project_without_answer(tmp_path):
    run_startup_check(tmp_path, """
        params = ParamDict()
        with patch.object(startup.drs_text, 'user_input', return_value=None):
            try:
                startup.ask_project_name(params)
            except base.PogosException as error:
                assert 'GLOBAL.PROJECT_NAME' in str(error)
            else:
                raise AssertionError('Missing project was accepted')
    """)


def test_setup_prompts_for_project_before_directory_creation(tmp_path):
    run_startup_check(tmp_path, """
        from aperocore.constants import load_functions
        from pogos.constants.constants import CDict

        configs = startup.initial_setup()
        config_list = load_functions.add_ext_config_list(
            [CDict], {'SOSSISSE': configs['SOSSISSE']})
        merged = startup.ConstDict.merge_configs(config_list)
        values, sources, instances = merged.unpack()
        params = load_functions.load_into_params(
            values, sources, instances, check=False)
        params['CONFIG_LIST'] = config_list
        params['LOG.HEADER'] = '=='
        params['GLOBAL.DATA_PATH'] = str(Path.cwd())
        params['GLOBAL.YAML_FILE'] = str(Path.cwd() / 'project.yaml')
        params['GLOBAL.INSTRUMENTMODE'] = 'JWST.NIRISS.SOSS'
        params['RUN.SOSSISSE'] = True
        params['SOSSISSE.INPUTS.OBJECTNAME'] = 'target'
        params['SOSSISSE.INPUTS.INSTRUMENTMODE'] = 'JWST.NIRISS.SOSS'
        assert params['GLOBAL.PROJECT_NAME'] is None
        assert params['SOSSISSE.INPUTS.PROJECT_NAME'] is None
        assert not params.instances['SOSSISSE.INPUTS.PROJECT_NAME'].not_none

        def answer_prompt(question, **options):
            assert 'SUBDIRECTORY' not in question.upper()
            assert 'SOSSISSE.INPUTS.PROJECT_NAME' not in question
            if 'GLOBAL.PROJECT_NAME' in question:
                assert params['GLOBAL.PROJECT_NAME'] is None
                assert not list(Path.cwd().iterdir())
                return 'target-1+visit.2_a'
            raise AssertionError('Unexpected prompt: ' + question)

        with patch.object(startup, 'WLOG'), patch.object(
                startup.drs_text, 'user_input', side_effect=answer_prompt) as prompt:
            config = startup.setup(params, start_from_demo=False)

        questions = [call.args[0] for call in prompt.call_args_list]
        project_questions = [question for question in questions
                             if 'GLOBAL.PROJECT_NAME' in question]
        assert len(project_questions) == 1, questions
        assert all('SUBDIRECTORY' not in question.upper() for question in questions)
        assert all('SOSSISSE.INPUTS.PROJECT_NAME' not in question
                   for question in questions)
        assert params['GLOBAL.PROJECT_NAME'] == 'target-1+visit.2_a'
        assert params['SOSSISSE.INPUTS.PROJECT_NAME'] is None
        root = Path.cwd() / 'projects' / 'target-1+visit.2_a'
        assert (root / 'sossisse').is_dir()
        assert params['SOSSISSE.INPUTS.SOSSIOPATH'] == str(Path.cwd())
        assert isinstance(config, startup.ConstDict)
        assert Path(params['GLOBAL.YAML_FILE']).is_file()
    """)


def test_setup_uses_demo_project_before_generic_directories(tmp_path):
    run_startup_check(tmp_path, """
        from contextlib import ExitStack
        from types import SimpleNamespace
        from pogos.core import definitions

        params = ParamDict()
        params['GLOBAL.DATA_PATH'] = str(Path.cwd())
        params['GLOBAL.PROJECT_NAME'] = None
        params['GLOBAL.YAML_FILE'] = str(Path.cwd() / 'project.yaml')
        params['GLOBAL.INSTRUMENTMODE'] = 'JWST.NIRISS.SOSS'
        params['SOSSISSE.INPUTS.SOSSIOPATH'] = None
        params['LOG.HEADER'] = '=='
        params['CONFIG_LIST'] = []
        params['RUN.TSOVORE'] = True
        params['RUN.SOSSISSE'] = True
        params['RUN.PRE_EUREKA'] = True
        config = SimpleNamespace(title='', save_yaml=lambda *inputs, **options: None)

        def demo_defaults(current, *inputs, **options):
            current['GLOBAL.PROJECT_NAME'] = 'demo-project'
            return current

        with ExitStack() as stack:
            stack.enter_context(patch.object(startup, 'WLOG'))
            stack.enter_context(patch.object(startup, '_load_demo_module'))
            stack.enter_context(patch.object(startup, 'core_setup',
                                             return_value=(params, {})))
            stack.enter_context(patch.object(startup.load_functions,
                'starting_point', side_effect=demo_defaults))
            stack.enter_context(patch.object(startup, 'core_yaml_setup',
                                             side_effect=lambda current: current))
            stack.enter_context(patch.object(startup.load_functions,
                'ask_for_missing_args', side_effect=lambda current, **options: current))
            stack.enter_context(patch.object(startup.ConstDict, 'merge_configs',
                                             return_value=config))
            stack.enter_context(patch.object(startup.drs_text, 'user_input',
                side_effect=AssertionError('Unexpected project prompt')))
            assert startup.setup(params) is config
        root = Path.cwd() / 'projects' / 'demo-project'
        assert (root / 'tsovore').is_dir()
        assert (root / 'sossisse').is_dir()
        assert not (root / 'pre_eureka').exists()
        assert not (Path.cwd() / 'tsovore').exists()
        assert params['SOSSISSE.INPUTS.SOSSIOPATH'] == str(Path.cwd())
        params['SOSSISSE.INPUTS.SOSSIOPATH'] = '/external/sossisse-root'
        with ExitStack() as stack:
            stack.enter_context(patch.object(startup, 'WLOG'))
            stack.enter_context(patch.object(startup, 'core_setup',
                                             return_value=(params, {})))
            stack.enter_context(patch.object(startup, 'core_yaml_setup',
                                             side_effect=lambda current: current))
            stack.enter_context(patch.object(startup.load_functions,
                'ask_for_missing_args', side_effect=lambda current, **options: current))
            stack.enter_context(patch.object(startup.ConstDict, 'merge_configs',
                                             return_value=config))
            startup.setup(params, start_from_demo=False)
        assert params['SOSSISSE.INPUTS.SOSSIOPATH'] == '/external/sossisse-root'
    """)


def test_initial_setup_hides_only_merged_sossisse_project(tmp_path):
    run_startup_check(tmp_path, """
        from aperocore.constants import load_functions
        from aperocore.constants.constant_functions import ConstantsDict
        from sossisse.core.constants import CDict

        original = CDict.get('INPUTS.PROJECT_NAME')
        original_flags = original.user, original.not_none
        configs = startup.initial_setup()
        copied = configs['SOSSISSE']
        hidden = copied.get('INPUTS.PROJECT_NAME')
        assert copied is not CDict
        assert hidden is not original
        assert not hidden.user
        assert not hidden.not_none
        assert (original.user, original.not_none) == original_flags
        assert original_flags == (True, True)
        nested = load_functions.add_ext_config_list([], {'SOSSISSE': copied})
        merged = ConstantsDict.merge_configs(nested)
        merged.title = 'POGOS merged SOSSISSE test'
        values, sources, instances = merged.unpack()
        params = load_functions.load_into_params(values, sources, instances, check=False)
        with patch.object(startup.drs_text, 'user_input') as prompt:
            load_functions.ask_for_missing_args(params,
                include_keys=['SOSSISSE.INPUTS.PROJECT_NAME'])
        prompt.assert_not_called()
        yaml_path = Path.cwd() / 'merged.yaml'
        merged.save_yaml(params, outpath=str(yaml_path), log=False)
        assert 'PROJECT_NAME:' not in yaml_path.read_text()
        assert 'SOSSISSE.INPUTS.PROJECT_NAME' in params
    """)


def test_copy_resets_only_paths_inside_prior_project(tmp_path):
    run_startup_check(tmp_path, """
        from aperocore.constants.constant_functions import ConstantsDict
        from aperocore.constants import load_functions

        root = Path.cwd()
        old_root = root / 'projects' / 'old'
        cdict = ConstantsDict('test')
        defaults = {
            'TSOVORE.PATHS.INPUT_PATH': 'inputs',
            'TSOVORE.PATHS.TEMP_PATH': 'temporary',
            'TSOVORE.PATHS.OUTPUT_PATH': 'outputs',
            'TSOVORE.PATHS.PLOT_PATH': 'plots',
            'EUREKA.GENERAL.TOPDIR': None,
            'STD_JWST.GENERAL.OUTPUT_DIR': None,
            'SOSSISSE.INPUTS.SOSSIOPATH': None,
            'SOSSISSE.PATHS.RAWPATH': None,
            'NAMELESS.PATHS.INPUT_PATH': 'inputs',
        }
        for key, value in defaults.items():
            cdict.add(key, value=value, dtype=str, source='test')
        values, sources, instances = cdict.unpack()
        params = load_functions.load_into_params(values, sources, instances, check=False)
        params['GLOBAL.PROJECT_NAME'] = 'old'
        params['GLOBAL.DATA_PATH'] = str(root)
        for key in defaults:
            params[key] = str(old_root / key.replace('.', '/'))
        params['TSOVORE.PATHS.PLOT_PATH'] = str(root / 'external-plots')
        params['NAMELESS.PATHS.INPUT_PATH'] = str(root / 'projects' / 'old-other' / 'inputs')
        params['SOSSISSE.INPUTS.SOSSIOPATH'] = str(root)
        with patch.object(startup.drs_text, 'user_input', return_value='new') as prompt:
            assert startup.copy_ask_project_name(params) is params
        assert prompt.call_count == 1
        assert params['GLOBAL.PROJECT_NAME'] == 'new'
        for key in ['TSOVORE.PATHS.INPUT_PATH', 'TSOVORE.PATHS.TEMP_PATH',
                    'TSOVORE.PATHS.OUTPUT_PATH', 'EUREKA.GENERAL.TOPDIR',
                    'STD_JWST.GENERAL.OUTPUT_DIR', 'SOSSISSE.PATHS.RAWPATH']:
            assert params[key] == defaults[key], (key, params[key])
        assert params['SOSSISSE.INPUTS.SOSSIOPATH'] == str(root)
        assert params['TSOVORE.PATHS.PLOT_PATH'] == str(root / 'external-plots')
        assert params['NAMELESS.PATHS.INPUT_PATH'] == str(root / 'projects' / 'old-other' / 'inputs')
    """)


def test_listing_shows_global_project_and_wrapper_roots(tmp_path):
    run_startup_check(tmp_path, """
        from contextlib import ExitStack
        from unittest.mock import mock_open
        config = {
            'GLOBAL': {'DATA_PATH': '/observations', 'PROJECT_NAME': 'target',
                       'INSTRUMENTMODE': 'JWST.NIRISS.SOSS'},
            'RUN': {'TSOVORE': True, 'PRE_EUREKA': True, 'EXT_EUREKA': True,
                    'PRE_JWST': True, 'EXT_NAMELESS': True,
                    'SORBET': {'WLCA': True}},
        }
        header = '# POGOS\\n# Version = 1\\n# Version Date = today\\n'
        output = []
        with ExitStack() as stack:
            stack.enter_context(patch.object(startup.glob, 'glob',
                                             return_value=['project.yaml']))
            stack.enter_context(patch('builtins.open', mock_open(read_data=header)))
            stack.enter_context(patch.object(startup.load_functions.base,
                                             'load_yaml', return_value=config))
            stack.enter_context(patch.object(startup.drs_text, 'cprint',
                side_effect=lambda text, **options: output.append(text)))
            stack.enter_context(patch('builtins.input', return_value=''))
            assert startup.list_yamls() is True
        text = '\\n'.join(output)
        assert 'Project: target' in text
        assert 'Project root: /observations/projects/target' in text
        for step, module in [('TSOVORE', 'tsovore'), ('PRE_EUREKA', 'eureka'),
                             ('EXT_EUREKA', 'eureka'), ('PRE_JWST', 'jwst'),
                             ('EXT_NAMELESS', 'nameless'), ('SORBET.WLCA', 'sorbet')]:
            assert f'{step}: /observations/projects/target/{module}' in text
    """)


def test_setup_cli_has_global_project_name(tmp_path):
    run_startup_check(tmp_path, """
        from pogos.recipes import pogos_setup
        assert 'GLOBAL.PROJECT_NAME' in pogos_setup.__inputs__
    """)


def test_invalid_project_fails_before_directory_creation(tmp_path):
    run_startup_check(tmp_path, """
        params = ParamDict()
        params['GLOBAL.PROJECT_NAME'] = '../escape'
        with patch.object(startup, 'core_setup', return_value=(params, {})), patch.object(
                startup, 'core_yaml_setup') as yaml_setup:
            try:
                startup.setup(params, start_from_demo=False)
            except base.PogosException:
                pass
            else:
                raise AssertionError('Invalid project was accepted')
        yaml_setup.assert_not_called()
        assert not list(Path.cwd().iterdir())
    """)


def test_copy_rejects_reusing_old_project(tmp_path):
    run_startup_check(tmp_path, """
        params = ParamDict()
        params['GLOBAL.PROJECT_NAME'] = 'old'
        params['GLOBAL.DATA_PATH'] = str(Path.cwd())
        with patch.object(startup.drs_text, 'user_input', return_value='old'):
            try:
                startup.copy_ask_project_name(params)
            except base.PogosException:
                pass
            else:
                raise AssertionError('Copy must not reuse the original project')
        assert params['GLOBAL.PROJECT_NAME'] == 'old'
    """)
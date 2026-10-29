from pathlib import Path

import pytest

from pogos.core import definitions
from pogos.core import reset


def make_params(tmp_path, *enabled):
    params = reset.ParamDict()
    params['GLOBAL.DATA_PATH'] = str(tmp_path)
    params['GLOBAL.PROJECT_NAME'] = 'project-a'
    for step in definitions.RED_STEPS:
        params[step.run_key] = step.name in enabled
    return params


@pytest.mark.parametrize('module', ['TSOVORE', 'MIRIAM'])
def test_global_project_routing(tmp_path, module):
    params = make_params(tmp_path, module)
    for kind in ['INPUT', 'TEMP', 'OUTPUT', 'PLOT']:
        params[f'{module}.PATHS.{kind}_PATH'] = kind.lower()
    targets, protected = reset.get_reset_targets(params)
    root = tmp_path / 'projects' / 'project-a' / module.lower()
    assert targets == {module: [str(root / kind)
                               for kind in ['temp', 'output', 'plot']]}
    assert protected == [str(root / 'input')]


ROUTING_CASES = [
    ('TSOVORE', 'TSOVORE', 'tsovore', ['temp', 'output', 'plot'], ['input']),
    ('MIRIAM', 'MIRIAM', 'miriam', ['temp', 'output', 'plot'], ['input']),
    ('SOSSISSE', 'SOSSISSE', 'sossisse',
     ['temporary', 'plots', 'other', 'outputs'],
     ['inputs', 'calibration', 'yamls']),
    ('SORBET.WLCA', 'SORBET.WLCA', 'sorbet',
     ['wlca-output', 'wlca-plot'], ['wlca-input']),
    ('SORBET.SLCA', 'SORBET.SLCA', 'sorbet',
     ['slca-output', 'slca-plot'], ['slca-input']),
    ('PRE_EUREKA', 'PRE_EUREKA', 'eureka', ['s1-out', 's2-out'],
     ['s1-in', 's2-in']),
    ('EXT_EUREKA', 'EXT_EUREKA', 'eureka', ['s3-out'], ['s3-in']),
    ('POST_EUREKA', 'POST_EUREKA', 'eureka',
     ['s4-out', 's5-out', 's6-out', 'ecf'], []),
    ('PRE_JWST', 'PRE_JWST', 'jwst', ['s1-out', 's2-out'],
     ['s1-in', 's2-in']),
    ('EXT_JWST', 'EXT_JWST', 'jwst', ['s3-out'], ['s3-in']),
    ('PRE_NAMELESS', 'NAMELESS', 'nameless',
     reset.NAMELESS_OUTPUT_SUBFOLDERS, ['raw']),
    ('EXT_NAMELESS', 'NAMELESS', 'nameless',
     reset.NAMELESS_OUTPUT_SUBFOLDERS, ['raw']),
]


def configured_params(tmp_path, *enabled):
    params = make_params(tmp_path, *enabled)
    for module in ['TSOVORE', 'MIRIAM']:
        for kind in ['INPUT', 'TEMP', 'OUTPUT', 'PLOT']:
            params[f'{module}.PATHS.{kind}_PATH'] = kind.lower()
    for method in ['WLCA', 'SLCA']:
        for kind in ['INPUT', 'OUTPUT', 'PLOT']:
            params[f'SORBET.{method}.{kind}_PATH'] = (
                f'{method.lower()}-{kind.lower()}')
    for prefix in ['EUREKA', 'STD_JWST']:
        for stage in [1, 2, 3]:
            for kind in ['IN', 'OUT']:
                params[f'{prefix}.PATHS.{kind}_S{stage}_PATH'] = (
                    f's{stage}-{kind.lower()}')
    for stage in [4, 5, 6]:
        params[f'EUREKA.STAGE{stage}.outputdir'] = f's{stage}-out'
    params['NAMELESS.GENERAL.INPUTDIR'] = 'raw'
    return params


@pytest.mark.parametrize('step,name,mode,outputs,inputs', ROUTING_CASES)
def test_all_enabled_step_routing(tmp_path, step, name, mode, outputs, inputs):
    params = configured_params(tmp_path, step)
    before = dict(params)
    targets, protected = reset.get_reset_targets(params)
    root = tmp_path / 'projects' / 'project-a' / mode
    assert targets == {name: [str(root / folder) for folder in outputs]}
    assert protected == [str(root / folder) for folder in inputs]
    assert dict(params) == before
    assert not (tmp_path / 'projects').exists()


@pytest.mark.parametrize('step,name,mode,outputs,inputs', ROUTING_CASES)
def test_project_isolation(tmp_path, step, name, mode, outputs, inputs):
    params = configured_params(tmp_path, step)
    first_targets, first_protected = reset.get_reset_targets(params)
    params['GLOBAL.PROJECT_NAME'] = 'project-b'
    targets, protected = reset.get_reset_targets(params)
    root = tmp_path / 'projects' / 'project-b' / mode
    assert targets == {name: [str(root / folder) for folder in outputs]}
    assert protected == [str(root / folder) for folder in inputs]
    first_paths = first_targets[name] + first_protected
    assert set(targets[name] + protected).isdisjoint(first_paths)


@pytest.mark.parametrize('enabled', [(), ('POST_JWST',), ('EXT_BOX',)])
def test_disabled_and_directory_free_steps(tmp_path, enabled):
    params = configured_params(tmp_path, *enabled)
    assert reset.get_reset_targets(params) == ({}, [])


@pytest.mark.parametrize('module', ['TSOVORE', 'MIRIAM'])
@pytest.mark.parametrize('value', [None, 'nested/../custom', 'absolute'])
def test_matches_prepare_directory(tmp_path, module, value):
    from pogos.core import general

    params = make_params(tmp_path, module)
    path_key = f'{module}.PATHS.OUTPUT_PATH'
    if value == 'absolute':
        value = str(tmp_path / 'custom-output')
    params[path_key] = value
    targets, _ = reset.get_reset_targets(params)
    general.prepare_directory(params, 'output', path_key, module.lower(),
                              verbose=False)
    assert targets[module][1] == params[path_key]


@pytest.mark.parametrize('prefix,mode,step,key', [
    ('SORBET.WLCA', 'sorbet', 'SORBET.WLCA', 'OUTPUT_PATH'),
    ('SORBET.SLCA', 'sorbet', 'SORBET.SLCA', 'PLOT_PATH'),
    ('EUREKA.PATHS', 'eureka', 'PRE_EUREKA', 'OUT_S1_PATH'),
    ('STD_JWST.PATHS', 'jwst', 'EXT_JWST', 'OUT_S3_PATH'),
    ('EUREKA.STAGE4', 'eureka', 'POST_EUREKA', 'outputdir'),
])
@pytest.mark.parametrize('absolute', [False, True])
def test_pogos_overrides(tmp_path, prefix, mode, step, key, absolute):
    params = configured_params(tmp_path, step)
    override = tmp_path / 'custom-output' if absolute else Path('custom-output')
    params[f'{prefix}.{key}'] = str(override)
    targets, _ = reset.get_reset_targets(params)
    expected = override if absolute else (
        tmp_path / 'projects' / 'project-a' / mode / override)
    assert str(expected) in targets[step]


def test_sossisse_uses_global_root_and_project(tmp_path):
    params = make_params(tmp_path, 'SOSSISSE')
    params['SOSSISSE.INPUTS.SOSSIOPATH'] = str(tmp_path / 'ignored')
    params['SOSSISSE.INPUTS.PROJECT_NAME'] = 'ignored-project'
    targets, protected = reset.get_reset_targets(params)
    root = tmp_path / 'projects' / 'project-a' / 'sossisse'
    assert targets['SOSSISSE'][-1] == str(root / 'outputs')
    assert protected[0] == str(root / 'inputs')


@pytest.mark.parametrize('relative', [False, True])
def test_sossisse_all_path_overrides(tmp_path, monkeypatch, relative):
    monkeypatch.chdir(tmp_path)
    params = make_params(tmp_path, 'SOSSISSE')
    keys = ['TEMP_PATH', 'PLOT_PATH', 'OTHER_PATH', 'OUT_PATH',
            'RAWPATH', 'CALIBPATH', 'YAMLPATH']
    for key in ['RUN_PATH'] + keys:
        path = Path(key.lower()) if relative else tmp_path / key.lower()
        params[f'SOSSISSE.PATHS.{key}'] = str(path)
    targets, protected = reset.get_reset_targets(params)
    assert targets['SOSSISSE'] == [str(tmp_path / key.lower())
                                   for key in keys[:4]]
    assert protected == [str(tmp_path / key.lower()) for key in keys[4:]]


@pytest.mark.parametrize('relative', [False, True])
def test_sossisse_run_path_override(tmp_path, monkeypatch, relative):
    monkeypatch.chdir(tmp_path)
    params = make_params(tmp_path, 'SOSSISSE')
    run_path = Path('custom-run') if relative else tmp_path / 'custom-run'
    params['SOSSISSE.PATHS.RUN_PATH'] = str(run_path)
    targets, protected = reset.get_reset_targets(params)
    root = tmp_path / 'custom-run'
    assert targets['SOSSISSE'] == [str(root / folder) for folder in
                                   ['temporary', 'plots', 'other', 'outputs']]
    assert protected == [str(root / folder) for folder in
                         ['inputs', 'calibration', 'yamls']]


def write_marker(path):
    path.mkdir(parents=True, exist_ok=True)
    marker = path / 'keep.txt'
    marker.write_text('preserve me')
    return marker


@pytest.fixture
def quiet_log(monkeypatch):
    monkeypatch.setattr(reset, 'WLOG', lambda *args, **kwargs: None)


def test_real_reset_all_modules(tmp_path, quiet_log):
    enabled = [step.name for step in definitions.RED_STEPS]
    params = configured_params(tmp_path, *enabled)
    params['NAMELESS.PATHS.ANCIL_PATH'] = str(tmp_path / 'calibrations')
    targets, protected = reset.get_reset_targets(params)
    output_paths = [Path(path) for paths in targets.values() for path in paths]
    for path in output_paths:
        write_marker(path)
    survivors = [write_marker(Path(path)) for path in protected]
    survivors.append(write_marker(tmp_path / 'projects' / 'project-b' / 'outputs'))
    survivors.append(write_marker(tmp_path / 'unrelated'))
    filtered, warnings = reset.filter_safe_targets(params, targets, protected)
    assert warnings == []
    reset.perform_reset(params, filtered)
    assert all(path.is_dir() and not list(path.iterdir())
               for path in output_paths)
    assert all(marker.read_text() == 'preserve me' for marker in survivors)


@pytest.mark.parametrize('protected_key', ['RAWPATH', 'CALIBPATH', 'YAMLPATH'])
@pytest.mark.parametrize('overlap', ['same', 'parent', 'child'])
def test_protected_sossisse_overrides(tmp_path, quiet_log, protected_key,
                                      overlap):
    params = make_params(tmp_path, 'SOSSISSE')
    sensitive = tmp_path / 'sensitive'
    survivor = write_marker(sensitive)
    params[f'SOSSISSE.PATHS.{protected_key}'] = str(sensitive)
    candidates = {'same': sensitive, 'parent': tmp_path,
                  'child': sensitive / 'nested'}
    target = candidates[overlap]
    target.mkdir(exist_ok=True)
    params['SOSSISSE.PATHS.OUT_PATH'] = str(target)
    targets, protected = reset.get_reset_targets(params)
    filtered, warnings = reset.filter_safe_targets(params, targets, protected)
    assert str(target) not in filtered.get('SOSSISSE', [])
    assert any(str(target) in warning for warning in warnings)
    reset.perform_reset(params, {'SOSSISSE': [str(target)]})
    assert survivor.read_text() == 'preserve me'


@pytest.mark.parametrize('kind', ['root', 'outside', 'prefix-sibling',
                                  'relative-escape'])
def test_unsafe_overrides_are_not_deleted(tmp_path, quiet_log, kind):
    data_root = tmp_path / 'database'
    params = configured_params(data_root, 'TSOVORE')
    paths = {'root': data_root, 'outside': tmp_path / 'outside',
             'prefix-sibling': tmp_path / 'database-sibling',
             'relative-escape': data_root / '..' / 'escaped'}
    target = paths[kind]
    survivor = write_marker(target)
    params['TSOVORE.PATHS.OUTPUT_PATH'] = str(target)
    targets, protected = reset.get_reset_targets(params)
    filtered, warnings = reset.filter_safe_targets(params, targets, protected)
    assert filtered == {}
    assert len(warnings) == 1
    reset.perform_reset(params, targets)
    assert survivor.read_text() == 'preserve me'


@pytest.mark.parametrize('kind', ['target', 'ancestor', 'protected-alias'])
def test_symlink_safety(tmp_path, quiet_log, kind):
    data_root = tmp_path / 'database'
    data_root.mkdir()
    params = configured_params(data_root, 'TSOVORE')
    destination = tmp_path / 'outside'
    if kind == 'protected-alias':
        destination = data_root / 'inputs'
        params['TSOVORE.PATHS.INPUT_PATH'] = str(destination)
    survivor = write_marker(destination / 'outputs')
    link = data_root / 'link'
    link.symlink_to(destination, target_is_directory=True)
    target = link if kind == 'target' else link / 'outputs'
    params['TSOVORE.PATHS.OUTPUT_PATH'] = str(target)
    targets, protected = reset.get_reset_targets(params)
    filtered, warnings = reset.filter_safe_targets(params, targets, protected)
    assert filtered == {}
    assert len(warnings) == 1
    reset.perform_reset(params, targets)
    assert survivor.read_text() == 'preserve me'
    assert link.is_symlink()


def test_symlink_changed_after_filter(tmp_path, quiet_log):
    data_root = tmp_path / 'database'
    params = configured_params(data_root, 'TSOVORE')
    target = data_root / 'outputs'
    target.mkdir(parents=True)
    params['TSOVORE.PATHS.OUTPUT_PATH'] = str(target)
    targets, protected = reset.get_reset_targets(params)
    filtered, warnings = reset.filter_safe_targets(params, targets, protected)
    assert warnings == []
    target.rmdir()
    outside = tmp_path / 'outside'
    survivor = write_marker(outside)
    target.symlink_to(outside, target_is_directory=True)
    reset.perform_reset(params, filtered)
    assert survivor.read_text() == 'preserve me'
    assert target.is_symlink()


def test_nested_symlinks_are_unlinked_without_following(tmp_path, quiet_log):
    data_root = tmp_path / 'database'
    params = configured_params(data_root, 'TSOVORE')
    target = data_root / 'outputs'
    target.mkdir(parents=True)
    outside = tmp_path / 'outside'
    survivor = write_marker(outside)
    (target / 'link').symlink_to(outside, target_is_directory=True)
    params['TSOVORE.PATHS.OUTPUT_PATH'] = str(target)
    targets, protected = reset.get_reset_targets(params)
    filtered, warnings = reset.filter_safe_targets(params, targets, protected)
    assert warnings == []
    reset.perform_reset(params, filtered)
    assert target.is_dir() and not list(target.iterdir())
    assert survivor.read_text() == 'preserve me'


def test_protected_symlink_inside_output_survives(tmp_path, quiet_log):
    data_root = tmp_path / 'database'
    params = configured_params(data_root, 'TSOVORE')
    target = data_root / 'outputs'
    target.mkdir(parents=True)
    outside = tmp_path / 'outside-inputs'
    survivor = write_marker(outside)
    input_link = target / 'inputs'
    input_link.symlink_to(outside, target_is_directory=True)
    params['TSOVORE.PATHS.INPUT_PATH'] = str(input_link)
    params['TSOVORE.PATHS.OUTPUT_PATH'] = str(target)
    targets, protected = reset.get_reset_targets(params)
    filtered, warnings = reset.filter_safe_targets(params, targets, protected)
    assert filtered == {}
    assert len(warnings) == 1
    reset.perform_reset(params, targets)
    assert input_link.is_symlink()
    assert survivor.read_text() == 'preserve me'


def test_filter_missing_and_duplicate_targets(tmp_path):
    params = make_params(tmp_path)
    target = tmp_path / 'outputs'
    target.mkdir()
    targets = {'first': [str(target), str(tmp_path / 'missing')],
               'second': [str(target)]}
    assert reset.filter_safe_targets(params, targets, []) == (
        {'first': [str(target)]}, [])
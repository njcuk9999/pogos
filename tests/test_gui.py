#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for the POGOS browser gui (pogos.gui)

Covers the setup choice numbering (it must match the pogos_setup prompt
answers), the command builders, the yaml / project / plot layout helpers
and the main gui routes (path lock, yaml save conflicts, project delete
confirmation).
"""
import importlib.util
import json
import os
import sys
from pathlib import Path

import pytest

# the conftest stubs "aperocore" without a package path - let the real
#   aperocore.gui sub package (stdlib + yaml only) be imported through it
_stub = sys.modules.get('aperocore')
if _stub is not None and not hasattr(_stub, '__path__'):
    # find the real package (editable installs need the meta path finders)
    del sys.modules['aperocore']
    try:
        _spec = importlib.util.find_spec('aperocore')
    finally:
        sys.modules['aperocore'] = _stub
    if _spec is not None and _spec.submodule_search_locations:
        _stub.__path__ = list(_spec.submodule_search_locations)

from pogos.core import definitions  # noqa: E402
from pogos.gui import app as gui_app  # noqa: E402
from pogos.gui import commands  # noqa: E402
from pogos.gui import layout  # noqa: E402
from aperocore.gui import webapp  # noqa: E402

# a minimal POGOS yaml
YAML = """#####################
# POGOS
#####################
# Version = 0.0.042
#     Date    = 2026-11-18
GLOBAL:
  DATA_PATH: {path}
  PROJECT_NAME: proj1
  INSTRUMENTMODE: JWST.NIRISS.SOSS
RUN:
  SOSSISSE: true
  SORBET:
    WLCA: true
    SLCA: false
"""


# =============================================================================
# Define fixtures
# =============================================================================
@pytest.fixture
def pogos_path(tmp_path: Path) -> Path:
    """
    A POGOS path with one yaml, one project and two plots

    :param tmp_path: Path, pytest temporary directory

    :return: Path, the POGOS path
    """
    (tmp_path / 'yamls').mkdir()
    (tmp_path / 'yamls' / 'a.yaml').write_text(YAML.format(path=tmp_path))
    plots = tmp_path / 'projects' / 'proj1' / 'sossisse' / 'plots'
    plots.mkdir(parents=True)
    (plots / 'p1.png').write_bytes(b'png')
    (plots / 'sub').mkdir()
    (plots / 'sub' / 'p2.png').write_bytes(b'png')
    return tmp_path


# =============================================================================
# Define tests
# =============================================================================
def test_setup_choices_match_prompt_numbers() -> None:
    """Instrument / mode / step numbers follow the pogos_setup prompts."""
    choices = commands.setup_choices()['instruments']
    names = list(definitions.mode_choices().keys())
    assert [inst['name'] for inst in choices] == names
    inst, mode = commands.find_mode('JWST.NIRISS.SOSS')
    assert inst['number'] == names.index('JWST.NIRISS') + 1
    expected = [m.name for m in definitions.mode_choices()['JWST.NIRISS']]
    assert mode['number'] == expected.index('JWST.NIRISS.SOSS') + 1
    # steps: 1-based among the supported steps of each level (0 = skip)
    for level in mode['levels']:
        level_def = [lvl for lvl in definitions.REDUCTION_LEVELS
                     if lvl.name == level['name']][0]
        defs = [step.name for step in definitions.steps_for_level(level_def)
                if step.supports(definitions.MODE_BY_NAME[mode['name']])]
        assert [step['name'] for step in level['steps']] == defs
        assert [step['number'] for step in level['steps']] == list(
            range(1, len(defs) + 1))
    with pytest.raises(commands.CommandError):
        commands.find_mode('JWST.NIRISS.AMI')


def test_setup_command(tmp_path: Path, monkeypatch) -> None:
    """The setup form becomes pogos_setup pre-answers."""
    # the project name rule lives in pogos.core.startup (full runtime)
    monkeypatch.setattr(commands, 'validate_project_name', lambda name: None)
    form = dict(project_name='p1', yaml_name='mine', demo='t1b.sossisse',
                instmode='JWST.NIRISS.SOSS',
                steps={'Extraction': ['SOSSISSE'],
                       'Post-extraction': ['SORBET.WLCA', 'SORBET.SLCA']},
                download='now')
    built = commands.setup_command(str(tmp_path), form)
    args = built['display'].split()
    assert args[0] == 'pogos_setup'
    assert '--data_path={0}'.format(tmp_path) in args
    assert '--yamlfile={0}'.format(tmp_path / 'yamls' / 'mine.yaml') in args
    assert '--preextract_step=0' in args
    assert '--extract_step=1' in args
    assert '--postextract_step=1,2' in args
    assert '--demo_select=t1b.sossisse' in args
    assert '--download=now' in args
    assert built['cmd'][1:3] == ['-m', 'pogos.recipes.pogos_setup']
    # no yaml name and no demo is refused
    with pytest.raises(commands.CommandError):
        commands.setup_command(str(tmp_path), dict(form, yaml_name='',
                                                   demo=''))
    # two extraction steps are refused (single choice level)
    bad = dict(form, steps={'Extraction': ['SOSSISSE', 'EXT_NAMELESS']})
    with pytest.raises(commands.CommandError):
        commands.setup_command(str(tmp_path), bad)


def test_setup_errors_lists_every_problem(tmp_path: Path,
                                          monkeypatch) -> None:
    """Validation reports all problems, incl. every stage skipped."""
    monkeypatch.setattr(commands, 'validate_project_name',
                        lambda name: 'bad name' if ' ' in name else None)
    form = dict(project_name='has space', yaml_name='', demo='',
                instmode='JWST.NIRISS.SOSS',
                steps={'Pre-extraction': [], 'Extraction': [],
                       'Post-extraction': []}, download='local')
    errors = commands.setup_errors(str(tmp_path), form)
    text = '\n'.join(errors)
    assert 'Project name: bad name' in text
    assert 'yaml file name' in text
    assert 'Every reduction stage is skipped' in text
    assert 'local mirror' in text
    with pytest.raises(commands.CommandError) as error:
        commands.setup_command(str(tmp_path), form)
    assert len(str(error.value).splitlines()) == len(errors)
    # no instrument chosen yet
    assert any('instrument' in err for err in commands.setup_errors(
        str(tmp_path), dict(project_name='ok', demo='d1')))


def test_run_reset_config_commands(pogos_path: Path) -> None:
    """Run / reset / config commands and their environment."""
    yaml_path = str(pogos_path / 'yamls' / 'a.yaml')
    run = commands.run_command(yaml_path, accept_old=True)
    assert run['env'] == {commands.ACCEPT_OLD_ENV: '1'}
    assert run['display'].startswith('POGOS_ACCEPT_OLD_YAML=1 pogos_run')
    check = commands.config_command(yaml_path, check_only=True)
    assert check['env'] == {'CI': '1'}
    assert commands.config_command(yaml_path, check_only=False)['env'] == {}
    batch = commands.batch_lines(yaml_path, workdir=str(pogos_path))
    assert batch['lines'][-1].startswith('pogos_run --yamlfile=')
    with pytest.raises(commands.CommandError):
        commands.reset_command(str(pogos_path / 'missing.yaml'))


def test_show_plots_arguments(pogos_path: Path) -> None:
    """The Run tab tick box becomes pogos_run --showplots=on / off."""
    yaml_path = str(pogos_path / 'yamls' / 'a.yaml')
    assert '--showplots' not in commands.run_command(yaml_path)['display']
    run_on = commands.run_command(yaml_path, show_plots=True)
    assert run_on['cmd'][-1] == '--showplots=on'
    run_off = commands.run_command(yaml_path, show_plots=False)
    assert run_off['display'].endswith('--showplots=off')
    batch = commands.batch_lines(yaml_path, show_plots=False)
    assert batch['lines'][-1].endswith('--showplots=off')
    # the gui streams unless the box is unticked
    assert gui_app.stream_plots(dict()) and gui_app.stream_plots(None)
    assert not gui_app.stream_plots(dict(stream_plots=False))
    assert not gui_app.stream_plots(dict(stream_plots='false'))
    app = gui_app.PogosGuiApp(str(pogos_path))
    built = app._build('run', dict(yaml=yaml_path))
    assert built['cmd'][-1] == '--showplots=on'
    built = app._build('batch', dict(yaml=yaml_path, stream_plots=False))
    assert built['lines'][-1].endswith('--showplots=off')


def test_apply_show_plots() -> None:
    """--showplots forces every flavour's PLOTS.SHOW (off clears users)."""
    from pogos.core import recipe_helpers
    logged = []

    class _Params(dict):
        def set(self, key, value=None, source=None):
            self[key] = value
    params = _Params({'GLOBAL.SHOW_PLOTS': 'on', 'SORBET.PLOTS.SHOW': False,
                      'SOSSISSE.PLOTS.SHOW': False,
                      'SOSSISSE.PLOTS.USER_SHOW': ['me']})
    recipe_helpers.apply_show_plots(params, lambda *a: logged.append(a))
    assert params['SORBET.PLOTS.SHOW'] and params['SOSSISSE.PLOTS.SHOW']
    # flavours not in the yaml are not added
    assert 'MIRIAM.PLOTS.SHOW' not in params
    params['GLOBAL.SHOW_PLOTS'] = 'off'
    recipe_helpers.apply_show_plots(params, lambda *a: logged.append(a))
    assert not params['SORBET.PLOTS.SHOW']
    assert params['SOSSISSE.PLOTS.USER_SHOW'] == []
    # without the argument the yaml decides
    params = _Params({'GLOBAL.SHOW_PLOTS': None, 'SORBET.PLOTS.SHOW': True})
    recipe_helpers.apply_show_plots(params, lambda *a: logged.append(a))
    assert params['SORBET.PLOTS.SHOW'] and len(logged) == 2


def test_layout_summary_projects_plots(pogos_path: Path) -> None:
    """Yaml summaries, project lists and the plot tree."""
    summary = layout.yaml_summary(str(pogos_path / 'yamls' / 'a.yaml'))
    assert summary['pogos'] and summary['version'] == '0.0.042'
    assert summary['instmode'] == 'JWST.NIRISS.SOSS'
    assert summary['steps'] == ['SOSSISSE', 'SORBET.WLCA']
    projects = layout.list_projects(str(pogos_path))
    assert projects[0]['name'] == 'proj1'
    assert projects[0]['modules'] == ['sossisse']
    assert len(projects[0]['yamls']) == 1
    plots = layout.collect_plots(str(pogos_path))
    assert plots['total'] == 2
    dirs = [d['dir'] for d in plots['projects'][0]['modules'][0]['dirs']]
    assert dirs == ['plots', os.path.join('plots', 'sub')]
    stats = layout.project_stats(str(pogos_path), 'proj1')
    assert stats['nfiles'] == 2


def _request(method: str, route: str, body: dict = None) -> webapp.Request:
    """
    Build a gui request

    :param method: str, GET or POST
    :param route: str, the route (with query string)
    :param body: dict or None, the json body

    :return: Request, the request
    """
    return webapp.Request(method, route, body, '127.0.0.1')


def test_app_path_lock_and_routes(pogos_path: Path) -> None:
    """Routes need the POGOS path; yamls and plots are listed."""
    app = gui_app.PogosGuiApp(None)
    response = app.handle(_request('GET', '/api/pogos/yamls'))
    assert response.code == 400
    missing = app.handle(_request('POST', '/api/pogos/path',
                                  dict(path=str(pogos_path / 'new'))))
    assert json.loads(missing.body)['missing']
    opened = app.handle(_request('POST', '/api/pogos/path',
                                 dict(path=str(pogos_path))))
    assert json.loads(opened.body)['success']
    yamls = json.loads(app.handle(_request('GET', '/api/pogos/yamls')).body)
    assert yamls['yamls'][0]['name'] == 'a.yaml'
    plots = json.loads(app.handle(_request('GET', '/api/pogos/plots')).body)
    assert plots['total'] == 2
    page = app.handle(_request('GET', '/'))
    assert b'POGOS path' in page.body and b'XX_' not in page.body


def test_app_yaml_save_conflict_and_backup(pogos_path: Path) -> None:
    """Saving keeps a backup and refuses stale (changed on disk) saves."""
    app = gui_app.PogosGuiApp(str(pogos_path))
    target = pogos_path / 'yamls' / 'a.yaml'
    mtime = os.path.getmtime(target)
    body = dict(path=str(target), text='x: 1\n', mtime=mtime - 100)
    stale = json.loads(app.handle(_request('POST', '/api/pogos/yaml_save',
                                           body)).body)
    assert stale['conflict']
    body['mtime'] = mtime
    saved = json.loads(app.handle(_request('POST', '/api/pogos/yaml_save',
                                           body)).body)
    assert saved['success'] and target.read_text() == 'x: 1\n'
    assert Path(saved['backup']).exists()
    bad = app.handle(_request('POST', '/api/pogos/yaml_save',
                              dict(path=str(pogos_path / 'a.txt'),
                                   text='x')))
    assert bad.code == 400


def test_app_project_delete_needs_name(pogos_path: Path) -> None:
    """Deleting a project needs its name typed as confirmation."""
    app = gui_app.PogosGuiApp(str(pogos_path))
    refused = app.handle(_request('POST', '/api/pogos/project_delete',
                                  dict(name='proj1', confirm='yes')))
    assert refused.code == 400
    assert (pogos_path / 'projects' / 'proj1').exists()
    done = json.loads(app.handle(_request(
        'POST', '/api/pogos/project_delete',
        dict(name='proj1', confirm='proj1'))).body)
    assert done['success']
    assert not (pogos_path / 'projects' / 'proj1').exists()
    # yamls are kept unless asked for
    assert (pogos_path / 'yamls' / 'a.yaml').exists()


def test_app_reset_needs_typed_confirmation(pogos_path: Path) -> None:
    """The reset route refuses without the typed RESET."""
    app = gui_app.PogosGuiApp(str(pogos_path))
    response = app.handle(_request('POST', '/api/pogos/reset', dict(
        yaml=str(pogos_path / 'yamls' / 'a.yaml'), confirm='reset')))
    assert response.code == 400


def test_progress_status_roundtrip(tmp_path: Path, monkeypatch) -> None:
    """Progress events of a run become the Status tab tables."""
    from pogos.core import progress
    from pogos.gui import status
    monkeypatch.delenv(progress.ENV_FILE, raising=False)
    steps = [['Extraction', 'SOSSISSE'], ['Post-extraction', 'SORBET']]
    with progress.run(str(tmp_path), 'a.yaml', 'proj1', 'MODE', steps):
        with progress.stage('Extraction', 'SOSSISSE'):
            with progress.substep('Linear reconstruction', total=4):
                progress.advance(2, 4, 'chunk 2', force=True)
            progress.start_substep('Spectral extraction')
    runs = status.list_runs(str(tmp_path))
    assert len(runs) == 1 and runs[0]['status'] == 'complete'
    run = status.get_run(str(tmp_path), runs[0]['id'])
    sossisse, sorbet = run['steps']
    assert sossisse['status'] == 'complete'
    names = [sub['name'] for sub in sossisse['children']]
    assert names == ['Linear reconstruction', 'Spectral extraction']
    assert sossisse['children'][0]['done'] == 4
    assert sorbet['status'] == 'pending'
    assert not progress.active()


def test_progress_stage_tags_figures(tmp_path: Path, monkeypatch) -> None:
    """Figures shown inside a stage know its level / flavour / step."""
    from aperocore import progress as gprogress
    from pogos.core import progress
    monkeypatch.delenv(progress.ENV_FILE, raising=False)
    with progress.run(str(tmp_path), 'a.yaml', 'p', 'M',
                      [['Extraction', 'SOSSISSE']]):
        with progress.stage('Extraction', 'SOSSISSE'):
            with progress.substep('Fit'):
                context = gprogress.context()
        after = gprogress.context()
    assert context == dict(level='Extraction', flavour='SOSSISSE',
                           path=['Fit'])
    # outside a stage figures are not tagged
    assert after == dict(path=[])


def test_app_stream_figure_paths(pogos_path: Path) -> None:
    """The stream route gives the pickled figure; only streams load."""
    app = gui_app.PogosGuiApp(str(pogos_path))
    folder = Path(app._stream_root()) / 'run1'
    folder.mkdir(parents=True)
    entry = dict(file='0001.png', figure='0001.mplfig', title='t',
                 step=dict(level='L', flavour='F', path=['A']))
    (folder / 'index.jsonl').write_text(json.dumps(entry) + '\n')
    response = app.handle(_request('GET', '/api/pogos/stream?name=run1'))
    figure = json.loads(response.body)['figures'][0]
    assert figure['figure_path'] == str(folder / '0001.mplfig')
    assert app.figure_roots() == [app._stream_root()]


def test_progress_failed_run(tmp_path: Path, monkeypatch) -> None:
    """A failing stage marks the stage, sub step and run as failed."""
    from pogos.core import progress
    from pogos.gui import status
    monkeypatch.delenv(progress.ENV_FILE, raising=False)
    with pytest.raises(ValueError):
        with progress.run(str(tmp_path), 'b.yaml', 'p', 'M',
                          [['Pre-extraction', 'TSOVORE'],
                           ['Extraction', 'SOSSISSE']]):
            with progress.stage('Pre-extraction', 'TSOVORE'):
                progress.start_substep('Process')
                raise ValueError('boom')
    run = status.get_run(str(tmp_path),
                         status.list_runs(str(tmp_path))[0]['id'])
    assert run['status'] == 'failed' and 'boom' in run['error']
    tsovore, sossisse = run['steps']
    assert tsovore['status'] == 'failed'
    assert tsovore['children'][0]['status'] == 'failed'
    assert sossisse['status'] == 'not run'
    # finished runs can be removed from the list
    assert status.remove_runs(str(tmp_path), [run['id']]) == 1


def test_progress_plan_tree(tmp_path: Path, monkeypatch) -> None:
    """Planned steps are pending, loops get one row per item and the
    steps after a failure are not run."""
    from aperocore import progress as gprogress
    from pogos.core import progress
    from pogos.gui import status
    monkeypatch.delenv(progress.ENV_FILE, raising=False)
    node = gprogress.node
    plan = [node('Prep', func='pkg.mod.prep', desc='Prepares'),
            node('Detector', node('Load', func='pkg.mod.load'), node('Fit'),
                 loop=True),
            node('Merge')]
    steps = [['Extraction', 'X']]
    plans = [dict(level='Extraction', flavour='X', plan=plan)]
    # a running record: everything planned is pending before it starts
    path = progress.start_run(str(tmp_path), 'c.yaml', 'p', 'M', steps,
                              plans)
    run = status.parse_run(path)
    stage = run['steps'][0]
    assert [c['name'] for c in stage['children']] == ['Prep', 'Detector',
                                                      'Merge']
    assert all(c['status'] == 'pending' for c in stage['children'])
    progress.end_run('complete')
    # a run that fails in the second detector
    with pytest.raises(ValueError):
        with progress.run(str(tmp_path), 'd.yaml', 'p', 'M', steps, plans):
            with progress.stage('Extraction', 'X'):
                gprogress.mark('Prep')
                with gprogress.step('Detector', items=['d1', 'd2']):
                    for det in ['d1', 'd2']:
                        with gprogress.step(det):
                            gprogress.mark('Load')
                            if det == 'd2':
                                raise ValueError('bad detector')
                            gprogress.mark('Fit')
                gprogress.mark('Merge')
    runs = status.list_runs(str(tmp_path))
    run = status.get_run(str(tmp_path), [r for r in runs
                                         if r['yaml_name'] == 'd.yaml'][0]
                         ['id'])
    prep, detector, merge = run['steps'][0]['children']
    assert prep['status'] == 'complete'
    assert detector['status'] == 'failed'
    d1, d2 = detector['children']
    assert d1['status'] == 'complete'
    assert [c['status'] for c in d1['children']] == ['complete',
                                                     'complete']
    assert [c['status'] for c in d2['children']] == ['failed', 'not run']
    assert 'bad detector' in d2['error']
    assert merge['status'] == 'not run'
    # the plan's function / description and the marking call site
    assert prep['func'] == 'pkg.mod.prep' and prep['desc'] == 'Prepares'
    assert d1['children'][0]['func'] == 'pkg.mod.load'
    assert prep['src_file'] == __file__ and prep['src_line'] > 0
    assert not gprogress.active()


def test_jwst_stpipe_steps() -> None:
    """stpipe log lines become steps (the pipeline line is not one, a
    skipped step ends as skipped)."""
    import logging
    from aperocore import progress as gprogress
    from pogos.jwst_wrap.core import progress_plan as jwplan
    events = []
    gprogress.set_writer(lambda event, **fields: events.append(
        (event, '/'.join(fields.get('path') or []), fields.get('status'))))
    log = logging.getLogger(jwplan.STPIPE_LOGGER)
    old_level = log.level
    log.setLevel(logging.INFO)
    try:
        with jwplan.StpipeSteps():
            log.info('Step %s running with args %s.', 'Detector1Pipeline',
                     ())
            log.info('Step %s running with args %s.', 'dq_init', ())
            log.info('Step %s done', 'dq_init')
            log.info('Step %s running with args %s.', 'ipc', ())
            log.info('Step skipped.')
            log.info('Step %s done', 'Detector1Pipeline')
    finally:
        log.setLevel(old_level)
        gprogress.set_writer(None)
    assert events == [('step_start', 'dq_init', None),
                      ('step_end', 'dq_init', 'complete'),
                      ('step_start', 'ipc', None),
                      ('step_end', 'ipc', 'skipped')]


def test_nameless_track_methods() -> None:
    """Methods of one object are recorded while tracked, then restored."""
    from aperocore import progress as gprogress
    from pogos.nameless_wrap.core import progress_plan as nlplan

    class Reduc:
        def badpixcorr(self, settings):
            return settings

    reduc = Reduc()
    events = []
    gprogress.set_writer(lambda event, **fields: events.append(
        (event, '/'.join(fields.get('path') or []))))
    try:
        with nlplan.track_methods(reduc, [('badpixcorr', 'NL_BADPIX')]):
            assert reduc.badpixcorr(3) == 3
    finally:
        gprogress.set_writer(None)
    assert events[0] == ('step_start', nlplan.NL_BADPIX)
    assert 'badpixcorr' not in vars(reduc)


def test_app_run_actions(pogos_path: Path, monkeypatch) -> None:
    """Reset run records (dry run / real), retry candidates (newest run
    per yaml, failed only, yaml must exist) and stop all."""
    from pogos.core import progress
    monkeypatch.delenv(progress.ENV_FILE, raising=False)
    yaml_a = str(pogos_path / 'yamls' / 'a.yaml')
    steps = [['Extraction', 'SOSSISSE']]
    # an old failed run of a.yaml, then a complete one: nothing to retry
    for fail in [True, False]:
        try:
            with progress.run(str(pogos_path), yaml_a, 'p', 'M', steps):
                if fail:
                    raise ValueError('boom')
        except ValueError:
            pass
    # a failed run of a yaml that no longer exists: not retried
    try:
        with progress.run(str(pogos_path), str(pogos_path / 'gone.yaml'),
                          'p', 'M', steps):
            raise ValueError('boom')
    except ValueError:
        pass
    app = gui_app.PogosGuiApp(str(pogos_path))
    assert app.retry_candidates() == []
    # the newest run of a.yaml fails: it is retried (on this machine)
    try:
        with progress.run(str(pogos_path), yaml_a, 'p', 'M', steps):
            raise ValueError('boom')
    except ValueError:
        pass
    candidates = app.retry_candidates()
    assert [os.path.basename(c['yaml']) for c in candidates] == ['a.yaml']
    assert candidates[0]['batch'] is None
    dry = json.loads(app.handle(_request('POST', '/api/pogos/retry_failed',
                                         dict(dry_run=True))).body)
    assert dry['local'] == 1 and dry['batch'] == 0
    # reset: dry run counts, then the failed records go
    dry = json.loads(app.handle(_request('POST', '/api/pogos/runs_reset',
                                         dict(state='failed',
                                              dry_run=True))).body)
    assert dry['runs'] == 3
    assert len(status_mod_list(pogos_path)) == 4
    done = json.loads(app.handle(_request('POST', '/api/pogos/runs_reset',
                                          dict(state='failed'))).body)
    assert done['runs'] == 3
    assert [r['status'] for r in status_mod_list(pogos_path)] == [
        'complete']
    bad = app.handle(_request('POST', '/api/pogos/runs_reset',
                              dict(state='running')))
    assert bad.code == 400
    # stop all: nothing started from the gui
    stop = json.loads(app.handle(_request('POST', '/api/pogos/stop_all',
                                          dict(dry_run=True))).body)
    assert stop['stopped'] == 0


def status_mod_list(pogos_path: Path) -> list:
    """The recorded runs of a POGOS path (helper)."""
    from pogos.gui import status
    return status.list_runs(str(pogos_path))


def test_app_project_delete_ignores_case(pogos_path: Path) -> None:
    """The typed project name may be in any case."""
    app = gui_app.PogosGuiApp(str(pogos_path))
    (pogos_path / 'projects' / 'MyProj').mkdir(parents=True)
    response = app.handle(_request('POST', '/api/pogos/project_delete',
                                   dict(name='MyProj', confirm='myproj')))
    assert response.code == 200
    assert not (pogos_path / 'projects' / 'MyProj').exists()
    wrong = app.handle(_request('POST', '/api/pogos/project_delete',
                                dict(name='MyProj', confirm='other')))
    assert wrong.code == 400


def test_app_stream_routes(pogos_path: Path) -> None:
    """Run jobs get a stream folder; its figures are listed."""
    app = gui_app.PogosGuiApp(str(pogos_path))
    env = app.stream_env(str(pogos_path / 'yamls' / 'a.yaml'), 'local')
    assert env['MPLBACKEND'] == gui_app.STREAM_BACKEND
    folder = Path(env[gui_app.STREAM_ENV])
    (folder / 'f1.png').write_bytes(b'png')
    (folder / 'index.jsonl').write_text(json.dumps(
        dict(file='f1.png', title='t', time=1.0)) + '\n')
    streams = json.loads(app.handle(_request('GET',
                                             '/api/pogos/streams')).body)
    assert streams['streams'][0]['count'] == 1
    name = streams['streams'][0]['name']
    data = json.loads(app.handle(_request(
        'GET', '/api/pogos/stream?name={0}&since=0'.format(name))).body)
    assert data['figures'][0]['path'] == str(folder / 'f1.png')
    bad = app.handle(_request('GET', '/api/pogos/stream?name=../x'))
    assert bad.code == 400


# the Preamble stage / late plans of a run (pogos_run)
PROGRESS_STAGES = [['Extraction', 'SOSSISSE'], ['Post-extraction', 'SORBET']]
PROGRESS_PLAN = [dict(name='Load data', children=[]),
                 dict(name='Fit', children=[])]


def _names(children):
    """The step names of a stage tree level."""
    return [child['name'] for child in children]


def _stage_of(parsed, level):
    """The parsed stage of a level."""
    return [stage for stage in parsed['steps'] if stage['level'] == level][0]


def test_stages_pending_before_plans_and_filled_later(tmp_path,
                                                      monkeypatch):
    """The Preamble runs first; flavour stages are pending (steps filled
    in by the later plans event)."""
    from pogos.core import progress
    from pogos.gui import status
    record = tmp_path / 'run.jsonl'
    monkeypatch.setenv(progress.ENV_FILE, str(record))
    monkeypatch.delenv(progress.ENV_LOG, raising=False)
    monkeypatch.delenv(progress.ENV_GUI_LOG, raising=False)
    steps = [progress.PREAMBLE_STAGE] + PROGRESS_STAGES
    progress.start_run(None, 'my.yaml', 'PROJ', 'MODE', steps,
                       [progress.preamble_plan()])
    try:
        with progress.stage(*progress.PREAMBLE_STAGE):
            for name in progress.PREAMBLE_STEPS[:3]:
                progress.start_substep(name)
            # while downloading: every stage shows, flavours pending
            parsed = status.parse_run(str(record))
            assert [stage['level'] for stage in parsed['steps']] == [
                'Preamble', 'Extraction', 'Post-extraction']
            preamble = _stage_of(parsed, 'Preamble')
            assert preamble['status'] == 'running'
            assert _names(preamble['children']) == progress.PREAMBLE_STEPS
            assert [c['status'] for c in preamble['children']] == [
                'complete', 'complete', 'running', 'pending']
            extraction = _stage_of(parsed, 'Extraction')
            assert extraction['status'] == 'pending'
            assert extraction['children'] == []
            # the preamble planned the flavour steps
            progress.start_substep(progress.PREAMBLE_STEPS[3])
            progress.set_plans([dict(level='Extraction', flavour='SOSSISSE',
                                     plan=PROGRESS_PLAN)])
        with progress.stage('Extraction', 'SOSSISSE'):
            parsed = status.parse_run(str(record))
            extraction = _stage_of(parsed, 'Extraction')
            assert extraction['status'] == 'running'
            assert _names(extraction['children']) == ['Load data', 'Fit']
            assert _stage_of(parsed, 'Preamble')['status'] == 'complete'
    finally:
        progress.end_run('complete')
    parsed = status.parse_run(str(record))
    assert parsed['status'] == 'complete'
    # the Preamble is not a flavour (Status tab filter)
    assert parsed['flavours'] == ['SORBET', 'SOSSISSE']


def test_plans_do_not_replace_a_started_stage(tmp_path, monkeypatch):
    """Late plans never replace the steps of a stage that started."""
    from pogos.core import progress
    from pogos.gui import status
    record = tmp_path / 'run.jsonl'
    monkeypatch.setenv(progress.ENV_FILE, str(record))
    progress.start_run(None, 'my.yaml', 'PROJ', 'MODE', PROGRESS_STAGES, [])
    try:
        with progress.stage('Extraction', 'SOSSISSE'):
            progress.start_substep('Something else')
            progress.set_plans([dict(level='Extraction', flavour='SOSSISSE',
                                     plan=PROGRESS_PLAN)])
            parsed = status.parse_run(str(record))
            assert _names(_stage_of(parsed, 'Extraction')['children']) == [
                'Something else']
    finally:
        progress.end_run('complete')


def test_failed_preamble_marks_flavours_not_run(tmp_path, monkeypatch):
    """A failing preamble (e.g. a download) fails the run visibly."""
    from pogos.core import progress
    from pogos.gui import status
    record = tmp_path / 'run.jsonl'
    monkeypatch.setenv(progress.ENV_FILE, str(record))
    steps = [progress.PREAMBLE_STAGE] + PROGRESS_STAGES
    try:
        with progress.run(None, 'my.yaml', 'PROJ', 'MODE', steps,
                          [progress.preamble_plan()]):
            with progress.stage(*progress.PREAMBLE_STAGE):
                progress.start_substep(progress.PREAMBLE_STEPS[2])
                raise ValueError('download failed')
    except ValueError:
        pass
    parsed = status.parse_run(str(record))
    assert parsed['status'] == 'failed'
    preamble = _stage_of(parsed, 'Preamble')
    assert preamble['status'] == 'failed'
    assert 'download failed' in preamble['error']
    assert _stage_of(parsed, 'Extraction')['status'] == 'not run'

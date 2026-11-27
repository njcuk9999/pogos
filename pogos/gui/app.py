#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The POGOS browser gui (pogos_gui)

A POGOS specific application on top of the generic aperocore.gui
framework. The page has one "POGOS path" (GLOBAL.DATA_PATH) at the top -
the whole page is locked until it is set - and these tabs:

    Info       what each tab does
    Setup      pogos_setup from a form (path, project, instrument / mode,
               reduction steps, demo, data download)
    Edit       load any yaml (from {path}/yamls or anywhere on disk), edit
               it as a form or as raw text, review the diff and save;
               create a new project from it (pogos_edit)
    Run        pogos_run on this machine (single process) or as a Slurm
               batch script; edit the batch templates
    Actions    pogos_config (check / fix with a diff of the changes),
               pogos_reset (preview + typed RESET confirmation) and a side
               by side diff of any two files
    Processes  every process started from the gui (logs, stop)
    Plots      the plot images of every project (tree + gallery)
    Files      project organiser / file browser (view FITS headers,
               images and tables, delete files and projects)

Every action runs the real POGOS recipe (interactive prompts are answered
in the browser console) so the gui never duplicates POGOS logic.

Created on 2026-11-26

@author: cook
"""
import json
import os
import re
import shlex
import subprocess
import sys
import threading
import time
from typing import Any, Dict, List, Optional

from aperocore.gui import files as gui_files
from aperocore.gui import procs as gui_procs
from aperocore.gui import slurm as gui_slurm
from aperocore.gui import webapp

from pogos.core import base as pogos_base
from pogos.gui import commands
from pogos.gui import layout
from pogos.gui import probe
from pogos.gui import status as run_status

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'pogos.gui.app.py'
__version__ = pogos_base.__version__
# the directory with the pogos gui page / assets
STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')
# the page template and the info markdown
TEMPLATE_PATH = os.path.join(STATIC_DIR, 'pogos_gui.html')
INFO_PATH = os.path.join(STATIC_DIR, 'pogos_info.md')
# environment variable for the supervised worker port
WORKER_ENV = 'POGOS_GUI_WORKER_PORT'
# the default port of the pogos gui
DEFAULT_PORT = 8097
# the activity log / console channels (one per page)
CHANNELS = ['setup', 'edit', 'run', 'actions', 'processes', 'files',
            'main']
# default batch template values for pogos_run jobs
POGOS_BATCH_DEFAULTS = dict(gui_slurm.BATCH_DEFAULTS, job_name='pogos_run',
                            time='24:00:00', cpus_per_task=8, mem='64G')
# seconds a probe may run
PROBE_TIMEOUT = 300
# the matplotlib backend that streams figures to the Plots tab (run jobs)
STREAM_BACKEND = 'module://aperocore.gui.mpl_stream'
STREAM_ENV = 'APEROCORE_PLOT_STREAM_DIR'
# directory (inside the gui state directory) of streamed figures
STREAM_DIR = 'plot_stream'
# valid stream folder names
STREAM_RE = re.compile(r'^[\w.+-]+$')


# =============================================================================
# Define classes
# =============================================================================
class PogosGuiApp(webapp.GuiApp):
    """
    The POGOS gui application (see module doc string)
    """
    name = 'POGOS'
    template_path = TEMPLATE_PATH
    app_static_dir = STATIC_DIR
    # the icon in the top right corner (and the browser tab)
    icon_name = 'pogos_icon.ico'
    worker_env = WORKER_ENV
    channels = CHANNELS
    batch_defaults = POGOS_BATCH_DEFAULTS

    def __init__(self, path: Optional[str] = None) -> None:
        """
        Initialise the POGOS gui

        :param path: str or None, the initial POGOS path (--path)

        :return: None
        """
        # the POGOS path (None until set from the command line or browser)
        self.path: Optional[str] = None
        # cache of demo probes: (mode, steps) -> result
        self.demo_cache: Dict[str, Any] = dict()
        self.demo_lock = threading.Lock()
        # cache of the constant descriptions (tool tips) - loaded once
        self.param_info: Optional[Dict[str, Any]] = None
        self.param_lock = threading.Lock()
        # the algorithm steps of every reduction step (docs page, cached)
        self.algorithm_info: Optional[Dict[str, Any]] = None
        self.algorithm_lock = threading.Lock()
        super().__init__()
        if path:
            result = self.set_path(path, create=False)
            if not result['success']:
                self.state.add_message(result['message'])

    # -------------------------------------------------------------------------
    # framework overrides
    # -------------------------------------------------------------------------
    def state_dir(self) -> Optional[str]:
        """
        Get the gui state directory ({path}/pogos_gui)

        :return: str or None, None until the POGOS path is set
        """
        if self.path is None:
            return None
        return layout.state_dir(self.path)

    def file_roots(self) -> List[str]:
        """
        Get the directories the gui may read / delete in: the POGOS path
        (plus the data paths of its yaml files if they differ)

        :return: list of str, the roots
        """
        if self.path is None:
            return []
        roots = [self.path]
        for ypath in layout.list_yaml_files(self.path):
            data_path = layout.yaml_summary(ypath).get('data_path')
            if data_path and os.path.isdir(str(data_path)):
                real = os.path.realpath(str(data_path))
                if real not in roots:
                    roots.append(real)
        return roots

    def artifact_roots(self) -> List[str]:
        """
        Get the directories of gui owned files (deleted with processes)

        :return: list of str, the batch script directory
        """
        if self.path is None:
            return []
        return [layout.batch_dir(self.path)]

    def page_tokens(self) -> Dict[str, str]:
        """
        Get the page template tokens

        :return: dict, token -> text
        """
        return dict(VERSION=__version__,
                    INFO=webapp.render_markdown_file(INFO_PATH),
                    PATH=json.dumps(self.path or ''))

    def state_extra(self) -> Dict[str, Any]:
        """
        Add the POGOS path to /api/state

        :return: dict, extra state values
        """
        return dict(path=self.path)

    def get_runtime_info(self) -> Dict[str, Any]:
        """
        Add the POGOS version to the runtime information

        :return: dict, the runtime information
        """
        info = super().get_runtime_info()
        info['pogos_version'] = __version__
        info['pogos_source'] = os.path.dirname(os.path.dirname(__file__))
        return info

    # -------------------------------------------------------------------------
    # routes
    # -------------------------------------------------------------------------
    def add_routes(self) -> None:
        """
        Register the POGOS routes

        :return: None
        """
        get, post = self.add_get, self.add_post
        get('/api/pogos/path', self.api_path)
        post('/api/pogos/path', self.api_set_path)
        post('/api/pogos/check_path', self.api_check_path)
        get('/api/pogos/yamls', self.api_yamls)
        get('/api/pogos/setup_choices',
            lambda req: webapp.Response.json(commands.setup_choices()))
        get('/api/pogos/demos', self.api_demos)
        get('/api/pogos/param_info', self.api_param_info)
        get('/api/pogos/algorithms', self.api_algorithms)
        post('/api/pogos/project_name', self.api_project_name)
        post('/api/pogos/preview', self.api_preview)
        post('/api/pogos/setup', self.api_setup)
        get('/api/pogos/yaml', self.api_yaml_load)
        post('/api/pogos/yaml_save', self.api_yaml_save)
        get('/api/pogos/backups', self.api_backups)
        post('/api/pogos/edit', self.api_edit)
        post('/api/pogos/run', self.api_run)
        post('/api/pogos/batch', self.api_batch)
        post('/api/pogos/config', self.api_config)
        post('/api/pogos/reset_preview', self.api_reset_preview)
        post('/api/pogos/reset', self.api_reset)
        get('/api/pogos/plots', self.api_plots)
        get('/api/pogos/projects', self.api_projects)
        get('/api/pogos/project_stats', self.api_project_stats)
        post('/api/pogos/project_delete', self.api_project_delete)
        get('/api/pogos/runs', self.api_runs)
        get('/api/pogos/run', self.api_run_detail)
        get('/api/pogos/run_log', self.api_run_log)
        post('/api/pogos/run_remove', self.api_run_remove)
        get('/api/pogos/streams', self.api_streams)
        get('/api/pogos/stream', self.api_stream)
        post('/api/pogos/stream_remove', self.api_stream_remove)

    # -------------------------------------------------------------------------
    # helpers
    # -------------------------------------------------------------------------
    def set_path(self, path: str, create: bool = False) -> Dict[str, Any]:
        """
        Set the POGOS path

        :param path: str, the POGOS path
        :param create: bool, create it (and yamls / projects) if needed

        :return: dict(success, message, info)
        """
        info = layout.check_pogos_path(path)
        if not info['is_dir']:
            if info['exists']:
                return dict(success=False, info=info,
                            message='not a directory: ' + info['path'])
            if not create:
                return dict(success=False, info=info, missing=True,
                            message='does not exist: ' + info['path'])
            layout.make_pogos_path(info['path'])
            info = layout.check_pogos_path(info['path'])
        if not info['writable']:
            return dict(success=False, info=info,
                        message='not writable: ' + info['path'])
        self.path = info['path']
        self.demo_cache.clear()
        message = 'POGOS path set to {0}'.format(self.path)
        self.state.add_message(message)
        self.state.bump()
        return dict(success=True, info=info, message=message)

    def _need_path(self) -> Optional[webapp.Response]:
        """
        Refuse requests while no POGOS path is set

        :return: Response or None, an error response if no path is set
        """
        if self.path is None:
            return webapp.Response.error('set the POGOS path first')
        return None

    def _start(self, channel: str, kind: str, built: Dict[str, Any],
               interactive: bool = True, stdin_text: Optional[str] = None,
               cwd: Optional[str] = None, on_done: Any = None
               ) -> webapp.Response:
        """
        Start a built command as the job of a channel

        :param channel: str, the console channel
        :param kind: str, the process kind
        :param built: dict(cmd, display, env), see commands
        :param interactive: bool, keep stdin open for browser answers
        :param stdin_text: str or None, answers written at start
        :param cwd: str or None, working directory (default POGOS path)
        :param on_done: callable or None, called with the return code

        :return: Response, json dict(started, message, display)
        """
        # gui jobs never open plot windows (run jobs stream them instead)
        env = dict(MPLBACKEND='Agg')
        env.update(built.get('env') or dict())
        jkwargs = dict(label=built['display'], cwd=cwd or self.path,
                       env=env, interactive=interactive,
                       stdin_text=stdin_text, on_done=on_done)
        result = self.jobs.start(channel, kind, built['cmd'], **jkwargs)
        result['display'] = built['display']
        return webapp.Response.json(result)

    def _run_probe(self, args: List[str]) -> Dict[str, Any]:
        """
        Run a pogos.gui.probe sub process and decode its result

        :param args: list of str, the probe arguments

        :return: dict, the probe result (dict(error) on failure)
        """
        cmd = [sys.executable, '-m', 'pogos.gui.probe'] + args
        env = dict(os.environ, PYTHONUNBUFFERED='1')
        try:
            output = subprocess.run(cmd, capture_output=True, text=True,
                                    timeout=PROBE_TIMEOUT, cwd=self.path,
                                    stdin=subprocess.DEVNULL, env=env)
        except (OSError, subprocess.SubprocessError) as error:
            return dict(error=str(error))
        for line in reversed(output.stdout.splitlines()):
            if line.startswith(probe.RESULT_PREFIX):
                return json.loads(line[len(probe.RESULT_PREFIX):])
        tail = (output.stdout + output.stderr).strip().splitlines()[-8:]
        return dict(error='probe failed:\n' + '\n'.join(tail))

    def stream_env(self, yaml_path: str, kind: str) -> Dict[str, str]:
        """
        Create the plot stream folder of a new run and the environment
        that makes its figures stream there (instead of plot windows)

        :param yaml_path: str, the yaml file being run
        :param kind: str, local or batch

        :return: dict, the environment variables
        """
        name = '{0}-{1}'.format(time.strftime('%Y%m%d-%H%M%S'),
                                gui_slurm.sanitize_template_name(
                                    os.path.splitext(
                                        os.path.basename(yaml_path))[0]))
        directory = os.path.join(layout.state_dir(self.path), STREAM_DIR,
                                 name)
        os.makedirs(directory, exist_ok=True)
        meta = dict(yaml=yaml_path, started=time.time(), kind=kind)
        with open(os.path.join(directory, 'meta.json'), 'w') as mfile:
            json.dump(meta, mfile)
        return {'MPLBACKEND': STREAM_BACKEND, STREAM_ENV: directory}

    def _stream_root(self) -> str:
        """
        Get the folder holding every plot stream

        :return: str, {path}/pogos_gui/plot_stream
        """
        return os.path.join(layout.state_dir(self.path), STREAM_DIR)

    # -------------------------------------------------------------------------
    # status routes
    # -------------------------------------------------------------------------
    def api_runs(self, request: webapp.Request) -> webapp.Response:
        """
        GET /api/pogos/runs: the recorded pogos_run runs (newest first)

        :param request: Request, the request

        :return: Response, json dict(runs)
        """
        _ = request
        missing = self._need_path()
        if missing is not None:
            return missing
        return webapp.Response.json(dict(runs=run_status.list_runs(
            self.path)))

    def api_run_detail(self, request: webapp.Request) -> webapp.Response:
        """
        GET /api/pogos/run?id=: one run with its stages and sub steps

        :param request: Request, the request

        :return: Response, json run (see status.parse_run)
        """
        missing = self._need_path()
        if missing is not None:
            return missing
        run = run_status.get_run(self.path, str(request.arg('id', '')))
        if run is None:
            return webapp.Response.error('unknown run', 404)
        return webapp.Response.json(run)

    def api_run_log(self, request: webapp.Request) -> webapp.Response:
        """
        GET /api/pogos/run_log?id=&offset=: (part of) the log of a run

        :param request: Request, the request

        :return: Response, json log response (see webapp.read_log)
        """
        run_id = str(request.arg('id', ''))
        out = webapp.empty_log('run:' + run_id)
        missing = self._need_path()
        if missing is not None:
            return missing
        run = run_status.get_run(self.path, run_id)
        if run is None:
            out['error'] = 'unknown run'
            return webapp.Response.json(out)
        growing = run['status'] in ['running', 'unknown']
        out['state'] = 'running' if growing else (
            'complete' if run['status'] == 'complete' else 'failed')
        if not run.get('log'):
            out['error'] = ('no log recorded for this run (it was started '
                            'outside the gui)')
            return webapp.Response.json(out)
        rargs = [out, str(run['log']), request.int_arg('offset', -1),
                 growing]
        return webapp.Response.json(webapp.read_log(*rargs))

    def api_run_remove(self, request: webapp.Request) -> webapp.Response:
        """
        POST /api/pogos/run_remove {ids}: remove finished run records

        :param request: Request, the request

        :return: Response, json dict(removed, message)
        """
        missing = self._need_path()
        if missing is not None:
            return missing
        ids = request.arg('ids', []) or []
        removed = run_status.remove_runs(self.path, [str(i) for i in ids])
        message = 'Removed {0} run record(s)'.format(removed)
        self.state.add_message(message, 'processes')
        return webapp.Response.json(dict(removed=removed, message=message))

    # -------------------------------------------------------------------------
    # plot stream routes
    # -------------------------------------------------------------------------
    def api_streams(self, request: webapp.Request) -> webapp.Response:
        """
        GET /api/pogos/streams: the plot streams (one per run, newest
        first)

        :param request: Request, the request

        :return: Response, json dict(streams)
        """
        _ = request
        missing = self._need_path()
        if missing is not None:
            return missing
        root = self._stream_root()
        streams = []
        if os.path.isdir(root):
            for name in sorted(os.listdir(root), reverse=True):
                folder = os.path.join(root, name)
                if not os.path.isdir(folder):
                    continue
                meta = dict()
                try:
                    with open(os.path.join(folder, 'meta.json')) as mfile:
                        meta = json.load(mfile)
                except (OSError, ValueError):
                    meta = dict()
                index = os.path.join(folder, 'index.jsonl')
                count, newest = 0, None
                if os.path.exists(index):
                    with open(index) as ifile:
                        count = sum(1 for _ in ifile)
                    newest = os.path.getmtime(index)
                streams.append(dict(name=name, count=count, newest=newest,
                                    yaml=meta.get('yaml'),
                                    started=meta.get('started'),
                                    kind=meta.get('kind')))
        return webapp.Response.json(dict(streams=streams))

    def api_stream(self, request: webapp.Request) -> webapp.Response:
        """
        GET /api/pogos/stream?name=&since=: the figures of one stream
        (since = the number of figures the browser already has)

        :param request: Request, the request

        :return: Response, json dict(name, figures, total)
        """
        missing = self._need_path()
        if missing is not None:
            return missing
        name = str(request.arg('name', ''))
        if not STREAM_RE.match(name):
            return webapp.Response.error('invalid stream')
        folder = os.path.join(self._stream_root(), name)
        index = os.path.join(folder, 'index.jsonl')
        figures = []
        if os.path.exists(index):
            with open(index) as ifile:
                for line in ifile:
                    try:
                        entry = json.loads(line)
                    except ValueError:
                        continue
                    if entry.get('file'):
                        entry['path'] = os.path.join(folder, entry['file'])
                    figures.append(entry)
        since = max(0, request.int_arg('since', 0))
        return webapp.Response.json(dict(name=name, total=len(figures),
                                         figures=figures[since:]))

    def api_stream_remove(self, request: webapp.Request
                          ) -> webapp.Response:
        """
        POST /api/pogos/stream_remove {names}: delete plot streams

        :param request: Request, the request

        :return: Response, json dict(success, message)
        """
        missing = self._need_path()
        if missing is not None:
            return missing
        names = [str(name) for name in request.arg('names', []) or []
                 if STREAM_RE.match(str(name))]
        paths = [os.path.join(self._stream_root(), name) for name in names]
        result = gui_files.delete_paths(paths, [self._stream_root()])
        return webapp.Response.json(result)

    # -------------------------------------------------------------------------
    # path routes
    # -------------------------------------------------------------------------
    def api_path(self, request: webapp.Request) -> webapp.Response:
        """
        GET /api/pogos/path: the current POGOS path and its layout

        :param request: Request, the request

        :return: Response, json dict(path, info)
        """
        _ = request
        info = None if self.path is None else (
            layout.check_pogos_path(self.path))
        return webapp.Response.json(dict(path=self.path, info=info))

    def api_check_path(self, request: webapp.Request) -> webapp.Response:
        """
        POST /api/pogos/check_path {path}: describe a candidate path

        :param request: Request, the request

        :return: Response, json (see layout.check_pogos_path)
        """
        path = str(request.arg('path', '') or '').strip()
        if path == '':
            return webapp.Response.error('enter a path')
        return webapp.Response.json(layout.check_pogos_path(path))

    def api_set_path(self, request: webapp.Request) -> webapp.Response:
        """
        POST /api/pogos/path {path, create}: set the POGOS path

        :param request: Request, the request

        :return: Response, json dict(success, message, info)
        """
        path = str(request.arg('path', '') or '').strip()
        if path == '':
            return webapp.Response.error('enter a path')
        create = bool(request.arg('create', False))
        return webapp.Response.json(self.set_path(path, create=create))

    # -------------------------------------------------------------------------
    # yaml routes
    # -------------------------------------------------------------------------
    def api_yamls(self, request: webapp.Request) -> webapp.Response:
        """
        GET /api/pogos/yamls: the yaml files in {path}/yamls (summaries)

        :param request: Request, the request

        :return: Response, json dict(yamls, directory)
        """
        _ = request
        missing = self._need_path()
        if missing is not None:
            return missing
        yamls = [layout.yaml_summary(ypath)
                 for ypath in layout.list_yaml_files(self.path)]
        return webapp.Response.json(dict(yamls=yamls,
                                         directory=layout.yaml_dir(
                                             self.path)))

    def api_yaml_load(self, request: webapp.Request) -> webapp.Response:
        """
        GET /api/pogos/yaml?path=: load a yaml file (any path on disk)

        :param request: Request, the request

        :return: Response, json dict(path, text, mtime, summary, error)
        """
        path = str(request.arg('path', '') or '')
        try:
            data = gui_files.read_text(path, None)
        except gui_files.FileAccessError as error:
            return webapp.Response.error(str(error))
        if data.get('error'):
            return webapp.Response.error(data['error'])
        data['summary'] = layout.yaml_summary(data['path'])
        return webapp.Response.json(data)

    def api_yaml_save(self, request: webapp.Request) -> webapp.Response:
        """
        POST /api/pogos/yaml_save {path, text, mtime, force}: save a yaml
        file (a backup of the previous version is kept); refuses if the
        file changed on disk since it was loaded (mtime) unless forced

        :param request: Request, the request

        :return: Response, json dict(success, message, path, backup, mtime)
        """
        missing = self._need_path()
        if missing is not None:
            return missing
        path = os.path.realpath(os.path.expanduser(
            str(request.arg('path', '') or '')))
        text = str(request.arg('text', ''))
        if not any(path.endswith(ext) for ext in layout.YAML_EXTS):
            return webapp.Response.error('only .yaml / .yml files can be '
                                         'saved here')
        loaded = request.arg('mtime', None)
        if (os.path.exists(path) and loaded is not None
                and not request.arg('force', False)):
            if abs(os.path.getmtime(path) - float(loaded)) > 1e-3:
                return webapp.Response.json(dict(
                    success=False, conflict=True,
                    message='the file changed on disk since it was loaded '
                            '- reload it (or save anyway)'))
        wkwargs = dict(backup_dir=layout.backup_dir(self.path))
        result = gui_files.write_text(path, text, None, **wkwargs)
        message = 'Saved {0}'.format(path)
        if result['backup']:
            message += ' (backup: {0})'.format(
                os.path.basename(result['backup']))
        self.state.add_message(message, 'edit')
        self.state.bump()
        return webapp.Response.json(dict(success=True, message=message,
                                         path=path, backup=result['backup'],
                                         mtime=os.path.getmtime(path)))

    def api_backups(self, request: webapp.Request) -> webapp.Response:
        """
        GET /api/pogos/backups?path=: the gui backups of a yaml file

        :param request: Request, the request

        :return: Response, json dict(backups)
        """
        missing = self._need_path()
        if missing is not None:
            return missing
        path = str(request.arg('path', '') or '')
        return webapp.Response.json(dict(
            backups=layout.list_backups(self.path, path)))

    # -------------------------------------------------------------------------
    # setup routes
    # -------------------------------------------------------------------------
    def api_demos(self, request: webapp.Request) -> webapp.Response:
        """
        GET /api/pogos/demos?instmode=&steps=: the demos pogos_setup offers
        (steps: json dict level -> list of step names)

        :param request: Request, the request

        :return: Response, json (see probe.probe_demos)
        """
        instmode = str(request.arg('instmode', '') or '')
        try:
            selection = json.loads(str(request.arg('steps', '{}') or '{}'))
            modes = commands.demo_modes(instmode, selection)
        except (ValueError, commands.CommandError) as error:
            return webapp.Response.error(str(error))
        key = '{0}|{1}'.format(instmode, ','.join(modes))
        with self.demo_lock:
            if key not in self.demo_cache:
                pargs = ['demos', '--instmode=' + instmode,
                         '--steps=' + ','.join(modes)]
                result = self._run_probe(pargs)
                if 'error' in result:
                    return webapp.Response.error(result['error'])
                self.demo_cache[key] = result
            return webapp.Response.json(self.demo_cache[key])

    def api_param_info(self, request: webapp.Request) -> webapp.Response:
        """
        GET /api/pogos/param_info: the description / type / default /
        options of every POGOS constant (the gui shows them as tool tips
        on setup fields and edit parameters) - probed once and cached

        :param request: Request, the request

        :return: Response, json dict(params=key -> info)
        """
        _ = request
        with self.param_lock:
            if self.param_info is None:
                result = self._run_probe(['params'])
                if 'error' in result:
                    return webapp.Response.error(result['error'])
                self.param_info = result
            return webapp.Response.json(self.param_info)

    def api_algorithms(self, request: webapp.Request) -> webapp.Response:
        """
        GET /api/pogos/algorithms: the algorithm steps (progress plans) of
        every reduction step for the docs page - probed once and cached
        (it loads the reduction backends: a few seconds)

        :param request: Request, the request

        :return: Response, json (see probe.probe_algorithms)
        """
        _ = request
        with self.algorithm_lock:
            if self.algorithm_info is None:
                result = self._run_probe(['algorithms'])
                if 'error' in result:
                    return webapp.Response.error(result['error'])
                self.algorithm_info = result
            return webapp.Response.json(self.algorithm_info)

    def api_project_name(self, request: webapp.Request) -> webapp.Response:
        """
        POST /api/pogos/project_name {name}: validate a project name

        :param request: Request, the request

        :return: Response, json dict(valid, error, exists)
        """
        name = str(request.arg('name', '') or '')
        error = commands.validate_project_name(name)
        exists = False
        if error is None and self.path is not None:
            exists = os.path.isdir(layout.project_dir(self.path, name))
        return webapp.Response.json(dict(valid=error is None, error=error,
                                         exists=exists))

    def _build(self, action: str, form: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build the command of one gui action from its form

        :param action: str, setup / edit / run / config_check / config_fix
                       / reset / batch
        :param form: dict, the form values

        :raises CommandError: for invalid forms

        :return: dict(cmd, display, env, ...) see commands
        """
        yaml_path = form.get('yaml')
        accept_old = bool(form.get('accept_old'))
        if action == 'setup':
            return commands.setup_command(self.path, form)
        if action == 'edit':
            return commands.edit_command(yaml_path)
        if action == 'run':
            return commands.run_command(yaml_path, accept_old)
        if action in ['config_check', 'config_fix']:
            return commands.config_command(yaml_path,
                                           action == 'config_check')
        if action == 'reset':
            return commands.reset_command(yaml_path, accept_old)
        if action == 'batch':
            built = commands.batch_lines(yaml_path, accept_old, self.path)
            built['display'] = 'sbatch <script running: {0}>'.format(
                built['display'])
            return built
        raise commands.CommandError('unknown action: ' + str(action))

    def api_preview(self, request: webapp.Request) -> webapp.Response:
        """
        POST /api/pogos/preview {action, form}: the cli equivalent of an
        action (or why the form is not valid yet - errors lists every
        problem)

        :param request: Request, the request

        :return: Response, json dict(display, error)
        """
        missing = self._need_path()
        if missing is not None:
            return missing
        form = request.arg('form', dict()) or dict()
        try:
            built = self._build(str(request.arg('action', '')), form)
        except commands.CommandError as error:
            # every problem on its own line (setup lists them all)
            errors = [line for line in str(error).splitlines() if line]
            return webapp.Response.json(dict(display='', error=str(error),
                                             errors=errors))
        return webapp.Response.json(dict(display=built['display'],
                                         error=None, errors=[],
                                         yaml_file=built.get('yaml_file')))

    def api_setup(self, request: webapp.Request) -> webapp.Response:
        """
        POST /api/pogos/setup {form}: run pogos_setup (interactive console)

        :param request: Request, the request

        :return: Response, json dict(started, message, display)
        """
        missing = self._need_path()
        if missing is not None:
            return missing
        try:
            built = self._build('setup', request.arg('form', dict()) or {})
        except commands.CommandError as error:
            return webapp.Response.error(str(error))
        os.makedirs(built['cwd'], exist_ok=True)
        return self._start('setup', 'setup', built, cwd=built['cwd'])

    def api_edit(self, request: webapp.Request) -> webapp.Response:
        """
        POST /api/pogos/edit {yaml}: new project from a yaml (pogos_edit)

        :param request: Request, the request

        :return: Response, json dict(started, message, display)
        """
        missing = self._need_path()
        if missing is not None:
            return missing
        try:
            built = self._build('edit', request.body)
        except commands.CommandError as error:
            return webapp.Response.error(str(error))
        return self._start('edit', 'edit', built)

    # -------------------------------------------------------------------------
    # run routes
    # -------------------------------------------------------------------------
    def api_run(self, request: webapp.Request) -> webapp.Response:
        """
        POST /api/pogos/run {yaml, accept_old}: run pogos_run on this
        machine (interactive console)

        :param request: Request, the request

        :return: Response, json dict(started, message, display)
        """
        missing = self._need_path()
        if missing is not None:
            return missing
        try:
            built = self._build('run', request.body)
        except commands.CommandError as error:
            return webapp.Response.error(str(error))
        # stream the figures of this run to the Plots tab
        built['env'] = dict(built['env'], **self.stream_env(
            str(request.arg('yaml')), 'local'))
        return self._start('run', 'run', built)

    def api_batch(self, request: webapp.Request) -> webapp.Response:
        """
        POST /api/pogos/batch {yaml, template, submit, accept_old, preview}:
        write a pogos_run sbatch script (and submit it) - preview only
        returns the script text

        :param request: Request, the request

        :return: Response, json dict(success, message, script, text,
                 job_id)
        """
        missing = self._need_path()
        if missing is not None:
            return missing
        out = self.batch_job(request.body if isinstance(request.body, dict)
                             else dict())
        if out.get('success') is False and 'script' not in out:
            return webapp.Response.error(out['message'])
        return webapp.Response.json(out)

    def batch_job(self, form: Dict[str, Any]) -> Dict[str, Any]:
        """
        Write a pogos_run sbatch script (and submit it) - used by the Run
        tab and by "Retry all failed"

        :param form: dict(yaml, template, submit, accept_old, preview)

        :return: dict(success, message, script, text, job_id)
        """
        try:
            built = self._build('batch', form)
        except commands.CommandError as error:
            return dict(success=False, message=str(error))
        template_name = gui_slurm.sanitize_template_name(
            form.get('template', None))
        template = gui_slurm.load_template(self.template_dir(),
                                           template_name,
                                           self.batch_defaults)
        # script / log names from the yaml name and a time stamp
        yaml_name = os.path.splitext(os.path.basename(
            str(form.get('yaml'))))[0]
        stem = '{0}-{1}'.format(gui_slurm.sanitize_template_name(yaml_name),
                                time.strftime('%Y%m%d-%H%M%S'))
        directory = layout.batch_dir(self.path)
        script = os.path.join(directory, stem + '.sbatch')
        log_path = os.path.join(directory, stem + '.out')
        job_name = '{0}_{1}'.format(template.get('job_name', 'pogos_run'),
                                    yaml_name)[:120]
        # the job records its log and streams its figures (Status / Plots)
        lines = list(built['lines'])
        if not form.get('preview', False):
            env = self.stream_env(str(form.get('yaml')), 'batch')
        else:
            env = {STREAM_ENV: '<stream folder>', 'MPLBACKEND':
                   STREAM_BACKEND}
        env['POGOS_RUN_LOG'] = log_path
        exports = ['export {0}={1}'.format(key, shlex.quote(value))
                   for key, value in env.items()]
        lines = exports + lines
        text = gui_slurm.build_script(template, job_name, lines, log_path)
        # preview only: show the script without writing it
        if form.get('preview', False):
            return dict(success=True, text=text, script=script,
                        preview=True)
        gui_slurm.write_script(script, text)
        out = dict(success=True, script=script, text=text, job_id=None,
                   log=log_path)
        if not form.get('submit', False):
            out['message'] = 'Batch script written: {0}'.format(script)
            self.state.add_message(out['message'], 'run')
            return out
        success, job_id, output = gui_slurm.submit(script)
        if not success:
            out.update(success=False, message='sbatch failed: ' + output)
            self.state.add_message(out['message'], 'run')
            return out
        # record the job (log viewer + stop from the processes page)
        rkwargs = dict(cmd='sbatch ' + script, owner='gui',
                       log_paths=[log_path], slurm_jobs=[job_id],
                       artifact_paths=[script])
        label = '{0} [slurm {1}]'.format(built['display'], job_id)
        proc_id = gui_procs.register(self.proc_dir(), 'batch', label,
                                     **rkwargs)
        # what "Retry all failed" needs to submit this run again
        gui_procs.update(self.proc_dir(), proc_id,
                         yaml=str(form.get('yaml')), template=template_name,
                         accept_old=bool(form.get('accept_old', False)))
        out.update(job_id=job_id,
                   message='Submitted Slurm job {0} ({1})'.format(
                       job_id, os.path.basename(script)))
        self.state.add_message(out['message'], 'run')
        self.state.bump()
        return out

    # -------------------------------------------------------------------------
    # action routes
    # -------------------------------------------------------------------------
    def api_config(self, request: webapp.Request) -> webapp.Response:
        """
        POST /api/pogos/config {yaml, fix}: run pogos_config - check only
        (nothing saved) or interactive fix (a snapshot of the yaml is taken
        first so the gui can show the changes)

        :param request: Request, the request

        :return: Response, json dict(started, message, display, snapshot)
        """
        missing = self._need_path()
        if missing is not None:
            return missing
        fix = bool(request.arg('fix', False))
        try:
            built = self._build('config_fix' if fix else 'config_check',
                                request.body)
        except commands.CommandError as error:
            return webapp.Response.error(str(error))
        snapshot = None
        if fix:
            snapshot = layout.snapshot_yaml(self.path,
                                            str(request.arg('yaml')))
        response = self._start('actions', 'config', built, interactive=fix)
        data = json.loads(response.body)
        data['snapshot'] = snapshot
        return webapp.Response.json(data)

    def api_reset_preview(self, request: webapp.Request
                          ) -> webapp.Response:
        """
        POST /api/pogos/reset_preview {yaml}: what pogos_reset would delete

        :param request: Request, the request

        :return: Response, json (see probe.probe_reset)
        """
        missing = self._need_path()
        if missing is not None:
            return missing
        yaml_path = str(request.arg('yaml', '') or '')
        if not os.path.isfile(yaml_path):
            return webapp.Response.error('choose a yaml file first')
        result = self._run_probe(['reset-preview',
                                  '--yamlfile=' + yaml_path])
        if 'error' in result:
            return webapp.Response.error(result['error'])
        return webapp.Response.json(result)

    def api_reset(self, request: webapp.Request) -> webapp.Response:
        """
        POST /api/pogos/reset {yaml, confirm, accept_old}: run pogos_reset
        (only after the user typed RESET - the gui answers its prompt)

        :param request: Request, the request

        :return: Response, json dict(started, message, display)
        """
        missing = self._need_path()
        if missing is not None:
            return missing
        if str(request.arg('confirm', '')) != 'RESET':
            return webapp.Response.error('type RESET to confirm')
        try:
            built = self._build('reset', request.body)
        except commands.CommandError as error:
            return webapp.Response.error(str(error))
        return self._start('actions', 'reset', built, interactive=False,
                           stdin_text='Y\n')

    # -------------------------------------------------------------------------
    # plots / projects routes
    # -------------------------------------------------------------------------
    def api_plots(self, request: webapp.Request) -> webapp.Response:
        """
        GET /api/pogos/plots: the plot images organised by project / module
        / directory

        :param request: Request, the request

        :return: Response, json (see layout.collect_plots)
        """
        _ = request
        missing = self._need_path()
        if missing is not None:
            return missing
        return webapp.Response.json(layout.collect_plots(self.path))

    def api_projects(self, request: webapp.Request) -> webapp.Response:
        """
        GET /api/pogos/projects: the projects (and yaml files) of the path

        :param request: Request, the request

        :return: Response, json dict(projects, yamls, path)
        """
        _ = request
        missing = self._need_path()
        if missing is not None:
            return missing
        yamls = [layout.yaml_summary(ypath)
                 for ypath in layout.list_yaml_files(self.path)]
        return webapp.Response.json(dict(
            projects=layout.list_projects(self.path), yamls=yamls,
            path=self.path, projects_dir=layout.project_dir(self.path),
            yaml_dir=layout.yaml_dir(self.path),
            state_dir=layout.state_dir(self.path)))

    def api_project_stats(self, request: webapp.Request) -> webapp.Response:
        """
        GET /api/pogos/project_stats?name=: file counts / sizes of one
        project

        :param request: Request, the request

        :return: Response, json (see layout.project_stats)
        """
        missing = self._need_path()
        if missing is not None:
            return missing
        name = os.path.basename(str(request.arg('name', '') or ''))
        return webapp.Response.json(layout.project_stats(self.path, name))

    def api_project_delete(self, request: webapp.Request
                           ) -> webapp.Response:
        """
        POST /api/pogos/project_delete {name, confirm, yamls}: delete a
        project directory (confirm must repeat the project name) and
        optionally the yaml files using it

        :param request: Request, the request

        :return: Response, json dict(success, message)
        """
        missing = self._need_path()
        if missing is not None:
            return missing
        name = str(request.arg('name', '') or '')
        if name in ['', '.', '..'] or os.sep in name:
            return webapp.Response.error('invalid project name')
        # the typed confirmation ignores case
        if str(request.arg('confirm', '')).strip().lower() != name.lower():
            return webapp.Response.error('type the project name to confirm')
        paths = [layout.project_dir(self.path, name)]
        # optionally also the yaml files that use this project
        if request.arg('yamls', False):
            for project in layout.list_projects(self.path):
                if project['name'] == name:
                    paths += project['yamls']
        result = gui_files.delete_paths(paths, [self.path])
        self.state.add_message('Project {0}: {1}'.format(name,
                                                          result['message']),
                               'files')
        self.state.bump()
        return webapp.Response.json(result)


# =============================================================================
# Define functions
# =============================================================================
def main(path: Optional[str] = None, host: str = webapp.DEFAULT_HOST,
         port: int = DEFAULT_PORT, headless: bool = False) -> None:
    """
    Start the POGOS gui (blocks until stopped)

    :param path: str or None, the initial POGOS path
    :param host: str, the host to listen on (default localhost only)
    :param port: int, the first port to try
    :param headless: bool, if True do not open a browser

    :return: None
    """
    skwargs = dict(host=host, port=port, headless=headless,
                   worker_env=WORKER_ENV, title='POGOS GUI')
    webapp.serve(lambda: PogosGuiApp(path), **skwargs)


# =============================================================================
# End of code
# =============================================================================

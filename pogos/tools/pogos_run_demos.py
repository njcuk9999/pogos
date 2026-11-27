#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
pogos_run_demos

Set up and run every POGOS demo (developer test of the whole pipeline)

Every demo is tried with every combination of its reduction steps that
pogos_setup can select (one step or skip per level, any subset on the
multiple choice levels) - e.g. SOSSISSE and SOSSISSE+SORBET.WLCA are two
separate tasks. Each task is:

    1. pogos_setup (non interactive, the demo id is the project and yaml
       name, online inputs are downloaded now - the shared download cache
       in {path}/downloads means each file is only fetched once)
    2. pogos_run of the yaml it created (plots off)

The setups run one at a time (so two setups never download the same file
at once); every finished setup goes straight into a pool of --cores
parallel pogos_run processes. A failing task never stops the others.

A task can only run if every selected step has input files: its main
input comes from the step of the level just before it (e.g. SOSSISSE ->
SORBET) or is defined by the demo (downloadable from MAST / the POGOS
server, or an existing absolute path). Tasks without them (e.g. SORBET on
its own when the demo gives no light curve) are flagged by --list, listed
in the summary as not run, and only tried with --all.

Every task is recorded in the pogos_gui process registry (kind "alldemo")
as "pending" first, so the Processes tab shows how many are left; a pending
task stopped there is skipped, a running one is stopped.

Output (in {path}/run_demos/{YYYYMMDD-HHMMSS}/):

    logs/{nn}_{demo id}.log   setup + run output of each task
    run_demos.log             this tool's own log
    summary.txt               timing / status table + the errors
    summary.json              the same as json

Usage:
    python -m pogos.tools.pogos_run_demos /path/to/pogos --cores=4
    python -m pogos.tools.pogos_run_demos /path/to/pogos --list
    python -m pogos.tools.pogos_run_demos /path/to/pogos --only=SOSS

Created on 2026-11-27

@author: cook
"""
import argparse
import concurrent.futures
import json
import os
import re
import shlex
import signal
import subprocess
import sys
import threading
import time
from typing import Any, Dict, List, Optional

from aperocore.gui import procs as gui_procs

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'pogos.tools.pogos_run_demos'
# the process registry kind of every task (and of this tool)
KIND = 'alldemo'
# directory (inside the POGOS path) holding every all-demos run
RUN_DIR = 'run_demos'
# local folders that would shadow the installed packages (see pogos_setup)
SHADOW_DIRS = ('aperocore', 'pogos', 'sossisse')
# environment variables of the gui job / plot stream that must not leak
#   into the task processes (they would write into the wrong log / stream)
DROP_ENV = ['APEROCORE_GUI_JOB_LOG', 'APEROCORE_PLOT_STREAM_DIR',
            'POGOS_PROGRESS_FILE', 'POGOS_RUN_LOG']
# the run progress (pogos.core.progress) log / status file variables
ENV_RUN_LOG = 'POGOS_RUN_LOG'
ENV_PROGRESS_FILE = 'POGOS_PROGRESS_FILE'
# download modes passed to pogos_setup
DOWNLOAD_MODES = ['now', 'run']
# ANSI colour codes (stripped from the error summaries)
ANSI_RE = re.compile(r'\x1b\[[0-9;]*[A-Za-z]')
# lines of a log that look like an error
ERROR_RE = re.compile(r'(error|exception|traceback|failed)', re.IGNORECASE)
# the most error lines kept per task
MAX_ERROR_LINES = 25
# prefix of the --list --json output line (other output may come first)
JSON_PREFIX = 'POGOS_RUN_DEMOS: '
# final task states
DONE_STATES = ['complete', 'failed', 'stopped', 'skipped']


# =============================================================================
# Define helper functions
# =============================================================================
def fmt_time(seconds: Optional[float]) -> str:
    """
    Format a duration

    :param seconds: float or None, the duration

    :return: str, e.g. 1h02m03s / 2m03s / 3.1s ('-' for None)
    """
    if seconds is None:
        return '-'
    seconds = float(seconds)
    if seconds < 60:
        return '{0:.1f}s'.format(seconds)
    minutes, sec = divmod(int(round(seconds)), 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return '{0}h{1:02d}m{2:02d}s'.format(hours, minutes, sec)
    return '{0}m{1:02d}s'.format(minutes, sec)


def safe_name(text: str) -> str:
    """
    Make a string safe as a file name

    :param text: str, the text

    :return: str, only letters, digits and ._+- kept
    """
    return re.sub(r'[^\w.+-]', '_', text)


class Logger:
    """Print messages to stdout and to the tool's log file (thread safe)"""

    def __init__(self, path: str):
        self.path = path
        # re-entrant: the stop signal handler logs from the main thread
        self.lock = threading.RLock()

    def __call__(self, message: str = '') -> None:
        line = '{0} | {1}'.format(time.strftime('%H:%M:%S'), message)
        with self.lock:
            print(line, flush=True)
            try:
                with open(self.path, 'a') as logfile:
                    logfile.write(line + '\n')
            except OSError:
                pass


# =============================================================================
# Define task functions
# =============================================================================
def _own_input_problem(demo: Any, key: str) -> Optional[str]:
    """
    Check that a demo defines a usable main input itself

    Usable = downloadable (source mast / pogos) or local files given as
    existing absolute paths (a bare local name would have to be put into
    the new project by hand).

    :param demo: PogoDemo, the demo (its step methods already run)
    :param key: str, the main input key (file_download.MAIN_INPUTS)

    :return: str or None, why the input is missing (None = usable)
    """
    const = demo.cdict.storage.get(key)
    if const is None:
        return 'not defined by the demo'
    value = const.value
    if value is None or value == '' or value == []:
        return 'not set by the demo'
    try:
        fileobj = const.parse(value)
    except Exception as error:
        return 'cannot be read ({0})'.format(error)
    if fileobj is None:
        return 'not set by the demo'
    if fileobj.source in ['mast', 'pogos']:
        return None
    files = fileobj.filelist
    if isinstance(files, str):
        files = [files]
    files = [str(name) for name in (files or [])]
    if files and all(os.path.isabs(name) and os.path.exists(name)
                     for name in files):
        return None
    return 'only local file(s) {0} with no download source'.format(
        ', '.join(files) if files else '(none)')


def input_problems(demo_class: Any, steps: List[str]) -> List[str]:
    """
    Check that every selected step of a demo has input files

    A step's main input (pogos.core.file_download.MAIN_INPUTS) comes either
    from the step of the level just before it (e.g. SOSSISSE -> SORBET,
    TSOVORE -> SOSSISSE) when that level is selected too, or from the demo
    itself (see _own_input_problem). With a gap (e.g. TSOVORE + SORBET, no
    extraction) POGOS treats the input as chained, but the earlier step
    does not make it - so that is a problem as well.

    :param demo_class: type, the demo class
    :param steps: list of str, the selected "level:step" names

    :return: list of str, the problems (empty = the task can run)
    """
    from pogos.core import definitions
    from pogos.core import file_download
    # a fresh demo filled with the selected steps (as pogos_setup does)
    demo = demo_class()
    for step in steps:
        for method in demo.redsteps[step]:
            method()
    levels = [level.name for level in definitions.REDUCTION_LEVELS]
    selected = dict()
    for step in steps:
        level, name = step.split(':', 1)
        selected.setdefault(level, []).append(name)
    problems = []
    for step in steps:
        level, name = step.split(':', 1)
        index = levels.index(level)
        earlier = [lvl for lvl in levels[:index] if lvl in selected]
        for key, step_name in file_download.MAIN_INPUTS.items():
            if step_name != name:
                continue
            # fed by the step just before it
            if index > 0 and levels[index - 1] in selected:
                continue
            if earlier:
                problems.append(
                    '{0}: {1} would come from {2} which does not make it '
                    '(no {3} step selected)'.format(
                        name, key, '+'.join(selected[earlier[-1]]),
                        levels[index - 1]))
                continue
            problem = _own_input_problem(demo, key)
            if problem is not None:
                problems.append('{0}: {1} {2}'.format(name, key, problem))
    return problems


def find_tasks() -> List[Dict[str, Any]]:
    """
    Find every demo and every reduction step combination it supports

    :return: list of dict(name, instmode, demo, steps, selection, title,
             runnable, problems) - name is the demo id (unique per step
             combination), runnable is False when a step has no input
             files (problems says why, see input_problems)
    """
    # deferred imports (the POGOS constants are slow to load)
    from pogos import demos as demo_module
    from pogos.core import startup
    from pogos.gui import probe
    tasks: List[Dict[str, Any]] = []
    for instmode in demo_module.DEMOS:
        if not demo_module.DEMOS[instmode]:
            continue
        for steps in probe.step_selections(instmode):
            demo_dict = startup.get_demo_choices(demo_module, steps)
            for key, demo in demo_dict.get(instmode, dict()).items():
                # only demos that support every selected step (a demo
                #   offered for one of them only is another combination)
                if not all(step in demo.redsteps for step in steps):
                    continue
                selection: Dict[str, List[str]] = dict()
                for step in steps:
                    level, name = step.split(':', 1)
                    selection.setdefault(level, []).append(name)
                problems = input_problems(type(demo), steps)
                tasks.append(dict(name=str(demo.get_prop('id')),
                                  instmode=instmode, demo=key,
                                  steps=list(steps), selection=selection,
                                  title=str(demo.get_prop('title')),
                                  runnable=len(problems) == 0,
                                  problems=problems))
    # one task per demo id (never run the same project twice)
    seen = set()
    unique = []
    for task in tasks:
        if task['name'] in seen:
            continue
        seen.add(task['name'])
        unique.append(task)
    return unique


def filter_tasks(tasks: List[Dict[str, Any]], only: List[str],
                 exclude: List[str]) -> List[Dict[str, Any]]:
    """
    Keep the tasks matching --only (any) and not matching --exclude (any)

    Matches are case insensitive substrings of the demo id, the instrument
    mode, the demo key or the steps.

    :param tasks: list of dict, see find_tasks
    :param only: list of str, keep tasks matching any of these
    :param exclude: list of str, drop tasks matching any of these

    :return: list of dict, the kept tasks
    """
    def text(task: Dict[str, Any]) -> str:
        return ' '.join([task['name'], task['instmode'], task['demo']] +
                        task['steps']).lower()

    out = []
    for task in tasks:
        tstr = text(task)
        if only and not any(item.lower() in tstr for item in only):
            continue
        if any(item.lower() in tstr for item in exclude):
            continue
        out.append(task)
    return out


def error_lines(log_path: str, offset: int) -> List[str]:
    """
    The error lines of one stage of a task log

    :param log_path: str, the task log
    :param offset: int, where the stage starts in the log (bytes)

    :return: list of str, the last traceback (or error lines, or the last
             lines of the stage)
    """
    try:
        with open(log_path, 'rb') as logfile:
            logfile.seek(offset)
            text = logfile.read().decode('utf-8', errors='replace')
    except OSError:
        return []
    lines = [ANSI_RE.sub('', line).rstrip() for line in text.splitlines()]
    lines = [line for line in lines if line.strip()]
    # the last traceback
    for index in range(len(lines) - 1, -1, -1):
        if lines[index].startswith('Traceback'):
            return lines[index:][-MAX_ERROR_LINES:]
    # otherwise lines that look like errors (plus the last lines)
    errors = [line for line in lines if ERROR_RE.search(line)]
    tail = lines[-8:]
    out = errors[-(MAX_ERROR_LINES - len(tail)):] + \
        [line for line in tail if line not in errors]
    return out[-MAX_ERROR_LINES:]


# =============================================================================
# Define the runner
# =============================================================================
class DemoRunner:
    """Set up and run every task (setups serial, runs in parallel)"""

    def __init__(self, args: argparse.Namespace, tasks: List[Dict[str, Any]],
                 out_dir: str, log: Logger,
                 not_run: Optional[List[Dict[str, Any]]] = None):
        self.args = args
        # tasks left out because a step has no input files
        self.not_run = list(not_run or [])
        self.path = args.path
        self.tasks = tasks
        self.out_dir = out_dir
        self.log = log
        self.registry = args.registry
        # re-entrant: the stop signal handler runs in the main thread
        self.lock = threading.RLock()
        self.stopping = threading.Event()
        # running child processes (pid -> Popen)
        self.children: Dict[int, subprocess.Popen] = dict()
        self.started = time.time()
        self.finished: Optional[float] = None
        self.manager_id: Optional[str] = None
        # the environment of every task process
        env = dict(os.environ)
        for key in DROP_ENV:
            env.pop(key, None)
        env.update(PYTHONUNBUFFERED='1', MPLBACKEND='Agg')
        self.env = env

    # -------------------------------------------------------------------------
    # registry
    # -------------------------------------------------------------------------
    def _record(self, task: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """The registry record of a task (None without a registry)"""
        if self.registry is None or task.get('proc_id') is None:
            return None
        return gui_procs.load(self.registry, task['proc_id'])

    def _cancelled(self, task: Dict[str, Any]) -> bool:
        """True if the task was stopped (Processes tab) or we are stopping"""
        if self.stopping.is_set():
            return True
        record = self._record(task)
        return bool(record and record.get('stopped'))

    def _update(self, task: Dict[str, Any], **fields: Any) -> None:
        """Update the registry record of a task (never if it was stopped)"""
        if self.registry is None or task.get('proc_id') is None:
            return
        record = self._record(task)
        if record is not None and record.get('finished'):
            return
        gui_procs.update(self.registry, task['proc_id'], **fields)

    def _finish(self, task: Dict[str, Any], returncode: int,
                stopped: bool = False) -> None:
        """Mark the registry record of a task finished"""
        if self.registry is None or task.get('proc_id') is None:
            return
        record = self._record(task)
        if record is not None and record.get('finished'):
            return
        gui_procs.finish(self.registry, task['proc_id'], returncode,
                         stopped=stopped)

    def register(self) -> None:
        """Record this tool and every task (pending) in the registry"""
        if self.registry is None:
            return
        os.makedirs(self.registry, exist_ok=True)
        ntask = len(self.tasks)
        owner = 'gui' if self.args.gui else 'cli'
        if not self.args.gui:
            # (a gui started run is already recorded by the gui)
            label = 'all demos: {0} tasks in {1} ({2} cores)'.format(
                ntask, self.path, self.args.cores)
            self.manager_id = gui_procs.register(
                self.registry, KIND, label, cmd=shlex.join(sys.argv),
                pid=os.getpid(), owner=owner,
                log_paths=[self.log.path])
        for task in self.tasks:
            label = '[{0}/{1}] {2}'.format(task['index'], ntask,
                                          task['name'])
            task['proc_id'] = gui_procs.register(
                self.registry, KIND, label, cmd='pogos_setup + pogos_run',
                owner=owner, log_paths=[task['log']],
                queued_by=os.getpid())

    # -------------------------------------------------------------------------
    # commands
    # -------------------------------------------------------------------------
    def setup_cmd(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """The pogos_setup command of a task (see pogos.gui.commands)"""
        from pogos.gui import commands
        form = dict(data_path=self.path, project_name=task['name'],
                    yaml_name=task['name'], instmode=task['instmode'],
                    steps=task['selection'], demo=task['demo'])
        if self.args.demolocal:
            form.update(download='local', demolocal=self.args.demolocal,
                        demosymlink=self.args.demosymlink)
        else:
            form['download'] = self.args.download
        return commands.setup_command(self.path, form)

    def run_cmd(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """The pogos_run command of a task"""
        from pogos.gui import commands
        return commands.run_command(task['yaml'], show_plots=False)

    def reset_cmd(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """The pogos_reset command of a task"""
        from pogos.gui import commands
        return commands.reset_command(task['yaml'])

    # -------------------------------------------------------------------------
    # running
    # -------------------------------------------------------------------------
    def _execute(self, task: Dict[str, Any], stage: str,
                 built: Dict[str, Any], env: Optional[Dict[str, str]] = None,
                 stdin_text: Optional[str] = None) -> int:
        """
        Run one stage of a task (output appended to the task log)

        :return: int, the exit code (-15 if stopped, -9 on a timeout)
        """
        full_env = dict(self.env)
        full_env.update(built.get('env') or dict())
        full_env.update(env or dict())
        with open(task['log'], 'a') as logfile:
            logfile.write('\n{0}\n{1} [{2}] {3}\n{0}\n'.format(
                '=' * 78, time.strftime('%Y-%m-%d %H:%M:%S'), stage,
                built['display']))
            logfile.flush()
            task[stage + '_offset'] = logfile.tell()
            stdin = subprocess.PIPE if stdin_text else subprocess.DEVNULL
            # own session: a stop of this task (Processes tab) only stops it
            process = subprocess.Popen(built['cmd'], stdout=logfile,
                                       stderr=subprocess.STDOUT, stdin=stdin,
                                       cwd=self.path, env=full_env,
                                       start_new_session=True)
            with self.lock:
                self.children[process.pid] = process
            if self.stopping.is_set():
                self._kill(process)
            self._update(task, pid=process.pid,
                         cmd=built['display'])
            if stdin_text and process.stdin is not None:
                try:
                    process.stdin.write(stdin_text.encode())
                    process.stdin.close()
                except (BrokenPipeError, OSError):
                    pass
            timeout = self.args.timeout if self.args.timeout > 0 else None
            try:
                returncode = process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                self._kill(process)
                returncode = process.wait()
                task['timeout'] = True
                logfile.write('\n[pogos_run_demos] {0} timed out after '
                              '{1}\n'.format(stage, fmt_time(timeout)))
            with self.lock:
                self.children.pop(process.pid, None)
        return returncode

    @staticmethod
    def _signal(process: subprocess.Popen, sig: int) -> None:
        """Signal the process group of a child (never raises)"""
        try:
            os.killpg(process.pid, sig)
        except (ProcessLookupError, PermissionError, OSError):
            pass

    def _kill(self, process: subprocess.Popen) -> None:
        """Stop a child process group (TERM, then KILL after 10 s)"""
        self._signal(process, signal.SIGTERM)
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self._signal(process, signal.SIGKILL)

    def _fail(self, task: Dict[str, Any], stage: str,
              returncode: int) -> None:
        """Record a failed (or stopped) stage"""
        record = self._record(task)
        stopped = bool(record and record.get('stopped')) or \
            self.stopping.is_set()
        if stopped:
            task['status'] = 'stopped'
            task['error'] = ['stopped during {0}'.format(stage)]
        else:
            task['status'] = 'failed'
            task['failed_stage'] = stage
            reason = 'timed out' if task.get('timeout') else \
                'exit code {0}'.format(returncode)
            task['error'] = ['{0} failed ({1})'.format(stage, reason)] + \
                error_lines(task['log'], task.get(stage + '_offset', 0))
        task['returncode'] = returncode
        self._finish(task, returncode if returncode != 0 else 1,
                     stopped=stopped)

    def do_setup(self, task: Dict[str, Any]) -> bool:
        """Set up one task (main thread). True if its run can start"""
        if self._cancelled(task):
            task['status'] = 'skipped'
            task['error'] = ['stopped before it started']
            self._finish(task, -15, stopped=True)
            return False
        task['status'] = 'setup'
        start = time.time()
        task['start'] = start
        try:
            built = self.setup_cmd(task)
            task['yaml'] = built['yaml_file']
            existed = os.path.exists(task['yaml'])
            self.log('[{0}/{1}] setup   {2}'.format(
                task['index'], len(self.tasks), task['name']))
            returncode = self._execute(task, 'setup', built)
            if returncode == 0 and self.args.reset and existed:
                # earlier outputs of this demo (pogos_reset asks Y/N)
                returncode = self._execute(task, 'reset',
                                           self.reset_cmd(task),
                                           stdin_text='Y\n')
                if returncode != 0:
                    task['setup_time'] = time.time() - start
                    self._fail(task, 'reset', returncode)
                    return False
        except Exception as error:
            task['setup_time'] = time.time() - start
            task['status'] = 'failed'
            task['failed_stage'] = 'setup'
            task['error'] = ['setup could not start: {0}'.format(error)]
            self._finish(task, 1)
            return False
        task['setup_time'] = time.time() - start
        if returncode != 0:
            self._fail(task, 'setup', returncode)
            return False
        if not os.path.isfile(task['yaml']):
            task['status'] = 'failed'
            task['failed_stage'] = 'setup'
            task['error'] = ['setup did not create {0}'.format(task['yaml'])]
            self._finish(task, 1)
            return False
        if self.args.setup_only:
            task['status'] = 'complete'
            self._finish(task, 0)
            return False
        # waiting for a run slot (pending again in the Processes tab)
        task['status'] = 'queued'
        task['queued'] = time.time()
        self._update(task, pid=None)
        return True

    def do_run(self, task: Dict[str, Any]) -> None:
        """Run one task (worker thread)"""
        try:
            if self._cancelled(task):
                task['status'] = 'stopped'
                task['error'] = ['stopped before its run started']
                self._finish(task, -15, stopped=True)
                return
            task['status'] = 'running'
            start = time.time()
            task['wait_time'] = start - task.get('queued', start)
            self.log('[{0}/{1}] run     {2}'.format(
                task['index'], len(self.tasks), task['name']))
            env = {ENV_RUN_LOG: task['log']}
            if self.args.status_dir:
                # the run shows in the Run tab of the gui that started us
                os.makedirs(self.args.status_dir, exist_ok=True)
                env[ENV_PROGRESS_FILE] = os.path.join(
                    self.args.status_dir, '{0}-{1}.jsonl'.format(
                        time.strftime('%Y%m%d-%H%M%S'),
                        safe_name(task['name'])))
            returncode = self._execute(task, 'run', self.run_cmd(task),
                                       env=env)
            task['run_time'] = time.time() - start
            if returncode != 0:
                self._fail(task, 'run', returncode)
            else:
                task['status'] = 'complete'
                task['returncode'] = 0
                self._finish(task, 0)
        except Exception as error:
            task['status'] = 'failed'
            task['failed_stage'] = 'run'
            task['error'] = ['run could not start: {0}'.format(error)]
            self._finish(task, 1)
        finally:
            self.task_done(task)

    def task_done(self, task: Dict[str, Any]) -> None:
        """Report one finished task and update the summary"""
        task['end'] = time.time()
        task['total_time'] = task['end'] - task.get('start', task['end'])
        ndone = len([t for t in self.tasks if t.get('status') in
                     DONE_STATES])
        self.log('[{0}/{1}] {2:8s} {3} ({4}) - {5}/{1} done'.format(
            task['index'], len(self.tasks), task['status'], task['name'],
            fmt_time(task['total_time']), ndone))
        self.write_summary()

    def stop(self, signum: int = signal.SIGTERM, frame: Any = None) -> None:
        """Stop everything (signal handler): kill the running tasks"""
        _ = frame
        if self.stopping.is_set():
            return
        self.stopping.set()
        self.log('Stopping (signal {0}) - killing the running tasks'.format(
            signum))
        with self.lock:
            children = list(self.children.values())
        for process in children:
            self._signal(process, signal.SIGTERM)

        # anything still alive after 5 s is killed
        def _force() -> None:
            time.sleep(5)
            for child in children:
                if child.poll() is None:
                    self._signal(child, signal.SIGKILL)

        threading.Thread(target=_force, daemon=True).start()

    def run(self) -> int:
        """Set up and run every task. Returns the number of failures"""
        self.register()
        cores = max(1, int(self.args.cores))
        self.log('{0} tasks, {1} parallel run(s), output: {2}'.format(
            len(self.tasks), cores, self.out_dir))
        if self.not_run:
            self.log('{0} demo(s) not run - no input files: {1}'.format(
                len(self.not_run), ', '.join(task['name']
                                             for task in self.not_run)))
        self.write_summary()
        futures = []
        with concurrent.futures.ThreadPoolExecutor(
                max_workers=cores, thread_name_prefix='demo') as pool:
            for task in self.tasks:
                if self.do_setup(task):
                    futures.append(pool.submit(self.do_run, task))
                else:
                    self.task_done(task)
            concurrent.futures.wait(futures)
        self.finished = time.time()
        self.write_summary()
        nfail = len([t for t in self.tasks if t['status'] != 'complete'])
        if self.manager_id is not None:
            gui_procs.finish(self.registry, self.manager_id,
                             0 if nfail == 0 else 1,
                             stopped=self.stopping.is_set())
        return nfail

    # -------------------------------------------------------------------------
    # summary
    # -------------------------------------------------------------------------
    def summary_text(self) -> str:
        """The summary table and the errors (text)"""
        counts: Dict[str, int] = dict()
        for task in self.tasks:
            counts[task['status']] = counts.get(task['status'], 0) + 1
        end = self.finished or time.time()
        lines = ['POGOS all demos run ({0})'.format(
                     'finished' if self.finished else 'in progress'),
                 '=' * 78,
                 'path:      {0}'.format(self.path),
                 'output:    {0}'.format(self.out_dir),
                 'started:   {0}'.format(time.strftime(
                     '%Y-%m-%d %H:%M:%S', time.localtime(self.started))),
                 'wall time: {0}'.format(fmt_time(end - self.started)),
                 'cores:     {0}'.format(self.args.cores),
                 'tasks:     {0} ({1})'.format(len(self.tasks), ', '.join(
                     '{0} {1}'.format(value, key)
                     for key, value in sorted(counts.items()))),
                 'not run:   {0} (no input files, see below)'.format(
                     len(self.not_run)),
                 '']
        header = '{0:>3s}  {1:9s} {2:>9s} {3:>9s} {4:>9s} {5:>9s}  {6}'
        lines.append(header.format('#', 'status', 'setup', 'wait', 'run',
                                   'total', 'demo (instrument mode: steps)'))
        lines.append('-' * 110)
        for task in self.tasks:
            status = task['status']
            if status == 'failed':
                status = 'FAILED'
            lines.append(header.format(
                str(task['index']), status,
                fmt_time(task.get('setup_time')),
                fmt_time(task.get('wait_time')),
                fmt_time(task.get('run_time')),
                fmt_time(task.get('total_time')),
                '{0}  ({1}: {2})'.format(task['name'], task['instmode'],
                                         ' + '.join(task['steps']))))
        # tasks with a step without input files (tried with --all)
        flagged = [task for task in self.tasks if not task['runnable']]
        if flagged:
            lines += ['', 'Tried with --all although a step has no input '
                          'files: ' + ', '.join(str(task['index'])
                                                 for task in flagged)]
        if self.not_run:
            lines += ['', 'Not run - a step has no input files (--all '
                          'tries them)', '=' * 78]
            for task in self.not_run:
                lines.append('{0}  ({1}: {2})'.format(
                    task['name'], task['instmode'],
                    ' + '.join(task['steps'])))
                lines += ['    - ' + problem
                          for problem in task['problems']]
        problems = [task for task in self.tasks if task.get('error')]
        if problems:
            lines += ['', 'Errors', '=' * 78]
            for task in problems:
                lines.append('[{0}] {1} - {2}'.format(
                    task['index'], task['name'], task['status']))
                lines.append('    log: {0}'.format(task['log']))
                lines += ['    | ' + line for line in task['error']]
                lines.append('')
        return '\n'.join(lines) + '\n'

    def write_summary(self) -> None:
        """Write summary.txt and summary.json (after every task)"""
        with self.lock:
            text = self.summary_text()
            keys = ['index', 'name', 'instmode', 'demo', 'steps', 'title',
                    'status', 'failed_stage', 'returncode', 'yaml', 'log',
                    'setup_time', 'wait_time', 'run_time', 'total_time',
                    'start', 'end', 'error', 'runnable', 'problems']
            data = dict(path=self.path, out_dir=self.out_dir,
                        cores=self.args.cores, started=self.started,
                        finished=self.finished,
                        not_run=[{key: task.get(key) for key in
                                  ['name', 'instmode', 'demo', 'steps',
                                   'problems']}
                                 for task in self.not_run],
                        tasks=[{key: task.get(key) for key in keys}
                               for task in self.tasks])
            try:
                for name, content in [('summary.txt', text),
                                      ('summary.json',
                                       json.dumps(data, indent=1))]:
                    path = os.path.join(self.out_dir, name)
                    with open(path + '.tmp', 'w') as sfile:
                        sfile.write(content)
                    os.replace(path + '.tmp', path)
            except OSError as error:
                print('Could not write the summary: {0}'.format(error))


# =============================================================================
# Define main functions
# =============================================================================
def get_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse the command line"""
    parser = argparse.ArgumentParser(
        prog='pogos_run_demos',
        description='Set up and run every POGOS demo (every reduction step '
                    'combination of every demo) and write a summary of the '
                    'timings and errors.')
    parser.add_argument('path', help='The POGOS path (GLOBAL.DATA_PATH) the '
                                     'demos are set up in (created if '
                                     'needed)')
    parser.add_argument('--cores', type=int, default=1,
                        help='Number of demos run in parallel (default 1). '
                             'Setups always run one at a time.')
    parser.add_argument('--only', action='append', default=[],
                        help='Only tasks matching this text (demo id, '
                             'instrument mode, demo key or step - case '
                             'insensitive, repeatable)')
    parser.add_argument('--exclude', action='append', default=[],
                        help='Skip tasks matching this text (repeatable)')
    parser.add_argument('--list', action='store_true',
                        help='List the tasks and exit')
    parser.add_argument('--all', action='store_true',
                        help='Also try the demos where a step has no input '
                             'files (by default they are only listed)')
    parser.add_argument('--json', action='store_true',
                        help='With --list: print the tasks as one json line '
                             '(prefixed with {0})'.format(JSON_PREFIX))
    parser.add_argument('--setup_only', action='store_true',
                        help='Only set up (and download the data of) every '
                             'demo, do not run them')
    parser.add_argument('--download', choices=DOWNLOAD_MODES, default='now',
                        help='Download the online inputs during setup '
                             '(now, default) or at the start of each run')
    parser.add_argument('--demolocal', default=None,
                        help='Use this local mirror of the demo data '
                             'instead of downloading')
    parser.add_argument('--demosymlink', action='store_true',
                        help='With --demolocal: symlink instead of copying')
    parser.add_argument('--reset', action='store_true',
                        help='Reset (pogos_reset) the outputs of demos that '
                             'were already set up in this path before '
                             'running them again')
    parser.add_argument('--timeout', type=float, default=0,
                        help='Stop a setup / run after this many seconds '
                             '(0 = never, default)')
    parser.add_argument('--registry', default=None,
                        help='Process registry directory (default: '
                             '{path}/pogos_gui/gui_processes, so pogos_gui '
                             'on this path shows the tasks)')
    parser.add_argument('--no_registry', action='store_true',
                        help='Do not record the tasks in a process registry')
    parser.add_argument('--status_dir', default=None,
                        help='Directory for the run progress files '
                             '(default: {path}/pogos_gui/run_status)')
    parser.add_argument('--gui', action='store_true',
                        help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    args.path = os.path.realpath(os.path.expanduser(args.path))
    if args.demolocal:
        args.demolocal = os.path.realpath(os.path.expanduser(args.demolocal))
    if args.no_registry:
        args.registry = None
    elif args.registry is None:
        args.registry = os.path.join(args.path, 'pogos_gui',
                                     gui_procs.PROC_DIR_NAME)
    return args


def main(argv: Optional[List[str]] = None) -> int:
    """
    Set up and run every demo

    :param argv: list of str or None, the arguments (None: sys.argv)

    :return: int, 0 if every task completed, 1 otherwise (2 on bad input)
    """
    args = get_args(argv)
    if args.cores < 1:
        print('--cores must be at least 1')
        return 2
    # setup runs in the POGOS path - it refuses package folders there
    shadow = [name for name in SHADOW_DIRS
              if os.path.exists(os.path.join(args.path, name))]
    if shadow:
        print('The POGOS path contains {0} (would shadow the installed '
              'packages) - choose another path'.format('/'.join(shadow)))
        return 2
    if args.demolocal and not os.path.isdir(args.demolocal):
        print('--demolocal does not exist: {0}'.format(args.demolocal))
        return 2
    print('Finding the demos ...', flush=True)
    tasks = filter_tasks(find_tasks(), args.only, args.exclude)
    # tasks without input files are not run (unless --all)
    not_run = [] if args.all else [task for task in tasks
                                   if not task['runnable']]
    to_run = [task for task in tasks if task not in not_run]
    nbad = len([task for task in tasks if not task['runnable']])
    if args.list and args.json:
        keys = ['name', 'instmode', 'demo', 'steps', 'runnable', 'problems']
        print(JSON_PREFIX + json.dumps(dict(
            path=args.path, include_all=args.all, nrun=len(to_run),
            tasks=[{key: task[key] for key in keys} for task in tasks])))
        return 0
    if args.list:
        number = 0
        for task in tasks:
            if task in to_run:
                number += 1
                prefix = '{0:3d}'.format(number)
            else:
                prefix = '  -'
            flag = '' if task['runnable'] else '  [CANNOT RUN: no inputs]'
            print('{0}  {1}{2}\n     {3} [{4}]: {5}'.format(
                prefix, task['name'], flag, task['instmode'], task['demo'],
                ' + '.join(task['steps'])))
            for problem in task['problems']:
                print('       - {0}'.format(problem))
        print('{0} tasks to run ({1} found, {2} without input files{3})'
              .format(len(to_run), len(tasks), nbad,
                      ' - included by --all' if args.all and nbad else
                      ' - not run, use --all to try them' if nbad else ''))
        return 0
    tasks = to_run
    if len(tasks) == 0:
        print('No runnable demos match the selection')
        return 2
    # the output directory of this run
    os.makedirs(args.path, exist_ok=True)
    stamp = time.strftime('%Y%m%d-%H%M%S')
    out_dir = os.path.join(args.path, RUN_DIR, stamp)
    count = 1
    while os.path.exists(out_dir):
        count += 1
        out_dir = os.path.join(args.path, RUN_DIR,
                               '{0}-{1}'.format(stamp, count))
    os.makedirs(os.path.join(out_dir, 'logs'))
    log = Logger(os.path.join(out_dir, 'run_demos.log'))
    for index, task in enumerate(tasks, start=1):
        task.update(index=index, status='pending', error=None,
                    log=os.path.join(out_dir, 'logs', '{0:02d}_{1}.log'.format(
                        index, safe_name(task['name']))))
    runner = DemoRunner(args, tasks, out_dir, log, not_run=not_run)
    signal.signal(signal.SIGTERM, runner.stop)
    signal.signal(signal.SIGINT, runner.stop)
    log('pogos_run_demos: {0}'.format(shlex.join(sys.argv)))
    nfail = runner.run()
    print()
    print(runner.summary_text())
    log('Summary: {0}'.format(os.path.join(out_dir, 'summary.txt')))
    return 0 if nfail == 0 else 1


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    sys.exit(main())

# =============================================================================
# End of code
# =============================================================================

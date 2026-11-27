#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
POGOS run progress events (for the pogos_gui Status tab)

pogos_run records where it is in the reduction as small json events
(one json object per line) in a run status file:

    {GLOBAL.DATA_PATH}/pogos_gui/run_status/{run id}.jsonl

(or the file named by the POGOS_PROGRESS_FILE environment variable). The
events form a tree: the run -> stages (Pre-extraction / Extraction /
Post-extraction, one per flavour e.g. SOSSISSE) -> nested steps marked by
the code with aperocore.progress (e.g. "Linear reconstruction" ->
"Detector" -> "nrs1" -> "Flat field") -> progress through a step (done /
total and a detail text). The run_start event holds the plan of every
stage (the steps it will go through) so they show as pending first. For
runs the gui logs (POGOS_RUN_LOG / APEROCORE_GUI_JOB_LOG set) a short
marker line ("POGOS PROGRESS | ...") is also printed so the gui can jump
to every step in the log; runs from a terminal do not print them.

Recording progress must never break a reduction: every write is guarded
and the functions do nothing when no run was started (e.g. when a module
is run on its own). Only the standard library and aperocore are used.

Created on 2026-11-26

@author: cook
"""
import contextlib
import json
import os
import signal
import socket
import sys
import threading
import time
from typing import Any, Dict, Iterator, List, Optional

from aperocore import progress as gprogress

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'pogos.core.progress.py'
# directories (inside GLOBAL.DATA_PATH) holding the run status files
STATE_DIR = 'pogos_gui'
STATUS_DIR = 'run_status'
# environment variables: an explicit status file / the log of this run
#    (set by the gui and its batch scripts)
ENV_FILE = 'POGOS_PROGRESS_FILE'
ENV_LOG = 'POGOS_RUN_LOG'
# the log path every gui job gets (aperocore.gui.jobs.JOB_LOG_ENV)
ENV_GUI_LOG = 'APEROCORE_GUI_JOB_LOG'
# set when the run accepts a yaml from an older POGOS version (retries
#   of the run need it again)
ENV_ACCEPT_OLD = 'POGOS_ACCEPT_OLD_YAML'
# the folder figures are streamed to (aperocore.gui.mpl_stream)
ENV_PLOT_STREAM = 'APEROCORE_PLOT_STREAM_DIR'
# the marker printed in the log for every step event
MARKER = 'POGOS PROGRESS'
# the current run (None = progress recording is off)
_RUN: Optional['RunProgress'] = None
_LOCK = threading.Lock()


# =============================================================================
# Define classes
# =============================================================================
class RunProgress:
    """
    The progress file of one pogos_run (append only json lines)
    """

    def __init__(self, path: str) -> None:
        """
        Initialise the progress file

        :param path: str, the json lines file (directory created)

        :return: None
        """
        self.path = path
        # the open stage (level / flavour added to every step event)
        self.stage: Optional[Dict[str, str]] = None
        os.makedirs(os.path.dirname(path) or '.', exist_ok=True)

    def write(self, event: str, **fields: Any) -> None:
        """
        Append one event (never raises)

        :param event: str, the event name
        :param fields: the event values

        :return: None
        """
        record = dict(event=event, time=time.time(), **fields)
        try:
            with open(self.path, 'a') as pfile:
                pfile.write(json.dumps(record, default=str) + '\n')
        except OSError:
            return

    def write_step(self, event: str, **fields: Any) -> None:
        """
        Write a step event of aperocore.progress (tagged with the open
        stage; a log marker line is printed when a step starts)

        :param event: str, the event name (step_start, step_end, ...)
        :param fields: the event values (path, ...)

        :return: None
        """
        if self.stage is None:
            return
        self.write(event, **dict(fields, **self.stage))
        if event == 'step_start':
            _marker(self.stage['level'], self.stage['flavour'],
                    ' / '.join(fields.get('path') or []))


# =============================================================================
# Define functions
# =============================================================================
def status_dir(data_path: str) -> str:
    """
    Get the run status directory of a POGOS data path

    :param data_path: str, GLOBAL.DATA_PATH

    :return: str, {data_path}/pogos_gui/run_status
    """
    return os.path.join(str(data_path), STATE_DIR, STATUS_DIR)


def _marker(*parts: str) -> None:
    """
    Print a progress marker line in the log - only for runs whose log the
    gui keeps (its Log buttons jump to these lines); a run from a terminal
    stays quiet

    :param parts: str, the marker fields

    :return: None
    """
    if not (os.environ.get(ENV_LOG) or os.environ.get(ENV_GUI_LOG)):
        return
    try:
        print('{0} | {1}'.format(MARKER, ' | '.join(parts)), flush=True)
    except (OSError, ValueError):
        return


def start_run(data_path: Optional[str], yaml_file: str, project: Any,
              instmode: Any, steps: List[List[str]],
              plans: Optional[List[Dict[str, Any]]] = None
              ) -> Optional[str]:
    """
    Start recording the progress of a run

    :param data_path: str or None, GLOBAL.DATA_PATH (where the status file
                      goes unless POGOS_PROGRESS_FILE is set)
    :param yaml_file: str, the yaml file being run
    :param project: str, GLOBAL.PROJECT_NAME
    :param instmode: str, GLOBAL.INSTRUMENTMODE
    :param steps: list of [level, flavour], the planned stages in order
    :param plans: list of dict(level, flavour, plan) or None - the steps
                  each stage will go through (aperocore.progress plan
                  nodes; shown as pending until they start)

    :return: str or None, the status file (None if recording is off)
    """
    global _RUN
    path = os.environ.get(ENV_FILE)
    if not path:
        if data_path is None:
            return None
        stamp = time.strftime('%Y%m%d-%H%M%S')
        name = '{0}-{1}-{2}.jsonl'.format(
            stamp, os.path.splitext(os.path.basename(yaml_file))[0],
            os.getpid())
        path = os.path.join(status_dir(data_path), name)
    try:
        run = RunProgress(path)
    except OSError:
        return None
    with _LOCK:
        _RUN = run
    run.write('run_start', yaml=os.path.realpath(yaml_file),
              project=project, instmode=instmode, steps=steps,
              pid=os.getpid(), host=socket.gethostname(),
              log=os.environ.get(ENV_LOG) or os.environ.get(ENV_GUI_LOG),
              plot_stream=os.environ.get(ENV_PLOT_STREAM),
              slurm_job=os.environ.get('SLURM_JOB_ID'),
              argv=' '.join(sys.argv), plans=plans or [],
              accept_old=bool(os.environ.get(ENV_ACCEPT_OLD)))
    # record the steps the code marks (aperocore.progress)
    gprogress.set_writer(run.write_step)
    _marker('run', 'start', os.path.basename(yaml_file))
    return path


def end_run(status: str, error: Optional[str] = None) -> None:
    """
    Finish the run record

    :param status: str, complete or failed
    :param error: str or None, the error message of a failed run

    :return: None
    """
    global _RUN
    with _LOCK:
        run = _RUN
        _RUN = None
    if run is None:
        return
    gprogress.set_writer(None)
    run.write('run_end', status=status, error=error)
    _marker('run', status)


@contextlib.contextmanager
def run(data_path: Optional[str], yaml_file: str, project: Any,
        instmode: Any, steps: List[List[str]],
        plans: Optional[List[Dict[str, Any]]] = None
        ) -> Iterator[Optional[str]]:
    """
    Record a whole run (complete, or failed if anything raises)

    :param data_path: str or None, GLOBAL.DATA_PATH
    :param yaml_file: str, the yaml file being run
    :param project: str, GLOBAL.PROJECT_NAME
    :param instmode: str, GLOBAL.INSTRUMENTMODE
    :param steps: list of [level, flavour], the planned stages
    :param plans: list of dict(level, flavour, plan) or None (see
                  start_run)

    :return: the status file path (context manager)
    """
    path = start_run(data_path, yaml_file, project, instmode, steps,
                     plans)
    # a stop (SIGTERM, e.g. from the gui or scancel) ends the run cleanly
    #   so it is recorded as stopped instead of lost
    previous = None
    if threading.current_thread() is threading.main_thread():
        previous = signal.signal(signal.SIGTERM, _stop_handler)
    try:
        yield path
    except BaseException as error:
        end_run('failed', '{0}: {1}'.format(type(error).__name__, error))
        raise
    finally:
        if previous is not None:
            signal.signal(signal.SIGTERM, previous)
    end_run('complete')


def _stop_handler(signum: int, frame: Any) -> None:
    """
    Turn SIGTERM into an exception (so the run records being stopped)

    :param signum: int, the signal number
    :param frame: the current stack frame

    :raises SystemExit: always

    :return: None
    """
    _ = frame
    raise SystemExit('stopped (signal {0})'.format(signum))


@contextlib.contextmanager
def stage(level: str, flavour: str) -> Iterator[None]:
    """
    Record one stage (a flavour of a reduction level, e.g. Extraction /
    SOSSISSE) - the steps marked inside it (aperocore.progress) are
    recorded with this level / flavour

    :param level: str, the reduction level (Pre-extraction, ...)
    :param flavour: str, the flavour (e.g. SOSSISSE)

    :return: None (context manager)
    """
    current = _RUN
    if current is None:
        yield
        return
    current.stage = dict(level=level, flavour=flavour)
    # forget any step left open by a previous stage
    gprogress.set_writer(current.write_step)
    current.write('stage_start', level=level, flavour=flavour)
    _marker(level, flavour, 'start')
    try:
        yield
    except BaseException as error:
        # close the open steps first (they failed with the stage)
        gprogress.close_all('failed')
        current.write('stage_end', level=level, flavour=flavour,
                      status='failed',
                      error='{0}: {1}'.format(type(error).__name__, error))
        current.stage = None
        raise
    gprogress.close_all('complete')
    current.write('stage_end', level=level, flavour=flavour,
                  status='complete')
    _marker(level, flavour, 'complete')
    current.stage = None


def start_substep(name: str, total: Optional[int] = None,
                  items: Optional[List[Any]] = None) -> None:
    """
    Start a sequential sub step of the current stage (ends the previous
    one) - see aperocore.progress.mark

    :param name: str, the sub step name (e.g. "Linear reconstruction")
    :param total: int or None, the number of items it will process
    :param items: list or None, loop items (one child step each - open
                  them with aperocore.progress.step / start)

    :return: None
    """
    gprogress.mark(name, total, items)


def substep(name: str, total: Optional[int] = None) -> Any:
    """
    Record one sub step of the current stage - see aperocore.progress.step

    :param name: str, the sub step name
    :param total: int or None, the number of items it will process

    :return: context manager
    """
    return gprogress.step(name, total)


def advance(done: Optional[int] = None, total: Optional[int] = None,
            detail: Optional[str] = None, force: bool = False) -> None:
    """
    Record progress through the current step (rate limited) - see
    aperocore.progress.advance

    :param done: int or None, the number of items done
    :param total: int or None, the number of items
    :param detail: str or None, what is being processed now
    :param force: bool, write even if the last event is very recent

    :return: None
    """
    gprogress.advance(done, total, detail, force)


def active() -> bool:
    """
    Whether a run is being recorded

    :return: bool, True during a recorded run
    """
    return _RUN is not None


# =============================================================================
# End of code
# =============================================================================

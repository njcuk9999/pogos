#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Run status for the POGOS gui (Status tab)

Reads the run progress files pogos_run writes (see pogos.core.progress):

    {path}/pogos_gui/run_status/{run id}.jsonl

and turns them into

    - a list of runs (started, yaml, project, instrument mode, status,
      where the run is now)
    - the steps of one run: one row per stage (level + flavour) and a
      tree of the steps inside it (planned steps are pending until they
      run, loops get one row per item) with start, duration, status and
      progress

A run without a run_end event is "running" while its process is alive
(checked on this machine, or through squeue for Slurm jobs), otherwise
"lost" (killed / crashed without a record).

Only the standard library is used.

Created on 2026-11-26

@author: cook
"""
import json
import os
import re
import socket
import time
from typing import Any, Dict, List, Optional

from aperocore.gui import procs as gui_procs

from pogos.core import progress

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'pogos.gui.status.py'
# valid run ids (file names without .jsonl) - refuses paths
RUN_ID_RE = re.compile(r'^[\w.+-]+$')
# the level of the Preamble stage (pogos.core.progress.PREAMBLE_STAGE -
#   not imported: the gui does not load the POGOS runtime)
PREAMBLE_LEVEL = 'Preamble'
# parsed runs: path -> ((size, mtime), events)
_CACHE: Dict[str, Any] = dict()


# =============================================================================
# Define step tree functions
# =============================================================================
def _new_node(name: str, path: List[str], planned: bool,
              loop: bool = False, desc: Optional[str] = None,
              template: Optional[List[Dict[str, Any]]] = None,
              func: Optional[str] = None) -> Dict[str, Any]:
    """
    Create one row of the step tree

    :param name: str, the step name
    :param path: list of str, the step names from the stage
    :param planned: bool, True if it comes from the plan
    :param loop: bool, True for a loop template (children per item)
    :param desc: str or None, a description from the plan
    :param template: list of dict or None, the plan nodes repeated for
                     every item of a loop
    :param func: str or None, the dotted path of the function doing the
                 work (from the plan)

    :return: dict, the tree node (src_file / src_line: where the code
             marked the step, once it started)
    """
    return dict(name=name, path=path, planned=planned, loop=loop,
                desc=desc, func=func, src_file=None, src_line=None,
                template=template or [], status='pending',
                started=None, ended=None, error=None, done=None,
                total=None, detail=None, children=[])


def _plan_nodes(plan: List[Dict[str, Any]], prefix: List[str]
                ) -> List[Dict[str, Any]]:
    """
    Turn plan nodes (aperocore.progress.node) into pending tree nodes

    :param plan: list of dict, the plan nodes
    :param prefix: list of str, the path of their parent

    :return: list of dict, the tree nodes
    """
    out = []
    for entry in plan or []:
        if not isinstance(entry, dict) or not entry.get('name'):
            continue
        name = str(entry['name'])
        path = prefix + [name]
        children = entry.get('children') or []
        if entry.get('loop'):
            # a loop: its children are repeated for every item
            out.append(_new_node(name, path, True, loop=True,
                                 desc=entry.get('desc'), template=children,
                                 func=entry.get('func')))
        else:
            tree_node = _new_node(name, path, True, desc=entry.get('desc'),
                                  func=entry.get('func'))
            tree_node['children'] = _plan_nodes(children, path)
            out.append(tree_node)
    return out


def _child(parent: Dict[str, Any], name: str) -> Dict[str, Any]:
    """
    Get (or add) the child of a tree node with this name - a new child of
    a loop gets the loop's template steps (pending)

    :param parent: dict, the tree node (or the stage, which has children)
    :param name: str, the child name

    :return: dict, the child node
    """
    for child in parent['children']:
        if child['name'] == name:
            return child
    path = list(parent.get('path') or []) + [name]
    if parent.get('loop'):
        child = _new_node(name, path, True)
        child['item'] = True
        child['children'] = _plan_nodes(parent['template'], path)
    else:
        child = _new_node(name, path, False)
    parent['children'].append(child)
    return child


def _find(stage: Dict[str, Any], path: List[str]) -> Dict[str, Any]:
    """
    Get (or add) the tree node of a step path

    :param stage: dict, the stage entry
    :param path: list of str, the step names from the stage

    :return: dict, the tree node
    """
    current = stage
    for name in path:
        current = _child(current, str(name))
    return current


def _add_items(tree_node: Dict[str, Any], items: Optional[List[Any]]
               ) -> None:
    """
    Add the announced items of a loop (pending, in order)

    :param tree_node: dict, the loop node
    :param items: list or None, the item names

    :return: None
    """
    for item in items or []:
        _child(tree_node, str(item))


def _finish_tree(children: List[Dict[str, Any]], parent_status: str,
                 run_status: str) -> None:
    """
    Settle the statuses of a finished part of the tree: steps still
    running in a run that ended did not finish; pending steps of a step
    that finished (or failed) were not run

    :param children: list of dict, the tree nodes
    :param parent_status: str, the status of their parent
    :param run_status: str, the run status

    :return: None
    """
    for child in children:
        if child['status'] == 'running' and run_status != 'running':
            child['status'] = ('unknown' if run_status == 'unknown'
                               else 'failed')
        if child['status'] == 'pending' and parent_status in [
                'complete', 'failed', 'not run', 'stopped', 'skipped']:
            child['status'] = 'not run'
        _finish_tree(child['children'], child['status'], run_status)


def _count(children: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Count the leaf steps (rows without children) of a tree by status and
    set every parent's done / total from its children (if not reported)

    :param children: list of dict, the tree nodes

    :return: dict(done, total) of the leaf steps
    """
    done, total = 0, 0
    for child in children:
        if child['children']:
            sub = _count(child['children'])
            child['leaves_done'] = sub['done']
            child['leaves_total'] = sub['total']
            done += sub['done']
            total += sub['total']
        elif child['status'] != 'not run':
            total += 1
            # a skipped step is finished too
            done += 1 if child['status'] in ['complete', 'skipped'] else 0
    return dict(done=done, total=total)


def _current(children: List[Dict[str, Any]]) -> List[str]:
    """
    Get the path of the innermost running step

    :param children: list of dict, the tree nodes

    :return: list of str, the path ([] if nothing runs)
    """
    for child in reversed(children):
        if child['status'] == 'running':
            return [child['name']] + _current(child['children'])
    return []


# =============================================================================
# Define functions
# =============================================================================
def run_dir(path: str) -> str:
    """
    Get the run status directory of a POGOS path

    :param path: str, the POGOS path (GLOBAL.DATA_PATH)

    :return: str, the directory
    """
    return progress.status_dir(path)


def run_path(path: str, run_id: str) -> Optional[str]:
    """
    Get the status file of one run (None for an invalid id)

    :param path: str, the POGOS path
    :param run_id: str, the run id

    :return: str or None, the status file
    """
    if not RUN_ID_RE.match(str(run_id)):
        return None
    return os.path.join(run_dir(path), '{0}.jsonl'.format(run_id))


def _events(file_path: str) -> List[Dict[str, Any]]:
    """
    Read the events of one status file (cached by size / mtime)

    :param file_path: str, the status file

    :return: list of dict, the events in order
    """
    try:
        info = os.stat(file_path)
    except OSError:
        return []
    stamp = (info.st_size, info.st_mtime)
    cached = _CACHE.get(file_path)
    if cached is not None and cached[0] == stamp:
        return cached[1]
    events = []
    with open(file_path, 'r', errors='replace') as sfile:
        for line in sfile:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except ValueError:
                # a line still being written
                continue
    _CACHE[file_path] = (stamp, events)
    return events


def _alive(start: Dict[str, Any]) -> Optional[bool]:
    """
    Whether the process of an unfinished run is still alive

    :param start: dict, the run_start event

    :return: True / False, or None if it cannot be checked from here
    """
    job = start.get('slurm_job')
    if job:
        states = gui_procs.slurm_states([str(job)])
        if states is not None:
            return str(job) in states
    if start.get('host') != socket.gethostname():
        return None
    return gui_procs.pid_alive(start.get('pid'))


def parse_run(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Build the full state of one run from its events

    :param file_path: str, the status file

    :return: dict or None - the run summary (id, yaml, project, instmode,
             started, ended, status, error, log, current) and the steps
             (list of stage dicts with level, flavour, status, started,
             ended, error, leaves_done, leaves_total and children = the
             step tree: dict(name, path, status, started, ended, error,
             done, total, detail, planned, loop, item, children))
    """
    events = _events(file_path)
    if len(events) == 0 or events[0].get('event') != 'run_start':
        return None
    start = events[0]
    run_id = os.path.basename(file_path)[:-len('.jsonl')]
    out: Dict[str, Any] = dict(id=run_id, yaml=start.get('yaml'),
                               yaml_name=os.path.basename(
                                   str(start.get('yaml'))),
                               project=start.get('project'),
                               instmode=start.get('instmode'),
                               host=start.get('host'), pid=start.get('pid'),
                               slurm_job=start.get('slurm_job'),
                               log=start.get('log'),
                               plot_stream=start.get('plot_stream'),
                               accept_old=bool(start.get('accept_old')),
                               started=start.get('time'), ended=None,
                               status='running', error=None, current=None,
                               updated=events[-1].get('time'))
    # the planned stages (pending until they start) with their planned
    #   steps (aperocore.progress plans written by pogos_run)
    plans = {'{0}|{1}'.format(entry.get('level'), entry.get('flavour')):
             entry.get('plan') or [] for entry in start.get('plans') or []
             if isinstance(entry, dict)}
    stages: List[Dict[str, Any]] = []
    index: Dict[str, Dict[str, Any]] = dict()

    def _stage(level: Any, flavour: Any) -> Dict[str, Any]:
        """
        Get (or add) a stage entry

        :param level: str, the reduction level
        :param flavour: str, the flavour

        :return: dict, the stage entry
        """
        key = '{0}|{1}'.format(level, flavour)
        if key not in index:
            index[key] = dict(level=level, flavour=flavour,
                              status='pending', started=None, ended=None,
                              error=None, path=[],
                              children=_plan_nodes(plans.get(key) or [],
                                                   []))
            stages.append(index[key])
        return index[key]

    for level, flavour in start.get('steps') or []:
        _stage(level, flavour)

    for event in events[1:]:
        kind = str(event.get('event'))
        when = event.get('time')
        if kind == 'run_end':
            out.update(status=event.get('status', 'complete'), ended=when,
                       error=event.get('error'))
            # a stop by the user (SIGTERM) is not a failure
            if 'stopped (signal' in str(out['error'] or ''):
                out['status'] = 'stopped'
            continue
        # plans recorded once known (after the preamble planned them):
        #   fill in the steps of stages that have not started yet
        if kind == 'plans':
            for entry in event.get('plans') or []:
                if not isinstance(entry, dict):
                    continue
                stage = _stage(entry.get('level'), entry.get('flavour'))
                if stage['status'] == 'pending':
                    stage['children'] = _plan_nodes(entry.get('plan') or [],
                                                    [])
            continue
        stage = _stage(event.get('level'), event.get('flavour'))
        if kind == 'stage_start':
            stage.update(status='running', started=when)
            continue
        if kind == 'stage_end':
            stage.update(status=event.get('status', 'complete'), ended=when,
                         error=event.get('error'))
            continue
        # the step path (records before nested steps had flat sub steps)
        if kind.startswith('substep_') or kind == 'advance':
            path = [str(event.get('name'))]
            kind = dict(substep_start='step_start', substep_end='step_end',
                        advance='step_advance').get(kind, kind)
        else:
            path = [str(name) for name in event.get('path') or []]
        if not path:
            continue
        tree_node = _find(stage, path)
        if kind == 'step_start':
            # a step may run again (e.g. a retry): start it afresh
            tree_node.update(status='running', started=when, ended=None,
                             error=None, done=None,
                             total=event.get('total'), detail=None,
                             src_file=event.get('src_file'),
                             src_line=event.get('src_line'))
            _add_items(tree_node, event.get('items'))
        elif kind == 'step_items':
            _add_items(tree_node, event.get('items'))
        elif kind == 'step_end':
            tree_node.update(status=event.get('status', 'complete'),
                             ended=when, error=event.get('error'))
            if tree_node['total'] and tree_node['status'] == 'complete':
                tree_node['done'] = tree_node['total']
        elif kind == 'step_advance':
            tree_node.update(done=event.get('done'),
                             total=event.get('total') or tree_node['total'],
                             detail=event.get('detail'))
    # an unfinished run whose process died was lost
    if out['ended'] is None:
        alive = _alive(start)
        if alive is False:
            out['status'] = 'lost'
        elif alive is None:
            out['status'] = 'unknown'
    # anything still "running" in a finished / lost run did not finish
    if out['status'] != 'running':
        for stage in stages:
            if stage['status'] == 'running':
                stage['status'] = ('failed' if out['status'] != 'unknown'
                                   else 'unknown')
            elif stage['status'] == 'pending' and out['status'] in [
                    'failed', 'lost', 'stopped']:
                stage['status'] = 'not run'
    for stage in stages:
        _finish_tree(stage['children'], stage['status'], out['status'])
        counts = _count(stage['children'])
        stage['leaves_done'] = counts['done']
        stage['leaves_total'] = counts['total']
    # where the run is now
    for stage in stages:
        if stage['status'] == 'running':
            out['current'] = ' / '.join([str(stage['level']),
                                         str(stage['flavour'])]
                                        + _current(stage['children']))
    out['steps'] = stages
    out['nstages'] = len(stages)
    # the flavours this run covers (for the Status tab filter)
    #   (not the Preamble every run has)
    out['flavours'] = sorted(set(str(stage['flavour']) for stage in stages
                                 if stage['flavour'] is not None
                                 and stage['level'] != PREAMBLE_LEVEL))
    out['ndone'] = len([stage for stage in stages
                        if stage['status'] == 'complete'])
    return out


def list_runs(path: str, limit: int = 200) -> List[Dict[str, Any]]:
    """
    List the recorded runs (newest first, without their steps)

    :param path: str, the POGOS path
    :param limit: int, the most runs returned

    :return: list of dict, the run summaries (see parse_run)
    """
    directory = run_dir(path)
    if not os.path.isdir(directory):
        return []
    names = sorted((name for name in os.listdir(directory)
                    if name.endswith('.jsonl')),
                   key=lambda name: os.path.getmtime(
                       os.path.join(directory, name)), reverse=True)
    runs = []
    for name in names[:limit]:
        run = parse_run(os.path.join(directory, name))
        if run is None:
            continue
        run = dict(run)
        run.pop('steps')
        runs.append(run)
    runs.sort(key=lambda run: run['started'] or 0, reverse=True)
    return runs


def get_run(path: str, run_id: str) -> Optional[Dict[str, Any]]:
    """
    Get one run with its steps

    :param path: str, the POGOS path
    :param run_id: str, the run id

    :return: dict or None, the run (see parse_run)
    """
    file_path = run_path(path, run_id)
    if file_path is None or not os.path.exists(file_path):
        return None
    return parse_run(file_path)


def remove_runs(path: str, run_ids: List[str]) -> int:
    """
    Remove the status records of finished runs (running runs are kept)

    :param path: str, the POGOS path
    :param run_ids: list of str, the run ids

    :return: int, the number of records removed
    """
    removed = 0
    for run_id in run_ids:
        run = get_run(path, run_id)
        if run is None or run['status'] in ['running', 'unknown']:
            continue
        try:
            os.remove(run_path(path, run_id))
            removed += 1
        except OSError:
            continue
    return removed


def age(epoch: Optional[float]) -> Optional[float]:
    """
    Seconds since a time stamp (None if unknown)

    :param epoch: float or None, the unix time

    :return: float or None, the age in seconds
    """
    return None if epoch is None else time.time() - epoch


# =============================================================================
# End of code
# =============================================================================

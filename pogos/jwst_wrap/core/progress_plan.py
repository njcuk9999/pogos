#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The JWST pipeline wrapper steps recorded for the pogos_gui Status tab
(aperocore.progress)

The jwst package is external (its code is not changed). The wrapper marks
its own steps (pogos.jwst_wrap.core.general) and, while a pipeline runs,
turns the stpipe log lines ("Step jump running ...", "Step jump done",
"Step skipped.") into steps (StpipeSteps), so every pipeline step of every
exposure is a row. The plan lists the steps of each stage's pipeline class
(its step_defs) so they show as pending first.

Every wrapper step has (see aperocore.progress.named_node):

    XXXX       the step name (used by progress.start_substep in the code)
    XXXX_FUNC  the dotted path of the function doing the work
    XXXX_DESC  a (long) description - None: the gui shows the docstring of
               XXXX_FUNC

Created on 2026-11-26

@author: cook
"""
import logging
from typing import Any, Dict, List, Optional

from aperocore import progress

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'pogos.jwst_wrap.core.progress_plan.py'
# the wrapper module
_GEN = 'pogos.jwst_wrap.core.general.'
# the logger stpipe writes "Step ... running / done" to
STPIPE_LOGGER = 'stpipe.step'
# -----------------------------------------------------------------------------
JW_IMPORT = 'Import the JWST pipeline'
JW_IMPORT_FUNC = _GEN + 'import_jwst'
JW_IMPORT_DESC = None
JW_DIRS = 'Directories'
JW_DIRS_FUNC = _GEN + 'make_jwst_dirs'
JW_DIRS_DESC = None
JW_ROUTE = 'Route inputs from the previous step'
JW_ROUTE_FUNC = 'pogos.core.general.route_step_inputs'
JW_ROUTE_DESC = None
JW_ASN = 'Stage 3 association'
JW_ASN_FUNC = _GEN + 'build_stage3_association'
JW_ASN_DESC = None
# the stages (FUNC None: the pipeline class of the instrument mode)
JW_S1 = 'Stage 1'
JW_S1_FUNC = None
JW_S1_DESC = None
JW_S2 = 'Stage 2'
JW_S2_FUNC = None
JW_S2_DESC = None
JW_S3 = 'Stage 3'
JW_S3_FUNC = None
JW_S3_DESC = None
# the stage keys by stage number
STAGE_KEYS = {1: 'JW_S1', 2: 'JW_S2', 3: 'JW_S3'}


# =============================================================================
# Define classes
# =============================================================================
class StpipeSteps(logging.Handler):
    """
    Turn the stpipe step log lines of one pipeline call into progress steps
    (the pipeline itself is the first "running" line and is not a step)
    """

    def __init__(self) -> None:
        """
        Initialise the handler

        :return: None
        """
        super().__init__(level=logging.INFO)
        # the open stpipe steps (None = the pipeline itself)
        self.stack: List[Optional[str]] = []

    def emit(self, record: logging.LogRecord) -> None:
        """
        Start / end a step from one stpipe log line (never raises)

        :param record: LogRecord, the log record

        :return: None
        """
        try:
            message = str(record.msg)
            if message.startswith('Step %s running'):
                name = str(record.args[0])
                # the first running line is the pipeline itself
                if not self.stack:
                    self.stack.append(None)
                    return
                progress.start(name)
                self.stack.append(name)
            elif message == 'Step skipped.' and self.stack:
                # a skipped step never logs "done"
                if self.stack[-1] is not None:
                    self.stack.pop()
                    progress.end('skipped')
            elif message.startswith('Step %s done') and self.stack:
                name = self.stack.pop()
                if name is not None:
                    progress.end('complete')
        except Exception:
            return

    def __enter__(self) -> 'StpipeSteps':
        """
        Listen to the stpipe log (only while steps are recorded)

        :return: StpipeSteps, this handler
        """
        if progress.active():
            logging.getLogger(STPIPE_LOGGER).addHandler(self)
        return self

    def __exit__(self, *exc: Any) -> None:
        """
        Stop listening (steps left open are closed by the enclosing step)

        :return: None
        """
        logging.getLogger(STPIPE_LOGGER).removeHandler(self)


# =============================================================================
# Define functions
# =============================================================================
def pipeline_nodes(pipe_class: Any) -> List[Dict[str, Any]]:
    """
    Get the plan nodes of the steps of a pipeline class (its step_defs)

    :param pipe_class: class, a jwst Pipeline class

    :return: list of dict, plan nodes (FUNC: the step class)
    """
    out = []
    for name, step_class in (getattr(pipe_class, 'step_defs', None)
                             or dict()).items():
        out.append(progress.node(name, func='{0}.{1}'.format(
            step_class.__module__, step_class.__name__)))
    return out


def get_plan(params: Any, flavour: str) -> List[Dict[str, Any]]:
    """
    Get the plan of one JWST wrapper run

    :param params: ParamDict, the pogos_run parameters
    :param flavour: str, PRE_JWST or EXT_JWST

    :return: list of dict, aperocore.progress plan nodes
    """
    from pogos.jwst_wrap.core import general
    _, pipelines = general.import_jwst(params)
    stages = dict(PRE_JWST=[1, 2], EXT_JWST=[3]).get(flavour, [])
    plan = [progress.named_node(globals(), 'JW_IMPORT'),
            progress.named_node(globals(), 'JW_DIRS')]
    if flavour == 'EXT_JWST':
        plan.append(progress.named_node(globals(), 'JW_ROUTE'))
    for stage in stages:
        pipe_class = None
        if pipelines is not None:
            pipe_class = general.get_pipeline_class(params, stage,
                                                    pipelines)
        steps = [] if pipe_class is None else pipeline_nodes(pipe_class)
        if stage == 3:
            # one pipeline run on an association of every input
            stage_node = progress.named_node(globals(), STAGE_KEYS[stage],
                                             *steps)
            plan.append(progress.named_node(globals(), 'JW_ASN'))
        else:
            # one pipeline run per exposure (a loop of the files)
            stage_node = progress.named_node(globals(), STAGE_KEYS[stage],
                                             *steps, loop=True)
        if pipe_class is not None and stage_node['func'] is None:
            stage_node['func'] = '{0}.{1}'.format(pipe_class.__module__,
                                                  pipe_class.__name__)
        plan.append(stage_node)
    return plan


# =============================================================================
# End of code
# =============================================================================

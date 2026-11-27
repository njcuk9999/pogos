#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The steps every POGOS flavour goes through (for the pogos_gui Status tab)

pogos_run writes these plans when a run starts so the gui shows every
step as pending before it runs. A plan is a list of aperocore.progress
nodes; the names must match the steps the code marks (progress.substep /
start_substep, aperocore.progress.step / mark). Loops (e.g. one step per
exposure) are templates filled in when the code announces their items.

Every flavour keeps its plan next to its code (a progress_plan module
with XXXX / XXXX_FUNC / XXXX_DESC constants and a get_plan function):
SOSSISSE (sossisse.general.progress_plan), TSOVORE, MIRIAM and SORBET (in
pogos) and the wrappers of the external packages Eureka, JWST and NAMELESS
(only the wrapper steps are marked - their code is not changed).

This module must stay light: no reduction backend is imported except a
flavour's (dependency free) plan module.

Created on 2026-11-26

@author: cook
"""
from importlib import import_module
from typing import Any, Callable, Dict, List


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'pogos.core.progress_plans.py'


# =============================================================================
# Define plan functions (one per reduction step)
# =============================================================================
def _plan_sossisse(params: Any) -> List[Dict[str, Any]]:
    """
    The SOSSISSE plan (declared by SOSSISSE itself)

    :param params: ParamDict, the pogos_run parameters

    :return: list of dict, the plan nodes
    """
    module = import_module('sossisse.general.progress_plan')

    def _get(key: str, default: Any) -> Any:
        """
        Read a SOSSISSE parameter through the POGOS parameters

        :param key: str, the SOSSISSE key (e.g. RUN.LINEAR_RECON)
        :param default: the value if it is not set

        :return: the value
        """
        return params.get('SOSSISSE.' + key, default)

    return module.get_plan(_get)


def _module_plan(module: str, *args: Any
                 ) -> Callable[[Any], List[Dict[str, Any]]]:
    """
    Build the plan function of a flavour whose plan lives in its own
    progress_plan module (a get_plan function)

    :param module: str, the plan module (e.g. pogos.miriam.general.
                   progress_plan)
    :param args: fixed arguments given to get_plan instead of the
                 parameters (e.g. the flavour); none: get_plan(params)

    :return: callable(params) -> list of plan nodes
    """
    def _plan(params: Any) -> List[Dict[str, Any]]:
        get_plan = import_module(module).get_plan
        return get_plan(*args) if args else get_plan(params)
    return _plan


def _params_plan(module: str, flavour: str
                 ) -> Callable[[Any], List[Dict[str, Any]]]:
    """
    Build the plan function of a flavour whose get_plan takes the
    parameters and the flavour

    :param module: str, the plan module
    :param flavour: str, the flavour (e.g. PRE_JWST)

    :return: callable(params) -> list of plan nodes
    """
    def _plan(params: Any) -> List[Dict[str, Any]]:
        return import_module(module).get_plan(params, flavour)
    return _plan


# the plan modules of the flavours
_TSOVORE = 'pogos.tsovore.core.progress_plan'
_EUREKA = 'pogos.eureka_wrap.core.progress_plan'
_JWST = 'pogos.jwst_wrap.core.progress_plan'
_NAMELESS = 'pogos.nameless_wrap.core.progress_plan'
_SORBET = 'pogos.sorbet.general.progress_plan'
_MIRIAM = 'pogos.miriam.general.progress_plan'
# the plan function of each reduction step (stage flavour)
PLANS: Dict[str, Callable[[Any], List[Dict[str, Any]]]] = dict(
    TSOVORE=_module_plan(_TSOVORE),
    PRE_NAMELESS=_module_plan(_NAMELESS, 'PRE_NAMELESS'),
    PRE_EUREKA=_module_plan(_EUREKA, 'PRE_EUREKA'),
    PRE_JWST=_params_plan(_JWST, 'PRE_JWST'),
    SOSSISSE=_plan_sossisse,
    MIRIAM=_module_plan(_MIRIAM),
    EXT_NAMELESS=_module_plan(_NAMELESS, 'EXT_NAMELESS'),
    EXT_EUREKA=_module_plan(_EUREKA, 'EXT_EUREKA'),
    EXT_JWST=_params_plan(_JWST, 'EXT_JWST'),
    SORBET=_module_plan(_SORBET),
    POST_EUREKA=_module_plan(_EUREKA, 'POST_EUREKA'),
)


# =============================================================================
# Define functions
# =============================================================================
def stage_plan(params: Any, flavour: str) -> List[Dict[str, Any]]:
    """
    Get the plan of one stage (never raises - a plan is only a display aid)

    :param params: ParamDict, the pogos_run parameters
    :param flavour: str, the stage flavour (e.g. SOSSISSE, SORBET)

    :return: list of dict, the plan nodes ([] if unknown)
    """
    func = PLANS.get(flavour)
    if func is None:
        return []
    try:
        return func(params)
    except Exception:
        return []


def run_plans(params: Any, stages: List[List[str]]) -> List[Dict[str, Any]]:
    """
    Get the plans of the stages a run will go through

    :param params: ParamDict, the pogos_run parameters
    :param stages: list of [level, flavour], the planned stages

    :return: list of dict(level, flavour, plan)
    """
    return [dict(level=level, flavour=flavour,
                 plan=stage_plan(params, flavour))
            for level, flavour in stages]


# =============================================================================
# End of code
# =============================================================================

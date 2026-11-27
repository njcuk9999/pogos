#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
POGOS gui command builders and setup choices

Builds the commands the gui runs (pogos_setup, pogos_edit, pogos_run,
pogos_config, pogos_reset and batch scripts) from the browser forms. Every
builder returns both the command that is executed (python -m ...) and the
"CLI equivalent" a user could type, so the two never drift apart.

The setup choices (instrument, mode, reduction steps) use exactly the same
numbering as the interactive prompts of pogos_setup (they are passed as
the --instrument_select / --instrument_mode / --*_step pre-answers).

Created on 2026-11-26

@author: cook
"""
import os
import re
import shlex
import sys
from typing import Any, Dict, List, Optional, Tuple

from pogos.core import definitions

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'pogos.gui.commands.py'
# recipe name -> module run with "python -m"
RECIPES = dict(pogos_setup='pogos.recipes.pogos_setup',
               pogos_edit='pogos.recipes.pogos_edit',
               pogos_run='pogos.recipes.pogos_run',
               pogos_config='pogos.recipes.pogos_config',
               pogos_reset='pogos.recipes.pogos_reset')
# the command line pre-answer of each reduction level
LEVEL_ARGS = {'Pre-extraction': 'preextract_step',
              'Extraction': 'extract_step',
              'Post-extraction': 'postextract_step'}
# environment variable accepting yaml files from older POGOS versions
ACCEPT_OLD_ENV = 'POGOS_ACCEPT_OLD_YAML'
# ANSI colour codes (POGOS exceptions are coloured)
ANSI_RE = re.compile(r'\x1b\[[0-9;]*m')
# download choices of the setup page
DOWNLOAD_CHOICES = ['run', 'now', 'local']


# =============================================================================
# Define classes
# =============================================================================
class CommandError(ValueError):
    """Raised when a gui form cannot be turned into a valid command"""


# =============================================================================
# Define setup choice functions
# =============================================================================
def setup_choices() -> Dict[str, Any]:
    """
    Get the instrument / mode / reduction step choices of pogos_setup

    Numbers are the answers pogos_setup expects: instruments and modes are
    1-based (in definitions order), steps are 0 (= skip) or the 1-based
    position among the steps of that level supporting the mode.

    :return: dict(instruments=list of dict(number, name, modes=list of
             dict(number, name, label, enabled, levels))) - levels lists
             dict(name, arg, multiple, steps=list of dict(number, name)) for
             every level with at least one supported step
    """
    instruments = []
    choices = definitions.mode_choices()
    for inum, instrument in enumerate(choices, start=1):
        modes = []
        for mnum, mode in enumerate(choices[instrument], start=1):
            levels = []
            for level in definitions.REDUCTION_LEVELS:
                steps = [step for step in definitions.steps_for_level(level)
                         if step.supports(mode)]
                if len(steps) == 0:
                    continue
                levels.append(dict(
                    name=level.name, arg=LEVEL_ARGS.get(level.name),
                    multiple=bool(level.allow_multiple),
                    steps=[dict(number=snum, name=step.name)
                           for snum, step in enumerate(steps, start=1)]))
            modes.append(dict(number=mnum, name=mode.name, label=mode.label,
                              enabled=bool(mode.enabled), levels=levels))
        instruments.append(dict(number=inum, name=instrument, modes=modes))
    return dict(instruments=instruments)


def find_mode(instmode: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Find the instrument and mode choice of an instrument mode name

    :param instmode: str, e.g. JWST.NIRISS.SOSS

    :raises CommandError: for an unknown or not yet supported mode

    :return: tuple, (instrument choice, mode choice) - see setup_choices
    """
    for instrument in setup_choices()['instruments']:
        for mode in instrument['modes']:
            if mode['name'] == instmode:
                if not mode['enabled']:
                    raise CommandError('{0} is not yet supported'.format(
                        instmode))
                return instrument, mode
    raise CommandError('unknown instrument mode: {0}'.format(instmode))


def demo_modes(instmode: str, selection: Dict[str, List[str]]) -> List[str]:
    """
    Get the "level:step" names of the selected reduction steps (as used
    by the demo definitions)

    :param instmode: str, the instrument mode
    :param selection: dict, level name -> list of step names

    :raises CommandError: for a step the mode does not support

    :return: list of str, e.g. ['Extraction:SOSSISSE']
    """
    _, mode = find_mode(instmode)
    out = []
    for level in mode['levels']:
        names = [step['name'] for step in level['steps']]
        for name in selection.get(level['name'], []) or []:
            if name not in names:
                raise CommandError('{0} is not a {1} step for {2}'.format(
                    name, level['name'], instmode))
            out.append('{0}:{1}'.format(level['name'], name))
    return out


def validate_project_name(name: str) -> Optional[str]:
    """
    Check a project name with the same rule pogos_setup uses

    :param name: str, the project name

    :return: str or None, the error message (None if valid)
    """
    # deferred import (startup loads the POGOS constants - slow)
    from pogos.core import startup
    from pogos.core import base as pogos_base
    try:
        startup.validate_project_name(name)
    except pogos_base.PogosException as error:
        message = ANSI_RE.sub('', str(error)).strip()
        # drop the exception class name POGOS adds to the text
        return re.sub(r'^\w*Exception:\s*', '', message)
    return None


# =============================================================================
# Define command functions
# =============================================================================
def _recipe_cmd(recipe: str, args: List[str]) -> Tuple[List[str], str]:
    """
    Build the executed command and the cli equivalent of a recipe

    :param recipe: str, the recipe name (key of RECIPES)
    :param args: list of str, the recipe arguments

    :return: tuple, (command list for subprocess, display string)
    """
    cmd = [sys.executable, '-m', RECIPES[recipe]] + list(args)
    display = shlex.join([recipe] + list(args))
    return cmd, display


def _env_display(env: Dict[str, str], display: str) -> str:
    """
    Prefix a display command with its environment variables

    :param env: dict, the environment variables
    :param display: str, the display command

    :return: str, e.g. "POGOS_ACCEPT_OLD_YAML=1 pogos_run ..."
    """
    prefix = ' '.join('{0}={1}'.format(key, shlex.quote(value))
                      for key, value in env.items())
    return (prefix + ' ' + display) if prefix else display


def _check_yaml(yaml_path: Any) -> str:
    """
    Check a yaml path from a form

    :param yaml_path: Any, the yaml path

    :raises CommandError: if missing / not a file

    :return: str, the absolute yaml path
    """
    text = str(yaml_path or '').strip()
    if text == '':
        raise CommandError('choose a yaml file first')
    real = os.path.realpath(os.path.expanduser(text))
    if not os.path.isfile(real):
        raise CommandError('yaml file does not exist: {0}'.format(real))
    return real


def setup_errors(pogos_path: str, form: Dict[str, Any]) -> List[str]:
    """
    Check the setup page form (every problem, not just the first)

    :param pogos_path: str, the POGOS path (GLOBAL.DATA_PATH default)
    :param form: dict, the setup form (see setup_command)

    :return: list of str, the problems (empty = ready to run)
    """
    errors: List[str] = []
    data_path = str(form.get('data_path') or pogos_path or '').strip()
    if data_path == '':
        errors.append('Enter the data path (GLOBAL.DATA_PATH).')
    # ---- project name (same rule as pogos_setup)
    project = str(form.get('project_name') or '').strip()
    if project == '':
        errors.append('Enter a project name (GLOBAL.PROJECT_NAME) - or '
                      'choose a demo to use its project name.')
    else:
        problem = validate_project_name(project)
        if problem is not None:
            errors.append('Project name: ' + problem)
    # ---- yaml file name
    yaml_name = str(form.get('yaml_name') or '').strip()
    demo = str(form.get('demo') or '').strip()
    if yaml_name and os.sep in yaml_name:
        errors.append('The yaml file name must be a file name (it is saved '
                      'in {0}).'.format(os.path.join(data_path, 'yamls')))
    elif not yaml_name and not demo:
        errors.append('Enter a yaml file name (only a demo can name the '
                      'yaml file automatically).')
    # ---- instrument / mode
    mode = None
    instmode = str(form.get('instmode') or '')
    if instmode == '':
        errors.append('Choose an instrument and an instrument mode.')
    else:
        try:
            mode = find_mode(instmode)[1]
        except CommandError as error:
            errors.append(str(error))
    # ---- reduction steps
    selection = form.get('steps') or dict()
    if not isinstance(selection, dict):
        errors.append('Invalid reduction step selection.')
        selection = dict()
    if mode is not None:
        nchosen = 0
        for level in mode['levels']:
            chosen = selection.get(level['name']) or []
            names = [step['name'] for step in level['steps']]
            unknown = [name for name in chosen if name not in names]
            if unknown:
                errors.append('{0} is not a {1} step for {2}.'.format(
                    ', '.join(unknown), level['name'], instmode))
            if len(chosen) > 1 and not level['multiple']:
                errors.append('Only one {0} step can be chosen.'.format(
                    level['name']))
            nchosen += len(chosen)
        if nchosen == 0:
            errors.append('Every reduction stage is skipped - choose at '
                          'least one pre-extraction, extraction or '
                          'post-extraction step.')
    # ---- downloads
    download = str(form.get('download') or 'run')
    if download not in DOWNLOAD_CHOICES:
        errors.append('Invalid download choice: {0}'.format(download))
    elif download == 'local':
        local = str(form.get('demolocal') or '').strip()
        if local == '':
            errors.append('Enter the local mirror directory.')
        elif not os.path.isdir(os.path.expanduser(local)):
            errors.append('The local mirror does not exist: {0}'.format(
                local))
    return errors


def setup_command(pogos_path: str, form: Dict[str, Any]
                  ) -> Dict[str, Any]:
    """
    Build the pogos_setup command from the setup page form

    :param pogos_path: str, the POGOS path (GLOBAL.DATA_PATH default)
    :param form: dict with data_path, project_name, yaml_name, instmode,
                 steps (level -> list of step names, empty = skip), demo
                 (key or ''), download (run / now / local), demolocal,
                 demosymlink

    :raises CommandError: for invalid forms (all problems, one per line)

    :return: dict(cmd, display, env, yaml_file, cwd)
    """
    errors = setup_errors(pogos_path, form)
    if errors:
        raise CommandError('\n'.join(errors))
    args: List[str] = []
    # ---- paths and names
    data_path = str(form.get('data_path') or pogos_path).strip()
    data_path = os.path.realpath(os.path.expanduser(data_path))
    args.append('--data_path={0}'.format(data_path))
    project = str(form.get('project_name')).strip()
    args.append('--project_name={0}'.format(project))
    yaml_file = None
    yaml_name = str(form.get('yaml_name') or '').strip()
    if yaml_name:
        if not yaml_name.endswith('.yaml'):
            yaml_name += '.yaml'
        yaml_file = os.path.join(data_path, 'yamls', yaml_name)
        args.append('--yamlfile={0}'.format(yaml_file))
    # ---- instrument / mode / steps (pogos_setup prompt numbers)
    instrument, mode = find_mode(str(form.get('instmode')))
    args.append('--instrument_select={0}'.format(instrument['number']))
    args.append('--instrument_mode={0}'.format(mode['number']))
    selection = form.get('steps') or dict()
    for level in mode['levels']:
        chosen = selection.get(level['name']) or []
        numbers = [step['number'] for step in level['steps']
                   if step['name'] in chosen]
        # 0 = skip this stage
        value = ','.join(str(num) for num in numbers) if numbers else '0'
        args.append('--{0}={1}'.format(level['arg'], value))
    # ---- demo
    demo = str(form.get('demo') or '').strip()
    args.append('--demo_select={0}'.format(demo if demo else 'none'))
    # ---- downloads
    download = str(form.get('download') or 'run')
    if download == 'local':
        local = str(form.get('demolocal')).strip()
        args.append('--demolocal={0}'.format(
            os.path.realpath(os.path.expanduser(local))))
        # bools are parsed with bool() - only ever pass True
        if form.get('demosymlink'):
            args.append('--demosymlink=True')
    else:
        args.append('--download={0}'.format(download))
    cmd, display = _recipe_cmd('pogos_setup', args)
    return dict(cmd=cmd, display=display, env=dict(), yaml_file=yaml_file,
                cwd=data_path)


def edit_command(yaml_path: Any) -> Dict[str, Any]:
    """
    Build the pogos_edit command (new project from an existing yaml)

    :param yaml_path: Any, the yaml used as a template

    :raises CommandError: if the yaml does not exist

    :return: dict(cmd, display, env)
    """
    real = _check_yaml(yaml_path)
    cmd, display = _recipe_cmd('pogos_edit',
                               ['--demo_file={0}'.format(real)])
    return dict(cmd=cmd, display=display, env=dict())


def show_plots_args(show_plots: Optional[bool]) -> List[str]:
    """
    Get the pogos_run --showplots argument

    :param show_plots: bool or None, force every flavour to show its plots
                       (True), never show them (False) or use the yaml
                       (None)

    :return: list of str, the arguments ([] for None)
    """
    if show_plots is None:
        return []
    return ['--showplots={0}'.format('on' if show_plots else 'off')]


def run_command(yaml_path: Any, accept_old: bool = False,
                show_plots: Optional[bool] = None) -> Dict[str, Any]:
    """
    Build the pogos_run command

    :param yaml_path: Any, the yaml to run
    :param accept_old: bool, accept a yaml from an older POGOS version
    :param show_plots: bool or None, see show_plots_args

    :raises CommandError: if the yaml does not exist

    :return: dict(cmd, display, env)
    """
    real = _check_yaml(yaml_path)
    rargs = ['--yamlfile={0}'.format(real)] + show_plots_args(show_plots)
    cmd, display = _recipe_cmd('pogos_run', rargs)
    env = {ACCEPT_OLD_ENV: '1'} if accept_old else dict()
    return dict(cmd=cmd, display=_env_display(env, display), env=env)


def config_command(yaml_path: Any, check_only: bool = True,
                   accept_old: bool = False) -> Dict[str, Any]:
    """
    Build the pogos_config command

    :param yaml_path: Any, the yaml to check
    :param check_only: bool, True = report only (CI mode, nothing saved),
                       False = interactive (fixes are saved to the yaml)
    :param accept_old: bool, unused by pogos_config (kept for symmetry)

    :raises CommandError: if the yaml does not exist

    :return: dict(cmd, display, env)
    """
    _ = accept_old
    real = _check_yaml(yaml_path)
    cmd, display = _recipe_cmd('pogos_config',
                               ['--yamlfile={0}'.format(real)])
    env = {'CI': '1'} if check_only else dict()
    return dict(cmd=cmd, display=_env_display(env, display), env=env)


def reset_command(yaml_path: Any, accept_old: bool = False
                  ) -> Dict[str, Any]:
    """
    Build the pogos_reset command (the gui answers its confirmation after
    the user typed RESET in the browser)

    :param yaml_path: Any, the yaml whose outputs are reset
    :param accept_old: bool, accept a yaml from an older POGOS version

    :raises CommandError: if the yaml does not exist

    :return: dict(cmd, display, env)
    """
    real = _check_yaml(yaml_path)
    cmd, display = _recipe_cmd('pogos_reset',
                               ['--yamlfile={0}'.format(real)])
    env = {ACCEPT_OLD_ENV: '1'} if accept_old else dict()
    return dict(cmd=cmd, display=_env_display(env, display), env=env)


def batch_lines(yaml_path: Any, accept_old: bool = False,
                workdir: Optional[str] = None,
                show_plots: Optional[bool] = None) -> Dict[str, Any]:
    """
    Build the shell lines of a pogos_run batch script

    :param yaml_path: Any, the yaml to run
    :param accept_old: bool, accept a yaml from an older POGOS version
    :param workdir: str or None, directory the job runs in
    :param show_plots: bool or None, see show_plots_args

    :raises CommandError: if the yaml does not exist

    :return: dict(lines, display) - lines go after the activation lines
    """
    real = _check_yaml(yaml_path)
    lines = []
    if workdir:
        lines.append('cd {0}'.format(shlex.quote(workdir)))
    if accept_old:
        lines.append('export {0}=1'.format(ACCEPT_OLD_ENV))
    run = shlex.join(['pogos_run', '--yamlfile={0}'.format(real)]
                     + show_plots_args(show_plots))
    lines.append(run)
    return dict(lines=lines, display=run)


# =============================================================================
# End of code
# =============================================================================

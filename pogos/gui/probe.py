#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
POGOS gui probes (run in a separate process)

Small helpers the POGOS gui runs as "python -m pogos.gui.probe ..." so the
POGOS runtime (constants, demo classes, yaml loading) never lives in the
long running gui process (the demo classes keep state between uses and
loading the constants takes a few seconds):

    demos --instmode=MODE --steps=LEVEL:STEP,...
        the demos pogos_setup offers for this mode and these steps
    reset-preview --yamlfile=FILE
        the directories pogos_reset would delete for this yaml
    params
        the description / type / default / options of every POGOS constant
        (POGOS and external ConstDicts) keyed by the full yaml key path
    algorithms
        the algorithm steps (progress plans) of every reduction step (per
        instrument mode where they depend on it)

The result is printed as one json line starting with RESULT_PREFIX (POGOS
logging may print other lines before it).

Created on 2026-11-26

@author: cook
"""
import argparse
import json
import os
import sys
from typing import Any, Dict, List

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'pogos.gui.probe.py'
# prefix of the json result line
RESULT_PREFIX = 'POGOS_GUI_RESULT: '
# version error text (as pogos_reset)
VERR = ('The POGOS version of the {0} is not compatible with the current '
        'version of the code ({1}).')


# =============================================================================
# Define functions
# =============================================================================
def probe_demos(instmode: str, steps: List[str]) -> Dict[str, Any]:
    """
    Get the demos pogos_setup offers for an instrument mode and steps

    :param instmode: str, the instrument mode (e.g. JWST.NIRISS.SOSS)
    :param steps: list of str, the selected "level:step" names

    :return: dict(instmode, demos=list of dict(key, number, id, project,
             title, object, keywords, description, date, author, data))
    """
    from pogos import demos as demo_module
    from pogos.core import startup
    demo_dict = startup.get_demo_choices(demo_module, steps)
    out: List[Dict[str, Any]] = []
    for number, (key, demo) in enumerate(demo_dict.get(instmode,
                                                       dict()).items(),
                                         start=1):
        info = demo.get_info()
        # the project name the demo would use (GLOBAL.PROJECT_NAME)
        project = demo.cdict.storage.get('GLOBAL.PROJECT_NAME')
        project = None if project is None else project.value
        out.append(dict(key=key, number=number, id=demo.get_prop('id'),
                        project=project,
                        title=info.get('title'), object=info.get('object'),
                        keywords=info.get('keywords') or [],
                        description=info.get('description'),
                        date=info.get('date'), author=info.get('author'),
                        data=info.get('data') or []))
    return dict(instmode=instmode, steps=steps, demos=out)


def probe_demo_counts() -> Dict[str, Any]:
    """
    Count the demos of every instrument mode: each object counts once per
    combination of its reduction steps that pogos_setup can select (one
    step or skip per level, any subset on multiple choice levels, at least
    one step) - e.g. SOSSISSE and SOSSISSE+SORBET.WLCA count as two

    :return: dict(counts=dict instrument mode -> number of demos)
    """
    from pogos import demos as demo_module
    from pogos.core import definitions
    counts: Dict[str, int] = dict()
    for instmode, demos in demo_module.DEMOS.items():
        mode = definitions.MODE_BY_NAME.get(instmode)
        total = 0
        for demo_class in demos.values():
            redsteps = demo_class().redsteps
            combos = 1
            for level in definitions.REDUCTION_LEVELS:
                nstep = len([step for step in definitions.steps_for_level(
                    level) if (mode is None or step.supports(mode)) and
                    '{0}:{1}'.format(level.name, step.name) in redsteps])
                combos *= 2 ** nstep if level.allow_multiple else nstep + 1
            # minus the all-skipped choice
            total += combos - 1
        counts[instmode] = total
    return dict(counts=counts)


def step_selections(instmode: str) -> List[List[str]]:
    """
    Every "level:step" selection pogos_setup can make for a mode (one step
    or skip per level, any subset on multiple choice levels, at least one
    step) - in the order the gui sends them (level order, then step order)

    :param instmode: str, the instrument mode

    :return: list of list of str, the selections
    """
    import itertools
    from pogos.core import definitions
    mode = definitions.MODE_BY_NAME[instmode]
    options = []
    for level in definitions.REDUCTION_LEVELS:
        names = ['{0}:{1}'.format(level.name, step.name)
                 for step in definitions.steps_for_level(level)
                 if step.supports(mode)]
        if len(names) == 0:
            continue
        if level.allow_multiple:
            # every subset (in step order)
            options.append([[name for bit, name in enumerate(names)
                             if mask >> bit & 1]
                            for mask in range(2 ** len(names))])
        else:
            options.append([[]] + [[name] for name in names])
    out = []
    for combo in itertools.product(*options):
        selection = [name for part in combo for name in part]
        if selection:
            out.append(selection)
    return out


def _mode_demos(instmode: str) -> Dict[str, Any]:
    """
    The demos of every step selection of one instrument mode

    :param instmode: str, the instrument mode

    :return: dict "{instmode}|{steps joined by ,}" -> the probe_demos
             result (only selections with at least one demo)
    """
    out: Dict[str, Any] = dict()
    for selection in step_selections(instmode):
        result = probe_demos(instmode, selection)
        if result['demos']:
            out['{0}|{1}'.format(instmode, ','.join(selection))] = result
    return out


def probe_demos_all(instmodes: List[str]) -> Dict[str, Any]:
    """
    The demo counts and the demos of every step selection of some
    instrument modes (all modes with demos if none given) - preloaded by
    the gui at start up; the modes run in parallel (forked after the
    slow import)

    :param instmodes: list of str, the instrument modes (empty = all)

    :return: dict(instmodes, counts (see probe_demo_counts), demos=dict
             "{instmode}|{steps joined by ,}" -> the probe_demos result)
    """
    import multiprocessing
    from pogos import demos as demo_module
    if not instmodes:
        instmodes = list(demo_module.DEMOS)
    counts = probe_demo_counts()['counts']
    todo = [mode for mode in instmodes if demo_module.DEMOS.get(mode)]
    out: Dict[str, Any] = dict()
    if len(todo) > 1:
        ctx = multiprocessing.get_context('fork')
        with ctx.Pool(min(len(todo), os.cpu_count() or 2)) as pool:
            for part in pool.map(_mode_demos, todo):
                out.update(part)
    else:
        for mode in todo:
            out.update(_mode_demos(mode))
    return dict(instmodes=instmodes, counts=counts, demos=out)


def _load_yaml_params(yaml_file: str) -> Any:
    """
    Load the parameters of a yaml as pogos_run does (without running)

    :param yaml_file: str, the yaml file (absolute)

    :return: tuple, (ParamDict, bool version ok)
    """
    from aperocore.constants import load_functions
    from pogos.constants.constants import CDict
    from pogos.core import base as pogos_base
    from pogos.core import definitions
    from pogos.core import startup
    # the recipes parse sys.argv - only give them the yaml file
    sys.argv = [sys.argv[0], '--yamlfile={0}'.format(yaml_file)]
    other_const = startup.initial_setup()
    gkwargs = dict(name='pogos.gui.probe', description='yaml probe',
                   inputargs=['GLOBAL.YAML_FILE', 'GLOBAL.LIST_YAMLS'],
                   param_file_path='GLOBAL.YAML_FILE', config_list=[CDict],
                   from_file=False, external_const=other_const)
    params = load_functions.get_all_params(**gkwargs)
    version_ok = load_functions._check_yaml_version(
        yaml_file, pogos_base.__version__, VERR, raise_exception=False)
    largs = dict(files=[yaml_file], params=params, version=None,
                 version_err=None)
    params = load_functions.load_from_yaml(**largs)
    # out of date yamls may lack run switches (as pogos_run / pogos_reset)
    for step in definitions.RED_STEPS:
        if params.get(step.run_key) is None:
            params[step.run_key] = False
    return params, bool(version_ok)


def probe_yaml_files(yaml_file: str) -> Dict[str, Any]:
    """
    Describe the input files (FileObjectConst parameters) of the enabled
    reduction steps of a yaml: where they come from, which directory they
    belong in and the files listed - the gui checks the disk itself (so
    this result can be cached until the yaml changes)

    :param yaml_file: str, the yaml file

    :return: dict(yaml, version_ok, download_dir, files=list of dict(key,
             step, source, label, chained, set, directory, cache_dir,
             files, always_download, error))
    """
    from aperocore.constants import custom_const_classes as ccc
    from aperocore.constants import file_sources
    from pogos.core import file_download
    yaml_file = os.path.realpath(yaml_file)
    params, version_ok = _load_yaml_params(yaml_file)
    chained = set(key.upper() for key in file_download.chained_keys(params))
    download_dir = file_download.download_directory(params)
    out = []
    for key in file_download.enabled_file_keys(params):
        step = file_download.step_for_key(key)
        instance = params.instances.get(key)
        fileobj = ccc.get_fileobj(params[key])
        entry: Dict[str, Any] = dict(
            key=key, step=None if step is None else step.name,
            source=None, label=None, chained=key.upper() in chained,
            set=fileobj is not None, directory=None, cache_dir=None,
            files=[], always_download=False, error=None)
        if fileobj is not None:
            entry['source'] = fileobj.source
            entry['label'] = file_sources._source_label(fileobj)
            if fileobj.source == 'mast':
                entry['label'] += ' ({0})'.format(fileobj.product)
            entry['files'] = fileobj.files
            entry['always_download'] = bool(fileobj.always_download)
            entry['cache_dir'] = file_sources.cache_directory(download_dir,
                                                              fileobj)
            try:
                if instance.path_key is not None:
                    path_key = (file_sources.module_prefix(key, instance)
                                + instance.path_key)
                    entry['directory'] = file_download.module_directory(
                        params, key, path_key)
            except Exception as error:
                entry['error'] = '{0}: {1}'.format(type(error).__name__,
                                                   error)
        out.append(entry)
    return dict(yaml=yaml_file, version_ok=version_ok,
                download_dir=download_dir, files=out)


def probe_reset(yaml_file: str) -> Dict[str, Any]:
    """
    Get the directories pogos_reset would delete (without deleting)

    Mirrors pogos_reset: load the yaml, work out the targets of the enabled
    steps and drop unsafe / missing ones.

    :param yaml_file: str, the yaml file

    :return: dict(yaml, version_ok, targets=dict(step -> list of dict(path,
             nfiles, size)), warnings, ndirs, nfiles, size)
    """
    from aperocore.constants import load_functions
    from aperocore.gui import files as gui_files
    from pogos.constants.constants import CDict
    from pogos.core import base as pogos_base
    from pogos.core import definitions
    from pogos.core import reset
    from pogos.core import startup
    yaml_file = os.path.realpath(yaml_file)
    # the recipes parse sys.argv - only give them the yaml file
    sys.argv = [sys.argv[0], '--yamlfile={0}'.format(yaml_file)]
    other_const = startup.initial_setup()
    gkwargs = dict(name='pogos.gui.probe', description='reset preview',
                   inputargs=['GLOBAL.YAML_FILE', 'GLOBAL.LIST_YAMLS'],
                   param_file_path='GLOBAL.YAML_FILE', config_list=[CDict],
                   from_file=False, external_const=other_const)
    params = load_functions.get_all_params(**gkwargs)
    version_ok = load_functions._check_yaml_version(
        yaml_file, pogos_base.__version__, VERR, raise_exception=False)
    largs = dict(files=[yaml_file], params=params, version=None,
                 version_err=None)
    params = load_functions.load_from_yaml(**largs)
    # out of date yamls may lack run switches (as pogos_reset)
    for step in definitions.RED_STEPS:
        if params.get(step.run_key) is None:
            params[step.run_key] = False
    targets, protected = reset.get_reset_targets(params)
    targets, warnings = reset.filter_safe_targets(params, targets, protected)
    out_targets: Dict[str, List[Dict[str, Any]]] = dict()
    totals = dict(ndirs=0, nfiles=0, size=0)
    for step_name, paths in targets.items():
        out_targets[step_name] = []
        for path in paths:
            stats = gui_files.dir_stats(path)
            out_targets[step_name].append(dict(path=path,
                                               nfiles=stats['nfiles'],
                                               size=stats['size']))
            totals['ndirs'] += 1
            totals['nfiles'] += stats['nfiles']
            totals['size'] += stats['size']
    return dict(yaml=yaml_file, version_ok=bool(version_ok),
                targets=out_targets, protected=protected,
                warnings=warnings, **totals)


def _jsonable(value: Any) -> Any:
    """
    Make a constant default json friendly (types become their names)

    :param value: any, the value

    :return: any, a json friendly value
    """
    if isinstance(value, type):
        return value.__name__
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    return str(value)


def _file_spec(const: Any) -> Dict[str, Any]:
    """
    Describe how a file constant (FileObjectConst) can be written in a yaml:
    its sources and the keys each source uses (for the gui source switch)

    :param const: FileObjectConst, the constant

    :return: dict(sources, base_keys, source_keys, defaults, multi,
             product, product_options, extras)
    """
    from aperocore.constants import custom_const_classes as ccc
    dtype = getattr(const, 'dtype', None)
    multi = dtype is list or bool(getattr(const, 'allow_list', False))
    extras = dict()
    for name, spec in (getattr(const, 'extras', None) or dict()).items():
        spec = spec if isinstance(spec, dict) else dict()
        extras[str(name)] = dict(
            dtype=_jsonable(spec.get('dtype')),
            options=_jsonable(spec.get('options')),
            default=_jsonable(spec.get('default')),
            description=str(spec.get('description') or ''))
    # default values written when a key is added by a source switch
    defaults = dict(always_download='False',
                    match=str(list(ccc.MAST_DEFAULT_MATCH)),
                    min_size_mb=str(ccc.MAST_DEFAULT_MIN_SIZE_MB))
    return dict(sources=list(ccc.FILE_SOURCES),
                base_keys=list(ccc.FILE_BASE_KEYS),
                source_keys={key: list(value) for key, value in
                             ccc.FILE_SOURCE_KEYS.items()},
                defaults=defaults, multi=multi,
                product=getattr(const, 'product', None),
                product_options=_jsonable(getattr(const, 'product_options',
                                                  None)),
                extras=extras)


def _const_info(const: Any) -> Dict[str, Any]:
    """
    Describe one constant (json friendly)

    :param const: Const, a constant of a ConstantsDict

    :return: dict(description, short, kind, file, dtype, default, yaml,
             options, user, filespec) - filespec describes file constants
             (see _file_spec, None otherwise), yaml is the default as
             written in a yaml file (e.g. the mapping of a file constant)
             and short is the constant specific description (without the
             generic usage text some classes add, e.g. FileObjectConst)
    """
    # the constant specific part of the description (file constants add a
    #   long generic usage text to their description)
    short = const.__dict__.get('_description', None)
    if not isinstance(short, str):
        short = str(getattr(const, 'description', '') or '')
    kind = type(const).__name__
    dtype = getattr(const, 'dtype', None)
    dtype = dtype.__name__ if isinstance(dtype, type) else (
        None if dtype is None else str(dtype))
    options = getattr(const, 'options', None)
    filespec = _file_spec(const) if kind == 'FileObjectConst' else None
    # the default as the yaml writer writes it (custom classes may write
    #   their own form, e.g. FileObjectConst mappings)
    default = getattr(const, 'value', None)
    yaml_default = default
    if hasattr(const, 'yaml_value'):
        try:
            yaml_default = const.yaml_value(default)
        except Exception:
            yaml_default = default
    return dict(filespec=filespec,
                description=str(getattr(const, 'description', '') or ''),
                short=short.strip(), kind=kind,
                file=kind == 'FileObjectConst',
                dtype=dtype, default=default,
                yaml=_jsonable(yaml_default),
                options=None if options is None else [str(opt)
                                                      for opt in options],
                user=bool(getattr(const, 'user', False)))


def probe_params() -> Dict[str, Any]:
    """
    Get the description of every POGOS constant (for gui tool tips)

    Keys are the full yaml key paths: POGOS constants as stored (e.g.
    GLOBAL.DATA_PATH, RUN.SOSSISSE) and external constants prefixed with
    their namespace (e.g. SOSSISSE.INPUTS.OBJECTNAME).

    :return: dict(params=dict(key -> dict(description, dtype, default,
             options, user)), flavours=list (see probe_flavours))
    """
    from pogos.constants.constants import CDict
    from pogos.core import startup
    out: Dict[str, Dict[str, Any]] = dict()
    for key, const in CDict.storage.items():
        out[key] = _const_info(const)
    for namespace, cdict in startup.initial_setup().items():
        for key, const in cdict.storage.items():
            out['{0}.{1}'.format(namespace, key)] = _const_info(const)
    return dict(params=out, flavours=probe_flavours())


def probe_flavours() -> List[Dict[str, Any]]:
    """
    Get the reduction flavours (steps) with the constant sections each one
    uses (for the docs page flavour selector)

    :return: list of dict(name, level, prefixes) in workflow order - the
             first entry is the general POGOS section (GLOBAL / RUN)
    """
    from pogos.core import definitions
    out: List[Dict[str, Any]] = [dict(name='GENERAL', level='POGOS',
                                      prefixes=['GLOBAL', 'RUN'])]
    for step in definitions.RED_STEPS:
        own = list(step.sub_prefixes) or [step.parameter_prefix]
        out.append(dict(name=step.name, level=step.level.name,
                        prefixes=own + list(step.shared_prefixes)))
    return out


class _PlanParams(dict):
    """
    The few parameters the plan functions read (a plain dict with the
    ParamDict methods they use)
    """

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a value

        :param key: str, the parameter key
        :param default: the value if it is not set

        :return: the value
        """
        return dict.get(self, key, default)

    def __getitem__(self, key: str) -> Any:
        """
        Get a value (None if it is not set)

        :param key: str, the parameter key

        :return: the value
        """
        return dict.get(self, key)

    def rget(self, key: str, **kwargs: Any) -> Any:
        """
        Get a value (ParamDict.rget)

        :param key: str, the parameter key
        :param kwargs: ignored

        :return: the value
        """
        _ = kwargs
        return dict.get(self, key)

    def set(self, key: str, value: Any = None, **kwargs: Any) -> None:
        """
        Set a value (ParamDict.set)

        :param key: str, the parameter key
        :param value: the value
        :param kwargs: ignored

        :return: None
        """
        _ = kwargs
        self[key] = value


# the reduction steps whose plan depends on the instrument mode
MODE_PLANS = ['TSOVORE', 'PRE_JWST', 'EXT_JWST']


def probe_algorithms() -> Dict[str, Any]:
    """
    Get the algorithm steps (progress plans) of every reduction step - for
    the docs page (one plan per instrument mode where the steps depend on
    it)

    :return: dict(flavours=list of dict(name, level, plans=dict(mode or
             '' -> list of plan nodes)))
    """
    from pogos.core import definitions
    from pogos.core import progress_plans
    from pogos.core import recipe_helpers
    out = []
    for step in definitions.RED_STEPS:
        flavour = recipe_helpers.step_flavour(step)
        # SORBET runs WLCA / SLCA in one stage: show only this one
        base = dict({'RUN.SORBET.WLCA': step.name == 'SORBET.WLCA',
                     'RUN.SORBET.SLCA': step.name == 'SORBET.SLCA',
                     'STD_JWST.GENERAL.TESTMODE': False})
        modes = ['']
        if step.name in MODE_PLANS:
            modes = [mode.name for mode in step.supported_modes
                     if mode.enabled]
        plans = dict()
        for mode in modes:
            params = _PlanParams(base)
            if mode:
                params['GLOBAL.INSTRUMENTMODE'] = mode
                params['TSOVORE.INPUTS.INSTRUMENTMODE'] = mode
            plan = progress_plans.stage_plan(params, flavour)
            if plan:
                plans[mode] = plan
        out.append(dict(name=step.name, level=step.level.name,
                        plans=plans))
    return dict(flavours=out)


def main(argv: List[str]) -> int:
    """
    Run one probe and print its json result line

    :param argv: list of str, the command line arguments

    :return: int, the exit code (0 = success)
    """
    parser = argparse.ArgumentParser(description='POGOS gui probes')
    parser.add_argument('probe', choices=['demos', 'demo-counts', 'demos-all',
                                          'yaml-files',
                                          'reset-preview', 'params',
                                          'algorithms'])
    parser.add_argument('--instmode', default='')
    parser.add_argument('--steps', default='')
    parser.add_argument('--yamlfile', default='')
    args = parser.parse_args(argv)
    try:
        if args.probe == 'demos':
            steps = [step for step in args.steps.split(',') if step]
            result = probe_demos(args.instmode, steps)
        elif args.probe == 'yaml-files':
            result = probe_yaml_files(args.yamlfile)
        elif args.probe == 'demos-all':
            result = probe_demos_all([mode for mode in
                                      args.instmode.split(',') if mode])
        elif args.probe == 'demo-counts':
            result = probe_demo_counts()
        elif args.probe == 'params':
            result = probe_params()
        elif args.probe == 'algorithms':
            result = probe_algorithms()
        else:
            result = probe_reset(args.yamlfile)
    except BaseException as error:
        # SystemExit too: POGOS errors exit after logging
        result = dict(error='{0}: {1}'.format(type(error).__name__, error))
    sys.stdout.write('\n' + RESULT_PREFIX + json.dumps(result, default=str)
                     + '\n')
    sys.stdout.flush()
    return 0 if 'error' not in result else 1


# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

# =============================================================================
# End of code
# =============================================================================

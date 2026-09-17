import sys
import types


def _ensure_module(name: str) -> types.ModuleType:
    module = sys.modules.get(name)
    if module is None:
        module = types.ModuleType(name)
        sys.modules[name] = module
    return module


# Provide lightweight stubs so tests can import pogos modules without the
# optional runtime stack installed.
aperocore = _ensure_module("aperocore")
aperocore_constants = _ensure_module("aperocore.constants")
aperocore_core = _ensure_module("aperocore.core")

param_functions = _ensure_module("aperocore.constants.param_functions")
constant_functions = _ensure_module("aperocore.constants.constant_functions")
load_functions = _ensure_module("aperocore.constants.load_functions")


class ParamDict(dict):
    def set(self, key, value=None, source=None):
        self[key] = value


param_functions.ParamDict = ParamDict
aperocore_constants.param_functions = param_functions


class Const:
    pass


class ConstantsDict(dict):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.title = ""

    def yaml_title(self, title, setup_program=None, version=None, date=None):
        return title

    def add_group(self, *args, **kwargs):
        return None

    def add(self, key, value=None, **kwargs):
        self[key] = value


constant_functions.Const = Const
constant_functions.ConstantsDict = ConstantsDict
aperocore_constants.constant_functions = constant_functions


def get_all_params(**kwargs):
    return {}


def download_data(params, demolocal=None, demosymlink=False):
    return None


def get_param_file(params, key, name):
    return params[key]


def load_from_yaml(**kwargs):
    return kwargs['params']


load_functions.get_all_params = get_all_params
load_functions.download_data = download_data
load_functions.get_param_file = get_param_file
load_functions.load_from_yaml = load_from_yaml
load_functions._check_yaml_version = lambda *args, **kwargs: True
aperocore_constants.load_functions = load_functions


drs_log = _ensure_module("aperocore.core.drs_log")


class AperoCodedException(Exception):
    pass


class AperoCodedWarning(Warning):
    pass


def wlog(params, level, message, **kwargs):
    return None


wlog.minimal_params = lambda params: params
drs_log.AperoCodedException = AperoCodedException
drs_log.AperoCodedWarning = AperoCodedWarning
drs_log.MPARAMS = {"LOG.HEADER": "=="}
drs_log.wlog = wlog
aperocore_core.drs_log = drs_log


drs_misc = _ensure_module("aperocore.core.drs_misc")
drs_text = _ensure_module("aperocore.core.drs_text")

def display_func(name, module):
    return f"{module}.{name}"


drs_misc.display_func = display_func
aperocore_core.drs_misc = drs_misc


def user_input(prompt, dtype="str", required=False):
    return True


drs_text.user_input = user_input
aperocore_core.drs_text = drs_text


sossisse = _ensure_module("sossisse")
sossisse_core = _ensure_module("sossisse.core")
sossisse_constants = _ensure_module("sossisse.core.constants")
sossisse_misc = _ensure_module("sossisse.core.misc")
sossisse_const_funcs = _ensure_module("sossisse.core.const_funcs")
sossisse_exceptions = _ensure_module("sossisse.core.exceptions")
sossisse_recipes = _ensure_module("sossisse.recipes")
sossisse_run = _ensure_module("sossisse.recipes.run_sossisse")
sossisse_instruments = _ensure_module("sossisse.instruments")
sossisse_default = _ensure_module("sossisse.instruments.default")


class CDict(dict):
    pass


sossisse_constants.CDict = CDict
sossisse_core.constants = sossisse_constants


def art(text, *args, **kwargs):
    return text


def printc(*args, **kwargs):
    return None


class SossisseFileException(Exception):
    pass


def run_time_params(params, only_create=False):
    params.setdefault("PATHS.RAWPATH", "")
    params.setdefault("PATHS.CALIBPATH", "")
    return params


def run_sossisse_main(__YAML_DICT__=None):
    return {"ok": True, "params": __YAML_DICT__}


class Instrument:
    pass


sossisse_misc.art = art
sossisse_misc.printc = printc
sossisse_const_funcs.run_time_params = run_time_params
sossisse_exceptions.SossisseFileException = SossisseFileException
sossisse_run.main = run_sossisse_main
sossisse_default.Instrument = Instrument
sossisse_core.misc = sossisse_misc
sossisse_core.const_funcs = sossisse_const_funcs
sossisse_core.exceptions = sossisse_exceptions
sossisse_recipes.run_sossisse = sossisse_run
sossisse_instruments.default = sossisse_default
sossisse.recipes = sossisse_recipes
sossisse.instruments = sossisse_instruments
sossisse.core = sossisse_core


astropy = _ensure_module("astropy")
astropy_time = _ensure_module("astropy.time")


class _FakeTimeNow:
    unix = 1234567890.1234
    iso = "2026-01-01 00:00:00.000"


class Time:
    @staticmethod
    def now():
        return _FakeTimeNow()


astropy_time.Time = Time
astropy.time = astropy_time


# Stub heavyweight modules imported by package __init__ files.
stub_ts_general = _ensure_module("pogos.tsovore.core.general")
stub_ts_general.run_tsovore = lambda *args, **kwargs: None
stub_ts_general.setup_tsovore_module = lambda params: params

stub_miriam_general = _ensure_module("pogos.miriam.general.general")
stub_miriam_general.run_miriam = lambda *args, **kwargs: None
stub_miriam_general.setup_miriam_module = lambda params: params
stub_miriam_pkg = _ensure_module("pogos.miriam.general")
stub_miriam_pkg.general = stub_miriam_general

stub_sorbet_general = _ensure_module("pogos.sorbet.general.general")
stub_sorbet_general.any_sorbet_run = lambda params: False
stub_sorbet_general.run_sorbet_module = lambda *args, **kwargs: None
stub_sorbet_general.setup_sorbet_module = lambda params: params
stub_sorbet_pkg = _ensure_module("pogos.sorbet.general")
stub_sorbet_pkg.general = stub_sorbet_general

stub_ts_default = _ensure_module("pogos.tsovore.instruments.default")


class JWST:
    pass


stub_ts_default.JWST = JWST


# Startup imports CRDS and other heavy dependencies; provide a light stub for
# recipe orchestration tests.
stub_startup = _ensure_module("pogos.core.startup")
stub_startup.quick_args = lambda argv: False
stub_startup.initial_setup = lambda: {}
stub_startup.setup = lambda params, start_from_demo=True: {"cdict": True}
stub_startup.check_crds = lambda params: None
stub_startup.check_red_steps = lambda params: None
stub_startup.check_instrument_modes = lambda params: None
stub_startup.copy_ask_description = lambda params: params
stub_startup.copy_ask_subdirectories = lambda params: params
stub_startup.copy_clear_files = lambda params: {}
stub_startup.copy_ask_req_module_params = lambda params: params


# Recipes import pogos.constants at module import time; provide a minimal stub
# to avoid pulling optional runtime dependencies.
stub_pogos_constants_pkg = _ensure_module("pogos.constants")
stub_pogos_constants_mod = _ensure_module("pogos.constants.constants")
stub_pogos_constants_mod.ConstDict = ConstantsDict
stub_pogos_constants_mod.CDict = ConstantsDict("pogos.constants.constants")
stub_pogos_constants_pkg.constants = stub_pogos_constants_mod



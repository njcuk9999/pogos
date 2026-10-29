from types import SimpleNamespace

from aperocore.constants.param_functions import ParamDict

from pogos.sossisse_wrap.core import core


class FakeSubParams(dict):
    def as_param_dict(self):
        return ParamDict(self)


def test_tsovore_input_copies_outputs_and_calib_files(tmp_path, monkeypatch):
    raw_dir = tmp_path / "sossisse_raw"
    calib_dir = tmp_path / "sossisse_calib"
    raw_dir.mkdir()
    calib_dir.mkdir()

    out_file = tmp_path / "seg1_rateints.fits"
    out_file.write_text("out")
    calib_file = tmp_path / "wave_x1d.fits"
    calib_file.write_text("calib")

    params = ParamDict({
        'GLOBAL.PROJECT_NAME': 'shared-project',
        'GLOBAL.DATA_PATH': str(tmp_path),
        "SOSSISSE": FakeSubParams(
            {
                'INPUTS.PROJECT_NAME': 'ignored-module-name',
                'INPUTS.SOSSIOPATH': '/ignored/module/root',
                "GENERAL.FILES": [],
                "GENERAL.WAVE_FILE": None,
                "GENERAL.WAVE_FILE_TYPE": None,
                "PATHS.RAWPATH": str(raw_dir),
                "PATHS.CALIBPATH": str(calib_dir),
            }
        )
    })

    def run_time_params(sparams, only_create=False):
        assert only_create is True
        assert sparams['INPUTS.PROJECT_NAME'] == 'shared-project'
        assert sparams['INPUTS.SOSSIOPATH'] == str(tmp_path)
        return sparams

    monkeypatch.setattr(core.const_funcs, 'run_time_params', run_time_params)

    class FakeTsovoreInst:
        variables = {
            "OUT": [str(out_file)],
            "CALIBS": {"X1D": str(calib_file)},
        }

    updated = core.tsovore_input(params, FakeTsovoreInst())

    copied_output = raw_dir / out_file.name
    copied_calib = calib_dir / calib_file.name

    assert copied_output.exists()
    assert copied_calib.exists()
    assert updated["GENERAL.FILES"] == [str(out_file)]
    assert updated["GENERAL.WAVE_FILE"] == calib_file.name
    assert updated["GENERAL.WAVE_FILE_TYPE"] == "ext_1d"
    assert updated['INPUTS.PROJECT_NAME'] == 'shared-project'
    assert updated['INPUTS.SOSSIOPATH'] == str(tmp_path)


def test_run_sossisse_forwards_global_identity(tmp_path, monkeypatch):
    params = ParamDict({
        'RUN.SOSSISSE': True,
        'GLOBAL.PROJECT_NAME': 'shared-project',
        'GLOBAL.DATA_PATH': str(tmp_path),
        'GLOBAL.YAML_FILE': str(tmp_path / 'profile.yaml'),
        'SOSSISSE': FakeSubParams({
            'INPUTS.PROJECT_NAME': 'ignored-module-name',
            'INPUTS.SOSSIOPATH': '/ignored/module/root',
            'PATHS.RAWPATH': str(tmp_path / 'external-raw'),
        }),
    })
    monkeypatch.setattr(core.sossisse_run, 'main',
                        lambda __YAML_DICT__: __YAML_DICT__)

    forwarded = core.run_sossisse_module(params, pre_inst={})

    assert forwarded['INPUTS.PROJECT_NAME'] == 'shared-project'
    assert forwarded['INPUTS.SOSSIOPATH'] == str(tmp_path)
    assert forwarded['INPUTS.PARAM_FILE'] == str(tmp_path / 'profile.yaml')
    assert forwarded['PATHS.RAWPATH'] == str(tmp_path / 'external-raw')


def test_setup_sossisse_forwards_global_identity_and_run_path(
        tmp_path, monkeypatch):
    run_path = tmp_path / 'projects' / 'shared-project' / 'sossisse'
    params = ParamDict({
        'RUN.SOSSISSE': True,
        'GLOBAL.PROJECT_NAME': 'shared-project',
        'GLOBAL.DATA_PATH': str(tmp_path),
        'GLOBAL.YAML_FILE': str(tmp_path / 'profile.yaml'),
        'GLOBAL.INSTRUMENTMODE': 'JWST.NIRISS.SOSS',
        'SOSSISSE': FakeSubParams({
            'INPUTS.PROJECT_NAME': 'ignored-module-name',
            'INPUTS.SOSSIOPATH': '/ignored/module/root',
        }),
        'SOSSISSE.PATHS.RUN_PATH': None,
    })

    def get_parameters(**setup_options):
        forwarded = setup_options['__YAML_DICT__']
        assert forwarded['INPUTS.PROJECT_NAME'] == 'shared-project'
        assert forwarded['INPUTS.SOSSIOPATH'] == str(tmp_path)
        assert forwarded['INPUTS.PARAM_FILE'] == str(tmp_path / 'profile.yaml')
        return SimpleNamespace(params={'PATHS': {'RUN_PATH': str(run_path)}})

    saved = []
    cdict = SimpleNamespace(save_yaml=lambda *values, **options: saved.append(
        options['outpath']))
    monkeypatch.setattr(core.sossisse, 'get_parameters', get_parameters,
                        raising=False)

    assert core.setup_sossisse_module(params, cdict) is params
    assert params['SOSSISSE.PATHS.RUN_PATH'] == str(run_path)
    assert params['GLOBAL.PROJECT_NAME'] == 'shared-project'
    assert saved == [str(tmp_path / 'profile.yaml')]


def test_run_sossisse_module_returns_early_when_disabled():
    params = {"RUN.SOSSISSE": False}

    assert core.run_sossisse_module(params, pre_inst={}) is None


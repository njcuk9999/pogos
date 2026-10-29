import pytest

from aperocore.constants.param_functions import ParamDict

from pogos.eureka_wrap.core import general as eureka_general
from pogos.jwst_wrap.core import general


class DummyPipeline:
    pass


@pytest.mark.parametrize('module, prefix, make_dirs', [
    ('jwst', 'STD_JWST', general.make_jwst_dirs),
    ('eureka', 'EUREKA', eureka_general.make_eureka_dirs),
])
def test_stage_dirs_use_global_project_and_absolute_override(
        tmp_path, module, prefix, make_dirs):
    absolute_output = tmp_path / 'external'
    params = ParamDict({
        'GLOBAL.DATA_PATH': str(tmp_path),
        'GLOBAL.PROJECT_NAME': 'shared-project',
        f'{prefix}.STAGE1.inputdir': 'input',
        f'{prefix}.STAGE1.outputdir': str(absolute_output),
    })

    make_dirs(params, stage=1)

    topdir = tmp_path / 'projects' / 'shared-project' / module
    assert params[f'{prefix}.STAGE1.topdir'] == str(topdir)
    assert params[f'{prefix}.PATHS.IN_S1_PATH'] == str(topdir / 'input')
    assert params[f'{prefix}.PATHS.OUT_S1_PATH'] == str(absolute_output)
    assert (topdir / 'input').is_dir()
    assert absolute_output.is_dir()


def test_eureka_late_stage_paths_use_global_project(tmp_path):
    absolute_output = tmp_path / 'external'
    params = ParamDict({
        'GLOBAL.DATA_PATH': str(tmp_path),
        'GLOBAL.PROJECT_NAME': 'shared-project',
        'EUREKA.STAGE4.inputdir': 'Stage3',
        'EUREKA.STAGE4.outputdir': str(absolute_output),
    })

    topdir = tmp_path / 'projects' / 'shared-project' / 'eureka'
    assert eureka_general._eureka_stage_input_dir(params, 4) == str(
        topdir / 'Stage3')
    assert eureka_general._eureka_stage_output_dir(params, 4) == str(
        absolute_output)


def test_get_pipeline_class_returns_class_for_supported_mode():
    params = {"GLOBAL.INSTRUMENTMODE": "JWST.NIRISS.SOSS"}
    pipelines = {"Spec2Pipeline": DummyPipeline}

    pipe_class = general.get_pipeline_class(params, stage=2, pipelines=pipelines)

    assert pipe_class is DummyPipeline


def test_get_pipeline_class_returns_none_for_unknown_mode():
    params = {"GLOBAL.INSTRUMENTMODE": "UNKNOWN.MODE"}
    pipelines = {"Spec2Pipeline": DummyPipeline}

    pipe_class = general.get_pipeline_class(params, stage=2, pipelines=pipelines)

    assert pipe_class is None


def test_jwst_result_builds_uniform_result_dict():
    params = {"STD_JWST.PATHS.OUT_S3_PATH": "/tmp/stage3"}

    result = general._jwst_result(params, stage=3)

    assert result == {
        "module": "jwst",
        "output_dir": "/tmp/stage3",
        "output_files": [],
        "stage": 3,
    }


def test_jwst_unique_id_format(monkeypatch):
    monkeypatch.setattr(
        general.pogos_general,
        "unix_char_code",
        lambda: (9876, "ignored", "WXYZ"),
    )

    unique_id = general.jwst_unique_id()

    assert unique_id == "JID-00000000000000009876-WXYZ"


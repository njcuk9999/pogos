from pogos.jwst_wrap.core import general


class DummyPipeline:
    pass


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
    params = {"JWST.PATHS.OUT_S3_PATH": "/tmp/stage3"}

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


from pogos.core.general import make_step_result
from pogos.nameless_wrap.core import general


def test_check_soss_returns_true_for_supported_mode():
    params = {"GLOBAL.INSTRUMENTMODE": "JWST.NIRISS.SOSS"}
    assert general.check_soss(params) is True


def test_check_soss_returns_false_for_unsupported_mode():
    params = {"GLOBAL.INSTRUMENTMODE": "JWST.MIRI.IMAGING"}
    assert general.check_soss(params) is False


def test_discover_files_autodetects_handle_segments_and_count(tmp_path):
    prefix = "P" * 29
    (tmp_path / f"{prefix}001_uncal.fits").write_text("a")
    (tmp_path / f"{prefix}002_uncal.fits").write_text("b")
    params = {
        "NAMELESS.GENERAL.HANDLE": None,
        "NAMELESS.GENERAL.NSEG": None,
        "NAMELESS.GENERAL.SEGS": None,
    }

    handle, nseg, segs = general.discover_files(params, str(tmp_path))

    assert handle == "P" * 25
    assert nseg == 2
    assert segs == ["001", "002"]


def test_discover_files_returns_none_when_no_uncal_files(tmp_path):
    params = {
        "NAMELESS.GENERAL.HANDLE": None,
        "NAMELESS.GENERAL.NSEG": None,
        "NAMELESS.GENERAL.SEGS": None,
    }

    assert general.discover_files(params, str(tmp_path)) is None


def test_nameless_unique_id_format(monkeypatch):
    monkeypatch.setattr(
        general.pogos_general,
        "unix_char_code",
        lambda: (1234, "ignored", "ABCD"),
    )

    unique_id = general.nameless_unique_id()

    assert unique_id == "NID-00000000000000001234-ABCD"


def test_make_step_result_can_be_used_as_uniform_payload():
    result = make_step_result("nameless", "/tmp/top", output_files=["x.fits"])
    assert result == {
        "module": "nameless",
        "output_dir": "/tmp/top",
        "output_files": ["x.fits"],
    }


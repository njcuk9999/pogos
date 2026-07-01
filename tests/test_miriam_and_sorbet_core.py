from pogos.miriam.core import general as miriam_general
from pogos.sorbet.core import core as sorbet_core


def test_miriam_unique_id_format(monkeypatch):
    monkeypatch.setattr(
        miriam_general.pogos_general,
        "unix_char_code",
        lambda: (42, "ignored", "ABCD"),
    )

    uid = miriam_general.miriam_unique_id()

    assert uid == "MID-00000000000000000042-ABCD"


def test_sorbet_unique_id_format(monkeypatch):
    monkeypatch.setattr(
        sorbet_core.pogos_general,
        "unix_char_code",
        lambda: (31415, "ignored", "WXYZ"),
    )

    uid = sorbet_core.sorbet_unique_id()

    assert uid == "SBID-00000000000000031415-WXYZ"


def test_sorbet_inst_mode_normalizes_underscores():
    params = {"GLOBAL.INSTRUMENTMODE": "jwst_niriss_soss"}

    assert sorbet_core.sorbet_inst_mode(params) == "JWST.NIRISS.SOSS"


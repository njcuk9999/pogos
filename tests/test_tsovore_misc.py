import pytest

from pogos.core import definitions
from pogos.tsovore.core import misc as ts_misc


class DummyConstDict:
    def __init__(self):
        self.calls = []

    def add(self, **kwargs):
        self.calls.append(kwargs)


def test_step_list_not_modes_excludes_rejected_mode():
    modes = ts_misc.StepList.not_modes("JWST.NIRISS.SOSS")

    assert definitions.NIRISS_SOSS not in modes
    assert len(modes) == len(definitions.ENABLED_INST_MODES) - 1


def test_step_rejects_unknown_mode():
    with pytest.raises(ts_misc.pogos_base.PogosException):
        ts_misc.Step(
            name="demo",
            flavour="jwst",
            fname="_uncal.fits",
            ftype="suffix",
            modes=["NOT.A.REAL.MODE"],
        )


def test_step_cdict_kwargs_omits_modes_when_all_modes_enabled():
    step = ts_misc.Step(
        name="demo",
        flavour="jwst",
        fname="_uncal.fits",
        ftype="suffix",
    )

    kwargs = step.cdict_kwargs(source="unit", group="TEST")

    assert kwargs["name"] == "DEMO"
    assert "modes" not in kwargs


def test_step_list_to_cdict_pushes_each_step():
    steps = ts_misc.StepList()
    steps.add_step("first", "jwst", "_a.fits", "suffix")
    steps.add_step("second", "jwst", "_b.fits", "suffix")
    cdict = DummyConstDict()

    steps.to_cdict(cdict, source="unit", group="TEST")

    assert len(cdict.calls) == 2
    assert cdict.calls[0]["name"] == "FIRST"
    assert cdict.calls[1]["name"] == "SECOND"


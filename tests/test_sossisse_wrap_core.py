from aperocore.constants.param_functions import ParamDict

from pogos.sossisse_wrap.core import core


class FakeSubParams(dict):
    def as_param_dict(self):
        return ParamDict(self)


def test_tsovore_input_copies_outputs_and_calib_files(tmp_path):
    raw_dir = tmp_path / "sossisse_raw"
    calib_dir = tmp_path / "sossisse_calib"
    raw_dir.mkdir()
    calib_dir.mkdir()

    out_file = tmp_path / "seg1_rateints.fits"
    out_file.write_text("out")
    calib_file = tmp_path / "wave_x1d.fits"
    calib_file.write_text("calib")

    params = {
        "SOSSISSE": FakeSubParams(
            {
                "GENERAL.FILES": [],
                "GENERAL.WAVE_FILE": None,
                "GENERAL.WAVE_FILE_TYPE": None,
                "PATHS.RAWPATH": str(raw_dir),
                "PATHS.CALIBPATH": str(calib_dir),
            }
        )
    }

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


def test_run_sossisse_module_returns_early_when_disabled():
    params = {"RUN.SOSSISSE": False}

    assert core.run_sossisse_module(params, pre_inst={}) is None


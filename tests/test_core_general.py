from pathlib import Path

from pogos.core import general


def test_make_step_result_includes_expected_fields():
    files = ["a.fits", "b.fits"]
    result = general.make_step_result(
        module="jwst", output_dir="/tmp/out", output_files=files, stage=2
    )

    assert result["module"] == "jwst"
    assert result["output_dir"] == "/tmp/out"
    assert result["output_files"] == files
    assert result["stage"] == 2
    assert result["output_files"] is not files


def test_step_output_files_uses_explicit_file_list(tmp_path):
    explicit = [str(tmp_path / "first.fits"), str(tmp_path / "second.fits")]
    out_dir, files = general.step_output_files(
        {"output_dir": str(tmp_path), "output_files": explicit}
    )

    assert out_dir == str(tmp_path)
    assert files == explicit


def test_step_output_files_falls_back_to_glob(tmp_path):
    (tmp_path / "one.fits").write_text("x")
    (tmp_path / "two.fits").write_text("x")
    (tmp_path / "ignore.txt").write_text("x")

    out_dir, files = general.step_output_files(
        {"output_dir": str(tmp_path), "output_files": []}
    )

    assert out_dir == str(tmp_path)
    assert files == sorted(
        [str(tmp_path / "one.fits"), str(tmp_path / "two.fits")]
    )


def test_route_step_inputs_copies_files_from_previous_step(tmp_path):
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir()
    dst.mkdir()
    fits_file = src / "s2_cal.fits"
    fits_file.write_text("fits-data")

    instances = {
        "pre_jwst": {
            "output_dir": str(src),
            "output_files": [str(fits_file)],
        }
    }

    general.route_step_inputs({}, instances, str(dst))

    copied = dst / fits_file.name
    assert copied.exists()
    assert copied.read_text() == "fits-data"


def test_route_step_inputs_skips_copy_when_source_matches_destination(tmp_path):
    src = tmp_path / "shared"
    src.mkdir()
    fits_file = src / "existing.fits"
    fits_file.write_text("already-here")

    instances = {
        "pre_jwst": {
            "output_dir": str(src),
            "output_files": [str(fits_file)],
        }
    }

    before = {p.name: p.read_text() for p in Path(src).glob("*.fits")}
    general.route_step_inputs({}, instances, str(src))
    after = {p.name: p.read_text() for p in Path(src).glob("*.fits")}

    assert before == after


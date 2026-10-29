from pathlib import Path
import subprocess
import sys
import textwrap

import pytest

from pogos.core import general


MODULE_NAMES = ['eureka', 'jwst', 'nameless', 'tsovore', 'miriam',
                'sorbet']


def run_directory_check(tmp_path, code):
    preamble = '''
from pathlib import Path
from aperocore.constants.param_functions import ParamDict
from pogos.core import base, general

def directory_params(data_path, project_name, path_value):
    params = ParamDict()
    params.set('GLOBAL.DATA_PATH', value=str(data_path), source='test')
    params.set('GLOBAL.PROJECT_NAME', value=project_name, source='test')
    params.set('TEST.PATH', value=path_value, source='test')
    return params
'''
    result = subprocess.run(
        [sys.executable, '-c', preamble + textwrap.dedent(code)],
        cwd=tmp_path, capture_output=True, text=True, timeout=90)
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize('module_name', MODULE_NAMES)
@pytest.mark.parametrize('path_value', [None, 'products'])
@pytest.mark.parametrize('relative_data_path', [False, True])
def test_prepare_directory_project_paths(tmp_path, module_name,
                                         path_value, relative_data_path):
    run_directory_check(tmp_path, f'''
        root = Path.cwd()
        (root / 'products').mkdir()
        data_path = ('storage/../storage' if {relative_data_path!r}
                     else root / 'storage')
        params = directory_params(data_path, 'project-1+v.2_test', {path_value!r})
        folder_name = 'output' if {path_value!r} is None else {path_value!r}
        expected = (root / 'storage' / 'projects' / 'project-1+v.2_test'
                    / {module_name!r} / folder_name)
        general.prepare_directory(params, 'output', 'TEST.PATH', {module_name!r})
        assert params['TEST.PATH'] == str(expected)
        assert expected.is_dir()
        marker = expected / 'keep.txt'
        marker.write_text('preserved')
        general.prepare_directory(params, 'output', 'TEST.PATH', {module_name!r},
                                  verbose=False)
        assert params['TEST.PATH'] == str(expected)
        assert marker.read_text() == 'preserved'
        assert not (root / 'products' / 'keep.txt').exists()
    ''')


@pytest.mark.parametrize('module_name', MODULE_NAMES)
@pytest.mark.parametrize('existing', [False, True])
def test_prepare_directory_absolute_override(tmp_path, module_name, existing):
    run_directory_check(tmp_path, f'''
        root = Path.cwd()
        override = root / 'override'
        if {existing!r}:
            override.mkdir()
        params = directory_params(root / 'storage', 'project', str(override))
        general.prepare_directory(params, 'output', 'TEST.PATH', {module_name!r})
        assert params['TEST.PATH'] == str(override)
        assert override.is_dir()
        assert not (root / 'storage').exists()
    ''')


@pytest.mark.parametrize('module_name', MODULE_NAMES)
def test_prepare_directory_isolates_projects(tmp_path, module_name):
    run_directory_check(tmp_path, f'''
        root = Path.cwd()
        resolved_paths = []
        for project_name in ['first', 'second']:
            params = directory_params(root, project_name, 'products')
            general.prepare_directory(params, 'output', 'TEST.PATH',
                                      {module_name!r})
            resolved = Path(params['TEST.PATH'])
            expected = root / 'projects' / project_name / {module_name!r} / 'products'
            assert resolved == expected
            assert resolved.is_dir()
            resolved_paths.append(resolved)
        assert resolved_paths[0] != resolved_paths[1]
    ''')


@pytest.mark.parametrize('project_name', [
    '', '.', '..', '../escape', '/absolute', 'nested/project', 'nested\\project',
    'white space', 'tab\tname', 'line\nname', 'null\x00name', 'bad:name', 123,
])
def test_prepare_directory_rejects_unsafe_project_name(tmp_path, project_name):
    run_directory_check(tmp_path, f'''
        root = Path.cwd()
        params = directory_params(root, {project_name!r}, None)
        try:
            general.prepare_directory(params, 'output', 'TEST.PATH', 'miriam')
        except base.PogosException as error:
            assert 'GLOBAL.PROJECT_NAME' in str(error)
        else:
            raise AssertionError('Unsafe project name was accepted')
        assert not (root / 'projects').exists()
    ''')


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


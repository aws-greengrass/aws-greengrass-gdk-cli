import logging
from pathlib import Path

import pytest
from urllib3.exceptions import HTTPError

import gdk.common.utils as utils


def test_get_static_file_path_exists(mocker):

    mock_is_file = mocker.patch("pathlib.Path.is_file", return_value=True)
    file_name = ""

    file_path = Path(".")
    mock_file_path = mocker.patch("pathlib.Path.resolve", return_value=file_path)

    assert utils.get_static_file_path(file_name) == file_path
    assert mock_is_file.called
    assert mock_file_path.called


def test_get_static_file_path_not_exists(mocker):
    mock_is_file = mocker.patch("pathlib.Path.is_file", return_value=False)
    file_name = ""

    file_path = Path(".")
    mock_file_path = mocker.patch("pathlib.Path.resolve", return_value=file_path)

    assert not utils.get_static_file_path(file_name)
    assert mock_file_path.called
    assert mock_is_file.called


def test_is_directory_empty_with_empty_dir(mocker):
    mock_is_dir = mocker.patch("pathlib.Path.is_dir", return_value=True)
    mock_iterdir = mocker.patch("pathlib.Path.iterdir", return_value=[])
    dir_path = ""

    assert utils.is_directory_empty(dir_path)
    assert mock_is_dir.call_count == 1
    assert mock_iterdir.call_count == 1


def test_is_directory_empty_with_empty_but_no_dir(mocker):
    mock_is_dir = mocker.patch("pathlib.Path.is_dir", return_value=False)
    mock_iterdir = mocker.patch("pathlib.Path.iterdir", return_value=[])
    dir_path = ""

    assert not utils.is_directory_empty(dir_path)
    assert mock_is_dir.call_count == 1
    assert mock_iterdir.call_count == 0


def test_is_directory_empty_with_non_empty_dir(mocker):
    mock_is_dir = mocker.patch("pathlib.Path.is_dir", return_value=True)
    mock_iterdir = mocker.patch("pathlib.Path.iterdir", return_value=[1])
    dir_path = ""

    assert not utils.is_directory_empty(dir_path)
    assert mock_is_dir.call_count == 1
    assert mock_iterdir.call_count == 1


def test_file_exists_valid(mocker):
    mock_is_file = mocker.patch("pathlib.Path.is_file", return_value=True)
    file_path = Path(".")
    assert utils.file_exists(file_path)
    assert mock_is_file.call_count == 1


def test_file_exists_not_a_file(mocker):
    mock_is_file = mocker.patch("pathlib.Path.is_file", return_value=False)
    file_path = Path(".")
    assert not utils.file_exists(file_path)
    assert mock_is_file.call_count == 1


def test_file_exists_exception(mocker):
    mock_is_file = mocker.patch("pathlib.Path.is_file", return_value=True, side_effect=HTTPError("some error"))
    file_path = Path(".")
    assert not utils.file_exists(file_path)
    assert mock_is_file.call_count == 1


def test_dir_exists_valid(mocker):
    mock_is_dir = mocker.patch("pathlib.Path.is_dir", return_value=True)
    dir_path = Path(".")
    assert utils.dir_exists(dir_path)
    assert mock_is_dir.call_count == 1


def test_dir_exists_not_a_dir(mocker):
    mock_is_dir = mocker.patch("pathlib.Path.is_dir", return_value=False)
    dir_path = Path(".")
    assert not utils.dir_exists(dir_path)
    assert mock_is_dir.call_count == 1


def test_dir_exists_exception(mocker):
    mock_is_dir = mocker.patch("pathlib.Path.is_dir", return_value=True, side_effect=HTTPError("some error"))
    dir_path = Path(".")
    assert not utils.dir_exists(dir_path)
    assert mock_is_dir.call_count == 1


def test_clean_dir(mocker):
    mock_rm = mocker.patch("shutil.rmtree")
    path = Path().resolve()
    utils.clean_dir(path)
    mock_rm.call_count == 1


def test_get_latest_cli_version(mocker):
    res_text = '__version__ = "10.0.0"\n'
    mock_response = mocker.Mock(status_code=200, text=res_text)
    mock_get_version = mocker.patch("requests.get", return_value=mock_response)

    assert utils.get_latest_cli_version() == "10.0.0"
    assert mock_get_version.called


def test_get_latest_cli_version_invalid_version(mocker):
    res_text = '__versions__ = "10.0.0"\n'
    mock_response = mocker.Mock(status_code=200, text=lambda: res_text)
    mock_get_version = mocker.patch("requests.get", return_value=mock_response)
    version = utils.get_latest_cli_version()
    assert version == utils.cli_version
    assert mock_get_version.called


def test_get_latest_cli_version_invalid_request(mocker):
    res_text = "__version__ = 1.0.0"
    mock_response = mocker.Mock(status_code=200, text=lambda: res_text)
    mock_get_version = mocker.patch("requests.get", return_value=mock_response, side_effect=HTTPError("hi"))
    # Since the request failed, it'll be the version of the cli tool installed.
    assert utils.get_latest_cli_version() == utils.cli_version
    assert mock_get_version.called


def test_cli_version_check_latest_not_available(mocker):
    mock_get_latest_cli_version = mocker.patch("gdk.common.utils.get_latest_cli_version", return_value=utils.cli_version)
    spy_log = mocker.spy(logging, "info")
    utils.cli_version_check()
    assert mock_get_latest_cli_version.called
    assert spy_log.call_count == 0


def test_cli_version_check_latest_available(mocker):
    mock_get_latest_cli_version = mocker.patch("gdk.common.utils.get_latest_cli_version", return_value="1000.0.0")
    spy_log = mocker.spy(logging, "info")
    utils.cli_version_check()
    assert mock_get_latest_cli_version.called
    assert spy_log.call_count == 1


@pytest.mark.parametrize(
    "version",
    [
        "1.0.0",
        "1.0.0-alpha+meta",
        "1.0.0-alpha",
        "1.0.0-alpha.beta",
        "1.0.0-alpha.beta.1",
        "1.0.0-alpha.123",
        "1.0.0-alpha0.valid",
        "1.0.0-alpha.0valid",
        "1.0.0-alpha-a.b-c-somethinglong+build.1-aef.1-its-okay",
        "1.0.0-rc.1+build.123",
        "1.0.0-DEV-SNAPSHOT",
        "1.0.0+meta",
        "1.0.0+meta-valid",
        "1.0.0+build.1848",
        "1.0.0-alpha+beta",
        "1.0.0----RC-SNAPSHOT.12.9.1--.12+788",
        "1.0.0----R-S.12.9.1--.12+meta",
        "1.0.0----RC-SNAPSHOT.12.9.1--.12",
        "1.0.0+0.build.1-rc.10000aaa-kk-0.1",
        "1.0.0-0A.is.legal",
    ],
)
def test_get_next_patch_version(version):
    assert utils.get_next_patch_version(version) == "1.0.1"


def test_valid_recipe_size(mocker):
    mock_response = mocker.Mock(st_size=1000)
    mocker.patch("pathlib.Path.stat", return_value=mock_response)
    is_valid_size, file_size = utils.is_recipe_size_valid('small_recipe.json')
    assert is_valid_size
    assert file_size == 1000


def test_invalid_recipe_size(mocker):
    mock_response = mocker.Mock(st_size=17000)
    mocker.patch("pathlib.Path.stat", return_value=mock_response)
    is_valid_size, file_size = utils.is_recipe_size_valid('large_recipe.yaml')
    assert not is_valid_size
    assert file_size == 17000

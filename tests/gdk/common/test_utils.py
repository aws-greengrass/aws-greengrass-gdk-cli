import json
import logging
from pathlib import Path

import jsonschema
import pytest
import yaml
from urllib3.exceptions import HTTPError

import gdk.common.utils as utils
from gdk.common.exceptions import syntax_error_message


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


def test_parse_json_error(caplog):
    error_message = "Expecting property name enclosed in double quotes: line 1 column 3 (char 2)"
    utils.parse_json_error(json.JSONDecodeError(error_message, "", 1))
    assert "Expecting property name enclosed in double quotes" in caplog.text
    assert "line 1" in caplog.text
    assert "This might be caused by one of the following reasons: " in caplog.text
    assert "the key is not enclosed in double quotes" in caplog.text
    assert "missing opening or closing quotes for key or value" in caplog.text
    assert "unexpected characters or tokens present" in caplog.text
    assert "trailing comma after the last key-value pair" in caplog.text
    assert "Please review the overall JSON syntax and resolve any issues." in caplog.text


def test_parse_json_error_not_in_list(caplog):
    error_message = "This is a new error message that not in maintained list: line 1 column 3 (char 2)"
    utils.parse_json_error(json.JSONDecodeError(error_message, "", 1))
    assert "The error occurs around line 1: " in caplog.text
    assert "This might be caused by one of the following reasons: " not in caplog.text
    assert "If none of the above is the cause," not in caplog.text
    assert "Please review the overall JSON syntax and resolve any issues." in caplog.text


def test_parse_yaml_error(caplog):
    error_message = "mapping values are not allowed here: line 3, column 1"
    err = yaml.scanner.ScannerError(None, None, error_message)
    utils.parse_yaml_error(err)
    assert "mapping values are not allowed here" in caplog.text
    assert "This might be caused by one of the following reasons: " in caplog.text
    assert "missing colon in the line above" in caplog.text
    assert "missing mandatory space after the colon in the line above" in caplog.text
    assert "Please review the overall YAML syntax and resolve any issues." in caplog.text


def test_parse_yaml_error_not_in_list(caplog):
    error_message = "new error message"
    err = yaml.scanner.ScannerError(None, None, error_message)
    utils.parse_yaml_error(err)
    assert "This might be caused by one of the following reasons: " not in caplog.text
    assert "If none of the above is the cause," not in caplog.text
    assert "Please review the overall YAML syntax and resolve any issues." in caplog.text


def test_parse_json_schema_errors(caplog):
    error_message = "Error message"
    error = jsonschema.exceptions.ValidationError(error_message)
    utils.parse_json_schema_errors(error)
    assert error_message in caplog.text


def test_parse_json_schema_errors_with_validator_value(caplog):
    error_message = "Error message"
    validator = "required"
    validator_value = "property_name"
    error = jsonschema.exceptions.ValidationError(error_message, validator=validator, validator_value=validator_value)
    utils.parse_json_schema_errors(error)
    assert error_message in caplog.text
    assert f"Validation failed for '{validator}: {validator_value}'" in caplog.text


def test_parse_json_schema_errors_with_instance(caplog):
    error_message = "Error message"
    instance = {'property_name': 'property_value'}
    error = jsonschema.exceptions.ValidationError(error_message, instance=instance)
    utils.parse_json_schema_errors(error)
    assert error_message in caplog.text
    assert f"On instance: '{instance}'" in caplog.text


def test_parse_json_schema_errors_with_known_validator(caplog):
    validator = "type"
    error = jsonschema.exceptions.ValidationError("", validator=validator)
    utils.parse_json_schema_errors(error)
    assert "This validation error may be due to: " in caplog.text
    for cause in syntax_error_message.JSON_SCHEMA_VALIDATION_KEYWORDS[validator]["causes"]:
        assert f"\t {cause}" in caplog.text
    assert "To address this issue, consider the following steps: " in caplog.text
    for fix in syntax_error_message.JSON_SCHEMA_VALIDATION_KEYWORDS[validator]["fixes"]:
        assert f"\t {fix}" in caplog.text


def test_parse_json_schema_errors_with_unknown_validator(caplog):
    validator = "unknown_validator"
    error = jsonschema.exceptions.ValidationError("", validator=validator)
    utils.parse_json_schema_errors(error)
    assert "This validation error may be due to: " not in caplog.text
    assert "To address this issue, consider the following steps: " not in caplog.text


def test_parse_json_schema_errors_show_recipe_reference_url(caplog):
    validator = "type"
    error = jsonschema.exceptions.ValidationError("", validator=validator)
    utils.parse_json_schema_errors(error)
    assert "For more guidance, visit the Greengrass Component Recipe Reference documentation at" in caplog.text


def test_valid_recipe_size(mocker):
    mocker.patch("os.path.getsize", return_value=1000)
    result = utils.valid_recipe_file_size('small_recipe.json')
    assert result


def test_invalid_recipe_size(mocker):
    mocker.patch("os.path.getsize", return_value=17000)
    result = utils.valid_recipe_file_size('large_recipe.yaml')
    assert not result

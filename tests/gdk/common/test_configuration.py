from pathlib import Path

import gdk.common.configuration as config
import gdk.common.consts as consts
import gdk.common.exceptions.error_messages as error_messages
import gdk.common.utils as utils
import pytest


def test_get_configuration_valid_component_config_found(mocker):
    expected_config = {
        "component": {
            "1": {
                "author": "abc",
                "version": "1.0.0",
                "build": {"build_system": "zip"},
                "publish": {"bucket": "default", "region": "us-east-1"},
            }
        },
        "gdk_version": "1.0.0",
    }

    mock_get_project_config_file = mocker.patch(
        "gdk.common.configuration._get_project_config_file",
        return_value=Path(".").joinpath("tests/gdk/static").joinpath("config.json"),
    )
    assert config.get_configuration() == expected_config
    assert mock_get_project_config_file.called


@pytest.mark.parametrize(
    "file_name",
    [
        "invalid_config.json",
        "invalid_case_config.json",
        "invalid_version_config.json",
        "invalid_multiple_components.json",
        "invalid_build_command.json",
        "invalid_build_command_string.json",
        "invalid_build_command_array.json",
        "invalid_region_config.json",
    ],
)
def test_get_configuration_invalid_config_file(mocker, file_name):
    mock_get_project_config_file = mocker.patch(
        "gdk.common.configuration._get_project_config_file",
        return_value=Path(".").joinpath("tests/gdk/static").joinpath(file_name).resolve(),
    )

    with pytest.raises(Exception) as err:
        config.get_configuration()
    assert mock_get_project_config_file.called
    assert "Please correct its format and try again." in err.value.args[0]


@pytest.mark.parametrize("file_name", ["valid_build_command.json"])
def test_get_configuration_config_file(mocker, file_name):
    mock_get_project_config_file = mocker.patch(
        "gdk.common.configuration._get_project_config_file",
        return_value=Path(".").joinpath("tests/gdk/static").joinpath(file_name).resolve(),
    )

    config.get_configuration()
    assert mock_get_project_config_file.called


def test_validate_configuration_schema_not_exists(mocker):
    mock_get_static_file_path = mocker.patch("gdk.common.utils.get_static_file_path", return_value=None)
    mock_jsonschema_validate = mocker.patch("jsonschema.validate", return_value=None)
    with pytest.raises(Exception) as e_info:
        config.validate_configuration("data")

    assert e_info.value.args[0] == error_messages.CONFIG_SCHEMA_FILE_NOT_EXISTS
    assert mock_jsonschema_validate.call_count == 0
    assert mock_get_static_file_path.call_count == 1


def test_get_configuration_no_project_config_file(mocker):
    mock_file_exists = mocker.patch("gdk.common.utils.file_exists", return_value=False)
    mock_validate_configuration = mocker.patch("gdk.common.configuration.validate_configuration", return_value="data")
    with pytest.raises(Exception) as e_info:
        config.get_configuration()

    assert e_info.value.args[0] == error_messages.CONFIG_FILE_NOT_EXISTS
    assert not mock_validate_configuration.called
    assert mock_file_exists.called


def test_get_project_config_file_exists(mocker):
    mock_file_exists = mocker.patch("gdk.common.utils.file_exists", return_value=True)
    assert (
        config._get_project_config_file() == Path(utils.current_directory).joinpath(consts.cli_project_config_file).resolve()
    )
    assert mock_file_exists.called


def test_get_project_config_file_not_exists(mocker):
    mock_file_exists = mocker.patch("gdk.common.utils.file_exists", return_value=False)

    with pytest.raises(Exception) as e_info:
        config._get_project_config_file()

    assert e_info.value.args[0] == error_messages.CONFIG_FILE_NOT_EXISTS
    assert mock_file_exists.called

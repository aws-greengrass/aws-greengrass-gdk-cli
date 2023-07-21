import logging
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


@pytest.mark.parametrize(
    "file_name",
    ["invalid_gdk_version.json"],
)
def test_get_configuration_invalid_gdk_version(mocker, file_name):
    mock_get_project_config_file = mocker.patch(
        "gdk.common.configuration._get_project_config_file",
        return_value=Path(".").joinpath("tests/gdk/static").joinpath(file_name).resolve(),
    )
    spy_log_debug = mocker.spy(logging, "debug")
    with pytest.raises(Exception) as err:
        config.get_configuration()
    assert mock_get_project_config_file.called
    assert (
        "This gdk project requires gdk cli version '1000.0.0' or above. Please update the cli using the command `pip3 install"
        " git+https://github.com/aws-greengrass/aws-greengrass-gdk-cli.git@v1000.0.0` before proceeding."
        == err.value.args[0]
    )

    assert spy_log_debug.call_count == 0


@pytest.mark.parametrize("file_name", ["valid_build_command.json"])
def test_get_configuration_config_file(mocker, file_name):
    mock_get_project_config_file = mocker.patch(
        "gdk.common.configuration._get_project_config_file",
        return_value=Path(".").joinpath("tests/gdk/static").joinpath(file_name).resolve(),
    )
    mock_validate_cli_version = mocker.patch("gdk.common.configuration.validate_cli_version", return_value=None)
    config.get_configuration()
    assert mock_get_project_config_file.called
    assert mock_validate_cli_version.called


def test_get_configuration_no_project_config_file(mocker):
    mock_file_exists = mocker.patch("gdk.common.utils.file_exists", return_value=False)
    mock_validate_configuration = mocker.patch("gdk.common.configuration.validate_configuration", return_value="data")
    mock_validate_cli_version = mocker.patch("gdk.common.configuration.validate_cli_version", return_value=None)
    with pytest.raises(Exception) as e_info:
        config.get_configuration()

    assert e_info.value.args[0] == error_messages.CONFIG_FILE_NOT_EXISTS
    assert not mock_validate_configuration.called
    assert mock_file_exists.called
    assert not mock_validate_cli_version.called


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

from pathlib import Path

import gdk.common.configuration as config
import gdk.common.consts as consts
import gdk.common.exceptions.error_messages as error_messages
import gdk.common.utils as utils
import pytest
import json


def test_get_static_file_path_cli_schema():
    # Integ test for the existence of command model file even before building the cli tool.
    model_file_path = utils.get_static_file_path(consts.config_schema_file)
    assert model_file_path is not None
    assert model_file_path.exists()


@pytest.mark.parametrize(
    "file_name",
    ["invalid_gdk_version.json"],
)
def test_get_configuration_invalid_gdk_version(mocker, file_name):
    mock_get_project_config_file = mocker.patch(
        "gdk.common.configuration._get_project_config_file",
        return_value=Path(".").joinpath("tests/gdk/static").joinpath(file_name).resolve(),
    )
    with pytest.raises(Exception) as err:
        config.get_configuration()
    assert mock_get_project_config_file.called
    assert (
        "This gdk project requires gdk cli version '1000.0.0' or above. Please update the cli using the command `pip3 install"
        " git+https://github.com/aws-greengrass/aws-greengrass-gdk-cli.git@v1000.0.0` before proceeding."
        == err.value.args[0]
    )


@pytest.mark.parametrize(
    "file_name",
    ["invalid_config.json"],
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
    ["config.json"],
)
def test_get_configuration_valid_component_config_found(mocker, file_name):
    config_file = Path(".").joinpath("tests/gdk/static").joinpath(file_name).resolve()
    mock_get_project_config_file = mocker.patch(
        "gdk.common.configuration._get_project_config_file",
        return_value=config_file,
    )

    _config = config.get_configuration()
    with open(config_file, "r") as f:
        assert _config == json.loads(f.read())
    assert mock_get_project_config_file.called


def test_get_project_config_file_not_exists(mocker):
    mock_file_exists = mocker.patch("gdk.common.utils.file_exists", return_value=False)

    with pytest.raises(Exception) as e_info:
        config.get_configuration()

    assert e_info.value.args[0] == error_messages.CONFIG_FILE_NOT_EXISTS
    assert mock_file_exists.called

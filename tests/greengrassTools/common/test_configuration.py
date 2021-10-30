import greengrassTools.common.configuration as config
from pathlib import Path
import pytest
import jsonschema
import greengrassTools.common.exceptions.error_messages as error_messages
import greengrassTools.common.utils as utils
import greengrassTools.common.consts as consts

def test_get_configuration_valid_component_config_found(mocker):
    expected_config = {"component" :{"1": {"author": "abc","version": "1.0.0","build": {"command" : ["default"]},"publish": {"bucket_name": "default"}}},"tools_version": "1.0.0"}

    mock__get_project_config_file=mocker.patch("greengrassTools.common.configuration._get_project_config_file", 
    return_value=Path(".").joinpath('tests/greengrassTools/static').joinpath('config.json'))
    assert config.get_configuration() == expected_config
    assert mock__get_project_config_file.called

@pytest.mark.parametrize("file_name", ["invalid_config.json", "invalid_case_config.json", "invalid_version_config.json", "invalid_multiple_components.json","invalid_build_command.json"])
def test_get_configuration_invalid_config_file(mocker, file_name):
    mock__get_project_config_file=mocker.patch("greengrassTools.common.configuration._get_project_config_file", 
    return_value=Path(".").joinpath('tests/greengrassTools/static').joinpath(file_name).resolve())

    with pytest.raises(Exception) as err:
        config.get_configuration()
    assert mock__get_project_config_file.called

def test_validate_configuration_schema_not_exists(mocker):
    mock_get_static_file_path = mocker.patch('greengrassTools.common.utils.get_static_file_path', return_value=None)
    mock_jsonschema_validate = mocker.patch('jsonschema.validate', return_value=None)
    with pytest.raises(Exception) as e_info:
        config.validate_configuration("data")

    assert e_info.value.args[0] == error_messages.CONFIG_SCHEMA_FILE_NOT_EXISTS
    assert mock_jsonschema_validate.call_count == 0 
    assert mock_get_static_file_path.call_count == 1   

def test_get_configuration_no_project_config_file(mocker):  
    mock_file_exists= mocker.patch("greengrassTools.common.utils.file_exists", return_value=False)
    mock_validate_configuration = mocker.patch("greengrassTools.common.configuration.validate_configuration",return_value="data")
    with pytest.raises(Exception) as e_info:
        config.get_configuration()

    assert e_info.value.args[0] == error_messages.CONFIG_FILE_NOT_EXISTS  
    assert not mock_validate_configuration.called

def test_get_project_config_file_exists(mocker):
    mock_file_exists= mocker.patch("greengrassTools.common.utils.file_exists", return_value=True)

    assert config._get_project_config_file() == Path(utils.current_directory).joinpath(consts.cli_project_config_file).resolve()

def test_get_project_config_file_not_exists(mocker):
    mock_file_exists= mocker.patch("greengrassTools.common.utils.file_exists", return_value=False)

    with pytest.raises(Exception) as e_info:
        config._get_project_config_file()

    assert e_info.value.args[0] == error_messages.CONFIG_FILE_NOT_EXISTS 
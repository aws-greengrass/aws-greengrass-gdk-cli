import greengrassTools.common.configuration as config
from pathlib import Path
import json
import pytest
import jsonschema
import greengrassTools.common.exceptions.error_messages as error_messages

def test_get_configuration_valid_component_config_found():
    component_config = '{"author": "abc","version": "1.0.0","build": {"command" : "default"},"publish": {"bucket_name": "default"}}'
    expected_config = json.loads(component_config)
    assert config.get_configuration(Path(".").joinpath('tests/greengrassTools/static').joinpath('config.json').resolve(), "1") == expected_config

def test_get_configuration_valid_component_config_no_found():
    assert config.get_configuration(Path(".").joinpath('tests/greengrassTools/static').joinpath('config.json').resolve(), "2") is None

@pytest.mark.parametrize("file_name", ["invalid_config.json", "invalid_case_config.json", "invalid_version_config.json"])
def test_get_configuration_invalid_config_file(file_name):
    with pytest.raises(jsonschema.exceptions.ValidationError) as err:
        config.get_configuration(Path(".").joinpath('tests/greengrassTools/static').joinpath(file_name).resolve(), "1")

def test_validate_configuration_not_exists(mocker):
    mock_get_static_file_path = mocker.patch('greengrassTools.common.utils.get_static_file_path', return_value=None)
    mock_jsonschema_validate = mocker.patch('jsonschema.validate', return_value=None)
    with pytest.raises(Exception) as e_info:
        config.validate_configuration("data")

    assert e_info.value.args[0] == error_messages.CONFIG_SCHEMA_FILE_NOT_EXISTS
    assert mock_jsonschema_validate.call_count == 0 
    assert mock_get_static_file_path.call_count == 1   
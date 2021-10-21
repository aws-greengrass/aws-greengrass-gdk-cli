import greengrassTools.common.configuration as config
from pathlib import Path
import json
import pytest
import jsonschema

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

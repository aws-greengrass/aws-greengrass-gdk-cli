import json
from pathlib import Path
from unittest.mock import mock_open, patch

import greengrassTools.commands.component.project_utils as project_utils
import greengrassTools.common.exceptions.error_messages as error_messages
import pytest
import yaml

valid_project_config_file = (
    Path(".").joinpath("tests/greengrassTools/static/project_utils").joinpath("valid_project_config.json").resolve()
)
valid_json_recipe_file = (
    Path(".").joinpath("tests/greengrassTools/static/project_utils").joinpath("valid_component_recipe.json").resolve()
)
valid_yaml_recipe_file = (
    Path(".").joinpath("tests/greengrassTools/static/project_utils").joinpath("valid_component_recipe.yaml").resolve()
)

invalid_json_recipe_file = (
    Path(".").joinpath("tests/greengrassTools/static/project_utils").joinpath("invalid_component_recipe.json").resolve()
)
invalid_yaml_recipe_file = (
    Path(".").joinpath("tests/greengrassTools/static/project_utils").joinpath("invalid_component_recipe.yaml").resolve()
)

with open(valid_project_config_file, "r") as f:
    parsed_config_file = json.loads(f.read())
with open(valid_json_recipe_file, "r") as f:
    parsed_json_recipe_file = json.loads(f.read())
with open(valid_yaml_recipe_file, "r") as f:
    parsed_yaml_recipe_file = yaml.safe_load(f.read())


def test_get_recipe_file_not_exists():
    # Checks in the current directory for json or yaml files. Since none of them are present, this will raise an exception
    with pytest.raises(Exception) as e:
        project_utils.get_recipe_file()
    assert e.value.args[0] == error_messages.PROJECT_RECIPE_FILE_NOT_FOUND


def test_get_recipe_file_json_exists(mocker):
    # Recipe json file exists.
    mock_json_file_path = Path("recipe.json")

    def use_this_for_recipe(*args):
        if args[0] == "recipe.json":
            return [mock_json_file_path]
        elif args[0] == "recipe.yaml":
            return []

    mock_glob = mocker.patch("pathlib.Path.glob", side_effect=use_this_for_recipe)
    recipe = project_utils.get_recipe_file()

    assert mock_glob.call_count == 2
    mock_glob.assert_any_call("recipe.json")
    mock_glob.assert_any_call("recipe.yaml")
    assert recipe.name == "recipe.json"


def test_get_recipe_file_yaml_exists(mocker):
    # Recipe json file not exists but yaml does.
    mock_yaml_file_path = Path("recipe.yaml")

    def use_this_for_recipe(*args):
        if args[0] == "recipe.json":
            return []
        elif args[0] == "recipe.yaml":
            return [mock_yaml_file_path]

    mock_glob = mocker.patch("pathlib.Path.glob", side_effect=use_this_for_recipe)
    recipe = project_utils.get_recipe_file()

    # Search for json file and then yaml file.
    assert mock_glob.call_count == 2
    assert type(recipe) == type(mock_yaml_file_path)
    mock_glob.assert_any_call("recipe.json")
    mock_glob.assert_any_call("recipe.yaml")
    assert recipe.name == "recipe.yaml"


def test_get_recipe_file_yaml_none_exists(mocker):
    # neither recipe.json not recipe.yaml exists
    def use_this_for_recipe(*args):
        if args[0] == "recipe.json":
            return []
        elif args[0] == "recipe.yaml":
            return []

    mock_glob = mocker.patch("pathlib.Path.glob", side_effect=use_this_for_recipe)
    with pytest.raises(Exception) as e:
        project_utils.get_recipe_file()
    assert e.value.args[0] == error_messages.PROJECT_RECIPE_FILE_NOT_FOUND
    # Search for json file and then yaml file.
    assert mock_glob.call_count == 2
    mock_glob.assert_any_call("recipe.json")
    mock_glob.assert_any_call("recipe.yaml")


def test_get_recipe_file_yaml_both_exist(mocker):
    # neither recipe.json not recipe.yaml exists
    def use_this_for_recipe(*args):
        if args[0] == "recipe.json":
            return [Path(".")]
        elif args[0] == "recipe.yaml":
            return [Path(".")]

    mock_glob = mocker.patch("pathlib.Path.glob", side_effect=use_this_for_recipe)
    with pytest.raises(Exception) as e:
        project_utils.get_recipe_file()
    assert error_messages.PROJECT_RECIPE_FILE_NOT_FOUND in e.value.args[0]
    assert mock_glob.call_count == 2
    mock_glob.assert_any_call("recipe.json")
    mock_glob.assert_any_call("recipe.yaml")


def test_parse_recipe_file_json(mocker):
    # Parse json file
    mock_yaml_loads = mocker.patch("yaml.safe_load")
    json_data = project_utils.parse_recipe_file(valid_json_recipe_file)
    assert not mock_yaml_loads.called
    assert type(json_data) == dict


def test_parse_recipe_file_yaml(mocker):
    # Parse yaml file
    mock_json_loads = mocker.patch("json.loads")
    yaml_dic = project_utils.parse_recipe_file(valid_yaml_recipe_file)
    assert not mock_json_loads.called
    assert type(yaml_dic) == dict


def test_parse_recipe_file_yaml_invalid(mocker):
    # Parse yaml file
    spy_json = mocker.spy(json, "loads")
    spy_yaml = mocker.spy(yaml, "safe_load")
    with pytest.raises(Exception) as e:
        project_utils.parse_recipe_file(invalid_yaml_recipe_file)
    assert "Unable to parse the recipe file - invalid_component_recipe.yaml" in e.value.args[0]
    spy_yaml.call_count == 0
    spy_json.call_count == 1


def test_parse_recipe_file_json_invalid(mocker):
    # Parse invalid json file
    spy_json = mocker.spy(json, "loads")
    spy_yaml = mocker.spy(yaml, "safe_load")
    with pytest.raises(Exception) as e:
        project_utils.parse_recipe_file(invalid_json_recipe_file)
    assert "Unable to parse the recipe file - invalid_component_recipe.json" in e.value.args[0]
    spy_yaml.call_count == 1
    spy_json.call_count == 0


def test_get_project_config_values(mocker):
    # Check if the values are correctly created with valid recipe and config files.
    mock_get_recipe_file = mocker.patch(
        "greengrassTools.commands.component.project_utils.get_recipe_file", return_value=valid_json_recipe_file
    )
    mock_get_parsed_json_recipe_file = mocker.patch(
        "greengrassTools.commands.component.project_utils.parse_recipe_file", return_value=parsed_json_recipe_file
    )
    mock_get_parsed_config = mocker.patch(
        "greengrassTools.common.configuration.get_configuration", return_value=parsed_config_file
    )
    values = project_utils.get_project_config_values()
    assert mock_get_recipe_file.call_count == 1
    assert mock_get_parsed_json_recipe_file.call_count == 1
    assert mock_get_parsed_config.call_count == 1
    assert type(values) == dict

    # Assert all keys exist
    assert "component_name" in values
    assert "component_build_config" in values
    assert "component_version" in values
    assert "component_author" in values
    assert "bucket" in values
    assert "gg_build_directory" in values
    assert "gg_build_artifacts_dir" in values
    assert "gg_build_recipes_dir" in values
    assert "gg_build_component_artifacts_dir" in values
    assert "component_recipe_file" in values
    assert "parsed_component_recipe" in values


def test_get_project_config_values_invalid_config(mocker):
    # Check if an exception is thrown with invalid config
    mock_get_recipe_file = mocker.patch(
        "greengrassTools.commands.component.project_utils.get_recipe_file", return_value=valid_json_recipe_file
    )
    mock_get_parsed_json_recipe_file = mocker.patch(
        "greengrassTools.commands.component.project_utils.parse_recipe_file", return_value=parsed_json_recipe_file
    )
    mock_get_parsed_config = mocker.patch(
        "greengrassTools.common.configuration.get_configuration", side_effect=KeyError("key")
    )
    with pytest.raises(Exception) as e:
        project_utils.get_project_config_values()

    assert e.value.args[0] == "key"
    assert not mock_get_recipe_file.called
    assert not mock_get_parsed_json_recipe_file.called
    assert mock_get_parsed_config.called


def test_get_project_config_values_invalid_json_recipe(mocker):
    # Check if an exception is thrown for invalid recipe and valid config files.
    mock_get_recipe_file = mocker.patch(
        "greengrassTools.commands.component.project_utils.get_recipe_file", return_value=invalid_json_recipe_file
    )
    mock_get_parsed_config = mocker.patch(
        "greengrassTools.common.configuration.get_configuration", return_value=parsed_config_file
    )
    with pytest.raises(Exception) as e:
        project_utils.get_project_config_values()
    assert "Unable to parse the recipe file - invalid_component_recipe.json" in e.value.args[0]

    assert mock_get_recipe_file.call_count == 1
    assert mock_get_parsed_config.call_count == 1


def test_get_project_config_values_invalid_yaml_recipe(mocker):
    # Check if an exception is thrown for invalid recipe and valid config files.
    mock_get_recipe_file = mocker.patch(
        "greengrassTools.commands.component.project_utils.get_recipe_file", return_value=invalid_yaml_recipe_file
    )
    mock_get_parsed_config = mocker.patch(
        "greengrassTools.common.configuration.get_configuration", return_value=parsed_config_file
    )
    with pytest.raises(Exception) as e:
        project_utils.get_project_config_values()
    assert "Unable to parse the recipe file - invalid_component_recipe.yaml" in e.value.args[0]

    assert mock_get_recipe_file.call_count == 1
    assert mock_get_parsed_config.call_count == 1


def test_get_project_config_values_recipe_file_not_exists(mocker):
    # Check if an exception is thrown for if no recipe file exists
    mock_get_parsed_config = mocker.patch(
        "greengrassTools.common.configuration.get_configuration", return_value=parsed_config_file
    )
    with pytest.raises(Exception) as e:
        project_utils.get_project_config_values()
    assert e.value.args[0] == error_messages.PROJECT_RECIPE_FILE_NOT_FOUND
    assert mock_get_parsed_config.call_count == 1


def test_get_project_config_values_config_file_not_exists():
    # Check if an exception is thrown for if no config file exists
    with pytest.raises(Exception) as e:
        project_utils.get_project_config_values()
    assert e.value.args[0] == error_messages.CONFIG_FILE_NOT_EXISTS


def test_component_version_build_specific_version(mocker):
    mock_get_recipe_file = mocker.patch(
        "greengrassTools.commands.component.project_utils.get_recipe_file", return_value=valid_json_recipe_file
    )
    mock_get_parsed_json_recipe_file = mocker.patch(
        "greengrassTools.commands.component.project_utils.parse_recipe_file", return_value=parsed_json_recipe_file
    )
    mock_get_parsed_config = mocker.patch(
        "greengrassTools.common.configuration.get_configuration", return_value=parsed_config_file
    )
    values = project_utils.get_project_config_values()
    assert values["component_version"] == "1.0.0"
    assert mock_get_recipe_file.call_count == 1
    assert mock_get_parsed_json_recipe_file.call_count == 1
    assert mock_get_parsed_config.call_count == 1


def test_service_clients(mocker):
    mock_s3_client = mocker.patch("greengrassTools.commands.component.project_utils.create_s3_client", return_value=None)
    mock_sts_client = mocker.patch("greengrassTools.commands.component.project_utils.create_sts_client", return_value=None)
    mock_greengrass_client = mocker.patch(
        "greengrassTools.commands.component.project_utils.create_greengrass_client", return_value=None
    )
    project_utils.get_service_clients("region")
    assert mock_s3_client.call_count == 1
    assert mock_sts_client.call_count == 1
    assert mock_greengrass_client.call_count == 1
    mock_s3_client.assert_any_call("region")
    mock_sts_client.assert_any_call("region")
    mock_greengrass_client.assert_any_call("region")


def test_service_clients_with_s3_region(mocker):
    mock_boto3_client = mocker.patch("boto3.client", return_value=None)
    project_utils.create_s3_client("region")
    assert mock_boto3_client.call_count == 1
    mock_boto3_client.assert_called_once_with("s3", region_name="region")


def test_service_clients_with_greengrassv2_region(mocker):
    mock_boto3_client = mocker.patch("boto3.client", return_value=None)
    project_utils.create_greengrass_client("region")
    assert mock_boto3_client.call_count == 1
    mock_boto3_client.assert_called_once_with("greengrassv2", region_name="region")


def test_service_clients_with_sts_region(mocker):
    mock_boto3_client = mocker.patch("boto3.client", return_value=None)
    project_utils.create_sts_client("region")
    assert mock_boto3_client.call_count == 1
    mock_boto3_client.assert_called_once_with("sts", region_name="region")


def test_get_supported_component_builds_not_exists(mocker):
    mock_file_not_exists = mocker.patch("greengrassTools.common.utils.get_static_file_path", return_value=None)
    project_utils.get_supported_component_builds()
    assert mock_file_not_exists.called


def test_get_supported_component_builds_exists(mocker):
    mock_file_path = Path(".").resolve()
    mock_file_not_exists = mocker.patch("greengrassTools.common.utils.get_static_file_path", return_value=mock_file_path)
    mock_json_loads = mocker.patch("json.loads")
    with patch("builtins.open", mock_open(read_data="{}")) as mock_file:
        project_utils.get_supported_component_builds()
        mock_file.assert_called_once_with(mock_file_path, "r")
        assert mock_file_not_exists.called
        assert mock_json_loads.called

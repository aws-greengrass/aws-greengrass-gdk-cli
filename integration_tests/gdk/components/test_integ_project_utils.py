import logging
from pathlib import Path

import gdk.commands.component.project_utils as project_utils
import gdk.common.consts as consts
import gdk.common.exceptions.error_messages as error_messages
import gdk.common.utils as utils
import pytest


def test_get_static_file_path_supported_builds():
    # Integ test for the existence of supported build file even before building the cli tool.
    model_file_path = utils.get_static_file_path(consts.project_build_system_file)
    assert model_file_path is not None
    assert model_file_path.exists()


def test_get_supported_component_builds():
    # Integ test for the correctly parsing the  supported builds json file as dict
    supported_component_builds = project_utils.get_supported_component_builds()
    if supported_component_builds:
        assert type(supported_component_builds) == dict
        assert len(supported_component_builds) > 0
        for k, v in supported_component_builds.items():
            assert "build_folder" in v
            assert "build_command" in v
            assert type(v) == dict


def test_get_project_config_values_without_recipe(mocker):

    mock_get_project_config_file = mocker.patch(
        "gdk.common.configuration._get_project_config_file",
        return_value=Path(".").joinpath("tests/gdk/static").joinpath("config.json").resolve(),
    )
    with pytest.raises(Exception) as e:
        project_utils.get_project_config_values()
    assert "No valid component recipe is found." in e.value.args[0]
    assert mock_get_project_config_file.call_count == 1


def test_get_project_config_values_with_recipe(mocker):

    mock_get_project_config_file = mocker.patch(
        "gdk.common.configuration._get_project_config_file",
        return_value=Path(".").joinpath("tests/gdk/static").joinpath("config.json").resolve(),
    )
    valid_json_recipe_file = (
        Path(".").joinpath("tests/gdk/static/project_utils").joinpath("valid_component_recipe.json").resolve()
    )
    mock_get_recipe_file = mocker.patch(
        "gdk.commands.component.project_utils.get_recipe_file", return_value=valid_json_recipe_file
    )
    values = project_utils.get_project_config_values()
    assert mock_get_project_config_file.call_count == 1
    assert mock_get_recipe_file.call_count == 1
    assert "component_name" in values
    assert "component_build_config" in values
    assert "component_version" in values
    assert "component_author" in values
    assert "bucket" in values
    assert "region" in values
    assert "gg_build_directory" in values
    assert "gg_build_artifacts_dir" in values
    assert "gg_build_recipes_dir" in values
    assert "gg_build_component_artifacts_dir" in values
    assert "component_recipe_file" in values


def test_get_project_config_values_both_exist(mocker):
    # Both recipe.json and recipe.yaml exists
    def use_this_for_recipe(*args):
        if args[0] == "recipe.json":
            return [Path(".")]
        elif args[0] == "recipe.yaml":
            return [Path(".")]

    mock_get_project_config_file = mocker.patch(
        "gdk.common.configuration._get_project_config_file",
        return_value=Path(".").joinpath("tests/gdk/static").joinpath("config.json").resolve(),
    )

    mock_glob = mocker.patch("pathlib.Path.glob", side_effect=use_this_for_recipe)
    spy_log = mocker.spy(logging, "error")
    with pytest.raises(Exception) as e:
        project_utils.get_project_config_values()
    assert mock_get_project_config_file.called
    assert error_messages.PROJECT_RECIPE_FILE_NOT_FOUND in e.value.args[0]
    assert mock_glob.call_count == 2
    mock_glob.assert_any_call("recipe.json")
    mock_glob.assert_any_call("recipe.yaml")
    assert spy_log.call_count == 1


def test_get_project_config_values_json_exists(mocker):
    # recipe.json exists
    valid_json_recipe_file = (
        Path(".").joinpath("tests/gdk/static/project_utils").joinpath("valid_component_recipe.json").resolve()
    )

    def use_this_for_recipe(*args):
        if args[0] == "recipe.json":
            return [valid_json_recipe_file]
        elif args[0] == "recipe.yaml":
            return []

    mock_get_project_config_file = mocker.patch(
        "gdk.common.configuration._get_project_config_file",
        return_value=Path(".").joinpath("tests/gdk/static").joinpath("config.json").resolve(),
    )

    mock_glob = mocker.patch("pathlib.Path.glob", side_effect=use_this_for_recipe)
    spy_log = mocker.spy(logging, "error")
    project_utils.get_project_config_values()
    assert mock_get_project_config_file.called
    assert mock_glob.call_count == 2
    mock_glob.assert_any_call("recipe.json")
    mock_glob.assert_any_call("recipe.yaml")
    assert spy_log.call_count == 0


def test_get_project_config_values_yaml_exists(mocker):
    # recipe.yaml exists
    valid_yaml_recipe_file = (
        Path(".").joinpath("tests/gdk/static/project_utils").joinpath("valid_component_recipe.yaml").resolve()
    )

    def use_this_for_recipe(*args):
        if args[0] == "recipe.json":
            return []
        elif args[0] == "recipe.yaml":
            return [valid_yaml_recipe_file]

    mock_get_project_config_file = mocker.patch(
        "gdk.common.configuration._get_project_config_file",
        return_value=Path(".").joinpath("tests/gdk/static").joinpath("config.json").resolve(),
    )

    mock_glob = mocker.patch("pathlib.Path.glob", side_effect=use_this_for_recipe)
    spy_log = mocker.spy(logging, "error")
    project_utils.get_project_config_values()
    assert mock_get_project_config_file.called
    assert mock_glob.call_count == 2
    mock_glob.assert_any_call("recipe.json")
    mock_glob.assert_any_call("recipe.yaml")
    assert spy_log.call_count == 0


def test_service_clients_no_mocks(mocker):
    spy_s3_client = mocker.spy(project_utils, "create_s3_client")
    spy_sts_client = mocker.spy(project_utils, "create_sts_client")
    spy_greengrass_client = mocker.spy(project_utils, "create_greengrass_client")
    project_utils.get_service_clients("region")
    assert spy_s3_client.call_count == 1
    assert spy_greengrass_client.call_count == 1
    assert spy_sts_client.call_count == 1
    spy_s3_client.assert_any_call("region")
    spy_sts_client.assert_any_call("region")
    spy_greengrass_client.assert_any_call("region")

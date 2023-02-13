import json
from pathlib import Path
from shutil import Error
from unittest.mock import mock_open, patch

import pytest

import gdk.CLIParser as CLIParser
import gdk.common.consts as consts
import gdk.common.exceptions.error_messages as error_messages
import gdk.common.parse_args_actions as parse_args_actions
import gdk.common.utils as utils
from gdk.commands.component.BuildCommand import BuildCommand

gradle_build_command = ["gradle", "clean", "build"]


@pytest.fixture()
def supported_build_system(mocker):
    builds_file = utils.get_static_file_path(consts.project_build_system_file)
    with open(builds_file, "r") as f:
        data = json.loads(f.read())
    mock_get_supported_component_builds = mocker.patch(
        "gdk.commands.component.project_utils.get_supported_component_builds", return_value=data
    )
    return mock_get_supported_component_builds


@pytest.fixture()
def rglob_build_file(mocker):
    def search(*args, **kwargs):
        if "build.gradle" in args[0] or "pom.xml" in args[0]:
            return [Path(utils.current_directory).joinpath("build_file")]
        return []

    mock_rglob = mocker.patch("pathlib.Path.rglob", side_effect=search)
    return mock_rglob


def test_build_command_instantiation(mocker):
    mock_get_supported_component_builds = mocker.patch(
        "gdk.commands.component.project_utils.get_supported_component_builds", return_value={}
    )
    mock_check_if_arguments_conflict = mocker.patch.object(BuildCommand, "check_if_arguments_conflict", return_value=None)
    mock_run = mocker.patch.object(BuildCommand, "run", return_value=None)
    mock_get_proj_config = mocker.patch(
        "gdk.commands.component.project_utils.get_project_config_values",
        return_value={},
    )
    parse_args_actions.run_command(CLIParser.cli_parser.parse_args(["component", "build"]))

    assert mock_get_proj_config.call_count == 1
    assert mock_get_supported_component_builds.call_count == 1
    assert mock_check_if_arguments_conflict.call_count == 1
    assert mock_run.call_count == 1


def test_build_command_instantiation_failed_fetching_config(mocker):
    mock_get_proj_config = mocker.patch(
        "gdk.commands.component.project_utils.get_project_config_values",
        side_effect=Exception("exception fetching proj values"),
    )
    mock_get_supported_component_builds = mocker.patch(
        "gdk.commands.component.project_utils.get_supported_component_builds", return_value={}
    )
    mock_check_if_arguments_conflict = mocker.patch.object(BuildCommand, "check_if_arguments_conflict", return_value=None)
    mock_run = mocker.patch.object(BuildCommand, "run", return_value=None)
    with pytest.raises(Exception) as e:
        parse_args_actions.run_command(CLIParser.cli_parser.parse_args(["component", "build"]))
    assert "exception fetching proj values" in e.value.args[0]
    assert mock_get_proj_config.call_count == 1
    assert mock_get_supported_component_builds.call_count == 0
    assert mock_check_if_arguments_conflict.call_count == 1
    assert mock_run.call_count == 0


def test_build_command_instantiation_failed_fetching_build_config(mocker):

    mock_get_supported_component_builds = mocker.patch(
        "gdk.commands.component.project_utils.get_supported_component_builds",
        side_effect=Exception("exception fetching build"),
    )
    mock_get_proj_config = mocker.patch(
        "gdk.commands.component.project_utils.get_project_config_values",
        return_value={},
    )
    mock_check_if_arguments_conflict = mocker.patch.object(BuildCommand, "check_if_arguments_conflict", return_value=None)
    mock_run = mocker.patch.object(BuildCommand, "run", return_value=None)
    with pytest.raises(Exception) as e:
        parse_args_actions.run_command(CLIParser.cli_parser.parse_args(["component", "build"]))
    assert "exception fetching build" in e.value.args[0]
    assert mock_get_proj_config.call_count == 1
    assert mock_get_supported_component_builds.call_count == 1
    assert mock_check_if_arguments_conflict.call_count == 1
    assert mock_run.call_count == 0


def test_build_command_instantiation_failed_conflicting_args(mocker):

    mock_get_supported_component_builds = mocker.patch(
        "gdk.commands.component.project_utils.get_supported_component_builds", return_value={}
    )
    mock_get_proj_config = mocker.patch(
        "gdk.commands.component.project_utils.get_project_config_values",
        side_effect=Exception("exception fetching proj values"),
    )
    mock_check_if_arguments_conflict = mocker.patch.object(
        BuildCommand,
        "check_if_arguments_conflict",
        side_effect=Exception("exception due to conflictins args"),
    )
    mock_run = mocker.patch.object(BuildCommand, "run", return_value=None)
    with pytest.raises(Exception) as e:
        parse_args_actions.run_command(CLIParser.cli_parser.parse_args(["component", "build"]))
    assert "exception due to conflictins args" in e.value.args[0]
    assert mock_get_proj_config.call_count == 0
    assert mock_get_supported_component_builds.call_count == 0
    assert mock_check_if_arguments_conflict.call_count == 1
    assert mock_run.call_count == 0


def test_build_run():
    with pytest.raises(Exception) as e:
        parse_args_actions.run_command(CLIParser.cli_parser.parse_args(["component", "build"]))
    assert "Could not build the project due to the following error." in e.value.args[0]


def test_build_run_default_zip_json(mocker, supported_build_system, rglob_build_file):
    mock_clean_dir = mocker.patch("gdk.common.utils.clean_dir", return_value=None)
    mock_create_dir = mocker.patch("pathlib.Path.mkdir", return_value=None)
    mock_copy_dir = mocker.patch("shutil.copytree", return_value=None)
    mock_archive_dir = mocker.patch("shutil.make_archive", return_value=None)
    mock_get_proj_config = mocker.patch(
        "gdk.commands.component.project_utils.get_project_config_values",
        return_value=project_config(),
    )

    mock_get_proj_config = mocker.patch(
        "gdk.commands.component.project_utils.get_project_config_values",
        return_value=project_config(),
    )
    mock_is_artifact_in_build = mocker.patch.object(BuildCommand, "is_artifact_in_build", return_value=True)

    mock_json_dump = mocker.patch("json.dumps")
    pc = mock_get_proj_config.return_value
    file_name = Path(pc["gg_build_recipes_dir"]).joinpath(pc["component_recipe_file"].name).resolve()
    with patch("builtins.open", mock_open()) as mock_file:
        parse_args_actions.run_command(CLIParser.cli_parser.parse_args(["component", "build"]))
        mock_file.assert_any_call(file_name, "w")
        mock_json_dump.call_count == 1

    assert mock_get_proj_config.assert_called_once
    assert mock_copy_dir.call_count == 1  # copy files to zip-build to create a zip
    assert mock_archive_dir.call_count == 1  # archiving directory
    assert mock_is_artifact_in_build.call_count == 1  # only one artifact in project_config. Available in build
    assert mock_clean_dir.call_count == 2  # clean zip-build, clean greengrass-build
    assert mock_create_dir.call_count == 2  # create gg directories


def test_build_run_default_maven_yaml(mocker, supported_build_system, rglob_build_file):

    mock_clean_dir = mocker.patch("gdk.common.utils.clean_dir", return_value=None)
    mock_create_dir = mocker.patch("pathlib.Path.mkdir", return_value=None)
    mock_copy_dir = mocker.patch("shutil.copytree", return_value=None)
    mock_archive_dir = mocker.patch("shutil.make_archive", return_value=None)
    pc = project_config()
    pc["component_build_config"] = {"build_system": "maven"}
    mock_get_proj_config = mocker.patch(
        "gdk.commands.component.project_utils.get_project_config_values",
        return_value=pc,
    )
    mock_platform = mocker.patch("platform.system", return_value="not-windows")
    pc["component_recipe_file"] = Path("/src/GDK-CLI-Internal/tests/gdk/static/build_command/recipe.yaml")
    mock_is_artifact_in_build = mocker.patch.object(BuildCommand, "is_artifact_in_build", return_value=True)

    mock_subprocess_run = mocker.patch("subprocess.run")
    pc = mock_get_proj_config.return_value
    file_name = Path(pc["gg_build_recipes_dir"]).joinpath(pc["component_recipe_file"].name).resolve()

    with patch("builtins.open", mock_open()) as mock_file:
        parse_args_actions.run_command(CLIParser.cli_parser.parse_args(["component", "build"]))
        mock_file.assert_any_call(file_name, "w")
    assert mock_get_proj_config.assert_called_once
    mock_subprocess_run.assert_called_with(["mvn", "clean", "package"])  # called maven build command
    assert mock_copy_dir.call_count == 0  # No copying directories
    assert supported_build_system.call_count == 1
    assert mock_archive_dir.call_count == 0  # Archvie never called in maven
    assert mock_is_artifact_in_build.call_count == 1  # only one artifact in project_config. Available in build
    assert mock_clean_dir.call_count == 1  # clean greengrass-build
    assert mock_create_dir.call_count == 2  # create gg directories
    assert mock_platform.call_count == 1


def test_build_run_default_maven_yaml_windows(mocker, supported_build_system, rglob_build_file):

    mock_clean_dir = mocker.patch("gdk.common.utils.clean_dir", return_value=None)
    mock_create_dir = mocker.patch("pathlib.Path.mkdir", return_value=None)
    mock_copy_dir = mocker.patch("shutil.copytree", return_value=None)
    mock_archive_dir = mocker.patch("shutil.make_archive", return_value=None)
    mock_platform = mocker.patch("platform.system", return_value="Windows")
    pc = project_config()
    pc["component_build_config"] = {"build_system": "maven"}
    mock_get_proj_config = mocker.patch(
        "gdk.commands.component.project_utils.get_project_config_values",
        return_value=pc,
    )

    mock_is_artifact_in_build = mocker.patch.object(BuildCommand, "is_artifact_in_build", return_value=True)

    mock_subprocess_run = mocker.patch("subprocess.run", side_effect="error with maven build cmd")
    mock_yaml_dump = mocker.patch("yaml.dump")
    pc = mock_get_proj_config.return_value
    file_name = Path(pc["gg_build_recipes_dir"]).joinpath(pc["component_recipe_file"].name).resolve()

    with patch("builtins.open", mock_open()) as mock_file:
        parse_args_actions.run_command(CLIParser.cli_parser.parse_args(["component", "build"]))
        mock_file.assert_any_call(file_name, "w")
        mock_yaml_dump.call_count == 1
    assert mock_get_proj_config.assert_called_once
    mock_subprocess_run.assert_called_with(["mvn.cmd", "clean", "package"])  # called maven build command
    assert mock_copy_dir.call_count == 0  # No copying directories
    assert supported_build_system.call_count == 1
    assert mock_archive_dir.call_count == 0  # Archvie never called in maven
    assert mock_is_artifact_in_build.call_count == 1  # only one artifact in project_config. Available in build
    assert mock_clean_dir.call_count == 1  # clean greengrass-build
    assert mock_create_dir.call_count == 2  # create gg directories
    assert mock_platform.call_count == 1


def test_build_run_default_maven_yaml_error(mocker, supported_build_system, rglob_build_file):

    mock_clean_dir = mocker.patch("gdk.common.utils.clean_dir", return_value=None)
    mock_create_dir = mocker.patch("pathlib.Path.mkdir", return_value=None)
    mock_copy_dir = mocker.patch("shutil.copytree", return_value=None)
    mock_archive_dir = mocker.patch("shutil.make_archive", return_value=None)
    mock_platform = mocker.patch("platform.system", return_value="Windows")
    pc = project_config()
    pc["component_build_config"] = {"build_system": "maven"}
    pc["component_recipe_file"] = Path("/src/GDK-CLI-Internal/tests/gdk/static/build_command/recipe.yaml")
    mock_get_proj_config = mocker.patch(
        "gdk.commands.component.project_utils.get_project_config_values",
        return_value=pc,
    )

    mock_is_artifact_in_build = mocker.patch.object(BuildCommand, "is_artifact_in_build", return_value=True)

    mock_subprocess_run = mocker.patch("subprocess.run", side_effect=Exception("error with maven build cmd"))
    pc = mock_get_proj_config.return_value

    with pytest.raises(Exception) as e:
        parse_args_actions.run_command(CLIParser.cli_parser.parse_args(["component", "build", "-d"]))
    assert "error with maven build cmd" in e.value.args[0]
    assert mock_get_proj_config.assert_called_once
    mock_subprocess_run.assert_called_with(["mvn.cmd", "clean", "package"])  # called maven build command
    assert mock_copy_dir.call_count == 0  # No copying directories
    assert supported_build_system.call_count == 1
    assert mock_archive_dir.call_count == 0  # Archvie never called in maven
    assert mock_is_artifact_in_build.call_count == 0  # only one artifact in project_config. Available in build
    assert mock_clean_dir.call_count == 1  # clean greengrass-build
    assert mock_create_dir.call_count == 2  # create gg directories
    assert mock_platform.called


def test_build_run_default_gradle_yaml_artifact_not_found(mocker, supported_build_system, rglob_build_file):

    mock_clean_dir = mocker.patch("gdk.common.utils.clean_dir", return_value=None)
    mock_create_dir = mocker.patch("pathlib.Path.mkdir", return_value=None)
    mock_copy_dir = mocker.patch("shutil.copytree", return_value=None)
    mock_archive_dir = mocker.patch("shutil.make_archive", return_value=None)
    pc = project_config()
    pc["component_build_config"] = {"build_system": "gradle"}
    pc["component_recipe_file"] = Path("/src/GDK-CLI-Internal/tests/gdk/static/build_command/recipe.yaml")
    mock_get_proj_config = mocker.patch(
        "gdk.commands.component.project_utils.get_project_config_values",
        return_value=pc,
    )

    mock_boto3_client = mocker.patch("boto3.client")
    mock_subprocess_run = mocker.patch("subprocess.run")
    mock_yaml_dump = mocker.patch("yaml.dump")
    pc = mock_get_proj_config.return_value

    with patch("builtins.open", mock_open()) as mock_file:
        with pytest.raises(Exception) as e:
            parse_args_actions.run_command(CLIParser.cli_parser.parse_args(["component", "build"]))
            assert (
                "Could not find artifact with URI"
                " 's3://DOC-EXAMPLE-BUCKET/artifacts/com.example.HelloWorld/1.0.0/hello_world.py' on s3 or inside"
                " the build folders."
                in e.value.args[0]
            )
            assert not mock_file.called
            mock_yaml_dump.call_count == 0
    assert mock_get_proj_config.assert_called_once
    mock_subprocess_run.assert_called_with(gradle_build_command)  # called gradle build command
    assert mock_copy_dir.call_count == 0  # No copying directories
    assert supported_build_system.call_count == 1
    assert mock_archive_dir.call_count == 0  # Archvie never called in gralde
    assert mock_boto3_client.call_count == 1
    assert mock_clean_dir.call_count == 1  # clean greengrass-build
    assert mock_create_dir.call_count == 2  # create gg directories


def test_build_run_default_exception(mocker, rglob_build_file):
    mock_create_gg_build_directories = mocker.patch.object(BuildCommand, "create_gg_build_directories")
    mock_default_build_component = mocker.patch.object(
        BuildCommand, "default_build_component", side_effect=Exception("error in default_build_component")
    )
    mock_get_proj_config = mocker.patch(
        "gdk.commands.component.project_utils.get_project_config_values",
        return_value=project_config(),
    )

    mock_get_supported_component_builds = mocker.patch(
        "gdk.commands.component.project_utils.get_supported_component_builds", return_value={}
    )
    mock_subprocess_run = mocker.patch("subprocess.run")
    with pytest.raises(Exception) as e:
        parse_args_actions.run_command(CLIParser.cli_parser.parse_args(["component", "build"]))
    assert "error in default_build_component" in e.value.args[0]
    assert mock_get_proj_config.called
    assert mock_get_supported_component_builds.called
    assert mock_create_gg_build_directories.assert_called_once
    assert mock_default_build_component.assert_called_once
    assert not mock_subprocess_run.called


def test_default_build_component_error_run_build_command(mocker, rglob_build_file):
    mock_clean_dir = mocker.patch("gdk.common.utils.clean_dir", return_value=None)
    mock_create_dir = mocker.patch("pathlib.Path.mkdir", return_value=None)
    mock_run_build_command = mocker.patch.object(
        BuildCommand, "run_build_command", side_effect=Error("err in run_build_command")
    )
    mock_find_artifacts_and_update_uri = mocker.patch.object(BuildCommand, "find_artifacts_and_update_uri")
    mock_create_build_recipe_file = mocker.patch.object(BuildCommand, "create_build_recipe_file")
    mock_get_proj_config = mocker.patch(
        "gdk.commands.component.project_utils.get_project_config_values",
        return_value=project_config(),
    )
    mock_get_supported_component_builds = mocker.patch(
        "gdk.commands.component.project_utils.get_supported_component_builds", return_value={}
    )
    with pytest.raises(Exception) as e:
        parse_args_actions.run_command(CLIParser.cli_parser.parse_args(["component", "build"]))
    assert error_messages.BUILD_FAILED in e.value.args[0]
    assert mock_run_build_command.assert_called_once
    assert not mock_find_artifacts_and_update_uri.called
    assert not mock_create_build_recipe_file.called

    assert mock_get_supported_component_builds.called
    assert mock_clean_dir.call_count == 1
    assert mock_create_dir.call_count == 2
    assert mock_get_proj_config.call_count == 1


def test_build_run_custom(mocker, supported_build_system, rglob_build_file):
    mock_clean_dir = mocker.patch("gdk.common.utils.clean_dir", return_value=None)
    mock_create_dir = mocker.patch("pathlib.Path.mkdir", return_value=None)
    mock_copy_dir = mocker.patch("shutil.copytree", return_value=None)
    pc = project_config()
    pc["component_build_config"] = {"build_system": "custom", "custom_build_command": ["some-command"]}
    mock_get_proj_config = mocker.patch(
        "gdk.commands.component.project_utils.get_project_config_values",
        return_value=pc,
    )

    mock_is_artifact_in_build = mocker.patch.object(BuildCommand, "is_artifact_in_build", return_value=False)
    mock_is_artifact_in_s3 = mocker.patch.object(BuildCommand, "is_artifact_in_s3", return_value=True)
    mock_boto3_client = mocker.patch("boto3.client")
    mock_subprocess_run = mocker.patch("subprocess.run")
    mock_yaml_dump = mocker.patch("yaml.dump")
    pc = mock_get_proj_config.return_value

    with patch("builtins.open", mock_open()) as mock_file:
        parse_args_actions.run_command(CLIParser.cli_parser.parse_args(["component", "build"]))
        assert not mock_file.called
        mock_yaml_dump.call_count == 0
    assert mock_get_proj_config.assert_called_once
    mock_subprocess_run.assert_called_with(["some-command"])  # called maven build command
    assert mock_copy_dir.call_count == 0  # No copying directories
    assert supported_build_system.call_count == 1
    assert mock_is_artifact_in_build.call_count == 0  # only one artifact in project_config. Not vailable in build
    assert mock_is_artifact_in_s3.call_count == 0  # only one artifact in project_config. Not available in s3
    assert mock_boto3_client.call_count == 0
    assert mock_clean_dir.call_count == 1  # clean greengrass-build
    assert mock_create_dir.call_count == 2  # create gg directories


def test_build_run_default_gradle_yaml_artifact_found_build(mocker, supported_build_system, rglob_build_file):

    mock_clean_dir = mocker.patch("gdk.common.utils.clean_dir", return_value=None)
    mock_create_dir = mocker.patch("pathlib.Path.mkdir", return_value=None)
    mock_copy_dir = mocker.patch("shutil.copytree", return_value=None)
    mock_archive_dir = mocker.patch("shutil.make_archive", return_value=None)
    pc = project_config()
    pc["component_build_config"] = {"build_system": "gradle"}
    pc["component_recipe_file"] = Path("/src/GDK-CLI-Internal/tests/gdk/static/build_command/recipe.yaml")
    mock_get_proj_config = mocker.patch(
        "gdk.commands.component.project_utils.get_project_config_values",
        return_value=pc,
    )

    mock_boto3_client = mocker.patch("boto3.client")
    mock_subprocess_run = mocker.patch("subprocess.run")
    mock_yaml_dump = mocker.patch("yaml.dump")
    pc = mock_get_proj_config.return_value
    mocker.patch("pathlib.Path.is_file", return_value=True)
    mock_copy_file = mocker.patch("shutil.copy", return_value=None)
    mock_exists = mocker.patch("pathlib.Path.exists", return_value=True)
    file_name = Path(pc["gg_build_recipes_dir"]).joinpath(pc["component_recipe_file"].name).resolve()
    with patch("builtins.open", mock_open()) as mock_file:
        parse_args_actions.run_command(CLIParser.cli_parser.parse_args(["component", "build"]))
        mock_file.assert_any_call(file_name, "w")
        mock_yaml_dump.call_count == 0
    assert mock_get_proj_config.assert_called_once
    mock_subprocess_run.assert_called_with(gradle_build_command)  # called gradle build command
    assert mock_copy_dir.call_count == 0  # No copying directories
    assert supported_build_system.call_count == 1
    assert mock_archive_dir.call_count == 0  # Archvie never called in gralde
    assert mock_boto3_client.call_count == 0  # artifacts found in s3
    assert mock_clean_dir.call_count == 1  # clean greengrass-build
    assert mock_create_dir.call_count == 2  # create gg directories
    assert mock_copy_file.call_count == 1
    assert mock_exists.called


def test_build_run_default_gradle_yaml_error_creating_recipe(mocker, supported_build_system, rglob_build_file):

    mock_clean_dir = mocker.patch("gdk.common.utils.clean_dir", return_value=None)
    mock_create_dir = mocker.patch("pathlib.Path.mkdir", return_value=None)
    mock_copy_dir = mocker.patch("shutil.copytree", return_value=None)
    mock_archive_dir = mocker.patch("shutil.make_archive", return_value=None)
    pc = project_config()
    pc["component_build_config"] = {"build_system": "gradle"}
    pc["component_recipe_file"] = Path("/src/GDK-CLI-Internal/tests/gdk/static/build_command/recipe.yaml")
    mock_get_proj_config = mocker.patch(
        "gdk.commands.component.project_utils.get_project_config_values",
        return_value=pc,
    )

    mock_boto3_client = mocker.patch("boto3.client")
    mock_subprocess_run = mocker.patch("subprocess.run")
    mock_yaml_dump = mocker.patch("yaml.dump", side_effect=Exception("writing failed"))
    pc = mock_get_proj_config.return_value
    mock_is_artifact_in_build = mocker.patch.object(BuildCommand, "is_artifact_in_build", return_value=True)
    file_name = Path(pc["gg_build_recipes_dir"]).joinpath(pc["component_recipe_file"].name).resolve()
    with patch("builtins.open", mock_open()) as mock_file:
        with pytest.raises(Exception) as e:
            parse_args_actions.run_command(CLIParser.cli_parser.parse_args(["component", "build"]))
            mock_file.assert_any_call(file_name, "w")
            mock_yaml_dump.call_count == 1
        assert "Failed to create build recipe file at" in e.value.args[0]
    assert mock_get_proj_config.assert_called_once
    mock_subprocess_run.assert_called_with(gradle_build_command)  # called gradle build command
    assert mock_copy_dir.call_count == 0  # No copying directories
    assert supported_build_system.call_count == 1
    assert mock_is_artifact_in_build.call_count == 1
    assert mock_archive_dir.call_count == 0  # Archvie never called in gralde
    assert mock_boto3_client.call_count == 0  # artifacts found in s3
    assert mock_clean_dir.call_count == 1  # clean greengrass-build
    assert mock_create_dir.call_count == 2  # create gg directories


def project_config():
    return {
        "component_name": "component_name",
        "component_build_config": {"build_system": "zip"},
        "component_version": "1.0.0",
        "component_author": "abc",
        "bucket": "default",
        "region": "us-east-1",
        "gg_build_directory": Path("/src/GDK-CLI-Internal/greengrass-build"),
        "gg_build_artifacts_dir": Path("/src/GDK-CLI-Internal/greengrass-build/artifacts"),
        "gg_build_recipes_dir": Path("/src/GDK-CLI-Internal/greengrass-build/recipes"),
        "gg_build_component_artifacts_dir": Path("/src/GDK-CLI-Internal/greengrass-build/artifacts/component_name/1.0.0"),
        "component_recipe_file": Path("/src/GDK-CLI-Internal/tests/gdk/static/build_command/valid_component_recipe.json"),
        "parsed_component_recipe": {
            "RecipeFormatVersion": "2020-01-25",
            "ComponentName": "com.example.HelloWorld",
            "ComponentVersion": "1.0.0",
            "ComponentDescription": "My first Greengrass component.",
            "ComponentPublisher": "Amazon",
            "ComponentConfiguration": {"DefaultConfiguration": {"Message": "world"}},
            "Manifests": [
                {
                    "Platform": {"os": "linux"},
                    "Lifecycle": {"Run": "python3 -u {artifacts:path}/hello_world.py '{configuration:/Message}'"},
                    "Artifacts": [{"URI": "s3://DOC-EXAMPLE-BUCKET/artifacts/com.example.HelloWorld/1.0.0/hello_world.py"}],
                }
            ],
        },
    }

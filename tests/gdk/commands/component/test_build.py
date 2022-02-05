from pathlib import Path
from shutil import Error
from unittest.mock import mock_open, patch

import gdk.common.utils as utils
import pytest
from gdk.common.exceptions import error_messages

json_values = {
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


def test_create_recipe_file_json_valid(mocker):
    # Tests if a new recipe file is created with updated values - json
    mock_get_parsed_config = mocker.patch(
        "gdk.commands.component.project_utils.get_project_config_values", return_value=json_values
    )

    import gdk.commands.component.build as build

    assert mock_get_parsed_config.call_count == 1
    file_name = Path(json_values["gg_build_recipes_dir"]).joinpath(json_values["component_recipe_file"].name).resolve()
    mock_json_dump = mocker.patch("json.dumps")
    mock_yaml_dump = mocker.patch("yaml.dump")
    with patch("builtins.open", mock_open()) as mock_file:
        build.create_build_recipe_file()
        mock_file.assert_any_call(file_name, "w")
        mock_json_dump.call_count == 1
        assert not mock_yaml_dump.called


def test_create_recipe_file_yaml_valid(mocker):
    # Tests if a new recipe file is created with updated values - yaml
    # Tests if a new recipe file is created with updated values - json
    import gdk.commands.component.build as build

    build.project_config["component_recipe_file"] = Path("some-yaml.yaml").resolve()
    file_name = (
        Path(json_values["gg_build_recipes_dir"])
        .joinpath(build.project_config["component_recipe_file"].resolve().name)
        .resolve()
    )
    mock_json_dump = mocker.patch("json.dumps")
    mock_yaml_dump = mocker.patch("yaml.dump")
    with patch("builtins.open", mock_open()) as mock_file:
        build.create_build_recipe_file()
        mock_file.assert_called_once_with(file_name, "w")
        mock_json_dump.call_count == 1
        assert mock_yaml_dump.called


def test_create_recipe_file_json_invalid(mocker):
    # Raise exception for when creating recipe failed due to invalid json
    import gdk.commands.component.build as build

    build.project_config["component_recipe_file"] = Path("some-json.json").resolve()
    file_name = Path(json_values["gg_build_recipes_dir"]).joinpath(json_values["component_recipe_file"].name).resolve()

    def throw_error(*args, **kwargs):
        if args[0] == json_values["parsed_component_recipe"]:
            raise TypeError("I mock json error")

    mock_json_dump = mocker.patch("json.dumps", side_effect=throw_error)
    mock_yaml_dump = mocker.patch("yaml.dump")
    with patch("builtins.open", mock_open()) as mock_file:
        with pytest.raises(Exception) as e:
            build.create_build_recipe_file()
        assert "Failed to create build recipe file at" in e.value.args[0]
        mock_file.assert_called_once_with(file_name, "w")
        mock_json_dump.call_count == 1
        assert not mock_yaml_dump.called


def test_create_recipe_file_yaml_invalid(mocker):
    # Raise exception for when creating recipe failed due to invalid yaml
    import gdk.commands.component.build as build

    build.project_config["component_recipe_file"] = Path("some-yaml.yaml").resolve()
    file_name = (
        Path(json_values["gg_build_recipes_dir"]).joinpath(build.project_config["component_recipe_file"].name).resolve()
    )

    def throw_error(*args, **kwargs):
        if args[0] == json_values["parsed_component_recipe"]:
            raise TypeError("I mock yaml error")

    mock_json_dump = mocker.patch("json.dumps")
    mock_yaml_dump = mocker.patch("yaml.dump", side_effect=throw_error)
    with patch("builtins.open", mock_open()) as mock_file:
        with pytest.raises(Exception) as e:
            build.create_build_recipe_file()
        assert "Failed to create build recipe file at" in e.value.args[0]
        mock_file.assert_called_once_with(file_name, "w")
        mock_json_dump.call_count == 1
        assert mock_yaml_dump.called


def test_get_build_folder_by_build_system():
    import gdk.commands.component.build as build

    paths = build._get_build_folder_by_build_system()
    assert len(paths) == 1
    assert Path(utils.current_directory).joinpath(*["zip-build"]).resolve() in paths


def test_create_gg_build_directories(mocker):
    mocker.patch("gdk.commands.component.project_utils.get_project_config_values", return_value=json_values)
    import gdk.commands.component.build as build

    mock_mkdir = mocker.patch("pathlib.Path.mkdir")
    mock_clean = mocker.patch("gdk.common.utils.clean_dir")
    build.create_gg_build_directories()

    assert mock_mkdir.call_count == 2
    assert mock_clean.call_count == 1

    mock_mkdir.assert_any_call(json_values["gg_build_recipes_dir"], parents=True, exist_ok=True)
    mock_mkdir.assert_any_call(json_values["gg_build_component_artifacts_dir"], parents=True, exist_ok=True)
    mock_clean.assert_called_once_with(json_values["gg_build_directory"])


def test_run_build_command_with_error_not_zip(mocker):
    mock_build_system_zip = mocker.patch("gdk.commands.component.build._build_system_zip", return_value=None)
    mock_subprocess_run = mocker.patch("subprocess.run", return_value=None, side_effect=Error("some error"))
    mock_platform_system = mocker.patch("platform.system", return_value=None)
    import gdk.commands.component.build as build

    build.project_config["component_build_config"]["build_system"] = "maven"
    with pytest.raises(Exception) as e:
        build.run_build_command()
    assert not mock_build_system_zip.called
    assert mock_subprocess_run.called
    assert mock_platform_system.called
    assert "Error building the component with the given build system." in e.value.args[0]


def test_run_build_command_with_error_with_zip_build(mocker):
    mock_build_system_zip = mocker.patch(
        "gdk.commands.component.build._build_system_zip", return_value=None, side_effect=Error("some error")
    )
    mock_platform_system = mocker.patch("platform.system", return_value=None)
    import gdk.commands.component.build as build

    build.project_config["component_build_config"]["build_system"] = "zip"
    with pytest.raises(Exception) as e:
        build.run_build_command()
    assert "Error building the component with the given build system." in e.value.args[0]
    assert mock_build_system_zip.called
    assert mock_platform_system.called


def test_run_build_command_not_zip_build(mocker):
    mock_build_system_zip = mocker.patch("gdk.commands.component.build._build_system_zip", return_value=None)
    mock_subprocess_run = mocker.patch("subprocess.run", return_value=None)
    mock_platform_system = mocker.patch("platform.system", return_value=None)
    import gdk.commands.component.build as build

    build.project_config["component_build_config"]["build_system"] = "maven"
    build.run_build_command()
    assert not mock_build_system_zip.called
    assert mock_subprocess_run.called
    assert mock_platform_system.called


def test_run_build_command_windows(mocker):
    mock_platform_system = mocker.patch("platform.system", return_value="Windows")
    mock_subprocess_run = mocker.patch("subprocess.run", return_value=None)
    import gdk.commands.component.build as build

    build.project_config["component_build_config"]["build_system"] = "maven"
    build.run_build_command()
    assert mock_subprocess_run.called
    assert mock_platform_system.called


def test_run_build_command_zip_build(mocker):
    mock_build_system_zip = mocker.patch("gdk.commands.component.build._build_system_zip", return_value=None)
    mock_platform_system = mocker.patch("platform.system", return_value=None)
    mock_subprocess_run = mocker.patch("subprocess.run", return_value=None)
    import gdk.commands.component.build as build

    build.project_config["component_build_config"]["build_system"] = "zip"
    build.run_build_command()
    assert not mock_subprocess_run.called
    assert mock_platform_system.called
    mock_build_system_zip.assert_called_with()


def test_build_system_zip_valid(mocker):
    zip_build_path = Path("zip-build").resolve()
    zip_artifacts_path = Path(zip_build_path).joinpath(utils.current_directory.name).resolve()
    mock_build_info = mocker.patch(
        "gdk.commands.component.build._get_build_folder_by_build_system", return_value={zip_build_path}
    )

    mock_clean_dir = mocker.patch("gdk.common.utils.clean_dir", return_value=None)
    mock_copytree = mocker.patch("shutil.copytree")
    mock_subprocess_run = mocker.patch("subprocess.run", return_value=None)
    mock_ignore_files_during_zip = mocker.patch("gdk.commands.component.build._ignore_files_during_zip", return_value=[])
    mock_make_archive = mocker.patch("shutil.make_archive")
    import gdk.commands.component.build as build

    build.project_config["component_build_config"]["build_system"] = "zip"
    build._build_system_zip()

    assert not mock_subprocess_run.called
    mock_build_info.assert_called_with()
    mock_clean_dir.assert_called_with(zip_build_path)

    curr_dir = Path(".").resolve()

    mock_copytree.assert_called_with(curr_dir, zip_artifacts_path, ignore=mock_ignore_files_during_zip)
    assert mock_make_archive.called
    zip_build_file = Path(zip_build_path).joinpath(utils.current_directory.name).resolve()
    mock_make_archive.assert_called_with(zip_build_file, "zip", root_dir=zip_artifacts_path)


def test_ignore_files_during_zip():
    import gdk.commands.component.build as build

    path = Path(".")
    names = ["1", "2"]
    li = build._ignore_files_during_zip(path, names)
    assert type(li) == list


def test_build_system_zip_error_archive(mocker):

    zip_build_path = Path("zip-build").resolve()
    zip_artifacts_path = Path(zip_build_path).joinpath(utils.current_directory.name).resolve()

    mock_build_info = mocker.patch(
        "gdk.commands.component.build._get_build_folder_by_build_system", return_value={zip_build_path}
    )
    mock_clean_dir = mocker.patch("gdk.common.utils.clean_dir", return_value=None)
    mock_copytree = mocker.patch("shutil.copytree")
    mock_subprocess_run = mocker.patch("subprocess.run", return_value=None)
    mock_ignore_files_during_zip = mocker.patch("gdk.commands.component.build._ignore_files_during_zip", return_value=[])
    mock_make_archive = mocker.patch("shutil.make_archive", side_effect=Error("some error"))
    import gdk.commands.component.build as build

    with pytest.raises(Exception) as e:
        build._build_system_zip()

    assert "Failed to zip the component in default build mode." in e.value.args[0]
    assert not mock_subprocess_run.called
    mock_build_info.assert_called_with()
    mock_clean_dir.assert_called_with(zip_build_path)

    curr_dir = Path(".").resolve()

    mock_copytree.assert_called_with(curr_dir, zip_artifacts_path, ignore=mock_ignore_files_during_zip)
    assert mock_make_archive.called
    zip_build_file = Path(zip_build_path).joinpath(utils.current_directory.name).resolve()
    mock_make_archive.assert_called_with(zip_build_file, "zip", root_dir=zip_artifacts_path)


def test_build_system_zip_error_copytree(mocker):
    zip_build_path = Path("zip-build").resolve()
    zip_artifacts_path = Path(zip_build_path).joinpath(utils.current_directory.name).resolve()

    mock_build_info = mocker.patch(
        "gdk.commands.component.build._get_build_folder_by_build_system", return_value={zip_build_path}
    )
    mock_clean_dir = mocker.patch("gdk.common.utils.clean_dir", return_value=None)
    mock_copytree = mocker.patch("shutil.copytree", side_effect=Error("some error"))
    mock_subprocess_run = mocker.patch("subprocess.run", return_value=None)
    mock_ignore_files_during_zip = mocker.patch("gdk.commands.component.build._ignore_files_during_zip", return_value=[])
    mock_make_archive = mocker.patch("shutil.make_archive")
    import gdk.commands.component.build as build

    with pytest.raises(Exception) as e:
        build._build_system_zip()

    assert "Failed to zip the component in default build mode." in e.value.args[0]
    assert not mock_subprocess_run.called
    mock_build_info.assert_called_with()
    mock_clean_dir.assert_called_with(zip_build_path)

    curr_dir = Path(".").resolve()

    mock_copytree.assert_called_with(curr_dir, zip_artifacts_path, ignore=mock_ignore_files_during_zip)
    assert not mock_make_archive.called


def test_build_system_zip_error_get_build_folder_by_build_system(mocker):
    zip_build_path = Path("zip-build").resolve()
    mock_build_info = mocker.patch(
        "gdk.commands.component.build._get_build_folder_by_build_system",
        return_value=zip_build_path,
        side_effect=Error("some error"),
    )
    mock_clean_dir = mocker.patch("gdk.common.utils.clean_dir", return_value=None)
    mock_copytree = mocker.patch("shutil.copytree")
    mock_subprocess_run = mocker.patch("subprocess.run", return_value=None)
    mock_ignore_files_during_zip = mocker.patch("gdk.commands.component.build._ignore_files_during_zip", return_value=[])
    mock_make_archive = mocker.patch("shutil.make_archive")
    import gdk.commands.component.build as build

    with pytest.raises(Exception) as e:
        build._build_system_zip()

    assert "Failed to zip the component in default build mode." in e.value.args[0]
    assert not mock_subprocess_run.called
    mock_build_info.assert_called_with()
    assert not mock_clean_dir.called
    assert not mock_copytree.called
    assert not mock_make_archive.called
    assert not mock_ignore_files_during_zip.called


def test_build_system_zip_error_clean_dir(mocker):
    zip_build_path = Path("zip-build").resolve()
    mock_build_info = mocker.patch(
        "gdk.commands.component.build._get_build_folder_by_build_system", return_value={zip_build_path}
    )
    mock_clean_dir = mocker.patch("gdk.common.utils.clean_dir", return_value=None, side_effect=Error("some error"))
    mock_copytree = mocker.patch("shutil.copytree")
    mock_subprocess_run = mocker.patch("subprocess.run", return_value=None)
    mock_make_archive = mocker.patch("shutil.make_archive")
    import gdk.commands.component.build as build

    with pytest.raises(Exception) as e:
        build._build_system_zip()

    assert "Failed to zip the component in default build mode." in e.value.args[0]
    assert not mock_subprocess_run.called
    mock_build_info.assert_called_with()
    assert mock_clean_dir.called
    assert not mock_copytree.called
    assert not mock_make_archive.called


def test_get_build_cmd_from_platform_non_windows(mocker):
    mock_platform_system = mocker.patch("platform.system", return_value=None)
    import gdk.commands.component.build as build

    build_command = build.get_build_cmd_from_platform("maven")
    assert build_command == ["mvn", "clean", "package"]

    build_command = build.get_build_cmd_from_platform("gradle")
    assert build_command == ["gradle", "build"]

    build_command = build.get_build_cmd_from_platform("zip")
    assert build_command == ["zip"]

    assert mock_platform_system.call_count == 3


def test_get_build_cmd_from_platform_windows(mocker):
    mock_platform_system = mocker.patch("platform.system", return_value="Windows")
    import gdk.commands.component.build as build

    build_command = build.get_build_cmd_from_platform("maven")
    assert build_command == ["mvn.cmd", "clean", "package"]

    build_command = build.get_build_cmd_from_platform("gradle")
    assert build_command == ["gradlew", "build"]

    build_command = build.get_build_cmd_from_platform("zip")
    assert build_command == ["zip"]
    assert mock_platform_system.call_count == 3


def test_find_artifacts_and_update_uri_valid(mocker):
    zip_build_path = [Path("zip-build").resolve()]
    mock_build_info = mocker.patch(
        "gdk.commands.component.build._get_build_folder_by_build_system", return_value=zip_build_path
    )
    mock_shutil_copy = mocker.patch("shutil.copy")
    mock_glob = mocker.patch("pathlib.Path.glob", return_value=[Path(".").joinpath("hello_world.py")])
    mock_is_artifact_in_s3 = mocker.patch("gdk.commands.component.build.is_artifact_in_s3", return_value=False)

    import gdk.commands.component.build as build

    build.find_artifacts_and_update_uri()
    assert mock_build_info.assert_called_once
    assert mock_glob.assert_called_once
    assert mock_shutil_copy.called
    assert not mock_is_artifact_in_s3.called


def test_find_artifacts_and_update_uri_recipe_uri_matches(mocker):
    # Copy only if the uri in recipe matches the artifact in build folder
    zip_build_path = [Path("zip-build").resolve()]
    mock_build_info = mocker.patch(
        "gdk.commands.component.build._get_build_folder_by_build_system", return_value=zip_build_path
    )
    mock_iter_dir_list = [Path("hello_world.py").resolve()]
    mock_shutil_copy = mocker.patch("shutil.copy")
    mock_glob = mocker.patch("pathlib.Path.glob", return_value=mock_iter_dir_list)
    mock_is_artifact_in_s3 = mocker.patch("gdk.commands.component.build.is_artifact_in_s3", return_value=False)
    import gdk.commands.component.build as build

    build.find_artifacts_and_update_uri()
    assert mock_shutil_copy.called
    assert mock_build_info.assert_called_once
    assert mock_glob.assert_called_once
    mock_shutil_copy.assert_called_with(Path("hello_world.py").resolve(), json_values["gg_build_component_artifacts_dir"])
    assert not mock_is_artifact_in_s3.called


def test_find_artifacts_and_update_uri_recipe_uri_not_matches_all(mocker):
    # Do not copy if the uri in recipe doesnt match the artifact in build folder

    zip_build_path = [Path("zip-build").resolve()]
    mock_build_info = mocker.patch(
        "gdk.commands.component.build._get_build_folder_by_build_system", return_value=zip_build_path
    )
    mock_shutil_copy = mocker.patch("shutil.copy")
    mock_glob = mocker.patch("pathlib.Path.glob", return_value=[])
    import gdk.commands.component.build as build

    mock_is_artifact_in_s3 = mocker.patch("gdk.commands.component.build.is_artifact_in_s3", return_value=False)
    with pytest.raises(Exception) as e:
        build.find_artifacts_and_update_uri()

    assert (
        "Could not find artifact with URI 's3://BUCKET_NAME/COMPONENT_NAME/COMPONENT_VERSION/hello_world.py' on s3 or inside"
        " the build folders."
        in e.value.args[0]
    )
    assert not mock_shutil_copy.called
    assert mock_build_info.assert_called_once
    assert mock_glob.assert_called_once
    assert mock_is_artifact_in_s3.called


def test_find_artifacts_and_update_uri_recipe_uri_not_matches_build_folder(mocker):
    # Do not copy if the uri in recipe doesnt match the artifact in build folder

    zip_build_path = [Path("zip-build").resolve()]
    mock_build_info = mocker.patch(
        "gdk.commands.component.build._get_build_folder_by_build_system", return_value=zip_build_path
    )
    mock_shutil_copy = mocker.patch("shutil.copy")
    mock_glob = mocker.patch("pathlib.Path.glob", return_value=[])
    import gdk.commands.component.build as build

    mock_client = mocker.patch("boto3.client", return_value=None)
    mock_create_s3_client = mocker.patch("gdk.commands.component.project_utils.create_s3_client", return_value=mock_client)
    mock_is_artifact_in_s3 = mocker.patch("gdk.commands.component.build.is_artifact_in_s3", return_value=True)
    build.find_artifacts_and_update_uri()

    assert not mock_shutil_copy.called
    assert mock_build_info.assert_called_once
    assert mock_glob.assert_called_once
    assert mock_is_artifact_in_s3.assert_called_once
    assert mock_create_s3_client.called


def test_default_build_component(mocker):
    mock_run_build_command = mocker.patch("gdk.commands.component.build.run_build_command")
    mock_find_artifacts_and_update_uri = mocker.patch("gdk.commands.component.build.find_artifacts_and_update_uri")
    mock_create_build_recipe_file = mocker.patch("gdk.commands.component.build.create_build_recipe_file")
    import gdk.commands.component.build as build

    build.default_build_component()
    assert mock_run_build_command.assert_called_once
    assert mock_find_artifacts_and_update_uri.assert_called_once
    assert mock_create_build_recipe_file.assert_called_once


def test_default_build_component_error_run_build_command(mocker):
    mock_run_build_command = mocker.patch("gdk.commands.component.build.run_build_command", side_effect=Error("command"))
    mock_find_artifacts_and_update_uri = mocker.patch("gdk.commands.component.build.find_artifacts_and_update_uri")
    mock_create_build_recipe_file = mocker.patch("gdk.commands.component.build.create_build_recipe_file")
    import gdk.commands.component.build as build

    with pytest.raises(Exception) as e:
        build.default_build_component()

    assert "\ncommand" in e.value.args[0]
    assert error_messages.BUILD_FAILED in e.value.args[0]
    assert mock_run_build_command.assert_called_once
    assert not mock_find_artifacts_and_update_uri.called
    assert not mock_create_build_recipe_file.called


def test_default_build_component_error_find_artifacts_and_update_uri(mocker):
    mock_run_build_command = mocker.patch("gdk.commands.component.build.run_build_command")
    mock_find_artifacts_and_update_uri = mocker.patch(
        "gdk.commands.component.build.find_artifacts_and_update_uri", side_effect=Error("copying")
    )
    mock_create_build_recipe_file = mocker.patch("gdk.commands.component.build.create_build_recipe_file")
    import gdk.commands.component.build as build

    with pytest.raises(Exception) as e:
        build.default_build_component()

    assert "\ncopy" in e.value.args[0]
    assert error_messages.BUILD_FAILED in e.value.args[0]
    assert mock_run_build_command.assert_called_once
    assert mock_find_artifacts_and_update_uri.assert_called_once
    assert not mock_create_build_recipe_file.called


def test_default_build_component_error_create_build_recipe_file(mocker):
    mock_run_build_command = mocker.patch("gdk.commands.component.build.run_build_command")
    mock_find_artifacts_and_update_uri = mocker.patch("gdk.commands.component.build.find_artifacts_and_update_uri")
    mock_create_build_recipe_file = mocker.patch(
        "gdk.commands.component.build.create_build_recipe_file", side_effect=Error("recipe")
    )
    import gdk.commands.component.build as build

    with pytest.raises(Exception) as e:
        build.default_build_component()

    assert "\nrecipe" in e.value.args[0]
    assert error_messages.BUILD_FAILED in e.value.args[0]
    assert mock_run_build_command.assert_called_once
    assert mock_find_artifacts_and_update_uri.assert_called_once
    assert mock_create_build_recipe_file.assert_called_once


def test_build_run_default(mocker):
    mock_create_gg_build_directories = mocker.patch("gdk.commands.component.build.create_gg_build_directories")
    mock_default_build_component = mocker.patch("gdk.commands.component.build.default_build_component")
    mock_subprocess_run = mocker.patch("subprocess.run")
    import gdk.commands.component.build as build

    build.run({})

    assert mock_create_gg_build_directories.assert_called_once
    assert mock_default_build_component.assert_called_once
    assert not mock_subprocess_run.called


def test_build_run_custom(mocker):
    mock_create_gg_build_directories = mocker.patch("gdk.commands.component.build.create_gg_build_directories")
    mock_default_build_component = mocker.patch("gdk.commands.component.build.default_build_component")
    mock_subprocess_run = mocker.patch("subprocess.run")
    import gdk.commands.component.build as build

    modify_build = build.project_config
    modify_build["component_build_config"]["build_system"] = "custom"
    modify_build["component_build_config"]["custom_build_command"] = ["a"]
    build.run({})
    assert mock_create_gg_build_directories.assert_called_once
    assert not mock_default_build_component.called
    assert mock_subprocess_run.called


def test_find_artifacts_and_update_uri_no_manifest_in_recipe(mocker):
    # Nothing to copy if manifest file doesnt exist
    # recipe with no manifest key

    import gdk.commands.component.build as build

    zip_build_path = Path("zip-build").resolve()
    mock_build_info = mocker.patch(
        "gdk.commands.component.build._get_build_folder_by_build_system", return_value={zip_build_path}
    )
    mock_is_artifact_in_build = mocker.patch("gdk.commands.component.build.is_artifact_in_build", return_value=False)
    mock_is_artifact_in_s3 = mocker.patch("gdk.commands.component.build.is_artifact_in_s3", return_value=False)

    modify_build = build.project_config
    modify_build["parsed_component_recipe"] = {
        "RecipeFormatVersion": "2020-01-25",
        "ComponentName": "com.example.HelloWorld",
        "ComponentVersion": "1.0.0",
        "ComponentDescription": "My first Greengrass component.",
        "ComponentPublisher": "Amazon",
        "ComponentConfiguration": {"DefaultConfiguration": {"Message": "world"}},
    }
    build.find_artifacts_and_update_uri()
    assert not mock_build_info.called
    assert not mock_is_artifact_in_build.called
    assert not mock_is_artifact_in_s3.called


def test_find_artifacts_and_update_uri_no_artifacts_in_recipe(mocker):
    # Nothing to copy if artifacts in recipe manifest don't exist

    import gdk.commands.component.build as build

    mock_is_artifact_in_build = mocker.patch("gdk.commands.component.build.is_artifact_in_build", return_value=False)
    zip_build_path = Path("zip-build").resolve()
    mock_build_info = mocker.patch(
        "gdk.commands.component.build._get_build_folder_by_build_system", return_value={zip_build_path}
    )
    mock_is_artifact_in_s3 = mocker.patch("gdk.commands.component.build.is_artifact_in_s3", return_value=False)
    modify_build = build.project_config
    modify_build["parsed_component_recipe"] = {
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
            }
        ],
    }

    build.find_artifacts_and_update_uri()
    assert mock_build_info.called
    assert not mock_is_artifact_in_build.called
    assert not mock_is_artifact_in_s3.called


def test_find_artifacts_and_update_uri_no_artifact_uri_in_recipe(mocker):
    # Nothing to copy if artifact uri don't exist in the recipe.

    import gdk.commands.component.build as build

    zip_build_path = Path("zip-build").resolve()
    mock_build_info = mocker.patch(
        "gdk.commands.component.build._get_build_folder_by_build_system", return_value={zip_build_path}
    )
    mock_is_artifact_in_build = mocker.patch("gdk.commands.component.build.is_artifact_in_build", return_value=False)
    mock_is_artifact_in_s3 = mocker.patch("gdk.commands.component.build.is_artifact_in_s3", return_value=False)
    modify_build = build.project_config
    modify_build["parsed_component_recipe"] = {
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
                "Artifacts": [{}],
            }
        ],
    }

    build.find_artifacts_and_update_uri()
    assert mock_build_info.called
    assert not mock_is_artifact_in_build.called
    assert not mock_is_artifact_in_s3.called


def test_is_artifact_in_build_artifact_exists(mocker):
    import gdk.commands.component.build as build

    zip_build_path = Path("zip-build").resolve()

    mock_iter_dir_list = Path("hello_world.py").resolve()
    mock_shutil_copy = mocker.patch("shutil.copy")
    mock_glob = mocker.patch("pathlib.Path.glob", return_value=[mock_iter_dir_list])
    artifact = {"URI": "s3://hello_world.py"}
    artifact_found = build.is_artifact_in_build(artifact, {zip_build_path})
    assert mock_shutil_copy.called
    assert mock_glob.called
    assert artifact_found


def test_is_artifact_in_build_artifact_not_exists(mocker):
    import gdk.commands.component.build as build

    zip_build_path = Path("zip-build").resolve()

    mock_shutil_copy = mocker.patch("shutil.copy")
    mock_glob = mocker.patch("pathlib.Path.glob", return_value=[])
    artifact = {"URI": "s3://artifact-not-exists.py"}
    artifact_found = build.is_artifact_in_build(artifact, {zip_build_path})
    assert not mock_shutil_copy.called
    assert not artifact_found
    assert mock_glob.called


def test_find_artifacts_and_update_uri_docker_uri_in_recipe(mocker):
    # Nothing to copy if artifact uri doesn't exist in the recipe.

    import gdk.commands.component.build as build

    zip_build_path = Path("zip-build").resolve()
    mock_build_info = mocker.patch(
        "gdk.commands.component.build._get_build_folder_by_build_system", return_value={zip_build_path}
    )
    mock_is_artifact_in_build = mocker.patch("gdk.commands.component.build.is_artifact_in_build", return_value=False)
    modify_build = build.project_config
    modify_build["parsed_component_recipe"] = {
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
                "Artifacts": [{"URI": "docker:uri"}],
            }
        ],
    }
    mock_is_artifact_in_s3 = mocker.patch("gdk.commands.component.build.is_artifact_in_s3")
    build.find_artifacts_and_update_uri()
    assert mock_build_info.called
    assert not mock_is_artifact_in_build.called
    assert not mock_is_artifact_in_s3.called


def test_find_artifacts_and_update_uri_mix_uri_in_recipe(mocker):
    # Nothing to copy if artifact uri don't exist in the recipe.

    import gdk.commands.component.build as build

    zip_build_path = Path("zip-build").resolve()
    mock_build_info = mocker.patch(
        "gdk.commands.component.build._get_build_folder_by_build_system", return_value={zip_build_path}
    )
    modify_build = build.project_config
    modify_build["parsed_component_recipe"] = {
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
                "Artifacts": [{"URI": "docker:uri"}, {"URI": "s3://hello_world.py"}],
            }
        ],
    }
    mock_is_artifact_in_build = mocker.patch("gdk.commands.component.build.is_artifact_in_build", return_value=True)
    mock_is_artifact_in_s3 = mocker.patch("gdk.commands.component.build.is_artifact_in_s3")
    build.find_artifacts_and_update_uri()
    assert mock_build_info.called
    assert mock_is_artifact_in_build.called
    assert not mock_is_artifact_in_s3.called


def test_find_artifacts_and_update_uri_mix_uri_in_recipe_call_counts(mocker):
    # Nothing to copy if artifact uri don't exist in the recipe.

    import gdk.commands.component.build as build

    zip_build_path = Path("zip-build").resolve()
    mock_build_info = mocker.patch(
        "gdk.commands.component.build._get_build_folder_by_build_system", return_value={zip_build_path}
    )
    modify_build = build.project_config
    modify_build["parsed_component_recipe"] = {
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
                "Artifacts": [
                    {"URI": "docker:uri"},
                    {"URI": "s3://hello_world.py"},
                    {"URI": "s3://not-exists1.py"},
                    {"URI": "s3://not-exists2.py"},
                    {"URI": "s3://not-exists3.py"},
                ],
            }
        ],
    }

    def artifact_found(*args, **kwargs):
        if args[0] == {"URI": "s3://hello_world.py"}:
            return True
        else:
            return False

    mock_client = mocker.patch("boto3.client", return_value=None)
    mock_is_artifact_in_build = mocker.patch("gdk.commands.component.build.is_artifact_in_build", side_effect=artifact_found)
    mock_create_s3_client = mocker.patch("gdk.commands.component.project_utils.create_s3_client", return_value=mock_client)
    mock_is_artifact_in_s3 = mocker.patch("gdk.commands.component.build.is_artifact_in_s3")
    build.find_artifacts_and_update_uri()
    assert mock_build_info.called
    # All 4 s3 uris are searched locally
    assert mock_is_artifact_in_build.call_count == 4
    # Only those uris that are not found locally are searched in s3
    assert mock_is_artifact_in_s3.call_count == 3
    # S3 client is created only once irrespective of no of artifacts.
    assert mock_create_s3_client.call_count == 1


def test_is_artifact_in_s3_found(mocker):
    import gdk.commands.component.build as build

    test_s3_uri = "s3://bucket/object-key.zip"
    mock_client = mocker.patch("boto3.client", return_value=None)
    mock_s3_client = mocker.patch("gdk.commands.component.project_utils.create_s3_client", return_value=mock_client)
    mock_s3_head_object = mocker.patch("boto3.client.head_object", return_value={"ResponseMetadata": {"HTTPStatusCode": 200}})
    artifact_found = build.is_artifact_in_s3(mock_client, test_s3_uri)
    assert artifact_found
    assert not mock_s3_client.called
    assert mock_s3_head_object.called
    mock_s3_head_object.assert_called_with(Bucket="bucket", Key="object-key.zip")


def test_is_artifact_in_s3_not_found(mocker):
    import gdk.commands.component.build as build

    test_s3_uri = "s3://bucket/object-key.zip"
    mock_client = mocker.patch("boto3.client", return_value=None)
    mock_s3_client = mocker.patch("gdk.commands.component.project_utils.create_s3_client", return_value=mock_client)
    mock_s3_head_object = mocker.patch("boto3.client.head_object", side_effect=Error("Some error"))
    artifact_found = build.is_artifact_in_s3(mock_client, test_s3_uri)
    assert not artifact_found
    assert not mock_s3_client.called
    assert mock_s3_head_object.called


def test_get_build_folder_by_build_system_maven(mocker):
    import gdk.commands.component.build as build

    dummy_paths = [Path("/").joinpath("path1"), Path("/").joinpath(*["path1", "path2"])]
    mock_get_build_folders = mocker.patch("gdk.commands.component.build.get_build_folders", return_value=dummy_paths)
    build.project_config["component_build_config"] = {"build_system": "maven"}
    maven_build_paths = build._get_build_folder_by_build_system()
    assert maven_build_paths == dummy_paths
    mock_get_build_folders.assert_any_call(["target"], "pom.xml")


def test_get_build_folder_by_build_system_gradle(mocker):
    import gdk.commands.component.build as build

    dummy_paths = [Path("/").joinpath("path1"), Path("/").joinpath(*["path1", "path2"])]
    mock_get_build_folders = mocker.patch("gdk.commands.component.build.get_build_folders", return_value=dummy_paths)
    build.project_config["component_build_config"] = {"build_system": "gradle"}
    gradle_build_paths = build._get_build_folder_by_build_system()
    assert gradle_build_paths == dummy_paths
    mock_get_build_folders.assert_any_call(["build", "libs"], "build.gradle")


def test_get_build_folders_maven(mocker):
    import gdk.commands.component.build as build

    dummy_build_file_paths = [Path("/").joinpath("path1"), Path("/").joinpath(*["path1", "path2"])]
    dummy_build_folder_paths = [
        Path("/").joinpath("path1"),
        Path("/").joinpath(*["path1", "path2"]),
        Path("/").joinpath(*["path3", "path1"]),
    ]

    def get_files(*args, **kwargs):
        if args[0] == "pom.xml":
            return dummy_build_file_paths
        else:
            return dummy_build_folder_paths

    mock_rglob = mocker.patch("pathlib.Path.rglob", side_effect=get_files)
    build.project_config["component_build_config"] = {"build_system": "maven"}
    maven_b_paths = build.get_build_folders(["target"], "pom.xml")
    mock_rglob.assert_any_call("pom.xml")
    mock_rglob.assert_any_call("target")
    assert maven_b_paths == {Path("/").joinpath(*["target"]), Path("/").joinpath(*["path1", "target"])}


def test_get_build_folders_gradle(mocker):
    import gdk.commands.component.build as build

    dummy_build_file_paths = [Path("/").joinpath("path1"), Path("/").joinpath(*["path1", "path2"])]
    dummy_build_folder_paths = [
        Path("/").joinpath("path1"),
        Path("/").joinpath(*["path1", "path2"]),
        Path("/").joinpath(*["path3", "path1"]),
    ]

    def get_files(*args, **kwargs):
        if args[0] == "build.gradle":
            return dummy_build_file_paths
        else:
            return dummy_build_folder_paths

    mock_rglob = mocker.patch("pathlib.Path.rglob", side_effect=get_files)
    build.project_config["component_build_config"] = {"build_system": "gradle"}
    maven_b_paths = build.get_build_folders(["build", "libs"], "build.gradle")
    mock_rglob.assert_any_call("build.gradle")
    mock_rglob.assert_any_call(str(Path(".").joinpath(*["build", "libs"])))
    assert maven_b_paths == {Path("/").joinpath(*["build", "libs"]), Path("/").joinpath(*["path1", "build", "libs"])}

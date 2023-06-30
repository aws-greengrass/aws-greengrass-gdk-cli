from pathlib import Path
from shutil import Error
from unittest import TestCase
from unittest.mock import patch, ANY

import pytest

import gdk.common.utils as utils
from gdk.build_system.ComponentBuildSystem import ComponentBuildSystem
from gdk.commands.component.BuildCommand import BuildCommand
from gdk.commands.component.transformer.BuildRecipeTransformer import BuildRecipeTransformer
from gdk.common.config.GDKProject import GDKProject


class BuildCommandTest(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker):
        self.mocker = mocker
        self.mock_get_proj_config = self.mocker.patch(
            "gdk.common.configuration.get_configuration",
            return_value=config(),
        )
        self.mocker.patch.object(GDKProject, "_get_recipe_file", return_value=Path(".").joinpath("recipe.json").resolve())

    def test_build_run_default(self):
        mock_create_gg_build_directories = self.mocker.patch.object(BuildCommand, "create_gg_build_directories")
        mock_default_build_component = self.mocker.patch.object(BuildCommand, "default_build_component")

        mock_subprocess_run = self.mocker.patch("subprocess.run")
        BuildCommand({}).run()

        assert self.mock_get_proj_config.assert_called_once
        assert mock_create_gg_build_directories.assert_called_once
        assert mock_default_build_component.assert_called_once
        assert not mock_subprocess_run.called

    def test_build_run_custom(self):
        mock_create_gg_build_directories = self.mocker.patch.object(BuildCommand, "create_gg_build_directories")
        mock_default_build_component = self.mocker.patch.object(BuildCommand, "default_build_component")
        mock_subprocess_run = self.mocker.patch("subprocess.run")
        build_config = config()
        build_config["component"]["com.example.PythonLocalPubSub"]["build"] = {
            "build_system": "custom",
            "custom_build_command": ["a"],
        }
        self.mock_get_proj_config = self.mocker.patch(
            "gdk.common.configuration.get_configuration",
            return_value=build_config,
        )
        build = BuildCommand({})

        build.run()
        assert mock_create_gg_build_directories.assert_called_once
        assert not mock_default_build_component.called
        assert mock_subprocess_run.called

    def test_default_build_component(self):
        mock_run_build_command = self.mocker.patch.object(BuildCommand, "run_build_command")
        mock_transform = self.mocker.patch.object(BuildRecipeTransformer, "transform")

        mock_build_info = self.mocker.patch.object(BuildCommand, "_get_build_folder_by_build_system", return_value=None)
        build = BuildCommand({})
        build.default_build_component()
        assert mock_run_build_command.assert_called_once
        assert mock_transform.assert_called_once

        assert mock_build_info.assert_called_once

    def test_default_build_component_error_transform(self):
        mock_run_build_command = self.mocker.patch.object(BuildCommand, "run_build_command")
        mock_transform = self.mocker.patch.object(BuildRecipeTransformer, "transform", side_effect=Error("generating"))

        mock_build_info = self.mocker.patch.object(BuildCommand, "_get_build_folder_by_build_system", return_value=None)
        build = BuildCommand({})
        with pytest.raises(Exception) as e:
            build.default_build_component()

        assert "generating" in e.value.args[0]
        assert mock_run_build_command.assert_called_once
        assert mock_transform.assert_called_once
        assert mock_build_info.assert_called_once

    def test_create_gg_build_directories(self):
        mock_mkdir = self.mocker.patch("pathlib.Path.mkdir")
        mock_clean = self.mocker.patch("gdk.common.utils.clean_dir")
        build = BuildCommand({})
        build.create_gg_build_directories()

        assert mock_mkdir.call_count == 2
        assert mock_clean.call_count == 1
        mock_mkdir.assert_any_call(build.project_config.gg_build_recipes_dir, parents=True, exist_ok=True)
        mock_mkdir.assert_any_call(build.project_config.gg_build_component_artifacts_dir, parents=True, exist_ok=True)
        mock_clean.assert_called_once_with(build.project_config.gg_build_dir)

    def test_run_build_command_with_error_not_zip(self):
        mock_subprocess_run = self.mocker.patch("subprocess.run", return_value=None, side_effect=Error("some error"))

        build_config = config()
        build_config["component"]["com.example.PythonLocalPubSub"]["build"] = {"build_system": "maven"}
        self.mock_get_proj_config = self.mocker.patch(
            "gdk.common.configuration.get_configuration",
            return_value=build_config,
        )

        build = BuildCommand({})
        with pytest.raises(Exception) as e:
            build.run_build_command()
        assert mock_subprocess_run.called
        assert "some error" in e.value.args[0]

    def test_run_build_command_with_error_with_zip_build(self):
        mock_build_system_zip = self.mocker.patch.object(
            BuildCommand, "run_build_command", return_value=None, side_effect=Error("some error")
        )
        build_config = config()
        build_config["component"]["com.example.PythonLocalPubSub"]["build"] = {"build_system": "zip"}
        self.mock_get_proj_config = self.mocker.patch(
            "gdk.common.configuration.get_configuration",
            return_value=build_config,
        )
        build = BuildCommand({})
        with pytest.raises(Exception) as e:
            build.run_build_command()
        assert "some error" in e.value.args[0]
        assert mock_build_system_zip.called

    def test_run_build_command_not_zip_build(self):
        mock_subprocess_run = self.mocker.patch("subprocess.run", return_value=None)
        build_config = config()
        build_config["component"]["com.example.PythonLocalPubSub"]["build"] = {"build_system": "maven"}
        self.mock_get_proj_config = self.mocker.patch(
            "gdk.common.configuration.get_configuration",
            return_value=build_config,
        )
        build = BuildCommand({})
        build.run_build_command()
        assert mock_subprocess_run.called

    def test_run_build_command_windows(self):
        mock_platform_system = self.mocker.patch("platform.system", return_value="Windows")
        mock_subprocess_run = self.mocker.patch("subprocess.run", return_value=None)
        build_config = config()
        build_config["component"]["com.example.PythonLocalPubSub"]["build"] = {"build_system": "maven"}
        self.mock_get_proj_config = self.mocker.patch(
            "gdk.common.configuration.get_configuration",
            return_value=build_config,
        )
        build = BuildCommand({})
        build.run_build_command()
        assert mock_subprocess_run.called
        assert mock_platform_system.called

    def test_run_build_command_zip_build(self):
        mock_subprocess_run = self.mocker.patch("subprocess.run", return_value=None)
        build_config = config()
        build_config["component"]["com.example.PythonLocalPubSub"]["build"] = {"build_system": "zip"}
        self.mock_get_proj_config = self.mocker.patch(
            "gdk.common.configuration.get_configuration",
            return_value=build_config,
        )

        build = BuildCommand({})
        build.run_build_command()
        assert not mock_subprocess_run.called

    def test_build_system_zip_valid(self):
        zip_build_path = utils.get_current_directory().joinpath("zip-build").resolve()
        zip_artifacts_path = Path(zip_build_path).joinpath(utils.get_current_directory().name).resolve()

        mock_clean_dir = self.mocker.patch("gdk.common.utils.clean_dir", return_value=None)
        mock_copytree = self.mocker.patch("shutil.copytree")
        mock_subprocess_run = self.mocker.patch("subprocess.run", return_value=None)
        mock_make_archive = self.mocker.patch("shutil.make_archive")
        build_config = config()
        build_config["component"]["com.example.PythonLocalPubSub"]["build"] = {
            "build_system": "zip",
            "options": {"zip_name": ""},
        }
        self.mock_get_proj_config = self.mocker.patch(
            "gdk.common.configuration.get_configuration",
            return_value=build_config,
        )
        build = BuildCommand({})
        build.run_build_command()

        assert not mock_subprocess_run.called
        mock_clean_dir.assert_called_with(zip_build_path)

        mock_copytree.assert_called_with(utils.get_current_directory(), zip_artifacts_path, ignore=ANY)
        assert mock_make_archive.called
        zip_build_file = Path(zip_build_path).joinpath("com.example.PythonLocalPubSub").resolve()
        mock_make_archive.assert_called_with(zip_build_file, "zip", root_dir=zip_artifacts_path)

    def test_get_build_folder_by_build_system_maven(self):
        dummy_paths = {Path("/").joinpath("path1"), Path("/").joinpath(*["path1", "path2"])}
        mock_get_build_folders = self.mocker.patch.object(BuildCommand, "get_build_folders", return_value=dummy_paths)

        build = BuildCommand({})
        build.component_build_system = ComponentBuildSystem.get("maven")
        maven_build_paths = build._get_build_folder_by_build_system()
        assert maven_build_paths == dummy_paths
        mock_get_build_folders.assert_any_call(["target"], "pom.xml")

    def test_get_build_folder_by_build_system_gradle(self):
        dummy_paths = {Path("/").joinpath("path1"), Path("/").joinpath(*["path1", "path2"])}
        mock_get_build_folders = self.mocker.patch.object(BuildCommand, "get_build_folders", return_value=dummy_paths)

        build = BuildCommand({})
        build.component_build_system = ComponentBuildSystem.get("gradle")
        gradle_build_paths = build._get_build_folder_by_build_system()
        assert gradle_build_paths == dummy_paths
        mock_get_build_folders.assert_any_call(["build", "libs"], "build.gradle")
        mock_get_build_folders.assert_any_call(["build", "libs"], "build.gradle.kts")

    def test_get_build_folders_maven(self):
        dummy_build_file_paths = [Path("/").joinpath("path1"), Path("/").joinpath(*["path1", "path2"])]

        def get_files(*args, **kwargs):
            if args[0] == "pom.xml":
                return dummy_build_file_paths

        def mock_exists(self):
            return str(self) == str(Path("/").joinpath(*["path1", "target"]).resolve())

        build_config = config()
        build_config["component"]["com.example.PythonLocalPubSub"]["build"] = {"build_system": "maven"}
        self.mock_get_proj_config = self.mocker.patch(
            "gdk.common.configuration.get_configuration",
            return_value=build_config,
        )
        build = BuildCommand({})
        with patch.object(Path, "exists", mock_exists):
            mock_rglob = self.mocker.patch("pathlib.Path.rglob", side_effect=get_files)
            maven_b_paths = build.get_build_folders(["target"], "pom.xml")
            mock_rglob.assert_any_call("pom.xml")
            assert maven_b_paths == {Path("/").joinpath(*["path1", "target"]).resolve()}

    def test_get_build_folders_gradle(self):
        dummy_build_file_paths = [Path("/").joinpath("path1"), Path("/").joinpath(*["path1", "path2"])]

        def get_files(*args, **kwargs):
            if args[0] == "build.gradle":
                return dummy_build_file_paths

        def mock_exists(self):
            return str(self) == str(Path("/").joinpath(*["build", "libs"]).resolve()) or str(self) == str(
                Path("/").joinpath(*["path1", "build", "libs"]).resolve()
            )

        build_config = config()
        build_config["component"]["com.example.PythonLocalPubSub"]["build"] = {"build_system": "gradle"}
        self.mock_get_proj_config = self.mocker.patch(
            "gdk.common.configuration.get_configuration",
            return_value=build_config,
        )
        build = BuildCommand({})
        with patch.object(Path, "exists", mock_exists):
            mock_rglob = self.mocker.patch("pathlib.Path.rglob", side_effect=get_files)
            gradle_b_paths = build.get_build_folders(["build", "libs"], "build.gradle")
            mock_rglob.assert_any_call("build.gradle")
            assert gradle_b_paths == {
                Path("/").joinpath(*["build", "libs"]).resolve(),
                Path("/").joinpath(*["path1", "build", "libs"]).resolve(),
            }


def config():
    return {
        "component": {
            "com.example.PythonLocalPubSub": {
                "author": "<PLACEHOLDER_AUTHOR>",
                "version": "NEXT_PATCH",
                "build": {"build_system": "zip"},
                "publish": {"bucket": "<PLACEHOLDER_BUCKET>", "region": "region"},
            }
        },
        "gdk_version": "1.0.0",
    }

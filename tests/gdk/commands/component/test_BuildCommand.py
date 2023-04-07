from pathlib import Path
from shutil import Error
from unittest import TestCase
from unittest.mock import patch, ANY

import pytest

import gdk.common.utils as utils
from gdk.build_system.Zip import Zip
from gdk.commands.component.BuildCommand import BuildCommand
from gdk.commands.component.transformer.BuildRecipeTransformer import BuildRecipeTransformer


class BuildCommandTest(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker):
        self.mocker = mocker
        self.mock_get_proj_config = self.mocker.patch(
            "gdk.commands.component.project_utils.get_project_config_values",
            return_value=project_config(),
        )

    def test_build_run_default(self):
        mock_create_gg_build_directories = self.mocker.patch.object(BuildCommand, "create_gg_build_directories")
        mock_default_build_component = self.mocker.patch.object(BuildCommand, "default_build_component")

        mock_get_supported_component_builds = self.mocker.patch(
            "gdk.commands.component.project_utils.get_supported_component_builds", return_value={}
        )
        mock_subprocess_run = self.mocker.patch("subprocess.run")
        BuildCommand({}).run()

        assert self.mock_get_proj_config.assert_called_once
        assert mock_create_gg_build_directories.assert_called_once
        assert mock_default_build_component.assert_called_once
        assert not mock_subprocess_run.called
        assert mock_get_supported_component_builds.called

    def test_build_run_custom(self):
        mock_create_gg_build_directories = self.mocker.patch.object(BuildCommand, "create_gg_build_directories")
        mock_default_build_component = self.mocker.patch.object(BuildCommand, "default_build_component")
        mock_subprocess_run = self.mocker.patch("subprocess.run")

        mock_get_supported_component_builds = self.mocker.patch(
            "gdk.commands.component.project_utils.get_supported_component_builds", return_value={}
        )
        build = BuildCommand({})
        build.project_config["component_build_config"]["build_system"] = "custom"
        build.project_config["component_build_config"]["custom_build_command"] = ["a"]

        build.run()
        assert mock_create_gg_build_directories.assert_called_once
        assert not mock_default_build_component.called
        assert mock_subprocess_run.called
        assert mock_get_supported_component_builds.called

    def test_default_build_component(self):
        mock_run_build_command = self.mocker.patch.object(BuildCommand, "run_build_command")
        mock_transform = self.mocker.patch.object(BuildRecipeTransformer, "transform")
        mock_get_supported_component_builds = self.mocker.patch(
            "gdk.commands.component.project_utils.get_supported_component_builds", return_value={}
        )
        mock_build_info = self.mocker.patch.object(BuildCommand, "_get_build_folder_by_build_system", return_value=None)
        build = BuildCommand({})
        build.default_build_component()
        assert mock_run_build_command.assert_called_once
        assert mock_transform.assert_called_once
        assert mock_get_supported_component_builds.called
        assert mock_build_info.assert_called_once

    def test_default_build_component_error_transform(self):
        mock_run_build_command = self.mocker.patch.object(BuildCommand, "run_build_command")
        mock_transform = self.mocker.patch.object(BuildRecipeTransformer, "transform", side_effect=Error("generating"))

        mock_get_supported_component_builds = self.mocker.patch(
            "gdk.commands.component.project_utils.get_supported_component_builds", return_value={}
        )
        mock_build_info = self.mocker.patch.object(BuildCommand, "_get_build_folder_by_build_system", return_value=None)
        build = BuildCommand({})
        with pytest.raises(Exception) as e:
            build.default_build_component()

        assert "generating" in e.value.args[0]
        assert mock_run_build_command.assert_called_once
        assert mock_transform.assert_called_once
        assert mock_build_info.assert_called_once

        assert mock_get_supported_component_builds.called

    def test_create_gg_build_directories(self):

        mock_get_supported_component_builds = self.mocker.patch(
            "gdk.commands.component.project_utils.get_supported_component_builds", return_value={}
        )

        mock_mkdir = self.mocker.patch("pathlib.Path.mkdir")
        mock_clean = self.mocker.patch("gdk.common.utils.clean_dir")
        build = BuildCommand({})
        build.create_gg_build_directories()

        assert mock_mkdir.call_count == 2
        assert mock_clean.call_count == 1
        pc = self.mock_get_proj_config.return_value
        mock_mkdir.assert_any_call(pc["gg_build_recipes_dir"], parents=True, exist_ok=True)
        mock_mkdir.assert_any_call(pc["gg_build_component_artifacts_dir"], parents=True, exist_ok=True)
        mock_clean.assert_called_once_with(pc["gg_build_directory"])
        assert mock_get_supported_component_builds.called

    def test_run_build_command_with_error_not_zip(self):
        mock_build_system_zip = self.mocker.patch.object(BuildCommand, "_build_system_zip", return_value=None)
        mock_subprocess_run = self.mocker.patch("subprocess.run", return_value=None, side_effect=Error("some error"))
        mock_get_cmd_from_platform = self.mocker.patch.object(
            BuildCommand, "get_build_cmd_from_platform", return_value="some-command"
        )

        mock_get_supported_component_builds = self.mocker.patch(
            "gdk.commands.component.project_utils.get_supported_component_builds", return_value={}
        )

        build = BuildCommand({})
        build.project_config["component_build_config"]["build_system"] = "maven"
        with pytest.raises(Exception) as e:
            build.run_build_command()
        assert not mock_build_system_zip.called
        assert mock_subprocess_run.called
        assert "some error" in e.value.args[0]

        assert mock_get_supported_component_builds.called
        assert mock_get_cmd_from_platform.called

    def test_run_build_command_with_error_with_zip_build(self):
        mock_build_system_zip = self.mocker.patch.object(
            BuildCommand, "_build_system_zip", return_value=None, side_effect=Error("some error")
        )
        mock_get_cmd_from_platform = self.mocker.patch.object(
            BuildCommand, "get_build_cmd_from_platform", return_value="some-command"
        )

        mock_get_supported_component_builds = self.mocker.patch(
            "gdk.commands.component.project_utils.get_supported_component_builds", return_value={}
        )
        build = BuildCommand({})
        build.project_config["component_build_config"]["build_system"] = "zip"
        with pytest.raises(Exception) as e:
            build.run_build_command()
        assert "some error" in e.value.args[0]
        assert mock_build_system_zip.called
        assert mock_get_cmd_from_platform.call_count == 1
        assert mock_get_supported_component_builds.call_count == 1

    def test_run_build_command_not_zip_build(self):
        mock_build_system_zip = self.mocker.patch.object(BuildCommand, "_build_system_zip", return_value=None)
        mock_subprocess_run = self.mocker.patch("subprocess.run", return_value=None)
        mock_get_cmd_from_platform = self.mocker.patch.object(
            BuildCommand, "get_build_cmd_from_platform", return_value="some-command"
        )

        mock_get_supported_component_builds = self.mocker.patch(
            "gdk.commands.component.project_utils.get_supported_component_builds", return_value={}
        )
        build = BuildCommand({})

        build.project_config["component_build_config"]["build_system"] = "maven"
        build.run_build_command()
        assert not mock_build_system_zip.called
        assert mock_subprocess_run.called
        assert mock_get_cmd_from_platform.call_count == 1
        assert mock_get_supported_component_builds.call_count == 1

    def test_get_build_folder_by_build_system(self):

        build_sys = {
            "zip": {
                "build_command": ["zip"],
                "build_folder": ["zip-build"],
            }
        }
        mock_get_supported_component_builds = self.mocker.patch(
            "gdk.commands.component.project_utils.get_supported_component_builds", return_value=build_sys
        )
        build = BuildCommand({})
        paths = build._get_build_folder_by_build_system()
        assert len(paths) == 1
        assert Path(utils.current_directory).joinpath(*["zip-build"]).resolve() in paths
        assert mock_get_supported_component_builds.call_count == 1

    def test_run_build_command_windows(self):
        mock_platform_system = self.mocker.patch("platform.system", return_value="Windows")
        mock_subprocess_run = self.mocker.patch("subprocess.run", return_value=None)

        build_sys = {
            "maven": {
                "build_command": ["mvn", "clean", "package"],
                "build_command_win": ["mvn.cmd", "clean", "package"],
                "build_folder": ["target"],
            }
        }
        mock_get_supported_component_builds = self.mocker.patch(
            "gdk.commands.component.project_utils.get_supported_component_builds", return_value=build_sys
        )
        build = BuildCommand({})

        build.project_config["component_build_config"]["build_system"] = "maven"
        build.run_build_command()
        assert mock_subprocess_run.called
        assert mock_platform_system.called
        assert mock_get_supported_component_builds.call_count == 1

    def test_run_build_command_zip_build(self):
        mock_build_system_zip = self.mocker.patch.object(BuildCommand, "_build_system_zip", return_value=None)
        mock_platform_system = self.mocker.patch("platform.system", return_value=None)
        mock_subprocess_run = self.mocker.patch("subprocess.run", return_value=None)

        build_sys = {
            "zip": {
                "build_command": ["zip"],
                "build_folder": ["zip-build"],
            }
        }
        mock_get_supported_component_builds = self.mocker.patch(
            "gdk.commands.component.project_utils.get_supported_component_builds", return_value=build_sys
        )
        build = BuildCommand({})

        build.project_config["component_build_config"]["build_system"] = "zip"
        build.run_build_command()
        assert not mock_subprocess_run.called
        assert mock_platform_system.called
        mock_build_system_zip.assert_called_with()
        assert mock_get_supported_component_builds.call_count == 1

    def test_build_system_zip_valid(self):
        zip_build_path = Path("zip-build").resolve()
        zip_artifacts_path = Path(zip_build_path).joinpath(utils.current_directory.name).resolve()
        mock_build_info = self.mocker.patch.object(
            BuildCommand, "_get_build_folder_by_build_system", return_value={zip_build_path}
        )

        mock_clean_dir = self.mocker.patch("gdk.common.utils.clean_dir", return_value=None)
        mock_copytree = self.mocker.patch("shutil.copytree")
        mock_subprocess_run = self.mocker.patch("subprocess.run", return_value=None)
        mock_make_archive = self.mocker.patch("shutil.make_archive")

        build_sys = {
            "zip": {
                "build_command": ["zip"],
                "build_folder": ["zip-build"],
            }
        }
        mock_get_supported_component_builds = self.mocker.patch(
            "gdk.commands.component.project_utils.get_supported_component_builds", return_value=build_sys
        )
        build = BuildCommand({})
        build.project_config["component_build_config"]["build_system"] = "zip"
        build._build_system_zip()

        assert not mock_subprocess_run.called
        mock_build_info.assert_called_with()
        mock_clean_dir.assert_called_with(zip_build_path)

        curr_dir = Path(".").resolve()

        mock_copytree.assert_called_with(curr_dir, zip_artifacts_path, ignore=ANY)
        assert mock_make_archive.called
        zip_build_file = Path(zip_build_path).joinpath(utils.current_directory.name).resolve()
        mock_make_archive.assert_called_with(zip_build_file, "zip", root_dir=zip_artifacts_path)
        assert mock_get_supported_component_builds.call_count == 1

    def test_build_system_zip_error_archive(self):

        zip_build_path = Path("zip-build").resolve()
        zip_artifacts_path = Path(zip_build_path).joinpath(utils.current_directory.name).resolve()

        mock_build_info = self.mocker.patch.object(
            BuildCommand, "_get_build_folder_by_build_system", return_value={zip_build_path}
        )
        mock_clean_dir = self.mocker.patch("gdk.common.utils.clean_dir", return_value=None)
        mock_copytree = self.mocker.patch("shutil.copytree")
        mock_subprocess_run = self.mocker.patch("subprocess.run", return_value=None)
        mock_make_archive = self.mocker.patch("shutil.make_archive", side_effect=Error("some error"))

        build_sys = {
            "zip": {
                "build_command": ["zip"],
                "build_folder": ["zip-build"],
            }
        }
        mock_get_supported_component_builds = self.mocker.patch(
            "gdk.commands.component.project_utils.get_supported_component_builds", return_value=build_sys
        )
        build = BuildCommand({})
        with pytest.raises(Exception) as e:
            build._build_system_zip()

        assert "some error" in e.value.args[0]
        assert not mock_subprocess_run.called
        mock_build_info.assert_called_with()
        mock_clean_dir.assert_called_with(zip_build_path)

        curr_dir = Path(".").resolve()

        mock_copytree.assert_called_with(curr_dir, zip_artifacts_path, ignore=ANY)
        assert mock_make_archive.called
        zip_build_file = Path(zip_build_path).joinpath(utils.current_directory.name).resolve()
        mock_make_archive.assert_called_with(zip_build_file, "zip", root_dir=zip_artifacts_path)

        assert mock_get_supported_component_builds.call_count == 1

    def test_build_system_zip_error_copytree(self):
        zip_build_path = Path("zip-build").resolve()
        zip_artifacts_path = Path(zip_build_path).joinpath(utils.current_directory.name).resolve()

        mock_build_info = self.mocker.patch.object(
            BuildCommand, "_get_build_folder_by_build_system", return_value={zip_build_path}
        )
        mock_clean_dir = self.mocker.patch("gdk.common.utils.clean_dir", return_value=None)
        mock_copytree = self.mocker.patch("shutil.copytree", side_effect=Error("some error"))
        mock_subprocess_run = self.mocker.patch("subprocess.run", return_value=None)

        build_sys = {
            "zip": {
                "build_command": ["zip"],
                "build_folder": ["zip-build"],
            }
        }
        mock_get_supported_component_builds = self.mocker.patch(
            "gdk.commands.component.project_utils.get_supported_component_builds", return_value=build_sys
        )
        mock_make_archive = self.mocker.patch("shutil.make_archive")
        build = BuildCommand({})
        with pytest.raises(Exception) as e:
            build._build_system_zip()

        assert "some error" in e.value.args[0]
        assert not mock_subprocess_run.called
        mock_build_info.assert_called_with()
        mock_clean_dir.assert_called_with(zip_build_path)

        curr_dir = Path(".").resolve()

        mock_copytree.assert_called_with(curr_dir, zip_artifacts_path, ignore=ANY)
        assert not mock_make_archive.called
        assert mock_get_supported_component_builds.call_count == 1

    def test_build_system_zip_error_get_build_folder_by_build_system(self):
        mock_build_info = self.mocker.patch.object(
            BuildCommand,
            "_get_build_folder_by_build_system",
            side_effect=Error("some-error"),
        )
        mock_clean_dir = self.mocker.patch("gdk.common.utils.clean_dir", return_value=None)
        mock_copytree = self.mocker.patch("shutil.copytree")
        mock_subprocess_run = self.mocker.patch("subprocess.run", return_value=None)
        mock_ignore_files_during_zip = self.mocker.patch.object(Zip, "get_ignored_file_patterns", return_value=[])
        mock_make_archive = self.mocker.patch("shutil.make_archive")

        build_sys = {
            "zip": {
                "build_command": ["zip"],
                "build_folder": ["zip-build"],
            }
        }
        mock_get_supported_component_builds = self.mocker.patch(
            "gdk.commands.component.project_utils.get_supported_component_builds", return_value=build_sys
        )
        build = BuildCommand({})

        with pytest.raises(Exception) as e:
            build._build_system_zip()

        assert "some-error" in e.value.args[0]
        assert not mock_subprocess_run.called
        mock_build_info.assert_called_with()
        assert not mock_clean_dir.called
        assert not mock_copytree.called
        assert not mock_make_archive.called
        assert not mock_ignore_files_during_zip.called
        assert mock_get_supported_component_builds.called

    def test_build_system_zip_error_clean_dir(self):
        zip_build_path = Path("zip-build").resolve()
        mock_build_info = self.mocker.patch.object(
            BuildCommand, "_get_build_folder_by_build_system", return_value={zip_build_path}
        )
        mock_clean_dir = self.mocker.patch("gdk.common.utils.clean_dir", return_value=None, side_effect=Error("some error"))
        mock_copytree = self.mocker.patch("shutil.copytree")
        mock_subprocess_run = self.mocker.patch("subprocess.run", return_value=None)
        mock_make_archive = self.mocker.patch("shutil.make_archive")

        build_sys = {
            "zip": {
                "build_command": ["zip"],
                "build_folder": ["zip-build"],
            }
        }
        mock_get_supported_component_builds = self.mocker.patch(
            "gdk.commands.component.project_utils.get_supported_component_builds", return_value=build_sys
        )
        build = BuildCommand({})

        with pytest.raises(Exception) as e:
            build._build_system_zip()

        assert "some error" in e.value.args[0]
        assert not mock_subprocess_run.called
        mock_build_info.assert_called_with()
        assert mock_clean_dir.called
        assert not mock_copytree.called
        assert not mock_make_archive.called
        assert mock_get_supported_component_builds.call_count == 1

    def test_get_build_cmd_from_platform_non_windows(self):
        mock_platform_system = self.mocker.patch("platform.system", return_value=None)

        build = BuildCommand({})

        build_command = build.get_build_cmd_from_platform("maven")
        assert build_command == ["mvn", "clean", "package"]

        build_command = build.get_build_cmd_from_platform("gradle")
        assert build_command == ["gradle", "clean", "build"]

        build_command = build.get_build_cmd_from_platform("zip")
        assert build_command == ["zip"]

        assert mock_platform_system.call_count == 3

    def test_get_build_cmd_from_platform_windows(self):
        mock_platform_system = self.mocker.patch("platform.system", return_value="Windows")

        build = BuildCommand({})

        build_command = build.get_build_cmd_from_platform("maven")
        assert build_command == ["mvn.cmd", "clean", "package"]

        build_command = build.get_build_cmd_from_platform("gradle")
        assert build_command == ["gradle", "clean", "build"]

        build_command = build.get_build_cmd_from_platform("zip")
        assert build_command == ["zip"]
        assert mock_platform_system.call_count == 3

    def test_get_build_folder_by_build_system_maven(self):
        dummy_paths = [Path("/").joinpath("path1"), Path("/").joinpath(*["path1", "path2"])]
        mock_get_build_folders = self.mocker.patch.object(BuildCommand, "get_build_folders", return_value=dummy_paths)

        build = BuildCommand({})
        build.project_config["component_build_config"] = {"build_system": "maven"}
        maven_build_paths = build._get_build_folder_by_build_system()
        assert maven_build_paths == dummy_paths
        mock_get_build_folders.assert_any_call(["target"], "pom.xml")

    def test_get_build_folder_by_build_system_gradle(self):
        dummy_paths = {Path("/").joinpath("path1"), Path("/").joinpath(*["path1", "path2"])}
        mock_get_build_folders = self.mocker.patch.object(BuildCommand, "get_build_folders", return_value=dummy_paths)

        build = BuildCommand({})
        build.project_config["component_build_config"] = {"build_system": "gradle"}
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

        build = BuildCommand({})
        with patch.object(Path, "exists", mock_exists):
            mock_rglob = self.mocker.patch("pathlib.Path.rglob", side_effect=get_files)
            build.project_config["component_build_config"] = {"build_system": "maven"}
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

        build = BuildCommand({})
        with patch.object(Path, "exists", mock_exists):
            mock_rglob = self.mocker.patch("pathlib.Path.rglob", side_effect=get_files)
            build.project_config["component_build_config"] = {"build_system": "gradle"}
            gradle_b_paths = build.get_build_folders(["build", "libs"], "build.gradle")
            mock_rglob.assert_any_call("build.gradle")
            assert gradle_b_paths == {
                Path("/").joinpath(*["build", "libs"]).resolve(),
                Path("/").joinpath(*["path1", "build", "libs"]).resolve(),
            }


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
    }

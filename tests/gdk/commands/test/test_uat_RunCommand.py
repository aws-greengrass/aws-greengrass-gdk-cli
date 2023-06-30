import pytest
from unittest import TestCase
from unittest.mock import call
from gdk.commands.test.RunCommand import RunCommand
from pathlib import Path
import os
from gdk.common.URLDownloader import URLDownloader
import gdk.common.consts as consts
import subprocess as sp
from gdk.common.config.GDKProject import GDKProject


class RunCommandUnitTest(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker, tmpdir):
        self.mocker = mocker
        self.tmpdir = Path(tmpdir)
        self.c_dir = Path(".").resolve()

        config = {
            "component": {
                "abc": {
                    "author": "abc",
                    "version": "1.0.0",
                    "build": {"build_system": "zip"},
                    "publish": {"bucket": "default", "region": "us-east-1"},
                }
            }
        }

        self.mocker.patch("gdk.common.configuration.get_configuration", return_value=config)
        self.mocker.patch.object(GDKProject, "_get_recipe_file", return_value=Path(".").joinpath("recipe.json").resolve())
        self.mock_sp = self.mocker.patch("subprocess.run", return_value=None)

        os.chdir(tmpdir)
        yield
        os.chdir(self.c_dir)

    def test_given_test_module_not_built_when_run_e2e_tests_then_raise_exception(self):
        def file_exists(self):
            return str(self) != str(Path().resolve().joinpath(f"greengrass-build/{consts.E2E_TESTS_DIR_NAME}/target"))

        self.mock_jar = self.mocker.patch("gdk.commands.test.RunCommand.RunCommand.run_testing_jar", return_value=None)
        self.mocker.patch.object(Path, "exists", file_exists)
        run_cmd = RunCommand({})
        with pytest.raises(Exception) as e:
            run_cmd.run()
        assert "E2E testing module is not built." in e.value.args[0]

    def test_given_nucleus_archive_at_default_path_when_run_e2e_tests_then_do_not_download_nucleus(self):
        mock_downloader = self.mocker.patch.object(URLDownloader, "download")
        self.mock_jar = self.mocker.patch("gdk.commands.test.RunCommand.RunCommand.run_testing_jar", return_value=None)
        self.mocker.patch("pathlib.Path.exists", return_value=True)
        run_cmd = RunCommand({})
        run_cmd.run()

        assert not mock_downloader.called

    def test_given_nucleus_does_not_exists_at_default_path_when_run_e2e_tests_then_download_nucleus(self):
        default_path = Path().resolve().joinpath("greengrass-build/greengrass-nucleus-latest.zip")
        self.mock_jar = self.mocker.patch("gdk.commands.test.RunCommand.RunCommand.run_testing_jar", return_value=None)

        def file_exists(self):
            return str(self) != str(default_path)

        mock_downloader = self.mocker.patch.object(URLDownloader, "download")
        self.mocker.patch.object(Path, "exists", file_exists)
        run_cmd = RunCommand({})
        run_cmd.run()

        mock_downloader.assert_called_once_with(default_path)

    def test_given_default_jar_exists_when_run_jar_then_default_jar_is_identified_and_run_as_testing_jar(self):
        self.mocker.patch("pathlib.Path.exists", return_value=True)
        _jar_identifier_args = [
            "java",
            "-jar",
            Path()
            .absolute()
            .joinpath(f"greengrass-build/{consts.E2E_TESTS_DIR_NAME}/target/{consts.E2E_TESTS_DIR_NAME}-1.0.0.jar")
            .__str__(),
            "--help",
        ]

        _jar_testing_args = [
            "java",
            "-jar",
            Path()
            .absolute()
            .joinpath(f"greengrass-build/{consts.E2E_TESTS_DIR_NAME}/target/{consts.E2E_TESTS_DIR_NAME}-1.0.0.jar")
            .__str__(),
            "--tags=Sample",
            "--ggc-archive=" + Path().absolute().joinpath("greengrass-build/greengrass-nucleus-latest.zip").__str__(),
        ]

        def sp_run(*args, **kwargs):
            if args[0] == _jar_identifier_args:
                return sp.CompletedProcess(args[0], 0, stdout="gg-test help text of testing jar".encode())
            else:
                return sp.CompletedProcess(args[0], 0, stdout="running testing jar".encode())

        self.mock_sp = self.mocker.patch("subprocess.run", side_effect=sp_run)
        run_cmd = RunCommand({})
        run_cmd.run()

        assert len(self.mock_sp.call_args_list) == 2
        assert self.mock_sp.call_args_list[0] == call(_jar_identifier_args, check=False, stderr=-2, stdout=-1)
        _second_call = self.mock_sp.call_args_list[1]
        # jar args can be appened in any order
        set(_second_call[0][0]) == set(_jar_testing_args)

    def test_given_default_config_when_error_running_jar_then_raise_exception(self):
        # self.mocker.patch("pathlib.Path.exists", return_value=True)

        def file_exists(self):
            return str(self) != str(
                Path()
                .resolve()
                .joinpath(f"greengrass-build/{consts.E2E_TESTS_DIR_NAME}/target/{consts.E2E_TESTS_DIR_NAME}-1.0.0.jar")
            )

        def glob(self, _name):
            return [Path().absolute().joinpath("a.jar")]

        self.mocker.patch.object(Path, "exists", file_exists)

        self.mocker.patch.object(Path, "glob", glob)
        _jar_identifier_args = [
            "java",
            "-jar",
            Path().absolute().joinpath("a.jar").__str__(),
            "--help",
        ]

        _jar_testing_args = [
            "java",
            "-jar",
            Path().absolute().joinpath("a.jar").__str__(),
            "--tags=Sample",
            "--ggc-archive=" + Path().absolute().joinpath("greengrass-build/greengrass-nucleus-latest.zip").__str__(),
        ]

        def sp_run(*args, **kwargs):
            if args[0] == _jar_identifier_args:
                return sp.CompletedProcess(args[0], 0, stdout="gg-test help text of testing jar".encode())
            else:
                raise Exception("Error running jar")

        self.mock_sp = self.mocker.patch("subprocess.run", side_effect=sp_run)
        run_cmd = RunCommand({})
        with pytest.raises(Exception) as e:
            run_cmd.run()
        assert "Error running jar" in e.value.args[0]
        assert len(self.mock_sp.call_args_list) == 2
        assert self.mock_sp.call_args_list[0] == call(_jar_identifier_args, check=False, stderr=-2, stdout=-1)
        _second_call = self.mock_sp.call_args_list[1]
        # jar args can be appened in any order
        set(_second_call[0][0]) == set(_jar_testing_args)

    def test_given_multiple_jars_when_no_testing_jar_identified_then_raise_Exception(self):
        def file_exists(self):
            return str(self) != str(
                Path()
                .resolve()
                .joinpath(f"greengrass-build/{consts.E2E_TESTS_DIR_NAME}/target/{consts.E2E_TESTS_DIR_NAME}-1.0.0.jar")
            )

        def glob(self, _name):
            return ["a.jar", "b.jar"]

        self.mocker.patch.object(Path, "exists", file_exists)

        self.mocker.patch.object(Path, "glob", glob)

        def sp_run(*args, **kwargs):
            return sp.CompletedProcess(args[0], 1, stdout="Error running jar".encode())

        self.mock_sp = self.mocker.patch("subprocess.run", side_effect=sp_run)
        run_cmd = RunCommand({})

        with pytest.raises(Exception) as e:
            run_cmd.run_testing_jar()

        assert "Unable to find testing jar in the build folder" in e.value.args[0]

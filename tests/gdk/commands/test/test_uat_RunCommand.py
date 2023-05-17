import pytest
from unittest import TestCase
from unittest.mock import ANY
from gdk.commands.test.RunCommand import RunCommand
from pathlib import Path
import os
from gdk.common.URLDownloader import URLDownloader


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
        self.mocker.patch("gdk.commands.component.project_utils.get_recipe_file", return_value=Path("."))
        self.mock_sp = self.mocker.patch("subprocess.run", return_value=None)
        os.chdir(tmpdir)
        yield
        os.chdir(self.c_dir)

    def test_given_test_module_not_built_when_run_uats_then_raise_exception(self):
        def file_exists(self):
            return str(self) != str(Path().resolve().joinpath("greengrass-build/uat-features/target"))

        self.mocker.patch.object(Path, "exists", file_exists)
        run_cmd = RunCommand({})
        with pytest.raises(Exception) as e:
            run_cmd.run()
        assert "UAT module is not built." in e.value.args[0]

    def test_given_nucleus_archive_at_default_path_when_run_uats_then_do_not_download_nucleus(self):
        mock_downloader = self.mocker.patch.object(URLDownloader, "download")
        self.mocker.patch("pathlib.Path.exists", return_value=True)
        run_cmd = RunCommand({})
        run_cmd.run()

        assert not mock_downloader.called

    def test_given_nucleus_does_not_exists_at_default_path_when_run_uats_then_download_nucleus(self):
        default_path = Path().resolve().joinpath("greengrass-build/greengrass-nucleus-latest.zip")

        def file_exists(self):
            return str(self) != str(default_path)

        mock_downloader = self.mocker.patch.object(URLDownloader, "download")
        self.mocker.patch.object(Path, "exists", file_exists)
        run_cmd = RunCommand({})
        run_cmd.run()

        mock_downloader.assert_called_once_with(default_path)

    def test_given_default_config_when_run_uats_then_run_testing_jar_with_default_options(self):
        self.mocker.patch("pathlib.Path.exists", return_value=True)
        run_cmd = RunCommand({})
        run_cmd.run()
        self.mock_sp.assert_called_once_with(ANY, check=True)
        command_arguments = self.mock_sp.call_args_list[0][0][0]
        assert set(command_arguments) == set(
            [
                "java",
                "-jar",
                Path().resolve().joinpath("greengrass-build/uat-features/target/uat-features-1.0.0.jar").__str__(),
                "--ggc-archive=" + Path().resolve().joinpath("greengrass-build/greengrass-nucleus-latest.zip").__str__(),
                "--tags=Sample",
            ]
        )

    def test_given_default_config_when_error_running_jar_then_raise_exception(self):
        self.mocker.patch("pathlib.Path.exists", return_value=True)
        self.mock_sp = self.mocker.patch("subprocess.run", side_effect=Exception("Error running jar"))
        run_cmd = RunCommand({})
        with pytest.raises(Exception) as e:
            run_cmd.run()
        assert "Error running jar" in e.value.args[0]
        self.mock_sp.assert_called_once_with(ANY, check=True)

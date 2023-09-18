from unittest import TestCase
from unittest.mock import call
import pytest
from pathlib import Path
import os
from gdk.commands.test.RunCommand import RunCommand
import shutil
from gdk.common.URLDownloader import URLDownloader
import subprocess as sp
import json
import gdk.common.consts as consts
from gdk.common.config.GDKProject import GDKProject


class E2ETestRunCommandTest(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker, tmpdir):
        self.mocker = mocker
        self.tmpdir = Path(tmpdir).resolve()
        self.c_dir = Path(".").resolve()
        template_path = Path(self.c_dir).joinpath("integration_tests/test_data/templates/TestTemplateForCLI.zip").resolve()
        with open(template_path, "rb") as f:
            template_content = f.read()
        mock_response = self.mocker.Mock(status_code=200, content=template_content)
        self.mock_template_download = self.mocker.patch("requests.get", return_value=mock_response)
        self.url_for_template = (
            "https://github.com/aws-greengrass/aws-greengrass-component-templates/releases/download/v1.0/"
            + "TestTemplateForCLI.zip"
        )
        self.mocker.patch.object(GDKProject, "_get_recipe_file", return_value=Path(".").joinpath("recipe.json").resolve())

        os.chdir(tmpdir)
        yield
        os.chdir(self.c_dir)

    def test_given_test_module_not_built_when_run_e2e_tests_then_raise_an_exception(self):
        self.setup_test_data_config("config_without_test.json")
        run_command = RunCommand({})
        with pytest.raises(Exception) as e:
            run_command.run()
        assert (
            "E2E testing module is not built. Please build the test module using `gdk test build`"
            + "command before running the tests."
        ) in e.value.args[0]

    def test_given_test_module_and_nucleus_archive_built_when_run_e2e_tests_then_run_e2e_tests(self):
        # Given
        self.setup_test_data_config("config_without_test.json")
        run_jar = self.mocker.patch("gdk.commands.test.RunCommand.RunCommand.run_testing_jar", return_value=None)
        target_path = self.tmpdir.joinpath(f"greengrass-build/{consts.E2E_TESTS_DIR_NAME}/target")
        _nucleus_path = self.tmpdir.joinpath("greengrass-build/greengrass-nucleus-latest.zip")
        url_downloader = self.mocker.patch.object(URLDownloader, "download", return_value=target_path)
        target_path.mkdir(parents=True)
        _nucleus_path.touch()

        run_command = RunCommand({})
        # When
        run_command.run()

        # Then
        assert not url_downloader.called
        assert run_jar.called

    def test_given_module_built_and_nucleus_zip_not_exists_when_run_e2e_tests_then_download_nucleus_and_run_e2e_tests(self):
        # Given
        self.setup_test_data_config("config_without_test.json")
        run_jar = self.mocker.patch("gdk.commands.test.RunCommand.RunCommand.run_testing_jar", return_value=None)
        target_path = self.tmpdir.joinpath(f"greengrass-build/{consts.E2E_TESTS_DIR_NAME}/target")
        _nucleus_path = self.tmpdir.joinpath("greengrass-build/greengrass-nucleus-latest.zip")
        target_path.mkdir(parents=True)

        run_command = RunCommand({})
        # When
        run_command.run()

        # Then
        assert run_jar.called
        assert _nucleus_path.exists()

    def test_given_built_module_and_nucleus_zip_when_no_testing_jar_found_then_raise_an_exception(self):
        # Given
        self.setup_test_data_config("config_without_test.json")
        target_path = self.tmpdir.joinpath(f"greengrass-build/{consts.E2E_TESTS_DIR_NAME}/target")
        _nucleus_path = self.tmpdir.joinpath("greengrass-build/greengrass-nucleus-latest.zip")
        target_path.mkdir(parents=True)
        _nucleus_path.touch()

        run_command = RunCommand({})
        # When and then
        with pytest.raises(Exception) as e:
            run_command.run()
        assert "Unable to find testing jar in the build folder" in e.value.args[0]

    def test_given_ggc_archive_config_and_nucleus_zip_not_exists_when_run_e2e_tests_then_raise_an_exception(self):
        # Given
        self.setup_test_data_config("config_without_test.json")
        run_jar = self.mocker.patch("gdk.commands.test.RunCommand.RunCommand.run_testing_jar", return_value=None)
        with open(Path().joinpath("gdk-config.json"), "r") as f:
            content = json.loads(f.read())
            content["test-e2e"] = {"otf_options": {"ggc-archive": "/doesn/not/exis/nucleus.zip"}}
        with open(Path().joinpath("gdk-config.json"), "w") as f:
            f.write(json.dumps(content))

        target_path = self.tmpdir.joinpath(f"greengrass-build/{consts.E2E_TESTS_DIR_NAME}/target")
        target_path.mkdir(parents=True)

        # When and then
        with pytest.raises(Exception) as e:
            RunCommand({})
        assert (
            "Cannot find nucleus archive at path /doesn/not/exis/nucleus.zip. Please check 'ggc-archive' in the test config"
            in e.value.args[0]
        )

        assert not run_jar.called

    def test_given_multiple_jars_and_when_not_testing_jar_found_then_raise_an_exception(self):
        # Given
        self.setup_test_data_config("config_without_test.json")
        target_path = self.tmpdir.joinpath(f"greengrass-build/{consts.E2E_TESTS_DIR_NAME}/target")
        _nucleus_path = self.tmpdir.joinpath("greengrass-build/greengrass-nucleus-latest.zip")
        target_path.mkdir(parents=True)
        _nucleus_path.touch()
        target_path.joinpath(f"{consts.E2E_TESTS_DIR_NAME}-1.0.0.jar").touch()
        target_path.joinpath("b.jar").touch()

        run_command = RunCommand({})
        # When and then
        with pytest.raises(Exception) as e:
            run_command.run()
        assert "Unable to find testing jar in the build folder" in e.value.args[0]

    def test_given_multiple_jars_and_when_run_e2e_tests_then_identify_default_jar_and_run_e2e_tests(self):
        # Given
        self.setup_test_data_config("config_without_test.json")
        self.update_pom()

        # Build test module
        shutil.copytree(
            self.tmpdir.joinpath(consts.E2E_TESTS_DIR_NAME),
            self.tmpdir.joinpath(f"greengrass-build/{consts.E2E_TESTS_DIR_NAME}/"),
        )

        Path().joinpath(f"greengrass-build/{consts.E2E_TESTS_DIR_NAME}/target/").mkdir(parents=True)
        Path().joinpath(
            f"greengrass-build/{consts.E2E_TESTS_DIR_NAME}/target/{consts.E2E_TESTS_DIR_NAME}-1.0.0.jar"
        ).resolve().touch()
        Path().joinpath(f"greengrass-build/{consts.E2E_TESTS_DIR_NAME}/target/b.jar").resolve().touch()

        # nucleus archive exists
        _nucleus_path = self.tmpdir.joinpath("greengrass-build/greengrass-nucleus-latest.zip")
        _nucleus_path.touch()

        jar = str(
            Path()
            .joinpath(f"greengrass-build/{consts.E2E_TESTS_DIR_NAME}/target/{consts.E2E_TESTS_DIR_NAME}-1.0.0.jar")
            .resolve()
        )

        def _sp_run(self, *args, **kwargs):
            if set(self) == set(["java", "-jar", jar, "--help"]):
                return sp.CompletedProcess(self, returncode=0, stdout="gg-test".encode())
            return sp.CompletedProcess(self, returncode=0)

        spy_run = self.mocker.patch.object(sp, "run", side_effect=_sp_run)

        run_command = RunCommand({})

        # When
        run_command.run()

        # Then
        assert len(spy_run.call_args_list) == 2

        _first_call = spy_run.call_args_list[0]
        _second_call = spy_run.call_args_list[1]
        assert _first_call == call(["java", "-jar", jar, "--help"], check=False, stderr=-2, stdout=-1)
        assert set(_second_call[0][0]) == set(
            [
                "java",
                "-jar",
                jar,
                "--tags=Sample",
                "--ggc-archive=" + str(Path().joinpath("greengrass-build/greengrass-nucleus-latest.zip").resolve()),
            ]
        )

    def test_given_multiple_jars_and_when_run_e2e_tests_with_non_default_jar_and_exception_then_raise_an_exception(self):
        # Given
        self.setup_test_data_config("config_without_test.json")
        self.update_pom()

        Path().joinpath(f"greengrass-build/{consts.E2E_TESTS_DIR_NAME}/target/").mkdir(parents=True)
        Path().joinpath(f"greengrass-build/{consts.E2E_TESTS_DIR_NAME}/target/a.jar").resolve().touch()
        Path().joinpath(f"greengrass-build/{consts.E2E_TESTS_DIR_NAME}/target/b.jar").resolve().touch()

        _non_default_jar = Path().joinpath(f"greengrass-build/{consts.E2E_TESTS_DIR_NAME}/target/a.jar").resolve()
        _nucleus_path = self.tmpdir.joinpath("greengrass-build/greengrass-nucleus-latest.zip")
        _nucleus_path.touch()

        def _sp_run(self, *args, **kwargs):
            if "--help" in set(self):
                if set(self) == set(["java", "-jar", str(_non_default_jar), "--help"]):
                    return sp.CompletedProcess(self, returncode=0, stdout="gg-test".encode())
                else:
                    return sp.CompletedProcess(self, returncode=1, stderr=b"Error running jar")
            else:
                raise Exception("Error running jar")

        sp_run = self.mocker.patch.object(sp, "run", side_effect=_sp_run)
        run_command = RunCommand({})

        # When
        with pytest.raises(Exception) as e:
            run_command.run()
        assert "Error running jar" in e.value.args[0]

        _jar_args = set(
            ["java", "-jar", str(_non_default_jar), "--tags=Sample", "--ggc-archive=" + str(_nucleus_path.resolve())]
        )

        _jar_run_proc = sp_run.call_args_list[-1]
        assert set(_jar_run_proc[0][0]) == _jar_args

    def setup_test_data_config(self, config_file):
        # Setup test data
        source = Path(self.c_dir).joinpath("integration_tests/test_data/config").joinpath(config_file).resolve()
        shutil.copy(source, Path(self.tmpdir).joinpath("gdk-config.json"))
        shutil.unpack_archive(
            Path(self.c_dir).joinpath("integration_tests/test_data/templates/TestTemplateForCLI.zip").resolve(),
            extract_dir=Path(self.tmpdir),
        )
        shutil.move(Path(self.tmpdir).joinpath("TestTemplateForCLI"), Path(self.tmpdir).joinpath(consts.E2E_TESTS_DIR_NAME))
        Path(self.tmpdir).joinpath("greengrass-build/recipes").mkdir(parents=True)

    def update_pom(self):
        with open(self.tmpdir.joinpath(f"{consts.E2E_TESTS_DIR_NAME}/pom.xml"), "r") as f:
            content = f.read()

        with open(self.tmpdir.joinpath(f"{consts.E2E_TESTS_DIR_NAME}/pom.xml"), "w") as f:
            f.write(content.replace("GDK_TESTING_VERSION", "1.0.0-SNAPSHOT"))

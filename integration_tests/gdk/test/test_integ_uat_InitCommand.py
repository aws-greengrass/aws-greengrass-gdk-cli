from unittest import TestCase
from unittest.mock import call
import pytest
from pathlib import Path
import os
from gdk.commands.test.InitCommand import InitCommand
import shutil
from urllib3.exceptions import HTTPError
import gdk.common.consts as consts


class E2ETestInitCommandTest(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker, tmpdir):
        self.mocker = mocker
        self.tmpdir = tmpdir
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
        os.chdir(tmpdir)
        yield
        os.chdir(self.c_dir)

    def test_init_run_gdk_project(self):
        self.setup_test_data_config("config.json")
        self.mocker.patch.object(InitCommand, "update_testing_module_build_identifiers")
        InitCommand({}).run()
        assert self.mock_template_download.call_args_list == [call(self.url_for_template, stream=True, timeout=30)]
        e2e_test_folder = Path(self.tmpdir).joinpath(consts.E2E_TESTS_DIR_NAME)
        assert e2e_test_folder.exists()
        assert e2e_test_folder.joinpath("pom.xml") in list(e2e_test_folder.iterdir())
        # Downloaded template has GDK_TESTING_VERSION variable in pom.xml
        with open(e2e_test_folder.joinpath("pom.xml"), "r", encoding="utf-8") as f:
            content = f.read()
            assert "GDK_TESTING_VERSION" in content

    def test_init_run_gdk_project_already_initiated(self):
        self.setup_test_data_config("config.json")
        self.mocker.patch.object(InitCommand, "update_testing_module_build_identifiers")
        # consts.E2E_TESTS_DIR_NAME already exists but is empty
        Path(self.tmpdir).joinpath(consts.E2E_TESTS_DIR_NAME).mkdir()

        InitCommand({}).run()
        assert not self.mock_template_download.called
        # existing consts.E2E_TESTS_DIR_NAME folder is not overridden
        assert Path(self.tmpdir).resolve(consts.E2E_TESTS_DIR_NAME).exists()
        assert list(Path(self.tmpdir).joinpath(consts.E2E_TESTS_DIR_NAME).iterdir()) == []

    def test_init_run_gdk_project_update_otf_version(self):
        self.setup_test_data_config("config.json")
        InitCommand({}).run()
        assert self.mock_template_download.call_args_list == [call(self.url_for_template, stream=True, timeout=30)]

        # existing consts.E2E_TESTS_DIR_NAME folder is not overridden
        e2e_test_folder = Path(self.tmpdir).joinpath(consts.E2E_TESTS_DIR_NAME)
        assert e2e_test_folder.exists()
        # OTF version is updated in pom.xml
        with open(e2e_test_folder.joinpath("pom.xml"), "r", encoding="utf-8") as f:
            content = f.read()
            assert "GDK_TESTING_VERSION" not in content
            # OTF version set in config file
            assert "<otf.version>1.2.0</otf.version>" in content

    def test_init_run_error_downloading_template(self):
        self.setup_test_data_config("config.json")
        mock_response = self.mocker.Mock(
            status_code=404, raise_for_status=self.mocker.Mock(side_effect=HTTPError("some error"))
        )
        self.mocker.patch("requests.get", return_value=mock_response)

        with pytest.raises(Exception) as e:
            InitCommand({}).run()
            assert self.mock_template_download.call_args_list == [call(self.url_for_template, stream=True, timeout=30)]
            assert "some error" in e.value.args[0]
        assert not Path(self.tmpdir).joinpath(consts.E2E_TESTS_DIR_NAME).exists()

    def setup_test_data_config(self, config_file):
        # Setup test data
        source = Path(self.c_dir).joinpath("integration_tests/test_data/config/").joinpath(config_file).resolve()
        shutil.copy(source, Path(self.tmpdir).joinpath("gdk-config.json"))

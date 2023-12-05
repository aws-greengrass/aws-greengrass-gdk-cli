from unittest import TestCase
from unittest.mock import call
import pytest
from pathlib import Path
import os
from gdk.commands.test.InitCommand import InitCommand
import shutil
from urllib3.exceptions import HTTPError
import gdk.common.consts as consts
from gdk.common.config.GDKProject import GDKProject
from gdk.common.GithubUtils import GithubUtils
import requests


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
        self.mocker.patch.object(GDKProject, "_get_recipe_file", return_value=Path(".").joinpath("recipe.json").resolve())
        self.mocker.patch.object(GithubUtils, "get_latest_release_name", return_value="1.2.0")

        os.chdir(tmpdir)
        yield
        os.chdir(self.c_dir)

    def test_Given_GDK_project_with_an_empty_e2e_test_folder_When_test_init_Then_download_template(self):
        self.setup_test_data_config("config.json")
        response = requests.Response()
        response.status_code = 200
        self.mocker.patch("requests.head", return_value=response)
        self.mocker.patch.object(InitCommand, "update_testing_module_build_identifiers")
        # consts.E2E_TESTS_DIR_NAME already exists but is empty
        Path(self.tmpdir).joinpath(consts.E2E_TESTS_DIR_NAME).mkdir()

        InitCommand({}).run()
        assert self.mock_template_download.call_args_list == [call(self.url_for_template, stream=True, timeout=30)]
        e2e_test_folder = Path(self.tmpdir).joinpath(consts.E2E_TESTS_DIR_NAME)
        assert e2e_test_folder.exists()
        assert e2e_test_folder.joinpath("pom.xml") in list(e2e_test_folder.iterdir())
        # Downloaded template has GDK_TESTING_VERSION variable in pom.xml
        with open(e2e_test_folder.joinpath("pom.xml"), "r", encoding="utf-8") as f:
            content = f.read()
            assert "GDK_TESTING_VERSION" in content

    def test_Given_GDK_project_with_non_empty_e2e_test_folder_When_test_init_Then_raise_exc(self):
        self.setup_test_data_config("config.json")
        response = requests.Response()
        response.status_code = 200
        self.mocker.patch("requests.head", return_value=response)
        self.mocker.patch.object(InitCommand, "update_testing_module_build_identifiers")
        Path(self.tmpdir).joinpath(consts.E2E_TESTS_DIR_NAME).mkdir()
        some_file = Path(self.tmpdir).joinpath(consts.E2E_TESTS_DIR_NAME).joinpath("some_file").resolve()
        some_file.touch()

        InitCommand({}).run()
        assert not self.mock_template_download.called
        # existing consts.E2E_TESTS_DIR_NAME folder is not overridden
        assert Path(self.tmpdir).resolve(consts.E2E_TESTS_DIR_NAME).exists()
        assert list(Path(self.tmpdir).joinpath(consts.E2E_TESTS_DIR_NAME).iterdir()) == [some_file]

    def test_GIVEN_gdk_project_WHEN_test_init_THEN_initialize_the_curr_dir_with_testing_template(self):
        self.setup_test_data_config("config.json")
        response = requests.Response()
        response.status_code = 200
        self.mocker.patch("requests.head", return_value=response)

        InitCommand({}).run()
        assert self.mock_template_download.call_args_list == [call(self.url_for_template, stream=True, timeout=30)]

        # existing consts.E2E_TESTS_DIR_NAME folder is not overridden
        e2e_test_folder = Path(self.tmpdir).joinpath(consts.E2E_TESTS_DIR_NAME)
        assert e2e_test_folder.exists()
        # GTF version is updated in pom.xml
        with open(e2e_test_folder.joinpath("pom.xml"), "r", encoding="utf-8") as f:
            content = f.read()
            assert "GDK_TESTING_VERSION" not in content
            # GTF version set in config file
            assert "<otf.version>1.2.0-SNAPSHOT</otf.version>" in content

    def test_GIVEN_gdk_project_WHEN_test_init_with_otf_version_arg_THEN_version_is_arg_is_used(self):
        self.setup_test_data_config("config.json")
        InitCommand({"otf_version": "1.0.0"}).run()
        assert self.mock_template_download.call_args_list == [call(self.url_for_template, stream=True, timeout=30)]

        # existing consts.E2E_TESTS_DIR_NAME folder is not overridden
        e2e_test_folder = Path(self.tmpdir).joinpath(consts.E2E_TESTS_DIR_NAME)
        assert e2e_test_folder.exists()
        # GTF version is updated in pom.xml
        with open(e2e_test_folder.joinpath("pom.xml"), "r", encoding="utf-8") as f:
            content = f.read()
            assert "GDK_TESTING_VERSION" not in content
            # GTF version set in config file
            assert "<otf.version>1.0.0-SNAPSHOT</otf.version>" in content

    def test_GIVEN_gdk_project_WHEN_test_init_with_gtf_version_arg_THEN_gtf_version_is_arg_is_used(self):
        self.setup_test_data_config("config.json")
        InitCommand({"gtf_version": "1.0.0"}).run()
        assert self.mock_template_download.call_args_list == [call(self.url_for_template, stream=True, timeout=30)]

        # existing consts.E2E_TESTS_DIR_NAME folder is not overridden
        e2e_test_folder = Path(self.tmpdir).joinpath(consts.E2E_TESTS_DIR_NAME)
        assert e2e_test_folder.exists()
        # GTF version is updated in pom.xml
        with open(e2e_test_folder.joinpath("pom.xml"), "r", encoding="utf-8") as f:
            content = f.read()
            assert "GDK_TESTING_VERSION" not in content
            # GTF version set in config file
            assert "<otf.version>1.0.0-SNAPSHOT</otf.version>" in content

    def test_GIVEN_gdk_project_WHEN_test_init_with_otf_and_gtf_version_arg_THEN_gtf_version_is_arg_is_used(self):
        self.setup_test_data_config("config.json")
        InitCommand({"gtf_version": "1.0.0", "otf_version": "1.1.0"}).run()
        assert self.mock_template_download.call_args_list == [call(self.url_for_template, stream=True, timeout=30)]

        # existing consts.E2E_TESTS_DIR_NAME folder is not overridden
        e2e_test_folder = Path(self.tmpdir).joinpath(consts.E2E_TESTS_DIR_NAME)
        assert e2e_test_folder.exists()
        # GTF version is updated in pom.xml
        with open(e2e_test_folder.joinpath("pom.xml"), "r", encoding="utf-8") as f:
            content = f.read()
            assert "GDK_TESTING_VERSION" not in content
            # GTF version set in config file
            assert "<otf.version>1.0.0-SNAPSHOT</otf.version>" in content

    def test_GIVEN_gdk_project_WHEN_test_init_with_otf_version_and_otf_version_not_exists_THEN_raise_exc(self):
        self.setup_test_data_config("config.json")

        with pytest.raises(ValueError) as e:
            InitCommand({"otf_version": "10.0.0"}).run()
        assert "The specified Greengrass Test Framework (GTF) version '10.0.0' does not exist." in e.value.args[0]

        assert not self.mock_template_download.called

        assert not Path(self.tmpdir).joinpath(consts.E2E_TESTS_DIR_NAME).exists()

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

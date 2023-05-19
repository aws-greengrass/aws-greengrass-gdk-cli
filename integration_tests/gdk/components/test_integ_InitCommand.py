from unittest import TestCase
from unittest.mock import call
import gdk.CLIParser as CLIParser
import gdk.common.exceptions.error_messages as error_messages
import gdk.common.parse_args_actions as parse_args_actions
import gdk.common.utils as utils
import pytest
from urllib3.exceptions import HTTPError
from pathlib import Path
import os
import requests


class InitCommandIntegTest(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker, tmpdir):
        self.mocker = mocker
        self.tmpdir = Path(tmpdir).resolve()
        self.c_dir = Path(".").resolve()
        self.url = "https://raw.githubusercontent.com/aws-greengrass/aws-greengrass-software-catalog/main/cli-components/"
        os.chdir(self.tmpdir)
        yield
        os.chdir(self.c_dir)

    def test_given_cur_dir_not_empty_when_init_in_cur_dir_then_raise_an_exception(self):
        # Given
        _file = Path(self.tmpdir).joinpath("some-file").resolve()
        _file.touch()

        with pytest.raises(Exception) as e:
            # When
            parse_args_actions.run_command(CLIParser.cli_parser.parse_args(["component", "init", "-d"]))
        # Then
        assert error_messages.INIT_NON_EMPTY_DIR_ERROR in e.value.args[0]

    def test_given_cur_dir_empty_when_init_with_template__then_dir_is_initialized(self):
        # When
        parse_args_actions.run_command(
            CLIParser.cli_parser.parse_args(["component", "init", "-t", "HelloWorld", "-l", "python"])
        )

        # Then
        assert self.tmpdir.joinpath("gdk-config.json").exists()

    def test_given_dir_doesnt_exist_when_init_with_repo_and_dir_name_then_dir_is_initialized(self):
        # When
        parse_args_actions.run_command(
            CLIParser.cli_parser.parse_args(
                ["component", "init", "--repository", "aws-greengrass-labs-database-postgresql", "-n", "new-dir"]
            )
        )
        _new_dir = Path(self.tmpdir).joinpath("new-dir").resolve()

        # Then
        assert _new_dir.exists()
        assert _new_dir.joinpath("gdk-config.json").exists()

    def test_given_dir_exists_and_not_empty_when_init_with_template_and_dir_name_then_raise_an_exception(self):
        # Given
        _new_dir = Path(self.tmpdir).joinpath("new-dir").resolve()
        _new_dir.mkdir()
        _file = Path(_new_dir).joinpath("gdk-config.json")
        _file.touch()

        # When and Then
        with pytest.raises(Exception) as e:
            parse_args_actions.run_command(
                CLIParser.cli_parser.parse_args(
                    ["component", "init", "--template", "HelloWorld", "-l", "python", "-n", "new-dir"]
                )
            )

        assert (
            "Could not initialize the project as the directory is not empty. Please initialize the project in an empty"
            " directory.\nTry `gdk component init --help`"
            in e.value.args[0]
        )
        # The directory and files in it should not be modified
        assert _file.exists()

    def test_given_cur_dir_when_init_with_repo_and_template_then_raise_an_exception(self):
        with pytest.raises(Exception) as e:
            parse_args_actions.run_command(
                CLIParser.cli_parser.parse_args(["component", "init", "-r", "dummy", "-t", "template"])
            )

        assert (
            "The command provided is invalid.\nArguments 'template' and 'repository' are conflicting and cannot be used"
            " together in a command."
            in e.value.args[0]
        )

        assert utils.is_directory_empty(self.tmpdir)

    def test_given_cur_dir_when_init_with_template_but_not_language_then_raise_an_exception(self):
        with pytest.raises(Exception) as e:
            parse_args_actions.run_command(CLIParser.cli_parser.parse_args(["component", "init", "-t", "dummy"]))

        assert (
            "Could not initialize the project as the arguments passed are invalid. Please initialize the project with"
            " correct arguments."
            in e.value.args[0]
        )

        assert utils.is_directory_empty(self.tmpdir)

    def test_given_error_during_download_when_init_with_template_then_raise_an_exception(self):
        mock_response = self.mocker.Mock(
            status_code=404, raise_for_status=self.mocker.Mock(side_effect=HTTPError("Not found"))
        )

        def requests_get(*args, **kwargs):
            if args[0] == "https://dummy-link":
                return mock_response
            else:
                res = requests.Response()
                res.status_code = 200
                res._content = '{"dummy-python": "https://dummy-link"}'.encode()
                return res

        mock_requests_get = self.mocker.patch("requests.get", side_effect=requests_get)

        with pytest.raises(Exception) as e:
            parse_args_actions.run_command(
                CLIParser.cli_parser.parse_args(["component", "init", "-t", "dummy", "-l", "python"])
            )
        assert "Not found" in e.value.args[0]
        assert mock_requests_get.call_args_list == [
            call(self.url + "templates.json"),
            call("https://dummy-link", stream=True, timeout=30),
        ]

        assert utils.is_directory_empty(self.tmpdir)

    def test_given_error_during_download_when_init_with_repository_then_raise_an_exception(self):
        mock_response = self.mocker.Mock(
            status_code=404, raise_for_status=self.mocker.Mock(side_effect=HTTPError("Not found"))
        )

        def requests_get(*args, **kwargs):
            if args[0] == "https://dummy-link":
                return mock_response
            else:
                res = requests.Response()
                res.status_code = 200
                res._content = '{"dummy": "https://dummy-link"}'.encode()
                return res

        mock_requests_get = self.mocker.patch("requests.get", side_effect=requests_get)

        with pytest.raises(Exception) as e:
            parse_args_actions.run_command(CLIParser.cli_parser.parse_args(["component", "init", "-r", "dummy"]))
        assert "Not found" in e.value.args[0]
        assert mock_requests_get.call_args_list == [
            call(self.url + "community-components.json"),
            call("https://dummy-link", stream=True, timeout=30),
        ]

        assert utils.is_directory_empty(self.tmpdir)

    def test_given_template_doesnt_exist_when_init_with_template_and_name_then_raise_an_exception_and_do_not_create_new_dir(
        self,
    ):
        def requests_get(*args, **kwargs):
            res = requests.Response()
            res.status_code = 200
            res._content = '{"dummy": "https://dummy-link"}'.encode()
            return res

        mock_requests_get = self.mocker.patch("requests.get", side_effect=requests_get)

        with pytest.raises(Exception) as e:
            parse_args_actions.run_command(
                CLIParser.cli_parser.parse_args(
                    ["component", "init", "-t", "template-not-exists", "-l", "python", "-n", "new-dir"]
                )
            )

        assert (
            "Could not find the component template 'template-not-exists-python' in Greengrass Software Catalog."
            in e.value.args[0]
        )

        assert mock_requests_get.call_args_list == [call(self.url + "templates.json")]
        _new_dir = Path(self.tmpdir).joinpath("new-dir").resolve()

        # Then
        assert not _new_dir.exists()

    def test_given_repo_doesnt_exist_when_init_with_repository_and_name_then_raise_an_exception_and_do_not_create_new_dir(
        self,
    ):
        def requests_get(*args, **kwargs):
            res = requests.Response()
            res.status_code = 200
            res._content = '{"dummy": "https://dummy-link"}'.encode()
            return res

        mock_requests_get = self.mocker.patch("requests.get", side_effect=requests_get)

        with pytest.raises(Exception) as e:
            parse_args_actions.run_command(
                CLIParser.cli_parser.parse_args(["component", "init", "--repository", "repo-not-exists", "-n", "new-dir"])
            )

        assert "Could not find the component repository 'repo-not-exists' in Greengrass Software Catalog." in e.value.args[0]
        assert mock_requests_get.call_args_list == [call(self.url + "community-components.json")]
        _new_dir = Path(self.tmpdir).joinpath("new-dir").resolve()

        # Then
        assert not _new_dir.exists()

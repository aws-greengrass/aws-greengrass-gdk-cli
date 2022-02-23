from unittest import TestCase
from unittest.mock import Mock, mock_open, patch

import gdk.CLIParser as CLIParser
import gdk.common.consts as consts
import gdk.common.parse_args_actions as parse_args_actions
import gdk.common.utils as utils
import pytest
from gdk.commands.component.InitCommand import InitCommand
from gdk.commands.component.ListCommand import ListCommand
from urllib3.exceptions import HTTPError


class CommandTest(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker):
        self.mocker = mocker

    def test_init_run_non_empty_dir(self):
        with pytest.raises(Exception) as e:
            parse_args_actions.run_command(CLIParser.cli_parser.parse_args(["component", "init", "-d"]))
        assert "The current directory is not empty.\nPlease initialize the project in an empty directory." in e.value.args[0]

        mock_non_empty_dir = self.mocker.patch("gdk.common.utils.is_directory_empty", return_value=False)
        mock_init_with_template = self.mocker.patch.object(InitCommand, "init_with_template", return_value=None)
        mock_init_with_repository = self.mocker.patch.object(InitCommand, "init_with_repository", return_value=None)
        mock_conflicting_args = self.mocker.patch.object(InitCommand, "check_if_arguments_conflict", return_value=None)
        with pytest.raises(Exception) as e:
            parse_args_actions.run_command(CLIParser.cli_parser.parse_args(["component", "init", "-d"]))
        assert "The current directory is not empty.\nPlease initialize the project in an empty directory." in e.value.args[0]
        assert mock_non_empty_dir.call_count == 1
        assert not mock_init_with_template.called
        assert not mock_init_with_repository.called
        assert mock_conflicting_args.called

    def test_init_run_empty_dir(self):
        mock_non_empty_dir = self.mocker.patch("gdk.common.utils.is_directory_empty", return_value=True)
        mock_init_with_template = self.mocker.patch.object(InitCommand, "init_with_template", return_value=None)
        mock_init_with_repository = self.mocker.patch.object(InitCommand, "init_with_repository", return_value=None)
        mock_conflicting_args = self.mocker.patch.object(InitCommand, "check_if_arguments_conflict", return_value=None)
        parse_args_actions.run_command(CLIParser.cli_parser.parse_args(["component", "init", "--repository", "dummy"]))

        assert mock_non_empty_dir.call_count == 1
        assert not mock_init_with_template.called
        assert mock_init_with_repository.call_count == 1
        assert mock_conflicting_args.call_count == 1

    def test_init_run_new_dir_repo_success(self):
        mock_non_empty_dir = self.mocker.patch("gdk.common.utils.is_directory_empty", return_value=False)
        mock_init_with_template = self.mocker.patch.object(InitCommand, "init_with_template", return_value=None)
        mock_init_with_repository = self.mocker.patch.object(InitCommand, "init_with_repository", return_value=None)
        mock_conflicting_args = self.mocker.patch.object(InitCommand, "check_if_arguments_conflict", return_value=None)
        mock_new_dir = self.mocker.patch("pathlib.Path.mkdir", return_value=None)
        parse_args_actions.run_command(
            CLIParser.cli_parser.parse_args(["component", "init", "--repository", "dummy", "-n", "new-dir"])
        )

        assert not mock_non_empty_dir.called
        assert mock_new_dir.call_count == 1
        assert not mock_init_with_template.called
        assert mock_init_with_repository.call_count == 1
        assert mock_conflicting_args.call_count == 1

    def test_init_run_new_dir_repo_fail(self):
        mock_non_empty_dir = self.mocker.patch("gdk.common.utils.is_directory_empty", return_value=False)
        mock_init_with_template = self.mocker.patch.object(InitCommand, "init_with_template", return_value=None)
        mock_init_with_repository = self.mocker.patch.object(InitCommand, "init_with_repository", return_value=None)
        mock_conflicting_args = self.mocker.patch.object(InitCommand, "check_if_arguments_conflict", return_value=None)
        mock_new_dir = self.mocker.patch("pathlib.Path.mkdir", side_effect=FileExistsError("File exists"))
        with pytest.raises(Exception) as e:
            parse_args_actions.run_command(
                CLIParser.cli_parser.parse_args(["component", "init", "--repository", "dummy", "-n", "new-dir"])
            )
        assert "Directory or a file named 'new-dir' already exsits in the current directory." in e.value.args[0]
        assert not mock_non_empty_dir.called
        assert mock_new_dir.call_count == 1
        assert not mock_init_with_template.called
        assert mock_init_with_repository.call_count == 0
        assert mock_conflicting_args.call_count == 1

    def test_init_run_with_conflicting_args(self):
        mock_is_directory_empty = self.mocker.patch("gdk.common.utils.is_directory_empty", return_value=True)
        mock_init_with_template = self.mocker.patch.object(InitCommand, "init_with_template", return_value=None)
        mock_init_with_repository = self.mocker.patch.object(InitCommand, "init_with_repository", return_value=None)
        mock_conflicting_args = self.mocker.patch.object(
            InitCommand, "check_if_arguments_conflict", side_effect=Exception("Some exception")
        )

        with pytest.raises(Exception) as e:
            parse_args_actions.run_command(CLIParser.cli_parser.parse_args(["component", "init", "--repository", "dummy"]))

        assert "Could not initialize the project due to the following error.\nError details: Some exception" in e.value.args[0]

        assert mock_is_directory_empty.call_count == 0
        assert mock_init_with_template.call_count == 0
        assert mock_init_with_repository.call_count == 0
        assert mock_conflicting_args.call_count == 1

    def test_init_run_invalid_args(self):
        mock_non_empty_dir = self.mocker.patch("gdk.common.utils.is_directory_empty", return_value=False)
        mock_init_with_template = self.mocker.patch.object(InitCommand, "init_with_template", return_value=None)
        mock_init_with_repository = self.mocker.patch.object(InitCommand, "init_with_repository", return_value=None)
        mock_conflicting_args = self.mocker.patch.object(InitCommand, "check_if_arguments_conflict", return_value=None)
        mock_new_dir = self.mocker.patch("pathlib.Path.mkdir", return_value=None)
        with pytest.raises(Exception) as e:
            parse_args_actions.run_command(
                CLIParser.cli_parser.parse_args(["component", "init", "-t", "dummy", "-n", "new-dir"])
            )
        assert (
            "The arguments passed with the command are invalid.\nPlease initialize the project with correct arguments."
            in e.value.args[0]
        )
        assert not mock_non_empty_dir.called
        assert mock_new_dir.call_count == 1
        assert not mock_init_with_template.called
        assert mock_init_with_repository.call_count == 0
        assert mock_conflicting_args.call_count == 1

    def test_init_run_with_template_download(self):
        mock_is_directory_empty = self.mocker.patch("gdk.common.utils.is_directory_empty", return_value=True)
        mock_download_and_clean = self.mocker.patch.object(InitCommand, "download_and_clean", return_value=None)
        mock_conflicting_args = self.mocker.patch.object(InitCommand, "check_if_arguments_conflict", return_value=None)

        parse_args_actions.run_command(
            CLIParser.cli_parser.parse_args(["component", "init", "-t", "template", "-l", "python"])
        )

        assert mock_is_directory_empty.call_count == 1
        assert mock_conflicting_args.call_count == 1
        mock_download_and_clean.assert_called_once_with("template-python", "template", utils.current_directory)

    def test_init_run_with_repository_download(self):
        mock_is_directory_empty = self.mocker.patch("gdk.common.utils.is_directory_empty", return_value=True)
        mock_download_and_clean = self.mocker.patch.object(InitCommand, "download_and_clean", return_value=None)
        mock_conflicting_args = self.mocker.patch.object(InitCommand, "check_if_arguments_conflict", return_value=None)

        parse_args_actions.run_command(CLIParser.cli_parser.parse_args(["component", "init", "-r", "repo"]))

        assert mock_is_directory_empty.call_count == 1
        assert mock_conflicting_args.call_count == 1
        mock_download_and_clean.assert_called_once_with("repo", "repository", utils.current_directory)

    @patch("zipfile.ZipFile")
    def test_init_run_with_repository_url(self, mock_zip):
        mock_response = self.mocker.Mock(status_code=200, content="".encode())
        mock_template_download = self.mocker.patch("requests.get", return_value=mock_response)

        mock_za = Mock()
        mock_za.return_value.namelist.return_value = ["one"]
        mock_za.return_value.extractall.return_value = None
        mock_zip.return_value.__enter__ = mock_za

        mock_iter_dir = self.mocker.patch("pathlib.Path.iterdir", return_value=["dummy-folder1"])
        mock_move = self.mocker.patch("shutil.move", return_value=None)
        mock_is_directory_empty = self.mocker.patch("gdk.common.utils.is_directory_empty", return_value=True)
        mock_get_download_url = self.mocker.patch.object(InitCommand, "get_download_url", return_value="url")

        mock_conflicting_args = self.mocker.patch.object(InitCommand, "check_if_arguments_conflict", return_value=None)

        parse_args_actions.run_command(CLIParser.cli_parser.parse_args(["component", "init", "-r", "repo"]))
        assert mock_is_directory_empty.call_count == 1
        assert mock_conflicting_args.called
        mock_get_download_url.assert_called_once_with("repo", "repository")
        mock_template_download.assert_called_once_with("url", stream=True)
        assert mock_iter_dir.call_count == 1
        assert mock_move.call_count == 1
        mock_move.assert_any_call("dummy-folder1", utils.current_directory)
        assert mock_template_download.call_count == 1

    @patch("zipfile.ZipFile")
    def test_init_run_with_template_url(self, mock_zip):
        mock_response = self.mocker.Mock(status_code=200, content="".encode())
        mock_template_download = self.mocker.patch("requests.get", return_value=mock_response)

        mock_za = Mock()
        mock_za.return_value.namelist.return_value = ["one"]
        mock_za.return_value.extractall.return_value = None
        mock_zip.return_value.__enter__ = mock_za

        mock_iter_dir = self.mocker.patch("pathlib.Path.iterdir", return_value=["dummy-folder1"])
        mock_move = self.mocker.patch("shutil.move", return_value=None)
        mock_is_directory_empty = self.mocker.patch("gdk.common.utils.is_directory_empty", return_value=True)
        mock_get_download_url = self.mocker.patch.object(InitCommand, "get_download_url", return_value="url")

        mock_conflicting_args = self.mocker.patch.object(InitCommand, "check_if_arguments_conflict", return_value=None)

        parse_args_actions.run_command(
            CLIParser.cli_parser.parse_args(["component", "init", "-t", "template", "-l", "python"])
        )
        assert mock_is_directory_empty.call_count == 1
        assert mock_conflicting_args.called
        mock_get_download_url.assert_called_once_with("template-python", "template")
        mock_template_download.assert_called_once_with("url", stream=True)
        assert mock_iter_dir.call_count == 1
        assert mock_move.call_count == 1
        mock_move.assert_any_call("dummy-folder1", utils.current_directory)
        assert mock_template_download.call_count == 1

    def test_init_run_with_template_download_fail(self):
        mock_is_directory_empty = self.mocker.patch("gdk.common.utils.is_directory_empty", return_value=True)
        mock_download_and_clean = self.mocker.patch.object(InitCommand, "download_and_clean", side_effect=HTTPError("error"))
        mock_conflicting_args = self.mocker.patch.object(InitCommand, "check_if_arguments_conflict", return_value=None)

        with pytest.raises(Exception) as e:
            parse_args_actions.run_command(
                CLIParser.cli_parser.parse_args(["component", "init", "-t", "template", "-l", "python"])
            )

        assert "Could not initialize the project due to the following error." in e.value.args[0]
        assert mock_is_directory_empty.call_count == 1
        assert mock_conflicting_args.call_count == 1
        mock_download_and_clean.assert_called_once_with("template-python", "template", utils.current_directory)

    def test_init_run_with_repository_download_fail(self):
        mock_is_directory_empty = self.mocker.patch("gdk.common.utils.is_directory_empty", return_value=True)
        mock_download_and_clean = self.mocker.patch.object(InitCommand, "download_and_clean", side_effect=HTTPError("error"))
        mock_conflicting_args = self.mocker.patch.object(InitCommand, "check_if_arguments_conflict", return_value=None)

        with pytest.raises(Exception) as e:
            parse_args_actions.run_command(CLIParser.cli_parser.parse_args(["component", "init", "--repository", "dummy"]))

        assert "Could not initialize the project due to the following error." in e.value.args[0]
        assert mock_is_directory_empty.call_count == 1
        assert mock_conflicting_args.call_count == 1
        mock_download_and_clean.assert_called_once_with("dummy", "repository", utils.current_directory)

    def test_init_with_template_invalid_url(self):
        # Raises an exception when the template url is not valid.
        mock_response = self.mocker.Mock(
            status_code=404, raise_for_status=self.mocker.Mock(side_effect=HTTPError("some error"))
        )
        mock_template_download = self.mocker.patch("requests.get", return_value=mock_response)
        mock_is_directory_empty = self.mocker.patch("gdk.common.utils.is_directory_empty", return_value=True)
        mock_get_download_url = self.mocker.patch.object(InitCommand, "get_download_url", return_value="url")

        mock_conflicting_args = self.mocker.patch.object(InitCommand, "check_if_arguments_conflict", return_value=None)
        with patch("builtins.open", mock_open()) as mock_file:
            with pytest.raises(Exception) as e:
                parse_args_actions.run_command(
                    CLIParser.cli_parser.parse_args(["component", "init", "-t", "template", "-l", "python"])
                )

                assert "Failed to download the selected component" in e.value.args[0]
                assert mock_template_download.call_count == 1
                assert mock_is_directory_empty.call_count == 1
                assert mock_conflicting_args.called
                mock_get_download_url.assert_called_once_with("template-python", "template")
                mock_template_download.assert_called_once_with("url", stream=True)
                assert not mock_file.called

    def test_init_with_repository_invalid_url(self):
        # Raises an exception when the template url is not valid.
        mock_response = self.mocker.Mock(
            status_code=404, raise_for_status=self.mocker.Mock(side_effect=HTTPError("some error"))
        )
        mock_template_download = self.mocker.patch("requests.get", return_value=mock_response)
        mock_is_directory_empty = self.mocker.patch("gdk.common.utils.is_directory_empty", return_value=True)
        mock_get_download_url = self.mocker.patch.object(InitCommand, "get_download_url", return_value="url")

        mock_conflicting_args = self.mocker.patch.object(InitCommand, "check_if_arguments_conflict", return_value=None)
        with patch("builtins.open", mock_open()) as mock_file:
            with pytest.raises(Exception) as e:
                parse_args_actions.run_command(CLIParser.cli_parser.parse_args(["component", "init", "-r", "repo"]))

                assert "Failed to download the selected component" in e.value.args[0]
                assert mock_template_download.call_count == 1
                assert mock_is_directory_empty.call_count == 1
                assert mock_conflicting_args.called
                mock_get_download_url.assert_called_once_with("repo", "repository")
                mock_template_download.assert_called_once_with("url", stream=True)
                assert not mock_file.called

    @patch("zipfile.ZipFile")
    def test_init_run_with_template_catalog(self, mock_zip):
        mock_response = self.mocker.Mock(status_code=200, content="".encode())
        mock_template_download = self.mocker.patch("requests.get", return_value=mock_response)

        mock_za = Mock()
        mock_za.return_value.namelist.return_value = ["one"]
        mock_za.return_value.extractall.return_value = None
        mock_zip.return_value.__enter__ = mock_za

        mock_iter_dir = self.mocker.patch("pathlib.Path.iterdir", return_value=["dummy-folder1"])
        mock_move = self.mocker.patch("shutil.move", return_value=None)
        mock_is_directory_empty = self.mocker.patch("gdk.common.utils.is_directory_empty", return_value=True)
        # mock_get_download_url = self.mocker.patch.object(InitCommand, "get_download_url", return_value="url")
        mock_get_component_list_from_github = self.mocker.patch.object(
            ListCommand,
            "get_component_list_from_github",
            return_value={"template-python": "template-url"},
        )
        mock_conflicting_args = self.mocker.patch.object(InitCommand, "check_if_arguments_conflict", return_value=None)
        parse_args_actions.run_command(
            CLIParser.cli_parser.parse_args(["component", "init", "-t", "template", "-l", "python"])
        )
        assert mock_is_directory_empty.call_count == 1
        assert mock_conflicting_args.called
        mock_get_component_list_from_github.assert_called_once_with(consts.templates_list_url)
        mock_template_download.assert_called_once_with("template-url", stream=True)
        assert mock_iter_dir.call_count == 1
        assert mock_move.call_count == 1
        mock_move.assert_any_call("dummy-folder1", utils.current_directory)
        assert mock_template_download.call_count == 1

    @patch("zipfile.ZipFile")
    def test_init_run_with_repository_catalog_url(self, mock_zip):
        mock_response = self.mocker.Mock(status_code=200, content="".encode())
        mock_template_download = self.mocker.patch("requests.get", return_value=mock_response)

        mock_za = Mock()
        mock_za.return_value.namelist.return_value = ["one"]
        mock_za.return_value.extractall.return_value = None
        mock_zip.return_value.__enter__ = mock_za

        mock_iter_dir = self.mocker.patch("pathlib.Path.iterdir", return_value=["dummy-folder1"])
        mock_move = self.mocker.patch("shutil.move", return_value=None)
        mock_is_directory_empty = self.mocker.patch("gdk.common.utils.is_directory_empty", return_value=True)
        mock_get_component_list_from_github = self.mocker.patch.object(
            ListCommand,
            "get_component_list_from_github",
            return_value={"repo": "repo-url"},
        )
        mock_conflicting_args = self.mocker.patch.object(InitCommand, "check_if_arguments_conflict", return_value=None)
        parse_args_actions.run_command(CLIParser.cli_parser.parse_args(["component", "init", "-r", "repo"]))
        assert mock_is_directory_empty.call_count == 1
        assert mock_conflicting_args.called
        mock_get_component_list_from_github.assert_called_once_with(consts.repository_list_url)
        mock_template_download.assert_called_once_with("repo-url", stream=True)
        assert mock_iter_dir.call_count == 1
        assert mock_move.call_count == 1
        mock_move.assert_any_call("dummy-folder1", utils.current_directory)
        assert mock_template_download.call_count == 1

    @patch("zipfile.ZipFile")
    def test_init_run_with_repository_catalog_url_not_found(self, mock_zip):
        mock_response = self.mocker.Mock(status_code=200, content="".encode())
        mock_template_download = self.mocker.patch("requests.get", return_value=mock_response)

        mock_za = Mock()
        mock_za.return_value.namelist.return_value = ["one"]
        mock_za.return_value.extractall.return_value = None
        mock_zip.return_value.__enter__ = mock_za

        mock_iter_dir = self.mocker.patch("pathlib.Path.iterdir", return_value=["dummy-folder1"])
        mock_move = self.mocker.patch("shutil.move", return_value=None)
        mock_is_directory_empty = self.mocker.patch("gdk.common.utils.is_directory_empty", return_value=True)
        mock_get_component_list_from_github = self.mocker.patch.object(
            ListCommand,
            "get_component_list_from_github",
            return_value={"repo": "repo-url"},
        )
        mock_conflicting_args = self.mocker.patch.object(InitCommand, "check_if_arguments_conflict", return_value=None)
        with pytest.raises(Exception) as e:
            parse_args_actions.run_command(CLIParser.cli_parser.parse_args(["component", "init", "-r", "repo-not-found"]))
        assert "Could not find the component repository 'repo-not-found' in Greengrass Software Catalog." in e.value.args[0]
        assert mock_is_directory_empty.call_count == 1
        assert mock_conflicting_args.called
        mock_get_component_list_from_github.assert_called_once_with(consts.repository_list_url)
        assert not mock_iter_dir.called
        assert not mock_move.called
        assert not mock_template_download.called

    @patch("zipfile.ZipFile")
    def test_init_run_with_template_catalog_url_not_found(self, mock_zip):
        mock_response = self.mocker.Mock(status_code=200, content="".encode())
        mock_template_download = self.mocker.patch("requests.get", return_value=mock_response)

        mock_za = Mock()
        mock_za.return_value.namelist.return_value = ["one"]
        mock_za.return_value.extractall.return_value = None
        mock_zip.return_value.__enter__ = mock_za

        mock_iter_dir = self.mocker.patch("pathlib.Path.iterdir", return_value=["dummy-folder1"])
        mock_move = self.mocker.patch("shutil.move", return_value=None)
        mock_is_directory_empty = self.mocker.patch("gdk.common.utils.is_directory_empty", return_value=True)
        mock_get_component_list_from_github = self.mocker.patch.object(
            ListCommand,
            "get_component_list_from_github",
            return_value={"repo": "repo-url"},
        )
        mock_conflicting_args = self.mocker.patch.object(InitCommand, "check_if_arguments_conflict", return_value=None)
        with pytest.raises(Exception) as e:
            parse_args_actions.run_command(
                CLIParser.cli_parser.parse_args(["component", "init", "-t", "template-not-found", "-l", "python"])
            )
        assert (
            "Could not find the component template 'template-not-found-python' in Greengrass Software Catalog."
            in e.value.args[0]
        )
        assert mock_is_directory_empty.call_count == 1
        assert mock_conflicting_args.called
        mock_get_component_list_from_github.assert_called_once_with(consts.templates_list_url)
        assert not mock_iter_dir.called
        assert not mock_move.called
        assert not mock_template_download.called

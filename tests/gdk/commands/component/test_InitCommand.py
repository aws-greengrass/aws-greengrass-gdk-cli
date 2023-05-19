from unittest import TestCase
from unittest.mock import Mock, mock_open, patch

import gdk.common.exceptions.error_messages as error_messages
import pytest
from gdk.commands.component.InitCommand import InitCommand
from gdk.commands.component.ListCommand import ListCommand
from gdk.common.exceptions.CommandError import ConflictingArgumentsError
from urllib3.exceptions import HTTPError
from pathlib import Path


class InitCommandTest(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker):
        self.mocker = mocker

    def test_init_run_with_non_empty_directory(self):
        test_d_args = {"language": "python", "template": "name", "name": None}
        mock_is_directory_empty = self.mocker.patch("gdk.common.utils.is_directory_empty", return_value=False)
        mock_init_with_template = self.mocker.patch.object(InitCommand, "init_with_template", return_value=None)
        mock_init_with_repository = self.mocker.patch.object(InitCommand, "init_with_repository", return_value=None)
        mock_conflicting_args = self.mocker.patch.object(InitCommand, "check_if_arguments_conflict", return_value=None)

        with pytest.raises(Exception) as e:
            InitCommand(test_d_args).run()

        assert e.value.args[0] == error_messages.INIT_NON_EMPTY_DIR_ERROR

        assert mock_is_directory_empty.call_count == 1
        assert mock_conflicting_args.call_count == 1
        assert mock_init_with_template.call_count == 0
        assert mock_init_with_repository.call_count == 0

    def test_init_run_with_empty_directory(self):
        # Test that an exception is not raised when init is run in an empty directory
        test_d_args = {"template": None, "language": None, "repository": "repository", "name": None}
        mock_is_directory_empty = self.mocker.patch("gdk.common.utils.is_directory_empty", return_value=True)
        mock_init_with_template = self.mocker.patch.object(InitCommand, "init_with_template", return_value=None)
        mock_init_with_repository = self.mocker.patch.object(InitCommand, "init_with_repository", return_value=None)
        mock_conflicting_args = self.mocker.patch.object(InitCommand, "check_if_arguments_conflict", return_value=False)
        InitCommand(test_d_args).run()

        assert mock_is_directory_empty.call_count == 1
        assert mock_init_with_template.call_count == 0
        assert mock_init_with_repository.call_count == 1
        assert mock_conflicting_args.call_count == 1

    def test_init_run_with_empty_args_repository(self):
        test_d_args = {"template": None, "language": None, "repository": None, "name": None}
        mock_is_directory_empty = self.mocker.patch("gdk.common.utils.is_directory_empty", return_value=True)
        mock_init_with_template = self.mocker.patch.object(InitCommand, "init_with_template", return_value=None)
        mock_init_with_repository = self.mocker.patch.object(InitCommand, "init_with_repository", return_value=None)
        mock_conflicting_args = self.mocker.patch.object(InitCommand, "check_if_arguments_conflict", return_value=False)

        with pytest.raises(Exception) as e:
            InitCommand(test_d_args).run()

        assert e.value.args[0] == error_messages.INIT_WITH_INVALID_ARGS

        assert mock_is_directory_empty.call_count == 1
        assert mock_init_with_template.call_count == 0
        assert mock_init_with_repository.call_count == 0
        assert mock_conflicting_args.call_count == 1

    def test_init_run_with_empty_args_template(self):
        # Test that an exception is not raised when init is run in an empty directory
        test_d_args = {"template": None, "language": "python", "repository": None, "name": None}
        mock_is_directory_empty = self.mocker.patch("gdk.common.utils.is_directory_empty", return_value=True)
        mock_init_with_template = self.mocker.patch.object(InitCommand, "init_with_template", return_value=None)
        mock_init_with_repository = self.mocker.patch.object(InitCommand, "init_with_repository", return_value=None)
        mock_conflicting_args = self.mocker.patch.object(InitCommand, "check_if_arguments_conflict", return_value=False)

        with pytest.raises(Exception) as e:
            InitCommand(test_d_args).run()

        assert e.value.args[0] == error_messages.INIT_WITH_INVALID_ARGS

        assert mock_is_directory_empty.call_count == 1
        assert mock_init_with_template.call_count == 0
        assert mock_init_with_repository.call_count == 0
        assert mock_conflicting_args.call_count == 1

    def test_init_run_with_conflicting_args(self):
        test_d_args = {"a": "a", "name": None, "b": "b"}
        mock_is_directory_empty = self.mocker.patch("gdk.common.utils.is_directory_empty", return_value=True)
        mock_init_with_template = self.mocker.patch.object(InitCommand, "init_with_template", return_value=None)
        mock_init_with_repository = self.mocker.patch.object(InitCommand, "init_with_repository", return_value=None)
        mock_conflicting_args = self.mocker.patch.object(
            InitCommand, "check_if_arguments_conflict", side_effect=ConflictingArgumentsError("a", "b")
        )

        with pytest.raises(Exception) as e:
            InitCommand(test_d_args).run()

        assert "Arguments 'a' and 'b' are conflicting and cannot be used together in a command." in e.value.args[0]

        assert mock_is_directory_empty.call_count == 0
        assert mock_init_with_template.call_count == 0
        assert mock_init_with_repository.call_count == 0
        assert mock_conflicting_args.call_count == 1

    def test_init_run_with_valid_args(self):
        test_d_args = {"language": "python", "template": "name", "name": None}
        mock_is_directory_empty = self.mocker.patch("gdk.common.utils.is_directory_empty", return_value=True)
        mock_init_with_template = self.mocker.patch.object(InitCommand, "init_with_template", return_value=None)
        mock_init_with_repository = self.mocker.patch.object(InitCommand, "init_with_repository", return_value=None)

        InitCommand(test_d_args).run()

        assert mock_is_directory_empty.call_count == 1
        assert mock_init_with_template.call_count == 1
        assert mock_init_with_repository.call_count == 0

    # def test_init_run_with_name_args_invalid(self):
    #     test_d_args = {"language": "python", "template": "name", "name": "new-dir"}
    #     mock_is_directory_empty = self.mocker.patch("gdk.common.utils.is_directory_empty", return_value=True)
    #     mock_init_with_template = self.mocker.patch.object(InitCommand, "init_with_template", return_value=None)
    #     mock_init_with_repository = self.mocker.patch.object(InitCommand, "init_with_repository", return_value=None)
    #     mock_mkdir = self.mocker.patch("pathlib.Path.mkdir", return_value=None, side_effect=FileExistsError("Some error"))
    #     with pytest.raises(Exception) as e:
    #         InitCommand(test_d_args).run()

    #     assert e.value.args[0] == error_messages.INIT_DIR_EXISTS_ERROR.format("new-dir")
    #     assert mock_is_directory_empty.call_count == 0
    #     assert mock_mkdir.call_count == 1
    #     assert mock_init_with_template.call_count == 0
    #     assert mock_init_with_repository.call_count == 0

    def test_init_run_with_invalid_args(self):
        test_d_args = {"language": None, "template": None, "repository": None, "name": None}
        mock_is_directory_empty = self.mocker.patch("gdk.common.utils.is_directory_empty", return_value=True)
        mock_init_with_template = self.mocker.patch.object(InitCommand, "init_with_template", return_value=None)
        mock_init_with_repository = self.mocker.patch.object(InitCommand, "init_with_repository", return_value=None)
        with pytest.raises(Exception) as e:
            InitCommand(test_d_args).run()

        assert e.value.args[0] == error_messages.INIT_WITH_INVALID_ARGS

        assert mock_is_directory_empty.call_count == 1
        assert mock_init_with_template.call_count == 0
        assert mock_init_with_repository.call_count == 0

    def test_init_with_template_valid(self):
        template = "template"
        language = "language"
        project_dir = "dir"
        self.mocker.patch.object(InitCommand, "__init__", return_value=None)
        mock_download_and_clean = self.mocker.patch.object(InitCommand, "download_and_clean", return_value=None)
        init = InitCommand({})
        init.init_with_template(template, language, project_dir)
        mock_download_and_clean.assert_any_call("template-language", "template", project_dir)

    def test_init_with_template_exception(self):
        template = "template"
        language = "language"
        project_dir = "dir"
        self.mocker.patch.object(InitCommand, "__init__", return_value=None)
        mock_download_and_clean = self.mocker.patch.object(
            InitCommand, "download_and_clean", side_effect=HTTPError("Some error")
        )
        init = InitCommand({})
        with pytest.raises(Exception) as e:
            init.init_with_template(template, language, project_dir)
        assert "Some error" in e.value.args[0]
        mock_download_and_clean.assert_any_call("template-language", "template", project_dir)

    def test_init_with_repository_valid(self):
        repository = "repository_name"
        project_dir = "dir"
        self.mocker.patch.object(InitCommand, "__init__", return_value=None)
        mock_download_and_clean = self.mocker.patch.object(InitCommand, "download_and_clean", return_value=None)
        init = InitCommand({})
        init.init_with_repository(repository, project_dir)
        mock_download_and_clean.assert_any_call(repository, "repository", project_dir)

    def test_init_with_repository_exception(self):
        repository = "repository_name"
        project_dir = "dir"
        mock_download_and_clean = self.mocker.patch.object(
            InitCommand, "download_and_clean", side_effect=HTTPError("Some error")
        )
        self.mocker.patch.object(InitCommand, "__init__", return_value=None)
        init = InitCommand({})
        with pytest.raises(Exception) as e:
            init.init_with_repository(repository, project_dir)
        assert "Some error" in e.value.args[0]
        mock_download_and_clean.assert_any_call(repository, "repository", project_dir)

    @patch("zipfile.ZipFile")
    def test_download_and_clean_valid(self, mock_zip):
        mock_get_available_templates = self.mocker.patch.object(
            ListCommand,
            "get_component_list_from_github",
            return_value={"template-language": "template-url"},
        )

        mock_response = self.mocker.Mock(status_code=200, content="".encode())
        mock_template_download = self.mocker.patch("requests.get", return_value=mock_response)
        mock_make_dir = self.mocker.patch("pathlib.Path.mkdir", return_value=None)
        mock_za = Mock()
        mock_za.return_value.namelist.return_value = ["one"]
        mock_za.return_value.extractall.return_value = None
        mock_zip.return_value.__enter__ = mock_za
        project_dir = Path("dir").resolve()

        mock_iter_dir = self.mocker.patch("pathlib.Path.iterdir", return_value=["dummy-folder1"])
        mock_move = self.mocker.patch("shutil.move", return_value=None)
        self.mocker.patch.object(InitCommand, "__init__", return_value=None)
        init = InitCommand({})
        init.download_and_clean("template-language", "template", project_dir)
        assert mock_iter_dir.call_count == 1
        assert mock_move.call_count == 1
        mock_move.assert_any_call("dummy-folder1", project_dir)
        assert mock_template_download.call_count == 1
        assert mock_get_available_templates.call_count == 1
        assert mock_make_dir.call_count == 1

    def test_init_with_template_invalid_url_server_error(self):
        template = "template"
        language = "language"
        project_dir = "dir"
        formatted_template_name = f"{template}-{language}"
        mock_get_available_templates = self.mocker.patch.object(
            ListCommand,
            "get_component_list_from_github",
            return_value={formatted_template_name: "template-url"},
        )
        mock_response = self.mocker.Mock(
            status_code=500, raise_for_status=self.mocker.Mock(side_effect=HTTPError("some error"))
        )
        mock_template_download = self.mocker.patch("requests.get", return_value=mock_response)
        self.mocker.patch.object(InitCommand, "__init__", return_value=None)
        init = InitCommand({})
        with patch("builtins.open", mock_open()) as mock_file:
            with pytest.raises(Exception) as e:
                init.download_and_clean(formatted_template_name, template, project_dir)

            assert "some error" in e.value.args[0]
            assert mock_template_download.call_count == 1
            assert mock_get_available_templates.call_count == 1
            assert not mock_file.called

    def test_init_with_template_invalid_url_not_found(self):
        template = "template"
        language = "language"
        project_dir = "dir"
        formatted_template_name = f"{template}-{language}"
        mock_get_available_templates = self.mocker.patch.object(
            ListCommand,
            "get_component_list_from_github",
            return_value={formatted_template_name: "template-url"},
        )
        mock_response = self.mocker.Mock(
            status_code=404, raise_for_status=self.mocker.Mock(side_effect=HTTPError("some error"))
        )
        mock_template_download = self.mocker.patch("requests.get", return_value=mock_response)
        self.mocker.patch.object(InitCommand, "__init__", return_value=None)
        init = InitCommand({})
        with patch("builtins.open", mock_open()) as mock_file:
            with pytest.raises(Exception) as e:
                init.download_and_clean(formatted_template_name, template, project_dir)

            assert "some error" in e.value.args[0]
            assert mock_template_download.call_count == 1
            assert mock_get_available_templates.call_count == 1
            assert not mock_file.called

    def test_get_download_url_valid_template(self):
        template = "template"
        language = "language"
        formatted_template_name = f"{template}-{language}"

        mock_get_component_list_from_github = self.mocker.patch.object(
            ListCommand,
            "get_component_list_from_github",
            return_value={formatted_template_name: "template-url"},
        )
        self.mocker.patch.object(InitCommand, "__init__", return_value=None)
        init = InitCommand({})
        url = init.get_download_url(formatted_template_name, "template")
        assert url == "template-url"
        assert mock_get_component_list_from_github.called

    def test_get_download_url_valid_repository(self):
        repository = "repository_name"
        mock_get_component_list_from_github = self.mocker.patch.object(
            ListCommand,
            "get_component_list_from_github",
            return_value={"repository_name": "repository-url"},
        )
        self.mocker.patch.object(InitCommand, "__init__", return_value=None)
        init = InitCommand({})
        url = init.get_download_url(repository, "repository")
        assert url == "repository-url"
        assert mock_get_component_list_from_github.called

    def test_get_download_url_invalid_template(self):
        template = "template-language"
        mock_get_component_list_from_github = self.mocker.patch.object(
            ListCommand,
            "get_component_list_from_github",
            return_value={"repository_name": "repository-url"},
        )
        self.mocker.patch.object(InitCommand, "__init__", return_value=None)
        init = InitCommand({})
        with pytest.raises(Exception) as e:
            init.get_download_url(template, "template")
        assert e.value.args[0] == "Could not find the component template 'template-language' in Greengrass Software Catalog."
        assert mock_get_component_list_from_github.called

    def test_get_download_url_invalid_repository(self):
        repository = "repository_name"
        mock_get_component_list_from_github = self.mocker.patch.object(
            ListCommand,
            "get_component_list_from_github",
            return_value={"template-language": "template-url"},
        )
        self.mocker.patch.object(InitCommand, "__init__", return_value=None)
        init = InitCommand({})
        with pytest.raises(Exception) as e:
            init.get_download_url(repository, "repository")
        assert e.value.args[0] == "Could not find the component repository 'repository_name' in Greengrass Software Catalog."
        assert mock_get_component_list_from_github.called

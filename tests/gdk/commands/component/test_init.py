from unittest.mock import Mock, mock_open, patch

import gdk.commands.component.init as init
import gdk.common.exceptions.error_messages as error_messages
import pytest
from urllib3.exceptions import HTTPError


def test_init_run_with_non_empty_directory(mocker):
    # Test that an exception is raised when init is run in non-empty directory
    test_d_args = {"language": "python", "template": "name", "name": None}
    mock_is_directory_empty = mocker.patch("gdk.common.utils.is_directory_empty", return_value=False)
    mock_init_with_template = mocker.patch("gdk.commands.component.init.init_with_template", return_value=None)
    mock_init_with_repository = mocker.patch("gdk.commands.component.init.init_with_repository", return_value=None)
    mock_conflicting_args = mocker.patch("gdk.common.parse_args_actions.conflicting_arg_groups", return_value=False)
    with pytest.raises(Exception) as e:
        init.run(test_d_args)

    assert e.value.args[0] == error_messages.INIT_NON_EMPTY_DIR_ERROR

    assert mock_is_directory_empty.call_count == 1
    assert mock_conflicting_args.call_count == 0
    assert mock_init_with_template.call_count == 0
    assert mock_init_with_repository.call_count == 0


def test_init_run_with_empty_directory(mocker):
    # Test that an exception is not raised when init is run in an empty directory
    test_d_args = {"template": None, "language": None, "repository": "repository", "name": None}
    mock_is_directory_empty = mocker.patch("gdk.common.utils.is_directory_empty", return_value=True)
    mock_init_with_template = mocker.patch("gdk.commands.component.init.init_with_template", return_value=None)
    mock_init_with_repository = mocker.patch("gdk.commands.component.init.init_with_repository", return_value=None)
    mock_conflicting_args = mocker.patch("gdk.common.parse_args_actions.conflicting_arg_groups", return_value=False)
    init.run(test_d_args)

    assert mock_is_directory_empty.call_count == 1
    assert mock_init_with_template.call_count == 0
    assert mock_init_with_repository.call_count == 1
    assert mock_conflicting_args.call_count == 1


def test_init_run_with_empty_args_repository(mocker):
    # Test that an exception is not raised when init is run in an empty directory
    test_d_args = {"template": None, "language": None, "repository": None, "name": None}
    mock_is_directory_empty = mocker.patch("gdk.common.utils.is_directory_empty", return_value=True)
    mock_init_with_template = mocker.patch("gdk.commands.component.init.init_with_template", return_value=None)
    mock_init_with_repository = mocker.patch("gdk.commands.component.init.init_with_repository", return_value=None)
    mock_conflicting_args = mocker.patch("gdk.common.parse_args_actions.conflicting_arg_groups", return_value=False)

    with pytest.raises(Exception) as e:
        init.run(test_d_args)

    assert e.value.args[0] == error_messages.INIT_WITH_INVALID_ARGS

    assert mock_is_directory_empty.call_count == 1
    assert mock_init_with_template.call_count == 0
    assert mock_init_with_repository.call_count == 0
    assert mock_conflicting_args.call_count == 1


def test_init_run_with_empty_args_template(mocker):
    # Test that an exception is not raised when init is run in an empty directory
    test_d_args = {"template": None, "language": "python", "repository": None, "name": None}
    mock_is_directory_empty = mocker.patch("gdk.common.utils.is_directory_empty", return_value=True)
    mock_init_with_template = mocker.patch("gdk.commands.component.init.init_with_template", return_value=None)
    mock_init_with_repository = mocker.patch("gdk.commands.component.init.init_with_repository", return_value=None)
    mock_conflicting_args = mocker.patch("gdk.common.parse_args_actions.conflicting_arg_groups", return_value=False)

    with pytest.raises(Exception) as e:
        init.run(test_d_args)

    assert e.value.args[0] == error_messages.INIT_WITH_INVALID_ARGS

    assert mock_is_directory_empty.call_count == 1
    assert mock_init_with_template.call_count == 0
    assert mock_init_with_repository.call_count == 0
    assert mock_conflicting_args.call_count == 1


def test_init_run_with_conflicting_args(mocker):
    # Test that an exception is not raised when init is run in an empty directory
    test_d_args = {"repository": "repository", "name": None}
    mock_is_directory_empty = mocker.patch("gdk.common.utils.is_directory_empty", return_value=True)
    mock_init_with_template = mocker.patch("gdk.commands.component.init.init_with_template", return_value=None)
    mock_init_with_repository = mocker.patch("gdk.commands.component.init.init_with_repository", return_value=None)
    mock_conflicting_args = mocker.patch("gdk.common.parse_args_actions.conflicting_arg_groups", return_value=True)

    with pytest.raises(Exception) as e:
        init.run(test_d_args)

    assert e.value.args[0] == error_messages.INIT_WITH_CONFLICTING_ARGS

    assert mock_is_directory_empty.call_count == 1
    assert mock_init_with_template.call_count == 0
    assert mock_init_with_repository.call_count == 0
    assert mock_conflicting_args.call_count == 1


def test_init_run_with_valid_args(mocker):
    # Checks if args are used correctly to run correct init method
    test_d_args = {"language": "python", "template": "name", "name": None}
    mock_is_directory_empty = mocker.patch("gdk.common.utils.is_directory_empty", return_value=True)
    mock_init_with_template = mocker.patch("gdk.commands.component.init.init_with_template", return_value=None)
    mock_init_with_repository = mocker.patch("gdk.commands.component.init.init_with_repository", return_value=None)

    init.run(test_d_args)

    assert mock_is_directory_empty.call_count == 1
    assert mock_init_with_template.call_count == 1
    assert mock_init_with_repository.call_count == 0


def test_init_run_with_name_args(mocker):
    # Checks if args are used correctly to run correct init method
    test_d_args = {"language": "python", "template": "name", "name": "new-dir"}
    mock_is_directory_empty = mocker.patch("gdk.common.utils.is_directory_empty", return_value=True)
    mock_init_with_template = mocker.patch("gdk.commands.component.init.init_with_template", return_value=None)
    mock_init_with_repository = mocker.patch("gdk.commands.component.init.init_with_repository", return_value=None)
    mock_mkdir = mocker.patch("pathlib.Path.mkdir", return_value=None)
    init.run(test_d_args)

    assert mock_is_directory_empty.call_count == 0
    assert mock_mkdir.call_count == 1
    assert mock_init_with_template.call_count == 1
    assert mock_init_with_repository.call_count == 0


def test_init_run_with_name_args_invalid(mocker):
    # Checks if args are used correctly to run correct init method
    test_d_args = {"language": "python", "template": "name", "name": "new-dir"}
    mock_is_directory_empty = mocker.patch("gdk.common.utils.is_directory_empty", return_value=True)
    mock_init_with_template = mocker.patch("gdk.commands.component.init.init_with_template", return_value=None)
    mock_init_with_repository = mocker.patch("gdk.commands.component.init.init_with_repository", return_value=None)
    mock_mkdir = mocker.patch("pathlib.Path.mkdir", return_value=None, side_effect=FileExistsError("Some error"))
    with pytest.raises(Exception) as e:
        init.run(test_d_args)

    assert e.value.args[0] == error_messages.INIT_DIR_EXISTS_ERROR.format("new-dir")
    assert mock_is_directory_empty.call_count == 0
    assert mock_mkdir.call_count == 1
    assert mock_init_with_template.call_count == 0
    assert mock_init_with_repository.call_count == 0


def test_init_run_with_invalid_args(mocker):
    test_d_args = {"language": None, "template": None, "repository": None, "name": None}
    mock_is_directory_empty = mocker.patch("gdk.common.utils.is_directory_empty", return_value=True)
    mock_init_with_template = mocker.patch("gdk.commands.component.init.init_with_template", return_value=None)
    mock_init_with_repository = mocker.patch("gdk.commands.component.init.init_with_repository", return_value=None)
    with pytest.raises(Exception) as e:
        init.run(test_d_args)

    assert e.value.args[0] == error_messages.INIT_WITH_INVALID_ARGS

    assert mock_is_directory_empty.call_count == 1
    assert mock_init_with_template.call_count == 0
    assert mock_init_with_repository.call_count == 0


def test_init_with_template_valid(mocker):
    template = "template"
    language = "language"
    project_dir = "dir"
    mock_download_and_clean = mocker.patch("gdk.commands.component.init.download_and_clean", return_value=None)
    init.init_with_template(template, language, project_dir)
    mock_download_and_clean.assert_any_call("template-language", "template", project_dir)


def test_init_with_template_exception(mocker):
    template = "template"
    language = "language"
    project_dir = "dir"
    mock_download_and_clean = mocker.patch(
        "gdk.commands.component.init.download_and_clean", side_effect=HTTPError("Some error")
    )
    with pytest.raises(Exception) as e:
        init.init_with_template(template, language, project_dir)
    assert "Could not initialize the project with component template" in e.value.args[0]
    mock_download_and_clean.assert_any_call("template-language", "template", project_dir)


def test_init_with_repository_valid(mocker):
    repository = "repository_name"
    project_dir = "dir"
    mock_download_and_clean = mocker.patch("gdk.commands.component.init.download_and_clean", return_value=None)
    init.init_with_repository(repository, project_dir)
    mock_download_and_clean.assert_any_call(repository, "repository", project_dir)


def test_init_with_repository_exception(mocker):
    repository = "repository_name"
    project_dir = "dir"
    mock_download_and_clean = mocker.patch(
        "gdk.commands.component.init.download_and_clean", side_effect=HTTPError("Some error")
    )
    with pytest.raises(Exception) as e:
        init.init_with_repository(repository, project_dir)
    assert "Could not initialize the project with component repository" in e.value.args[0]
    mock_download_and_clean.assert_any_call(repository, "repository", project_dir)


@patch("zipfile.ZipFile")
def test_download_and_clean_valid(mock_zip, mocker):
    mock_get_available_templates = mocker.patch(
        "gdk.commands.component.list.get_component_list_from_github",
        return_value={"template-language": "template-url"},
    )

    mock_response = mocker.Mock(status_code=200, content="".encode())
    mock_template_download = mocker.patch("requests.get", return_value=mock_response)

    mock_za = Mock()
    mock_za.return_value.namelist.return_value = ["one"]
    mock_za.return_value.extractall.return_value = None
    mock_zip.return_value.__enter__ = mock_za
    project_dir = "dir"
    # mock_tmp = ""
    # mock_tempdir.return_value.__enter__ = mock_tmp

    mock_iter_dir = mocker.patch("pathlib.Path.iterdir", return_value=["dummy-folder1"])
    mock_move = mocker.patch("shutil.move", return_value=None)

    init.download_and_clean("template-language", "template", project_dir)
    assert mock_iter_dir.call_count == 1
    assert mock_move.call_count == 1
    mock_move.assert_any_call("dummy-folder1", project_dir)
    assert mock_template_download.call_count == 1
    assert mock_get_available_templates.call_count == 1


def test_init_with_template_invalid_url(mocker):
    # Raises an exception when the template url is not valid.
    template = "template"
    language = "language"
    project_dir = "dir"
    formatted_template_name = f"{template}-{language}"
    mock_get_available_templates = mocker.patch(
        "gdk.commands.component.list.get_component_list_from_github",
        return_value={formatted_template_name: "template-url"},
    )
    mock_response = mocker.Mock(status_code=404, raise_for_status=mocker.Mock(side_effect=HTTPError("some error")))
    mock_template_download = mocker.patch("requests.get", return_value=mock_response)

    with patch("builtins.open", mock_open()) as mock_file:
        with pytest.raises(Exception) as e:
            init.download_and_clean(formatted_template_name, template, project_dir)

        assert "Failed to download the selected component" in e.value.args[0]
        assert mock_template_download.call_count == 1
        assert mock_get_available_templates.call_count == 1
        assert not mock_file.called


def test_get_download_url_valid_template(mocker):
    template = "template"
    language = "language"
    formatted_template_name = f"{template}-{language}"

    mock_get_component_list_from_github = mocker.patch(
        "gdk.commands.component.list.get_component_list_from_github",
        return_value={formatted_template_name: "template-url"},
    )
    url = init.get_download_url(formatted_template_name, "template")
    assert url == "template-url"
    assert mock_get_component_list_from_github.called


def test_get_download_url_valid_repository(mocker):
    repository = "repository_name"
    mock_get_component_list_from_github = mocker.patch(
        "gdk.commands.component.list.get_component_list_from_github",
        return_value={"repository_name": "repository-url"},
    )
    url = init.get_download_url(repository, "repository")
    assert url == "repository-url"
    assert mock_get_component_list_from_github.called


def test_get_download_url_invalid_template(mocker):
    template = "template-language"
    mock_get_component_list_from_github = mocker.patch(
        "gdk.commands.component.list.get_component_list_from_github",
        return_value={"repository_name": "repository-url"},
    )
    with pytest.raises(Exception) as e:
        init.get_download_url(template, "template")
    assert e.value.args[0] == "Could not find the component template 'template-language' in Greengrass Software Catalog."
    assert mock_get_component_list_from_github.called


def test_get_download_url_invalid_repository(mocker):
    repository = "repository_name"
    mock_get_component_list_from_github = mocker.patch(
        "gdk.commands.component.list.get_component_list_from_github",
        return_value={"template-language": "template-url"},
    )
    with pytest.raises(Exception) as e:
        init.get_download_url(repository, "repository")
    assert e.value.args[0] == "Could not find the component repository 'repository_name' in Greengrass Software Catalog."
    assert mock_get_component_list_from_github.called

import logging

import gdk.CLIParser as CLIParser
import gdk.common.consts as consts
import gdk.common.parse_args_actions as parse_args_actions
import pytest
from urllib3.exceptions import HTTPError


def test_list_run():
    with pytest.raises(Exception) as e:
        parse_args_actions.run_command(CLIParser.cli_parser.parse_args(["component", "list", "-d"]))
    assert "supply either `--template` or `--repository` as an argument to the list command." in e.value.args[0]


def test_list_template():
    parse_args_actions.run_command(CLIParser.cli_parser.parse_args(["component", "list", "--template"]))


def test_list_repository():
    parse_args_actions.run_command(CLIParser.cli_parser.parse_args(["component", "list", "--repository"]))


def test_list_template_failed_request(mocker):
    mock_response = mocker.Mock(status_code=404, raise_for_status=mocker.Mock(side_effect=HTTPError("some error")))
    mock_list_req = mocker.patch("requests.get", return_value=mock_response)
    with pytest.raises(Exception) as e:
        parse_args_actions.run_command(CLIParser.cli_parser.parse_args(["component", "list", "--template"]))
    assert mock_list_req.called
    assert "some error" in e.value.args[0]


def test_list_repository_failed_request(mocker):
    mock_response = mocker.Mock(status_code=404, raise_for_status=mocker.Mock(side_effect=HTTPError("some error")))
    mock_list_req = mocker.patch("requests.get", return_value=mock_response)
    with pytest.raises(Exception) as e:
        parse_args_actions.run_command(CLIParser.cli_parser.parse_args(["component", "list", "--repository"]))
    assert mock_list_req.called
    assert "some error" in e.value.args[0]


def test_list_template_not_json(mocker):
    def modify_response(*args, **kwargs):
        if args[0] == consts.templates_list_url:
            return mocker.Mock(status_code=200, json="not-a-json")

    mock_get_list = mocker.patch("requests.get", side_effect=modify_response)
    spy_log_info = mocker.spy(logging, "info")
    parse_args_actions.run_command(CLIParser.cli_parser.parse_args(["component", "list", "--template"]))
    assert mock_get_list.called

    spy_log_info.assert_called_with("Found '0' component templates to display.")


def test_list_repository_not_json(mocker):
    def modify_response(*args, **kwargs):
        if args[0] == consts.repository_list_url:
            return mocker.Mock(status_code=200, json="not-a-json")

    mock_get_list = mocker.patch("requests.get", side_effect=modify_response)
    spy_log_info = mocker.spy(logging, "info")
    parse_args_actions.run_command(CLIParser.cli_parser.parse_args(["component", "list", "--repository"]))
    assert mock_get_list.called

    spy_log_info.assert_called_with("Found '0' component repositories to display.")

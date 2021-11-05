import greengrassTools.CLIParser as CLIParser
import pytest
import greengrassTools.common.parse_args_actions as parse_args_actions

def test_main_parse_args_init(mocker):
    mock_component_init = mocker.patch("greengrassTools.commands.component.component.init", return_value = None)
    parse_args_actions.run_command(CLIParser.cli_parser.parse_args(["component", "init", "-d"]))
    assert mock_component_init.called

def test_main_parse_args_build(mocker):
    mock_component_build = mocker.patch("greengrassTools.commands.component.component.build", return_value = None)
    parse_args_actions.run_command(CLIParser.cli_parser.parse_args(["component", "build", "-d"]))
    assert mock_component_build.called

def test_main_parse_args_publish(mocker):
    mock_component_publish= mocker.patch("greengrassTools.commands.component.component.publish", return_value = None)
    parse_args_actions.run_command(CLIParser.cli_parser.parse_args(["component", "publish", "-d"]))
    assert mock_component_publish.called

def test_main_parse_args_list(mocker):
    mock_component_list= mocker.patch("greengrassTools.commands.component.component.list", return_value = None)
    parse_args_actions.run_command(CLIParser.cli_parser.parse_args(["component", "list", "-d"]))
    assert mock_component_list.called

def test_main_parse_args_raise_exit(mocker):
    mock_component_list= mocker.patch("greengrassTools.commands.component.component.list", return_value = None)
    mock_exit = mocker.patch("argparse.ArgumentParser.exit")
    parse_args_actions.run_command(CLIParser.cli_parser.parse_args(["component", "list", "--unknown arg"]))
    assert mock_exit.called
    assert mock_component_list.called

    
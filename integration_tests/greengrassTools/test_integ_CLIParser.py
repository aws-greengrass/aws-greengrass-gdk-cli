import greengrassTools.CLIParser as CLIParser
import greengrassTools.common.parse_args_actions as parse_args_actions


def test_main_parse_args_init(mocker):
    mock_component_init = mocker.patch("greengrassTools.commands.component.component.init", return_value=None)
    parse_args_actions.run_command(CLIParser.cli_parser.parse_args(["component", "init", "-d"]))
    assert mock_component_init.called


def test_main_parse_args_case_insenstive_language(mocker):
    mocker.patch("greengrassTools.commands.component.component.init", return_value=None)
    x = CLIParser.cli_parser.parse_args(["component", "init", "-l", "PYTHON", "-d"])
    assert x.language == "python"


def test_main_parse_args_build(mocker):
    mock_component_build = mocker.patch("greengrassTools.commands.component.component.build", return_value=None)
    parse_args_actions.run_command(CLIParser.cli_parser.parse_args(["component", "build", "-d"]))
    assert mock_component_build.called


def test_main_parse_args_publish(mocker):
    mock_component_publish = mocker.patch("greengrassTools.commands.component.component.publish", return_value=None)
    parse_args_actions.run_command(CLIParser.cli_parser.parse_args(["component", "publish", "-d"]))
    assert mock_component_publish.called


def test_main_parse_args_list(mocker):
    mock_component_list = mocker.patch("greengrassTools.commands.component.component.list", return_value=None)
    args = CLIParser.cli_parser.parse_args(["component", "list", "--template", "-d"])
    parse_args_actions.run_command(args)
    assert mock_component_list.called

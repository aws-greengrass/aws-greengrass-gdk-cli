import gdk.CLIParser as CLIParser
import gdk.common.parse_args_actions as parse_args_actions


def test_main_parse_args_init(mocker):
    mock_component_init = mocker.patch("gdk.commands.component.component.init", return_value=None)
    parse_args_actions.run_command(CLIParser.cli_parser.parse_args(["component", "init", "-d"]))
    assert mock_component_init.called


def test_main_parse_args_case_insenstive_language(mocker):
    mocker.patch("gdk.commands.component.component.init", return_value=None)
    x = CLIParser.cli_parser.parse_args(["component", "init", "-l", "PYTHON", "-d"])
    assert x.language == "python"


def test_main_parse_args_build(mocker):
    mock_component_build = mocker.patch("gdk.commands.component.component.build", return_value=None)
    parse_args_actions.run_command(CLIParser.cli_parser.parse_args(["component", "build", "-d"]))
    assert mock_component_build.called


def test_main_parse_args_publish(mocker):
    mock_component_publish = mocker.patch("gdk.commands.component.component.publish", return_value=None)
    parse_args_actions.run_command(CLIParser.cli_parser.parse_args(["component", "publish", "-d"]))
    assert mock_component_publish.called


def test_main_parse_args_list(mocker):
    mock_component_list = mocker.patch("gdk.commands.component.component.list", return_value=None)
    args = CLIParser.cli_parser.parse_args(["component", "list", "--template", "-d"])
    parse_args_actions.run_command(args)
    assert mock_component_list.called


def test_main_parse_args_test_init(mocker):
    mock_test_init = mocker.patch("gdk.commands.test.test.init", return_value=None)
    args = CLIParser.cli_parser.parse_args(["test-e2e", "init"])
    parse_args_actions.run_command(args)
    assert mock_test_init.called


def test_main_parse_args_test_run(mocker):
    mock_test_run = mocker.patch("gdk.commands.test.test.run", return_value=None)
    args = CLIParser.cli_parser.parse_args(["test-e2e", "run"])
    parse_args_actions.run_command(args)
    assert mock_test_run.called


def test_main_parse_args_test_build(mocker):
    mock_test_build = mocker.patch("gdk.commands.test.test.build", return_value=None)
    args = CLIParser.cli_parser.parse_args(["test-e2e", "build"])
    parse_args_actions.run_command(args)
    assert mock_test_build.called


def test_main_parse_args_gdk(capsys):
    args = CLIParser.cli_parser.parse_args([])
    parse_args_actions.run_command(args)
    command_output = capsys.readouterr().out
    CLIParser.cli_parser.print_help()
    help_output = capsys.readouterr().out
    print(command_output)
    print(help_output)
    assert command_output == help_output

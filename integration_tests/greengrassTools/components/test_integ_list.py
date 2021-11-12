import greengrassTools.CLIParser as CLIParser
import greengrassTools.common.exceptions.error_messages as error_messages
import greengrassTools.common.parse_args_actions as parse_args_actions
import pytest


def test_list_run():
    with pytest.raises(Exception) as e:
        parse_args_actions.run_command(CLIParser.cli_parser.parse_args(["component", "list", "-d"]))
    assert e.value.args[0] == error_messages.LIST_WITH_INVALID_ARGS

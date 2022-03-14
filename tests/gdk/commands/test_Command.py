import unittest
from unittest import TestCase

import gdk
import pytest
from gdk.commands.Command import Command
from gdk.common.exceptions.CommandError import ConflictingArgumentsError


class CommandTest(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker):
        self.mocker = mocker

    def test_Command_instantiation_without_conflicting_args(self):
        command_args = {"a": "b"}
        mock_conflicting_arg_groups = self.mocker.patch.object(Command, "check_if_arguments_conflict", return_value=False)
        mock_run = self.mocker.patch.object(Command, "run", return_value=None)
        comm = Command(command_args, "init")
        assert mock_conflicting_arg_groups.call_count == 1
        assert mock_run.call_count == 0
        assert comm.arguments == command_args
        assert comm.name == "init"

    def test_Command_instantiation_with_conflicting_args(self):
        command_args = {"a": "b"}
        mock_conflicting_arg_groups = self.mocker.patch.object(
            Command, "check_if_arguments_conflict", side_effect=ConflictingArgumentsError("a", "b")
        )
        mock_run = self.mocker.patch.object(Command, "run", return_value=None)
        with pytest.raises(Exception) as e:
            Command(command_args, "init")
        assert "Arguments 'a' and 'b' are conflicting and cannot be used together in a command." in e.value.args[0]
        assert not mock_run.called
        assert mock_conflicting_arg_groups.call_count == 1

    def test_check_if_arguments_conflict_with_empty_dict(self):
        mock_init = self.mocker.patch.object(Command, "__init__", return_value=None)
        command_args = {"a": "b"}
        mock_non_conflicting_args_map = self.mocker.patch.object(Command, "_non_conflicting_args_map", return_value={})
        mock__identify_conflicting_args_in_command = self.mocker.patch.object(
            Command, "_identify_conflicting_args_in_command", return_value=None
        )
        c = Command(command_args, "init")
        assert mock_init.called
        assert not c.check_if_arguments_conflict()
        assert mock_non_conflicting_args_map.call_count == 1
        assert not mock__identify_conflicting_args_in_command.called

    def test_check_if_arguments_conflict_with_conflicting_args(self):
        mock_init = self.mocker.patch.object(Command, "__init__", return_value=None)
        command_args = {"a": "b"}
        mock_non_conflicting_args_map = self.mocker.patch.object(
            Command, "_non_conflicting_args_map", return_value={"non-empty-key": "value"}
        )
        mock__identify_conflicting_args_in_command = self.mocker.patch.object(
            Command, "_identify_conflicting_args_in_command", side_effect=ConflictingArgumentsError("a", "b")
        )
        cli_model = {
            "init": {"conflicting_arg_groups": [["language", "template"], ["repository"], ["project"], ["interactive"]]}
        }
        self.mocker.patch.object(gdk.CLIParser.cli_tool, "cli_model", cli_model)
        c = Command(command_args, "init")
        assert mock_init.called
        with pytest.raises(ConflictingArgumentsError):
            c.check_if_arguments_conflict()
        assert mock_non_conflicting_args_map.call_count == 1
        assert mock__identify_conflicting_args_in_command.call_count == 1

    def test_check_if_arguments_conflict_without_conflicting_args(self):
        mock_init = self.mocker.patch.object(Command, "__init__", return_value=None)
        command_args = {"a": "b"}
        mock_non_conflicting_args_map = self.mocker.patch.object(
            Command, "_non_conflicting_args_map", return_value={"non-empty-key": "value"}
        )
        mock__identify_conflicting_args_in_command = self.mocker.patch.object(
            Command, "_identify_conflicting_args_in_command", return_value=False
        )
        cli_model = {
            "init": {"conflicting_arg_groups": [["language", "template"], ["repository"], ["project"], ["interactive"]]}
        }
        self.mocker.patch.object(gdk.CLIParser.cli_tool, "cli_model", cli_model)
        c = Command(command_args, "init")
        assert mock_init.called
        assert not c.check_if_arguments_conflict()
        assert mock_non_conflicting_args_map.call_count == 1
        assert mock__identify_conflicting_args_in_command.call_count == 1

    def test__identify_conflicting_args_in_command_with_no_args(self):
        mock_init = self.mocker.patch.object(Command, "__init__", return_value=None)
        conflicting_arg_groups = {}
        command_args = {"a": "b"}
        mock_arguments_list = self.mocker.patch.object(Command, "_arguments_list", return_value=[])

        c = Command(command_args, "init")
        assert mock_init.called
        assert not c._identify_conflicting_args_in_command(conflicting_arg_groups)
        assert mock_arguments_list.call_count == 1

    def test__identify_conflicting_args_in_command_with_conflicting_args(self):
        mock_arguments_list = self.mocker.patch.object(Command, "_arguments_list", return_value=["language", "repository"])

        conflicting_arg_groups = {
            "language": {"language", "template"},
            "template": {"language", "template"},
            "repository": {"repository"},
        }
        mock_init = self.mocker.patch.object(Command, "__init__", return_value=None)
        command_args = {}
        c = Command(command_args, "init")
        assert mock_init.called
        with pytest.raises(ConflictingArgumentsError) as cae:
            c._identify_conflicting_args_in_command(conflicting_arg_groups)
        assert (
            "Arguments 'language' and 'repository' are conflicting and cannot be used together in a command."
            in cae.value.args[0]
        )
        assert mock_arguments_list.call_count == 1

    def test__identify_conflicting_args_in_command_without_conflicting_args(self):
        mock_arguments_list = self.mocker.patch.object(Command, "_arguments_list", return_value=["language", "template"])

        conflicting_arg_groups = {
            "language": {"language", "template"},
            "template": {"language", "template"},
            "repository": {"repository"},
        }
        mock_init = self.mocker.patch.object(Command, "__init__", return_value=None)
        command_args = {}
        c = Command(command_args, "init")
        assert mock_init.called
        assert not c._identify_conflicting_args_in_command(conflicting_arg_groups)
        assert mock_arguments_list.call_count == 1

    def test__identify_conflicting_args_in_command_mixed_args(self):
        mock_arguments_list = self.mocker.patch.object(
            Command, "_arguments_list", return_value=["language", "template", "repository"]
        )

        conflicting_arg_groups = {
            "language": {"language", "template"},
            "template": {"language", "template"},
            "repository": {"repository"},
        }
        mock_init = self.mocker.patch.object(Command, "__init__", return_value=None)
        command_args = {}
        c = Command(command_args, "init")
        assert mock_init.called
        with pytest.raises(ConflictingArgumentsError) as cae:
            c._identify_conflicting_args_in_command(conflicting_arg_groups)

        assert (
            "Arguments 'language' and 'repository' are conflicting and cannot be used together in a command."
            in cae.value.args[0]
        )
        assert mock_arguments_list.call_count == 1

    def test_arguments_list(self):
        command_args = {
            "component": "init",
            "init": None,
            "language": "python",
            "template": "HelloWorld-python",
            "repository": None,
            "gdk": "component",
        }
        conf_args_dict = {
            "language": {"language", "template"},
            "template": {"language", "template"},
            "repository": {"repository"},
        }
        expected_list = ["language", "template"]
        c = Command(command_args, "init")
        assert c._arguments_list(conf_args_dict) == expected_list

        c.arguments = {}
        conf_args_dict = {
            "language": {"language", "template"},
            "template": {"language", "template"},
            "repository": {"repository"},
        }
        expected_list = []
        assert c._arguments_list(conf_args_dict) == expected_list

        c.arguments = {}
        conf_args_dict = {}
        expected_list = []
        assert c._arguments_list(conf_args_dict) == expected_list

        command_args = {
            "component": "init",
            "init": None,
            "language": "python",
            "template": "HelloWorld-python",
            "repository": None,
            "gdk": "component",
        }
        conf_args_dict = {}
        expected_list = []
        assert c._arguments_list(conf_args_dict) == expected_list

    def test_non_conflicting_args_map(self):
        # Test if dictionary of conflicting args of a commmand is correctly formed.
        cli_model = {
            "init": {"conflicting_arg_groups": [["language", "template"], ["repository"], ["project"], ["interactive"]]}
        }
        expected_dic = {
            "language": {"language", "template"},
            "template": {"language", "template"},
            "repository": {"repository"},
            "project": {"project"},
            "interactive": {"interactive"},
        }
        command_args = {}
        # Not to run conflicting args check during initiation
        self.mocker.patch.object(Command, "__init__", return_value=None)

        c = Command(command_args, "init")
        c.arguments = command_args
        c.name = "init"
        self.mocker.patch.object(gdk.CLIParser.cli_tool, "cli_model", cli_model)
        assert c._non_conflicting_args_map() == expected_dic

        cli_model = {"init": {"arguments": []}}
        self.mocker.patch.object(gdk.CLIParser.cli_tool, "cli_model", cli_model)
        assert c._non_conflicting_args_map() == {}

        cli_model = {"init": {"conflicting_arg_groups": []}}
        self.mocker.patch.object(gdk.CLIParser.cli_tool, "cli_model", cli_model)
        assert c._non_conflicting_args_map() == {}

        cli_model = {"init": {"conflicting_arg_groups": [["language", "template"], []]}}
        expected_dic = {"language": {"language", "template"}, "template": {"language", "template"}}
        self.mocker.patch.object(gdk.CLIParser.cli_tool, "cli_model", cli_model)
        assert c._non_conflicting_args_map() == expected_dic

        cli_model = {"init": {"conflicting_arg_groups": [["language", "template"], []]}}
        c.name = "invalid-command"
        expected_dic = {}
        self.mocker.patch.object(gdk.CLIParser.cli_tool, "cli_model", cli_model)
        assert c._non_conflicting_args_map() == expected_dic


if __name__ == "__main__":
    unittest.main()

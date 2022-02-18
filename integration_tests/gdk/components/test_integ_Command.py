import unittest
from unittest import TestCase

import pytest
from gdk.commands.Command import Command


class CommandTest(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker):
        self.mocker = mocker

    def test_Command_instantiation_without_conflicting_args(self):
        command_args = {
            "component": "init",
            "init": None,
            "language": "python",
            "template": "HelloWorld-python",
            "repository": None,
            "gdk": "component",
        }
        spy_conflicting_arg_groups = self.mocker.spy(Command, "check_if_arguments_conflict")
        comm = Command(command_args, "init")
        assert comm.arguments == command_args
        assert comm.name == "init"
        spy_conflicting_arg_groups.assert_called_with(comm)
        assert spy_conflicting_arg_groups.return_value

    def test_Command_instantiation_with_conflicting_args(self):
        command_args = {
            "component": "init",
            "init": None,
            "language": "python",
            "template": "HelloWorld-python",
            "repository": "conflicts",
            "gdk": "component",
        }
        mock_run = self.mocker.patch.object(Command, "run", return_value=None)
        mock_conflicting_arg_groups = self.mocker.spy(Command, "check_if_arguments_conflict")
        with pytest.raises(Exception) as e:
            comm = Command(command_args, "init")
            mock_conflicting_arg_groups.assert_called_with(comm)
            assert comm.arguments == command_args
            assert comm.name == "init"
        assert (
            "Arguments 'language' and 'repository' are conflicting and cannot be used together in a command."
            in e.value.args[0]
        )
        assert mock_run.call_count == 0

    def test_Command_instantiation_with_no_args(self):
        command_args = {
            "component": "build",
            "build": None,
            "gdk": "component",
        }
        mock_run = self.mocker.patch.object(Command, "run", return_value=None)
        mock_conflicting_arg_groups = self.mocker.spy(Command, "check_if_arguments_conflict")
        comm = Command(command_args, "build")
        assert mock_run.call_count == 0
        assert comm.arguments == command_args
        assert comm.name == "build"
        mock_conflicting_arg_groups.assert_called_with(comm)


if __name__ == "__main__":
    unittest.main()

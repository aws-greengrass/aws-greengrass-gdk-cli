import argparse
import logging

import gdk.commands.methods as methods
import gdk.common.parse_args_actions as actions
import pytest


def test_run_command_with_valid_namespace_without_debug(mocker):
    # Integ test that appropriate action is called only once with valid command namespace.
    args_namespace = argparse.Namespace(component="init", init=None, lang="python", template="name", **{"gdk": "component"})
    spy_component_build = mocker.spy(methods, "_gdk_component_build")
    spy_call_action_by_name = mocker.spy(actions, "call_action_by_name")
    spy_get_method_from_command = mocker.spy(actions, "get_method_from_command")
    spy_logger = mocker.spy(logging, "basicConfig")
    mock_component_init = mocker.patch("gdk.commands.methods._gdk_component_init", return_value=None)
    actions.run_command(args_namespace)
    assert mock_component_init.call_count == 1
    assert spy_component_build.call_count == 0
    assert spy_call_action_by_name.call_count == 1
    assert spy_get_method_from_command.call_count == 3  # Recursively called for three times
    assert spy_logger.call_count == 0


def test_run_command_with_valid_debug_enabled(mocker):
    # Integ test that appropriate action is called only once with valid command namespace.
    args_namespace = argparse.Namespace(
        component="init", init=None, lang="python", template="name", **{"gdk": "component"}, debug=True
    )
    spy_component_build = mocker.spy(methods, "_gdk_component_build")
    spy_call_action_by_name = mocker.spy(actions, "call_action_by_name")
    spy_get_method_from_command = mocker.spy(actions, "get_method_from_command")
    mock_component_init = mocker.patch("gdk.commands.methods._gdk_component_init", return_value=None)

    spy_logging_ = mocker.spy(logging.getLogger(), "setLevel")
    actions.run_command(args_namespace)
    assert mock_component_init.call_count == 1
    assert spy_component_build.call_count == 0
    assert spy_call_action_by_name.call_count == 1
    assert spy_get_method_from_command.call_count == 3  # Recursively called for three times
    spy_logging_.assert_called_once_with(logging.DEBUG)
    with pytest.raises(AssertionError):
        spy_logging_.assert_called_once_with(logging.WARN)


def test_run_command_with_invalid_namespace_method(mocker):
    # Test that action when the method doesn't exist for an invalid namespace
    args_namespace = argparse.Namespace(component="invalid", invalid=None, **{"gdk": "component"})
    spy_get_method_from_command = mocker.spy(actions, "get_method_from_command")
    spy_call_action_by_name = mocker.spy(actions, "call_action_by_name")
    with pytest.raises(SystemExit):
        actions.run_command(args_namespace)
    assert spy_call_action_by_name.call_count == 1  # No method name to call if namespace is invalid
    assert spy_get_method_from_command.call_count == 3  # Recursively called for three times


def test_conflicting_args_with_conflict(mocker):
    # Test conflicting args of command with its namespace args.
    mock_dic_of_conflicting_args = mocker.spy(actions, "_dic_of_conflicting_args")
    mock_check_command_args_with_conflicting_args = mocker.spy(actions, "check_command_args_with_conflicting_args")
    command_args = {
        "component": "init",
        "init": None,
        "language": "python",
        "template": "HelloWorld-python",
        "repository": "conflicts",
        "gdk": "component",
    }

    assert actions.conflicting_arg_groups(command_args, "init")
    assert mock_dic_of_conflicting_args.call_count == 1
    assert mock_check_command_args_with_conflicting_args.call_count == 1


def test_conflicting_args_with_no_conflict(mocker):
    # Test conflicting args of command with its namespace args.
    mock_dic_of_conflicting_args = mocker.spy(actions, "_dic_of_conflicting_args")
    mock_check_command_args_with_conflicting_args = mocker.spy(actions, "check_command_args_with_conflicting_args")
    command_args = {
        "component": "init",
        "init": None,
        "language": "python",
        "template": "HelloWorld-python",
        "repository": None,
        "gdk": "component",
    }

    assert not actions.conflicting_arg_groups(command_args, "init")
    assert mock_dic_of_conflicting_args.call_count == 1
    assert mock_check_command_args_with_conflicting_args.call_count == 1

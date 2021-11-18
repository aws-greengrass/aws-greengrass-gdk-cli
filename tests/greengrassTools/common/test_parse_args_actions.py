import argparse

import greengrassTools.CLIParser
import greengrassTools.commands.methods as methods
import greengrassTools.common.consts as consts
import greengrassTools.common.parse_args_actions as actions
import pytest


def test_run_command_with_mocks(mocker):
    # Test that appropriate action is called only once with valid command namespace.
    args_namespace = argparse.Namespace(component="init", init=None, lang="python", template="name", **{"gdk": "component"})
    mock_get_method_from_command = mocker.patch(
        "greengrassTools.common.parse_args_actions.get_method_from_command", return_value="_gdk_component_init"
    )
    mock_component_init = mocker.patch("greengrassTools.commands.methods._gdk_component_init", return_value=None)
    spy_call_action_by_name = mocker.spy(actions, "call_action_by_name")

    actions.run_command(args_namespace)
    assert mock_component_init.call_count == 1
    assert spy_call_action_by_name.call_count == 1
    assert mock_get_method_from_command.call_count == 1
    mock_get_method_from_command.assert_any_call(vars(args_namespace), consts.cli_tool_name, "")


def test_run_command_with_invalid_namespace(mocker):
    # Test that action is not called when the namespace is invalid
    args_namespace = argparse.Namespace(component="init", lang="python", template="name", **{"gdk": "component"})
    spy_get_method_from_command = mocker.spy(actions, "get_method_from_command")
    spy_call_action_by_name = mocker.spy(actions, "call_action_by_name")

    actions.run_command(args_namespace)
    assert spy_call_action_by_name.call_count == 0  # No method name to call if namespace is invalid
    assert spy_get_method_from_command.call_count == 3  # Recursively called for three times


def test_run_command_namespace_as_dict(mocker):
    # Integ test that appropriate action is called only once with valid command namespace.
    args_namespace = argparse.Namespace(component="init", init=None, lang="python", template="name", **{"gdk": "component"})
    spy_component_build = mocker.spy(methods, "_gdk_component_build")
    spy_call_action_by_name = mocker.spy(actions, "call_action_by_name")
    spy_get_method_from_command = mocker.spy(actions, "get_method_from_command")
    mock_component_init = mocker.patch("greengrassTools.commands.methods._gdk_component_init", return_value=None)
    actions.run_command(args_namespace)
    assert mock_component_init.call_count == 1
    assert spy_component_build.call_count == 0
    assert spy_call_action_by_name.call_count == 1
    assert spy_get_method_from_command.call_count == 3  # Recursively called for three times
    spy_get_method_from_command.assert_any_call(vars(args_namespace), consts.cli_tool_name, "")
    spy_get_method_from_command.assert_any_call(vars(args_namespace), "component", "_gdk")
    spy_get_method_from_command.assert_any_call(vars(args_namespace), "init", "_gdk_component")


def test_get_method_from_command(mocker):
    # Test if the method name is correctly formed from the command
    test_d_args = {"gdk": "component", "component": "init", "init": None, "lang": "python", "template": "name"}
    test_command = "gdk"
    test_method_name = ""
    spy_get_method_from_command = mocker.spy(actions, "get_method_from_command")
    mocker.patch("greengrassTools.commands.methods._gdk_component_init", return_value=None)
    method_name_from_command = actions.get_method_from_command(test_d_args, test_command, test_method_name)
    spy_get_method_from_command.assert_any_call(test_d_args, test_command, test_method_name)
    assert method_name_from_command == "_gdk_component_init"
    assert spy_get_method_from_command.call_count == 3

    test_method_name = ""
    test_command = "component"
    spy_get_method_from_command.reset_mock()
    method_name_from_command = actions.get_method_from_command(test_d_args, test_command, test_method_name)
    assert method_name_from_command == "_component_init"
    assert spy_get_method_from_command.call_count == 2
    spy_get_method_from_command.assert_any_call(test_d_args, test_command, test_method_name)


def test_get_method_from_command_invalid(mocker):
    # Test if the method name is None when the command is invalid
    test_d_args = {"gdk": "component", "component": "init", "init": None, "lang": "python", "template": "name"}
    test_method_name = ""
    test_command = ""
    spy_get_method_from_command = mocker.spy(actions, "get_method_from_command")
    method_name_from_command = actions.get_method_from_command(test_d_args, test_command, test_method_name)
    assert method_name_from_command is None
    assert spy_get_method_from_command.call_count == 1

    test_method_name = ""
    test_command = "command_not_in_model"
    spy_get_method_from_command.reset_mock()
    method_name_from_command = actions.get_method_from_command(test_d_args, test_command, test_method_name)
    assert method_name_from_command is None
    assert spy_get_method_from_command.call_count == 1


def test_get_method_from_command_invalid_subcommand():
    # Test if the method name is None when the command is invalid.
    # There is no init-> None which is invalid for a parsed arg namespace.
    test_d_args = {"gdk": "component", "component": "init", "lang": "python", "template": "name"}
    test_method_name = ""
    test_command = "gdk"
    method_name_from_command = actions.get_method_from_command(test_d_args, test_command, test_method_name)

    assert method_name_from_command is None


def test_call_action_by_name_valid(mocker):
    # Action is called by its name when the method name is valid and exists in the methods file
    test_d_args = {"gdk": "component", "component": "init", "init": None, "lang": "python", "template": "name"}
    method_name = "_gdk_component_init"
    method_mocker = mocker.patch("greengrassTools.commands.methods._gdk_component_init", return_value=None)
    actions.call_action_by_name(method_name, test_d_args)

    assert method_mocker.call_count == 1


def test_call_action_by_name_invalid(mocker):
    # Action is not called by its name when the method name doesn't exists in the methods file
    test_d_args = {"gdk": "component", "component": "init", "init": None, "lang": "python", "template": "name"}
    method_name = "invalid_method_name"
    with pytest.raises(Exception) as e_info:
        actions.call_action_by_name(method_name, test_d_args)
    expected_err_message = "{} does not support the given command.".format(consts.cli_tool_name)
    assert e_info.value.args[0] == expected_err_message


def test_dic_of_conflicting_args():
    # Test if dictionary of conflicting args of a commmand is correctly formed.
    cli_model = {"init": {"conflicting_arg_groups": [["language", "template"], ["repository"], ["project"], ["interactive"]]}}
    command = "init"
    expected_dic = {
        "language": {"language", "template"},
        "template": {"language", "template"},
        "repository": {"repository"},
        "project": {"project"},
        "interactive": {"interactive"},
    }
    assert actions._dic_of_conflicting_args(cli_model, command) == expected_dic

    cli_model = {"init": {"arguments": []}}
    command = "init"
    assert actions._dic_of_conflicting_args(cli_model, command) == {}

    cli_model = {"init": {"conflicting_arg_groups": []}}
    command = "init"
    assert actions._dic_of_conflicting_args(cli_model, command) == {}

    cli_model = {"init": {"conflicting_arg_groups": [["language", "template"], []]}}
    command = "init"
    expected_dic = {"language": {"language", "template"}, "template": {"language", "template"}}
    assert actions._dic_of_conflicting_args(cli_model, command) == expected_dic

    cli_model = {"init": {"conflicting_arg_groups": [["language", "template"], []]}}
    command = "try"
    expected_dic = {}
    assert actions._dic_of_conflicting_args(cli_model, command) == expected_dic


def test_list_of_command_args():
    # Check that the list of command args contain only conflicting args that are not None in namespace args
    command_args = {
        "component": "init",
        "init": None,
        "language": "python",
        "template": "HelloWorld-python",
        "repository": None,
        "gdk": "component",
    }
    conf_args_dict = {"language": {"language", "template"}, "template": {"language", "template"}, "repository": {"repository"}}
    expected_list = ["language", "template"]
    assert actions._list_of_command_args(command_args, conf_args_dict) == expected_list

    command_args = {}
    conf_args_dict = {"language": {"language", "template"}, "template": {"language", "template"}, "repository": {"repository"}}
    expected_list = []
    assert actions._list_of_command_args(command_args, conf_args_dict) == expected_list

    command_args = {}
    conf_args_dict = {}
    expected_list = []
    assert actions._list_of_command_args(command_args, conf_args_dict) == expected_list

    command_args = {
        "component": "init",
        "init": None,
        "lang": "python",
        "temp": "HelloWorld-python",
        "repository": None,
        "gdk": "component",
    }
    conf_args_dict = {"language": {"language", "template"}, "template": {"language", "template"}, "repository": {"repository"}}
    expected_list = []
    assert actions._list_of_command_args(command_args, conf_args_dict) == expected_list


def test_check_command_args_with_conflicting_args(mocker):
    # Test if the args are correctly identified as conflicting
    mock_list_of_command_args = mocker.patch(
        "greengrassTools.common.parse_args_actions._list_of_command_args", return_value=["language", "template"]
    )

    conflicting_arg_groups = {
        "language": {"language", "template"},
        "template": {"language", "template"},
        "repository": {"repository"},
    }
    assert not actions.check_command_args_with_conflicting_args({}, conflicting_arg_groups)
    assert mock_list_of_command_args.call_count == 1

    mock_list_of_command_args1_conflicting = mocker.patch(
        "greengrassTools.common.parse_args_actions._list_of_command_args", return_value=["language", "repository"]
    )

    conflicting_arg_groups = {
        "language": {"language", "template"},
        "template": {"language", "template", "repository"},
        "repository": {"repository", "template"},
    }
    assert actions.check_command_args_with_conflicting_args({}, conflicting_arg_groups)
    assert mock_list_of_command_args1_conflicting.call_count == 1

    mock_list_of_command_args2_mix_of_both = mocker.patch(
        "greengrassTools.common.parse_args_actions._list_of_command_args", return_value=["template", "language", "repository"]
    )

    conflicting_arg_groups = {
        "language": {"language", "template"},
        "template": {"language", "template", "repository"},
        "repository": {"repository", "template"},
    }
    assert actions.check_command_args_with_conflicting_args({}, conflicting_arg_groups)
    assert mock_list_of_command_args2_mix_of_both.call_count == 1


def test_conflicting_args_with_conflict(mocker):
    # Test conflicting args of command with its namespace args.
    conflicting_arg_groups = {
        "language": {"language", "template"},
        "template": {"language", "template", "repository"},
        "repository": {"repository", "template"},
    }

    mock_dic_of_conflicting_args = mocker.patch(
        "greengrassTools.common.parse_args_actions._dic_of_conflicting_args", return_value=conflicting_arg_groups
    )

    mock_check_command_args_with_conflicting_args = mocker.patch(
        "greengrassTools.common.parse_args_actions.check_command_args_with_conflicting_args", return_value=True
    )

    command_args = {
        "component": "init",
        "init": None,
        "language": "python",
        "template": "HelloWorld-python",
        "repository": None,
        "gdk": "component",
    }
    cli_model = {"init": {"conflicting_arg_groups": [["language", "template"], ["repository"], ["project"], ["interactive"]]}}
    mocker.patch.object(greengrassTools.CLIParser.cli_tool, "cli_model", cli_model)

    assert actions.conflicting_arg_groups(command_args, "init")
    assert mock_dic_of_conflicting_args.call_count == 1
    assert mock_check_command_args_with_conflicting_args.call_count == 1


def test_conflicting_args_with_no_conflict(mocker):
    # Test conflicting args of command with its namespace args.
    conflicting_arg_groups = {
        "language": {"language", "template"},
        "template": {"language", "template", "repository"},
        "repository": {"repository", "template"},
    }

    mock_dic_of_conflicting_args = mocker.patch(
        "greengrassTools.common.parse_args_actions._dic_of_conflicting_args", return_value=conflicting_arg_groups
    )

    mock_check_command_args_with_conflicting_args = mocker.patch(
        "greengrassTools.common.parse_args_actions.check_command_args_with_conflicting_args", return_value=False
    )

    command_args = {
        "component": "init",
        "init": None,
        "language": "python",
        "template": "HelloWorld-python",
        "repository": None,
        "gdk": "component",
    }
    cli_model = {"init": {"conflicting_arg_groups": [["language", "template"], ["repository"], ["project"], ["interactive"]]}}
    mocker.patch.object(greengrassTools.CLIParser.cli_tool, "cli_model", cli_model)

    assert not actions.conflicting_arg_groups(command_args, "init")
    assert mock_dic_of_conflicting_args.call_count == 1
    assert mock_check_command_args_with_conflicting_args.call_count == 1

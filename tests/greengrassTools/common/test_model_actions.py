from pathlib import Path
from unittest.mock import mock_open, patch

import greengrassTools.common.consts as consts
import greengrassTools.common.model_actions as model_actions
import pytest


def test_get_validated_model_file_not_exists(mocker):
    mock_get_static_file_path = mocker.patch("greengrassTools.common.utils.get_static_file_path", return_value=None)
    mock_is_valid_model = mocker.patch("greengrassTools.common.model_actions.is_valid_model", return_value=False)
    with pytest.raises(Exception) as e_info:
        model_actions.get_validated_model()

    expected_err_message = "expected str, bytes or os.PathLike object, not NoneType"
    assert e_info.value.args[0] == expected_err_message
    assert not mock_is_valid_model.called
    assert mock_get_static_file_path.call_count == 1


def test_get_validated_model_file_exists(mocker):
    file_path = Path("path/to/open")
    mock_get_static_file_path = mocker.patch("greengrassTools.common.utils.get_static_file_path", return_value=file_path)
    mock_is_valid_model = mocker.patch("greengrassTools.common.model_actions.is_valid_model", return_value=True)

    with patch("builtins.open", mock_open(read_data="{}")) as mock_file:
        model_actions.get_validated_model()
        assert open(file_path).read() == "{}"
        mock_file.assert_called_with(file_path)
        assert not mock_is_valid_model.called
        assert mock_get_static_file_path.call_count == 1


def test_get_validated_model_with_valid_model(mocker):
    # Should return model when the model is valid
    mocker.patch("greengrassTools.common.model_actions.is_valid_model", return_value=True)
    command_model = model_actions.get_validated_model()
    assert command_model


def test_get_validated_model_with_invalid_model(mocker):
    # Should raise an exception when the model is invalid
    mock_is_valid_model = mocker.patch("greengrassTools.common.model_actions.is_valid_model", return_value=False)
    model_actions.get_validated_model()
    assert not mock_is_valid_model.called


def test_is_valid_argument_model_valid():
    # Valid argument that contains both name and help.
    valid_arg = {"name": ["-l", "--lang"], "help": "language help", "choices": ["p", "j"]}
    assert model_actions.is_valid_argument_model(valid_arg)


def test_is_valid_argument_model_without_name():
    # Invalid arg without name.
    invalid_arg_without_name = {"names": ["-l", "--lang"], "help": "help"}
    assert not model_actions.is_valid_model(invalid_arg_without_name, consts.cli_tool_name)


def test_is_valid_argument_model_without_help():
    # Invalid arg without help.
    invalid_arg_without_help = {"name": ["-l", "--lang"], "helper": "help"}
    assert not model_actions.is_valid_model(invalid_arg_without_help, consts.cli_tool_name)


def test_is_valid_subcommand_model_valid():
    # Valid subcommand with valid commmand key in the cli model.
    model = {
        "gdk": {"sub-commands": ["component"], "help": "help"},
        "component": {"help": "help", "sub-commands": ["init", "build"]},
        "build": {"help": "help"},
        "init": {"help": "help"},
    }
    valid_model_subcommands = ["component"]
    assert model_actions.is_valid_subcommand_model(model, valid_model_subcommands)


def test_is_valid_subcommand_model_valid_without_help():
    # Valid subcommand without help in the cli model.
    model = {
        "gdk": {"sub-commands": ["component"]},
        "component": {"sub-commands": ["init", "build"]},
        "build": {},
        "init": {},
    }
    valid_model_subcommands = ["component"]
    assert not model_actions.is_valid_subcommand_model(model, valid_model_subcommands)


def test_is_valid_subcommand_model_invalid():
    # Invalid subcommand with no key in the cli model.
    model = {
        "gdk": {"sub-commands": ["component"]},
        "component": {"sub-commands": ["init", "build"]},
        "init": {},
        "build": {},
    }
    invalid_model_subcommands = ["component", "invalid-subcommand-that-is-not-present-as-key"]
    assert not model_actions.is_valid_subcommand_model(model, invalid_model_subcommands)


def test_is_valid_model_without_help_in_command():
    # Invalid model without help for commands
    valid_model = {
        "gdk": {"sub-commands": ["component"]},
        "component": {"sub-commands": ["init", "build"]},
        "init": {"arguments": {"lang": {"name": ["-l", "--lang"], "help": "help"}}},
        "build": {},
    }
    assert not model_actions.is_valid_model(valid_model, consts.cli_tool_name)


def test_is_valid_model():
    # Valid model with correct args ang sub-commands.
    valid_model = {
        "gdk": {"sub-commands": ["component"], "help": "help"},
        "component": {"help": "help", "sub-commands": ["init", "build"]},
        "init": {"help": "help", "arguments": {"lang": {"name": ["-l", "--lang"], "help": "help"}}},
        "build": {"help": "help"},
    }
    assert model_actions.is_valid_model(valid_model, consts.cli_tool_name)


def test_is_valid_model_without_name():
    # Invalid model with incorrect sub-commands. Subcommand with no key in the cli model.
    invalid_model_without_name_in_args = {
        "gdk": {
            "sub-commands": ["component"],
            "arguments": {"lang": {"names": ["-l", "--lang"], "help": "help"}},
        },
        "component": {},
    }
    assert not model_actions.is_valid_model(invalid_model_without_name_in_args, consts.cli_tool_name)


def test_is_valid_model_without_help():
    # Invalid model with incorrect arguments. Argument without name.
    invalid_model_args_without_help = {
        "gdk": {
            "sub-commands": ["component"],
            "arguments": {"lang": {"names": ["-l", "--lang"], "help": "help"}},
        },
        "component": {},
    }
    assert not model_actions.is_valid_model(invalid_model_args_without_help, consts.cli_tool_name)


def test_is_valid_model_with_invalid_sub_command():
    # Invalid model with incorrect sub-commands. Subcommand with no key in the cli model.
    invalid_model_subcommands = {
        "gdk": {"sub-commands": ["component", "invalid-sub-command"]},
        "component": {},
    }
    assert not model_actions.is_valid_model(invalid_model_subcommands, consts.cli_tool_name)


def test_is_valid_model_with_invalid_arg_group():
    # Valid model with correct args ang sub-commands.
    valid_model = {
        "gdk": {"sub-commands": ["component"]},
        "component": {"sub-commands": ["init", "build"]},
        "init": {
            "arguments": {"lang": {"name": ["-l", "--lang"], "help": "help"}},
            "arg_groups": {
                "title": "Greengrass component templates.",
                "args": ["language", "template"],
                "description": "description",
            },
        },
        "build": {},
    }
    assert not model_actions.is_valid_model(valid_model, consts.cli_tool_name)


def test_is_valid_argument_group_valid():
    # Valid argument group model with correct arguments
    t_arg_group = {"title": "Greengrass component templates.", "args": ["language", "template"], "description": "description"}
    t_args = {
        "language": {"name": ["-l", "--language"], "help": "help", "choices": ["p", "j"]},
        "template": {"name": ["-t", "--template"], "help": "help"},
        "repository": {"name": ["-r", "--repository"], "help": "help"},
    }
    assert model_actions.is_valid_argument_group_model(t_arg_group, t_args)


def test_is_valid_argument_group_invalid_group():
    # Invalid argument group model without title
    t_arg_group = {"args": ["language", "template"], "description": "description"}
    t_args = {
        "language": {"name": ["-l", "--language"], "help": "help", "choices": ["p", "j"]},
        "template": {"name": ["-t", "--template"], "help": "help"},
        "repository": {"name": ["-r", "--repository"], "help": "help"},
    }
    assert not model_actions.is_valid_argument_group_model(t_arg_group, t_args)

    # Invalid argument group model without args
    t_arg_group = {"title": "title", "description": "description"}
    t_args = {
        "language": {"name": ["-l", "--language"], "help": "help", "choices": ["p", "j"]},
        "template": {"name": ["-t", "--template"], "help": "help"},
        "repository": {"name": ["-r", "--repository"], "help": "help"},
    }
    assert not model_actions.is_valid_argument_group_model(t_arg_group, t_args)

    # Invalid argument group model without description
    t_arg_group = {"title": "title", "args": ["language", "template"]}
    t_args = {
        "language": {"name": ["-l", "--language"], "help": "help", "choices": ["p", "j"]},
        "template": {"name": ["-t", "--template"], "help": "help"},
        "repository": {"name": ["-r", "--repository"], "help": "help"},
    }
    assert not model_actions.is_valid_argument_group_model(t_arg_group, t_args)


def test_is_valid_argument_group_invalid_with_arg_not_in_arguments():
    # Invalid argument group model with arg not in arguments
    t_arg_group = {
        "args": ["this-arg-not-in-arguments", "template"],
        "description": "description",
        "title": "title",
    }
    t_args = {
        "language": {"name": ["-l", "--language"], "help": "help", "choices": ["p", "j"]},
        "template": {"name": ["-t", "--template"], "help": "help"},
        "repository": {"name": ["-r", "--repository"], "help": "help"},
    }
    assert not model_actions.is_valid_argument_group_model(t_arg_group, t_args)

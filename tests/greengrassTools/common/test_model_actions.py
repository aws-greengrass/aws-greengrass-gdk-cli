from unittest.mock import mock_open, patch

import greengrassTools.common.consts as consts
import greengrassTools.common.exceptions.error_messages as error_messages
import greengrassTools.common.model_actions as model_actions
import pytest


def test_model_existence(mocker):
    # Integ test for the existence of command model file even before building the cli tool.
    command_model = model_actions.get_validated_model()
    assert type(command_model) == dict  # Command model obtained should always be a dictionary
    assert len(command_model) > 0  # Command model is never empty
    assert consts.cli_tool_name in command_model  # Command model should contain the name of CLI as a key


def test_get_validated_model_file_not_exists(mocker):
    mock_get_static_file_path = mocker.patch("greengrassTools.common.utils.get_static_file_path", return_value=None)
    mock_is_valid_model = mocker.patch("greengrassTools.common.model_actions.is_valid_model", return_value=False)
    with pytest.raises(Exception) as e_info:
        model_actions.get_validated_model()

    expected_err_message = "Model validation failed. CLI model file doesn't exist."
    assert e_info.value.args[0] == expected_err_message
    assert mock_is_valid_model.call_count == 0
    assert mock_get_static_file_path.call_count == 1


def test_get_validated_model_file_exists(mocker):
    file_path = "path/to/open"
    mock_get_static_file_path = mocker.patch("greengrassTools.common.utils.get_static_file_path", return_value=file_path)
    mock_is_valid_model = mocker.patch("greengrassTools.common.model_actions.is_valid_model", return_value=True)

    with patch("builtins.open", mock_open(read_data="{}")) as mock_file:
        model_actions.get_validated_model()
        assert open(file_path).read() == "{}"
        mock_file.assert_called_with(file_path)
        assert mock_is_valid_model.call_count == 1
        assert mock_get_static_file_path.call_count == 1


def test_get_validated_model_with_valid_model(mocker):
    # Should return model when the model is valid
    mocker.patch("greengrassTools.common.model_actions.is_valid_model", return_value=True)
    command_model = model_actions.get_validated_model()
    assert command_model


def test_get_validated_model_with_invalid_model(mocker):
    # Should raise an exception when the model is invalid
    mocker.patch("greengrassTools.common.model_actions.is_valid_model", return_value=False)

    with pytest.raises(Exception) as e_info:
        model_actions.get_validated_model()
    assert e_info.value.args[0] == error_messages.INVALID_CLI_MODEL


def test_is_valid_argument_model_valid():
    # Valid argument that contains both name and help.
    valid_arg = {
        "name": ["-l", "--lang"],
        "help": "language help",
        "choices": ["p", "j"],
    }
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
    # Valid subcommand with key in the cli model.
    model = {
        "greengrass-tools": {"sub-commands": ["component"]},
        "component": {"sub-commands": ["init", "build"]},
        "build": {},
        "init": {},
    }
    valid_model_subcommands = ["component"]
    assert model_actions.is_valid_subcommand_model(model, valid_model_subcommands)


def test_is_valid_subcommand_model_invalid():
    # Invalid subcommand with no key in the cli model.
    model = {
        "greengrass-tools": {"sub-commands": ["component"]},
        "component": {"sub-commands": ["init", "build"]},
        "init": {},
        "build": {},
    }
    invalid_model_subcommands = ["component", "invalid-subcommand-that-is-not-present-as-key"]
    assert not model_actions.is_valid_subcommand_model(model, invalid_model_subcommands)


def test_is_valid_model():
    # Valid model with correct args ang sub-commands.
    valid_model = {
        "greengrass-tools": {"sub-commands": ["component"]},
        "component": {"sub-commands": ["init", "build"]},
        "init": {"arguments": {"lang": {"name": ["-l", "--lang"], "help": "help"}}},
        "build": {},
    }
    assert model_actions.is_valid_model(valid_model, consts.cli_tool_name)


def test_is_valid_model_without_name():
    # Invalid model with incorrect sub-commands. Subcommand with no key in the cli model.
    invalid_model_without_name_in_args = {
        "greengrass-tools": {
            "sub-commands": ["component"],
            "arguments": {"lang": {"names": ["-l", "--lang"], "help": "help"}},
        },
        "component": {},
    }
    assert not model_actions.is_valid_model(invalid_model_without_name_in_args, consts.cli_tool_name)


def test_is_valid_model_without_help():
    # Invalid model with incorrect arguments. Argument without name.
    invalid_model_args_without_help = {
        "greengrass-tools": {
            "sub-commands": ["component"],
            "arguments": {"lang": {"names": ["-l", "--lang"], "help": "help"}},
        },
        "component": {},
    }
    assert not model_actions.is_valid_model(invalid_model_args_without_help, consts.cli_tool_name)


def test_is_valid_model_with_invalid_sub_command():
    # Invalid model with incorrect sub-commands. Subcommand with no key in the cli model.
    invalid_model_subcommands = {
        "greengrass-tools": {"sub-commands": ["component", "invalid-sub-command"]},
        "component": {},
    }
    assert not model_actions.is_valid_model(invalid_model_subcommands, consts.cli_tool_name)

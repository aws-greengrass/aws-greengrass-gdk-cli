from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

import gdk.common.consts as consts
import gdk.common.model_actions as model_actions


def test_get_validated_model_file_not_exists(mocker):
    mock_get_static_file_path = mocker.patch("gdk.common.utils.get_static_file_path", return_value=None)
    mock_is_valid_model = mocker.patch("gdk.common.model_actions.is_valid_model", return_value=False)
    with pytest.raises(Exception) as e_info:
        model_actions.get_validated_model()

    expected_err_message = "expected str, bytes or os.PathLike object, not NoneType"
    assert e_info.value.args[0] == expected_err_message
    assert not mock_is_valid_model.called
    assert mock_get_static_file_path.call_count == 1


def test_get_validated_model_file_exists(mocker):
    file_path = Path("path/to/open")
    mock_get_static_file_path = mocker.patch("gdk.common.utils.get_static_file_path", return_value=file_path)
    mock_is_valid_model = mocker.patch("gdk.common.model_actions.is_valid_model", return_value=True)

    with patch("builtins.open", mock_open(read_data="{}")) as mock_file:
        model_actions.get_validated_model()
        assert open(file_path).read() == "{}"
        mock_file.assert_called_with(file_path)
        assert not mock_is_valid_model.called
        assert mock_get_static_file_path.call_count == 1


def test_get_validated_model_with_valid_model(mocker):
    # Should return model when the model is valid
    mocker.patch("gdk.common.model_actions.is_valid_model", return_value=True)
    command_model = model_actions.get_validated_model()
    assert command_model


def test_get_validated_model_with_invalid_model(mocker):
    # Should raise an exception when the model is invalid
    mock_is_valid_model = mocker.patch("gdk.common.model_actions.is_valid_model", return_value=False)
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
        "gdk": {
            "sub-commands": {
                "component": {
                    "help": "help",
                    "sub-commands": {
                        "build": {"help": "help"},
                        "init": {"help": "help"},
                    },
                }
            },
            "help": "help",
        },
    }
    assert model_actions.is_valid_subcommand_model(model["gdk"]["sub-commands"])


def test_is_valid_subcommand_model_valid_without_help():
    # Valid subcommand without help in the cli model.
    model = {
        "gdk": {
            "sub-commands": {
                "component": {
                    "help": "help",
                    "sub-commands": {
                        "build": {},
                        "init": {},
                    },
                }
            },
            "help": "help",
        },
    }
    assert not model_actions.is_valid_subcommand_model(model["gdk"]["sub-commands"])


def test_is_valid_model_call_counts(mocker):
    valid_model = {
        "gdk": {
            "sub-commands": {
                "component": {
                    "sub-commands": {
                        "init": {
                            "arguments": {
                                "lang": {"name": ["-l", "--lang"], "help": "help"},
                                "temp": {"name": ["-t", "--temp"], "help": "help"},
                            },
                            "arg_groups": [
                                {
                                    "title": "Greengrass component templates.",
                                    "args": ["lang"],
                                    "description": "description",
                                }
                            ],
                            "help": "help",
                        },
                        "build": {"help": "help"},
                    },
                    "help": "help",
                },
            },
            "help": "help",
        }
    }
    spy_is_valid_argument_model = mocker.spy(model_actions, "is_valid_argument_model")

    spy_is_valid_argument_group_model = mocker.spy(model_actions, "is_valid_argument_group_model")
    spy_is_valid_sub_command = mocker.spy(model_actions, "is_valid_subcommand_model")
    assert model_actions.is_valid_model(valid_model, consts.cli_tool_name)
    assert spy_is_valid_argument_model.call_count == 2
    assert spy_is_valid_argument_group_model.call_count == 1
    assert spy_is_valid_sub_command.call_count == 2


def test_is_valid_model_invalid_argument_model(mocker):
    invalid_model = {
        "gdk": {
            "sub-commands": {
                "component": {
                    "sub-commands": {
                        "init": {
                            "arguments": {
                                "lang": {"name": ["-l", "--lang"]},
                                "temp": {"name": ["-t", "--temp"]},
                            },
                            "arg_groups": [
                                {
                                    "title": "title",
                                    "args": ["lang"],
                                    "description": "description",
                                }
                            ],
                            "help": "help",
                        },
                    },
                    "help": "help",
                }
            },
            "help": "help",
        },
    }

    spy_is_valid_argument_model = mocker.spy(model_actions, "is_valid_argument_model")

    spy_is_valid_argument_group_model = mocker.spy(model_actions, "is_valid_argument_group_model")
    spy_is_valid_sub_command = mocker.spy(model_actions, "is_valid_subcommand_model")
    assert not model_actions.is_valid_model(invalid_model, consts.cli_tool_name)
    assert spy_is_valid_argument_model.call_count == 1
    assert spy_is_valid_argument_group_model.call_count == 0
    assert spy_is_valid_sub_command.call_count == 2  # gdk, component


def test_is_valid_model_invalid_argument_group_model(mocker):
    valid_model = {
        "gdk": {
            "sub-commands": {
                "init": {
                    "arguments": {
                        "lang": {"name": ["-l", "--lang"], "help": "help"},
                        "temp": {"name": ["-t", "--temp"], "help": "help"},
                    },
                    "arg_groups": [
                        {
                            "title": "Greengrass component templates.",
                            "args": ["lang", "template"],
                            "description": "description",
                        }
                    ],
                    "help": "help",
                },
                "build": {"help": "help"},
            },
            "help": "help",
        }
    }
    spy_is_valid_argument_model = mocker.spy(model_actions, "is_valid_argument_model")

    spy_is_valid_argument_group_model = mocker.spy(model_actions, "is_valid_argument_group_model")
    spy_is_valid_sub_command = mocker.spy(model_actions, "is_valid_subcommand_model")
    assert not model_actions.is_valid_model(valid_model, consts.cli_tool_name)
    assert spy_is_valid_argument_model.call_count == 2
    assert spy_is_valid_argument_group_model.call_count == 1
    assert spy_is_valid_sub_command.call_count == 1  # gdk


def test_is_valid_model_invalid_sub_commands(mocker):
    valid_model = {
        "gdk": {
            "sub-commands": {
                "component": {
                    "sub-commands": {
                        "init": {
                            "arguments": {
                                "lang": {"name": ["-l", "--lang"], "help": "help"},
                                "temp": {"name": ["-t", "--temp"], "help": "help"},
                            },
                            "arg_groups": [
                                {
                                    "title": "Greengrass component templates.",
                                    "args": ["lang", "temp"],
                                    "description": "description",
                                }
                            ],
                            "help": "help",
                        },
                        "not-valid": {},
                        "build": {"help": "help"},
                    },
                    "help": "help",
                }
            },
            "help": "help",
        },
    }
    spy_is_valid_argument_model = mocker.spy(model_actions, "is_valid_argument_model")

    spy_is_valid_argument_group_model = mocker.spy(model_actions, "is_valid_argument_group_model")
    spy_is_valid_sub_command = mocker.spy(model_actions, "is_valid_subcommand_model")
    assert not model_actions.is_valid_model(valid_model, consts.cli_tool_name)
    assert spy_is_valid_argument_model.call_count == 2
    assert spy_is_valid_argument_group_model.call_count == 1
    assert spy_is_valid_sub_command.call_count == 2  # gdk, component


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

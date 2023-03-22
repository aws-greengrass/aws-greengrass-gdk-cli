import json

import jsonschema

import gdk.common.consts as consts
import gdk.common.model_actions as model_actions
import gdk.common.utils as utils

cli_model_schema = "cli_model_schema.json"


def test_is_valid_model():
    # Integ test for validating the cli model with arguments, commands and sub-commands.
    model = model_actions.get_validated_model()
    assert model_actions.is_valid_model(model, consts.cli_tool_name)


def test_get_static_file_path_cli_model():
    # Integ test for the existence of command model file even before building the cli tool.
    model_file_path = utils.get_static_file_path(consts.cli_model_file)
    model_schema_file_path = utils.get_static_file_path(cli_model_schema)
    assert model_file_path is not None
    assert model_schema_file_path is not None
    assert model_file_path.exists()
    assert model_schema_file_path.exists()


def test_model_existence(mocker):
    # Integ test for validating the cli model type
    command_model = model_actions.get_validated_model()
    assert type(command_model) == dict  # Command model obtained should always be a dictionary
    assert len(command_model) > 0  # Command model is never empty
    assert consts.cli_tool_name in command_model  # Command model should contain the name of CLI as a key


def test_cli_model(mocker):
    # Integ test for validating the cli model type
    with open(utils.get_static_file_path(consts.cli_model_file), "r") as config_file:
        cli_data = json.loads(config_file.read())

    with open(utils.get_static_file_path(cli_model_schema), "r") as schemaFile:
        schema = json.loads(schemaFile.read())
    jsonschema.validate(cli_data, schema)


def test_is_valid_model_without_help_in_command():
    # Invalid model without help for commands
    valid_model = {
        "gdk": {"sub-commands": ["component"]},
        "component": {"sub-commands": ["init", "build"]},
        "init": {"arguments": {"lang": {"name": ["-l", "--lang"], "help": "help"}}},
        "build": {},
    }
    assert not model_actions.is_valid_model(valid_model, consts.cli_tool_name)


def test_is_valid_model_with_invalid_argument():
    # Invalid model with incorrect sub-commands. Subcommand with no key in the cli model.
    invalid_model_without_name_in_args = {
        "gdk": {
            "sub-commands": ["component"],
            "arguments": {"lang": {"names": ["-l", "--lang"], "help": "help"}},
            "help": "help",
        },
        "component": {"help": "help"},
    }
    assert not model_actions.is_valid_model(invalid_model_without_name_in_args, consts.cli_tool_name)


def test_is_valid_model_with_invalid_sub_command():
    # Invalid model with incorrect sub-commands. Subcommand with no key in the cli model.
    invalid_model_subcommands = {
        "gdk": {"sub-commands": ["component", "invalid-sub-command"]},
        "component": {},
    }
    assert not model_actions.is_valid_model(invalid_model_subcommands, consts.cli_tool_name)


def test_is_valid_model_with_invalid_arg_group_missing_title():
    # Valid model with correct args ang sub-commands.
    invalid_model = {
        "gdk": {
            "sub-commands": {
                "component": {
                    "sub-commands": {
                        "init": {
                            "arguments": {"lang": {"name": ["-l", "--lang"], "help": "help"}},
                            "arg_groups": [
                                {
                                    "args": ["lang"],
                                    "description": "description",
                                }
                            ],
                            "help": "help",
                        },
                        "build": {"help": "help"},
                    },
                    "help": "help",
                }
            },
            "help": "help",
        },
    }
    assert not model_actions.is_valid_model(invalid_model, consts.cli_tool_name)


def test_is_valid_model_with_invalid_arg_group_missing_arg():
    # Valid model with correct args ang sub-commands.
    invalid_model = {
        "gdk": {
            "sub-commands": {
                "component": {
                    "sub-commands": {
                        "init": {
                            "arguments": {"lang": {"name": ["-l", "--lang"], "help": "help"}},
                            "arg_groups": [
                                {
                                    "title": "title",
                                    "args": ["lang", "template"],
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

    assert not model_actions.is_valid_model(invalid_model, consts.cli_tool_name)


def test_is_valid_model_with_valid_cli_model():
    # Valid model with correct args ang sub-commands.
    valid_model = {
        "gdk": {
            "sub-commands": {
                "component": {
                    "sub-commands": {
                        "init": {
                            "arguments": {"lang": {"name": ["-l", "--lang"], "help": "help"}},
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

    assert model_actions.is_valid_model(valid_model, consts.cli_tool_name)

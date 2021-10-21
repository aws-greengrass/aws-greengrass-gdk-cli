import greengrassTools.common.consts as consts
import greengrassTools.common.model_actions as model_actions


def test_model_existence(mocker):
    # Integ test for the existence of command model file even before building the cli tool.
    command_model = model_actions.get_validated_model()
    assert type(command_model) == dict  # Command model obtained should always be a dictionary
    assert len(command_model) > 0  # Command model is never empty
    assert consts.cli_tool_name in command_model  # Command model should contain the name of CLI as a key


def test_get_validated_model_with_valid_model(mocker):
    # Should return model when the model is valid
    mocker.patch("greengrassTools.common.model_actions.is_valid_model", return_value=True)
    command_model = model_actions.get_validated_model()
    assert command_model


def test_get_validated_model_with_invalid_model(mocker):
    # Should return empty model when the model is invalid
    mocker.patch("greengrassTools.common.model_actions.is_valid_model", return_value=False)
    command_model = model_actions.get_validated_model()
    assert not command_model


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
        "init": {
            "arguments": [
                {
                    "name": ["-l", "--lang"],
                    "help": "language help",
                    "choices": ["p", "j"],
                },
                {"name": ["template"], "help": "template help"},
            ]
        },
        "build": {},
    }
    valid_model_subcommands = ["component"]
    assert model_actions.is_valid_subcommand_model(model, valid_model_subcommands)


def test_is_valid_subcommand_model_invalid():
    # Invalid subcommand with no key in the cli model.
    model = {
        "greengrass-tools": {"sub-commands": ["component"]},
        "component": {"sub-commands": ["init", "build"]},
        "init": {
            "arguments": [
                {
                    "name": ["-l", "--lang"],
                    "help": "language help",
                    "choices": ["p", "j"],
                },
                {"name": ["template"], "help": "template help"},
            ]
        },
        "build": {},
    }
    invalid_model_subcommands = [
        "component",
        "invalid-subcommand-that-is-not-present-as-key",
    ]
    assert not model_actions.is_valid_subcommand_model(model, invalid_model_subcommands)


def test_is_valid_model():
    # Valid model with correct args ang sub-commands.
    valid_model = {
        "greengrass-tools": {"sub-commands": ["component"]},
        "component": {"sub-commands": ["init", "build"]},
        "init": {
            "arguments": [
                {
                    "name": ["-l", "--lang"],
                    "help": "language help",
                    "choices": ["p", "j"],
                },
                {"name": ["template"], "help": "template help"},
            ]
        },
        "build": {},
    }
    assert model_actions.is_valid_model(valid_model, consts.cli_tool_name)


def test_is_valid_model_without_name():
    # Invalid model with incorrect arguments. Argument without name.
    invalid_model_without_name_in_args = {
        "greengrass-tools": {
            "sub-commands": ["component"],
            "arguments": [{"names": ["-l", "--lang"], "help": "help"}],
        },
        "component": {},
    }
    assert not model_actions.is_valid_model(invalid_model_without_name_in_args, consts.cli_tool_name)


def test_is_valid_model_without_help():
    # Invalid model with incorrect arguments. Argument without help.
    invalid_model_args_without_help = {
        "greengrass-tools": {
            "sub-commands": ["component"],
            "arguments": [{"name": ["-l", "--lang"], "helper": "help"}],
        },
        "component": {},
    }
    assert not model_actions.is_valid_model(invalid_model_args_without_help, consts.cli_tool_name)


def test_is_valid_model_without_invalid_sub_command():
    # Invalid model with incorrect sub-commands. Subcommand with no key in the cli model.
    invalid_model_subcommands = {
        "greengrass-tools": {"sub-commands": ["component", "invalid-sub-command"]},
        "component": {},
    }
    assert not model_actions.is_valid_model(invalid_model_subcommands, consts.cli_tool_name)

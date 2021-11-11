import json

import greengrassTools.common.consts as consts
import greengrassTools.common.exceptions.error_messages as error_messages
import greengrassTools.common.utils as utils


def is_valid_model(cli_model, command):
    """
    Validates CLI model of arguments and subcommands at the specified command level.

    Parameters
    ----------
      cli_model(dict): A dictonary object which contains CLI arguments and sub-commands at each command level.
      command(string): Command in the cli_model which is used to validate args and subcommands at its level.

    Returns
    -------
      (bool): Returns True when the cli model is valid else False.
    """
    if command not in cli_model:
        return False
    else:
        # Validate args
        if "arguments" in cli_model[command]:
            for arg_name in cli_model[command]["arguments"]:
                argument = cli_model[command]["arguments"][arg_name]
                if not is_valid_argument_model(argument):
                    return False

        # Validate sub-commands
        if "sub-commands" in cli_model[command]:
            if not is_valid_subcommand_model(cli_model, cli_model[command]["sub-commands"]):
                return False
    return True


def is_valid_argument_model(argument):
    """
    Validates CLI model specified argument level.

    With this validation, every argument is mandated to have name and help at the minimum.
    Any other custom validation to the arguments can go here.

    Parameters
    ----------
      argument(dict): A dictonary object which argument parameters.
                      Full list: greengrassTools.common.consts.arg_parameters

    Returns
    -------
      (bool): Returns True when the argument is valid else False.
    """
    if "name" not in argument or "help" not in argument:
        return False
    # Add custom validation for args if needed.
    return True


def is_valid_subcommand_model(cli_model, subcommands):
    """
    Validates CLI model specified subcommand level.

    With this validation, every subcommand is mandated to be present as an individual key in the cli_model.

    Parameters
    ----------
      cli_model(dict): A dictonary object which contains CLI arguments and sub-commands at each command level.
      subcommands(list): List of subcommands of a command.

    Returns
    -------
      (bool): Returns True when the subcommand is valid else False.
    """
    for subc in subcommands:
        if not is_valid_model(cli_model, subc):
            return False
    return True


def get_validated_model():
    """
    This function loads the cli model json file from static location as a dict and validates it.

    Parameters
    ----------
      None

    Returns
    -------
      cli_model(dict): Empty if the model is invalid otherwise returns cli model.
    """
    model_file = utils.get_static_file_path(consts.cli_model_file)
    if model_file:
        with open(model_file) as f:
            cli_model = json.loads(f.read())
            if is_valid_model(cli_model, consts.cli_tool_name):
                return cli_model
            raise Exception(error_messages.INVALID_CLI_MODEL)
    raise Exception(error_messages.CLI_MODEL_FILE_NOT_EXISTS)

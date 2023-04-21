import json

import gdk.common.consts as consts
import gdk.common.utils as utils


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
    if command not in cli_model or "help" not in cli_model[command]:
        return False

    if "arguments" in cli_model[command]:
        arguments = cli_model[command]["arguments"]
        for arg_name in arguments:
            if not is_valid_argument_model(arguments[arg_name]):
                return False
        # Validate arg groups
        if "arg_groups" in cli_model[command]:
            for arg_group in cli_model[command]["arg_groups"]:
                if not is_valid_argument_group_model(arg_group, arguments):
                    return False

    # Validate sub-commands
    if "sub-commands" in cli_model[command]:
        if not is_valid_subcommand_model(cli_model[command]["sub-commands"]):
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
                      Full list: gdk.common.consts.arg_parameters

    Returns
    -------
      (bool): Returns True when the argument is valid else False.
    """
    if "name" not in argument or "help" not in argument:
        return False
    # Add custom validation for args if needed.
    return True


def is_valid_subcommand_model(cli_model):
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
    for subc in cli_model:
        if not is_valid_model(cli_model, subc):
            return False
    return True


def is_valid_argument_group_model(arg_group, arguments):
    """
    Validates CLI model at specified argument group level.

    With this validation, every argument group is mandated to have title, description and arguments that go as a group.

    Parameters
    ----------
      arg_group(dict): A dictonary object which contains argument group at a command level.
      arguments(dict): A dictonary object which contains all arguments at a command level.

    Returns
    -------
      (bool): Returns True when the argument group is valid. Else False.
    """

    # Every argument group should have title, description and args that go in a group
    if "title" not in arg_group or "description" not in arg_group or "args" not in arg_group:
        return False

    # Args of a group must be there in args of the command
    for arg in arg_group["args"]:
        if arg not in arguments:
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
    with open(model_file) as f:
        cli_model = json.loads(f.read())
        return cli_model

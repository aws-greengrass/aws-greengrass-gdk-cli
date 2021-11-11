import logging

import greengrassTools.CLIParser
import greengrassTools.commands.methods as command_methods
import greengrassTools.common.consts as consts


def run_command(args_namespace):
    """
    Performs appropriate action based on the namespace args.

    Parameters
    ----------
      args_namespace(argparse.NameSpace): An object holding attributes from parsed command.

    Returns
    -------
      None
    """
    d_args = vars(args_namespace)  # namespace as dictionary
    if "debug" in d_args and d_args["debug"]:
        logging.info("Setting command output mode to DEBUG.")
        logging.getLogger().setLevel(logging.DEBUG)
    method_name = get_method_from_command(d_args, consts.cli_tool_name, "")
    if method_name:
        call_action_by_name(method_name, d_args)


def call_action_by_name(method_name, d_args):
    """
    Identifies the method for given method name based on namespace and executes the method

    Since method names cannot have "-" and "greengrass-tools" contain a "-", we substitute
    "greengrass-tools" with "greengrass_tools"

    Parameters
    ----------
      method_name(string): Method name determined from the args namespace.
      d_args(dict): A dictionary object that contains parsed args namespace is passed to
                    appropriate action.

    Returns
    -------
      None
    """
    method_name = method_name.replace(consts.cli_tool_name, consts.cli_tool_name_in_method_names)
    method_to_call = getattr(command_methods, method_name, None)
    if method_to_call:
        logging.debug("Calling '{}'.".format(method_name))
        method_to_call(d_args)
    else:
        raise Exception("{} does not support the given command.".format(consts.cli_tool_name))


def get_method_from_command(d_args, command, method_name):
    """
    A recursive function that builds the method_name from the command.

    'greengrass-tools component init --lang python --template template-name'
    When the above command is parsed(parse_args), the following namespace is returned.
    Namespace(greengrass-tools='component', foo=None, component='init', init=None, lang='python', template='template-name')
    where,
    greengrass-tools -> component, component -> init, init -> None and we derive the method name from this as
    '_greengrass-tools_component_init'

    Parameters
    ----------
      d_args(dict): A dictionary object that contains parsed args namespace of a command.
      command(string): Command from the namespace that is appended to method name and is used to determine its subcommand
      method_name(string): Method name determined from the args namespace.

    Returns
    -------
      method_name(string): Method name determined from the args namespace. None if the command is invalid
    """
    method_name = "{}_{}".format(method_name, command)
    if command and command in d_args:
        if d_args[command] is None:
            return method_name
        return get_method_from_command(d_args, d_args[command], method_name)


def conflicting_arg_groups(command_args, command):
    """
    Checks if the command namespace provided to the parser has conflicting arguments

    Parameters
    ----------
      command_args(dict): A dictionary object that contains parsed args namespace.
      command(string): Last part of the command in namespace that contains arguments(which may conflict)

    Returns
    -------
      (bool) Returns True if the command arguments conflict. Else False.
    """
    cli_model = greengrassTools.CLIParser.cli_tool.cli_model
    conf_args_dict = _dic_of_conflicting_args(cli_model, command)
    logging.debug("Checking if arguments in the command conflict.")
    return check_command_args_with_conflicting_args(command_args, conf_args_dict)


def check_command_args_with_conflicting_args(command_args, conf_args_dict):
    """
    Checks if the command namespace provided to the parser has conflicting arguments by using the conflicting
    arguments provided in the cli model file.

    Parameters
    ----------
      command_args(dict): A dictionary object that contains parsed args namespace of a command.
      conf_args_dict(dict): A dictionary object formed that's formed with argument as a key and
                           a set of its non-conflicting args as value.

    Returns
    -------
      (bool) Returns True if the command arguments conflict. Else False.
    """
    command_arg_keys = _list_of_command_args(command_args, conf_args_dict)
    for i in range(len(command_arg_keys)):
        for j in range(i + 1, len(command_arg_keys)):
            if command_arg_keys[i] in conf_args_dict and command_arg_keys[j] in conf_args_dict:
                if command_arg_keys[j] not in conf_args_dict[command_arg_keys[i]]:
                    logging.error(
                        "Arguments '{}' and '{}' cannot be used together in the command.".format(
                            command_arg_keys[i], command_arg_keys[j]
                        )
                    )
                    return True
    return False


def _list_of_command_args(command_args, conf_args_dict):
    """
    Creates a reduced list of argument-only commands from the namespace args dictionary by removing both
    non-argument commands and None arguments from the namespace args.

    Parameters
    ----------
      command_args(dict): A dictionary object that contains parsed args namespace of a command.
      conf_args_dict(dict): A dictionary object formed that's formed with argument as a key and
                           a set of its non-conflicting args as value.

    Returns
    -------
      command_arg_keys_as_list(list): Modified list of command keys in the namespace.
    """
    command_arg_keys_as_list = []
    for k, v in command_args.items():
        if k in conf_args_dict and v is not None:
            command_arg_keys_as_list.append(k)
    return command_arg_keys_as_list


def _dic_of_conflicting_args(cli_model, command):
    """
    Creates a dictionary object with argument as a key and a set of its non-conflicting args as value.

    Parameters
    ----------
      cli_model(dict): A dictonary object which contains CLI arguments and sub-commands at each command level.
      command(string): Last part of the command in namespace that contains arguments(which may conflict)

    Returns
    -------
      conf_args_dict(dict): A dictionary object formed that's formed with argument as a key and
                           a set of its non-conflicting args as value.
    """
    conf_args_dict = {}
    if command in cli_model and "conflicting_arg_groups" in cli_model[command]:
        c_arg_groups = cli_model[command]["conflicting_arg_groups"]
        for c_group in c_arg_groups:
            for c_arg in c_group:
                c_arg_set = conf_args_dict.get(c_arg, set())
                c_arg_set.update(set(c_group))
                conf_args_dict[c_arg] = c_arg_set
    return conf_args_dict

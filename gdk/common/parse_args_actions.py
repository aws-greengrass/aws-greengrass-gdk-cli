import logging

import gdk.CLIParser
import gdk.commands.methods as command_methods
import gdk.common.consts as consts


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

    Parameters
    ----------
      method_name(string): Method name determined from the args namespace.
      d_args(dict): A dictionary object that contains parsed args namespace is passed to
                    appropriate action.

    Returns
    -------
      None
    """
    method_name = method_name.replace("-", "_hyphen_")
    method_to_call = getattr(command_methods, method_name, None)
    if method_to_call:
        logging.debug("Calling '{}'.".format(method_name))
        method_to_call(d_args)
    else:
        gdk.CLIParser.cli_parser.error(
            f"{consts.cli_tool_name}-v{gdk.CLIParser.utils.cli_version} does not support the given command."
        )


def get_method_from_command(d_args, command, method_name):
    """
    A recursive function that builds the method_name from the command.

    'gdk component init --lang python --template template-name'
    When the above command is parsed(parse_args), the following namespace is returned.
    Namespace(gdk='component', foo=None, component='init', init=None, lang='python', template='template-name')
    where,
    gdk -> component, component -> init, init -> None and we derive the method name from this as
    '_gdk_component_init'

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

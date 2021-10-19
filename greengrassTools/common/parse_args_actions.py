import greengrassTools.commands.methods as command_methods
import greengrassTools.common.consts as consts

def run_command(args_namespace):
    """ 
    Based on the namespace, appropriate action is determined and called by its name.  

    Parameters
    ----------
      args_namespace(argparse.NameSpace): An object holding attributes from parsed command.

    Returns
    -------
      None
    """
    d_args = vars(args_namespace) # args as dictionary
    method_name = get_method_from_command(d_args, consts.cli_tool_name, "") 
    call_action_by_name(method_name, d_args)

def call_action_by_name(method_name, d_args):
    """
    Method name determined from the namespace is modified to choose and call actual method by its name. 

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
    method_to_call = getattr(command_methods, method_name)
    method_to_call(d_args)

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
      method_name(string): Method name determined from the args namespace.
    """
    method_name = "{}_{}".format(method_name,command)
    if d_args[command] == None: 
        return method_name
    else:
        return get_method_from_command(d_args, d_args[command], method_name)



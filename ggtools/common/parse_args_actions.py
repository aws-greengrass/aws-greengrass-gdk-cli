
import ggtools.commands.methods as command_methods
import ggtools.common.consts as consts

def run_command(args):
    """
    This method takes in the parsed args from command and calls appropriate action based on that.
    """
    d_args = vars(args) # args as dictionary
    method_name = get_method_from_command(d_args, consts.cli_tool_name, "") 
    call_action_by_name(method_name, d_args)

def call_action_by_name(method_name, d_args):
    """
    This calls the method for execution by its name.
    """
    method_to_call = getattr(command_methods, method_name)
    method_to_call(d_args)

def get_method_from_command(d_args, command, method_name):
    """
    :return :  
    "ggt component init --lang python --template template-name"

    When the above command is parsed(parse_args), the following namespace is returned. 

    Namespace(ggt='component', foo=None, component='init', init=None, lang='python', template='template-name')
    where, 

    ggt -> component, component -> init, init -> None and we derive the method name from this as 
    '_ggt_component_init'

    """
    method_name = "{}_{}".format(method_name,command)
    if d_args[command] == None: 
        return method_name
    else:
        return get_method_from_command(d_args, d_args[command], method_name)

import argparse

import greengrassTools.common.parse_args_actions as parse_args_actions
import greengrassTools.common.consts as consts
import greengrassTools.common.model_actions as model_actions

class CLIParser:
  def __init__(self, command, top_level_parser):
    """ A class that represents an argument parser at command level."""
    self.command = command
    if command != consts.cli_tool_name:
      self.top_level_parser=top_level_parser
      self.parser=self.top_level_parser.add_parser(command, help='{} help'.format(command))
    else:
      self.parser=argparse.ArgumentParser(prog=consts.cli_tool_name)
    self.subparsers=self.parser.add_subparsers(dest=command, help='{} help'.format(command))
    
  def create_parser(self, cli_model):
    """ 
    Creates a parser with arguments and subcommands at specified command level and returns it. 

    Parameters
    ----------
      cli_model(dict): A dictonary object which contains CLI arguments and sub-commands at each command level.

    Returns
    -------
      parser(argparse.ArgumentParser): ArgumentParser object which can parse args at its command level.
    """
    if self.command in cli_model:
      self.command_model = cli_model[self.command]
      self._add_arguments()
      self._get_subcommands_from_model(cli_model)
    return self.parser
    
  def _add_arguments(self):
    """ 
    Adds command-line argument to the parser to define how it should be parsed from commandline. 
  
    Retrieves and passes positionl/optional args along with all other parameters as kwargs from the 
    provided at each command level.

    Parameters
    ----------
      None

    Returns
    -------
      None
    """  
    if "arguments" in self.command_model:
      arguments = self.command_model["arguments"]
      for argument in arguments:
        name, other_args=self._get_arg_from_model(argument)
        if len(name)==2: # For optional args
          self.parser.add_argument(name[0],name[1], **other_args)
        elif len(name) == 1:  # For positional args
          self.parser.add_argument(name[0], **other_args)

  def _get_subcommands_from_model(self, cli_model):
    """ 
    Creates a subparser for every subcommand of a command.
  
    Retrieves and passes positionl/optional args along with all other parameters as kwargs from the 
    provided at each command level.

    Parameters
    ----------
      cli_model(dict): A dictonary object which contains CLI arguments and sub-commands at each command level.

    Returns
    -------
      None
    """  

    if "sub-commands" in self.command_model:
      sub_commands=self.command_model["sub-commands"]
      for sub_command in sub_commands:
        CLIParser(sub_command, self.subparsers).create_parser(cli_model)

  def _get_arg_from_model(self,argument):
    """ 
    Creates parameters of parser.add_argument from the argument in cli_model. 

    Parameters
    ----------
      argument(dict): A dictonary object which argument parameters.  
                      Full list: greengrassTools.common.consts.arg_parameters

    Returns
    -------
      argument["name"](list): List of all optional and positional argument parameters 
      modified_arg(dict): A dictionary object with all other parameters that 'argument' param has.
    """  
    modified_arg={}
    for param in consts.arg_parameters:
      if param in argument and param!="name":
        modified_arg[param]=argument[param]
    return argument["name"],modified_arg 

def main():
  cli_tool=CLIParser(consts.cli_tool_name, None)
  cli_model = model_actions.get_validated_model()
  if cli_model:
    cli_parser=cli_tool.create_parser(cli_model)
    args_namespace=cli_parser.parse_args()
    parse_args_actions.run_command(args_namespace)
  else: 
    print("Please provide a valid model to create a CLI parser")
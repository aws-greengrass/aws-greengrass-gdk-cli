import argparse
import logging

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
    self.parser.add_argument("-d", "--debug", help="Increase command output to debug level", action="store_true")
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
      added_args={}
      # Add arguments in groups first
      if "arg_groups" in self.command_model:
        for arg_group in self.command_model["arg_groups"]:
          group_description = arg_group["description"]
          group_title = arg_group["title"]
          group = self.parser.add_argument_group(title=group_title, description = group_description)
          for arg in arg_group["args"]:
            if arg not in added_args:
              if self._add_arg_to_group_or_parser(arguments[arg],group):
                added_args[arg] = True

        # Add individual args that are not part of groups. Skip if they're already added.
        for arg in arguments:
            if arg not in added_args:
              if self._add_arg_to_group_or_parser(arguments[arg], None):
                added_args[arg] = True

  def _add_arg_to_group_or_parser(self, argument, group):
    """ 
    Adds argument to either group or command level parser based on group parameter.

    Parameters
    ----------
      argument(dict): A dictonary object which argument parameters.  
                      Full list: greengrassTools.common.consts.arg_parameters
      group(Argument group obect): Argument group object created for each group of arguments that go together.

    Returns
    -------
      (bool): Return True if the argument is added to the group or parser.
    """  
    if group:
      parser = group
    else:
      parser = self.parser
    name, other_args=self._get_arg_from_model(argument)
    if len(name)==2: # For optional args
      parser.add_argument(name[0],name[1], **other_args)
      return True
    elif len(name) == 1:  # For positional args
      parser.add_argument(name[0], **other_args)
      return True

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
  try: 
    args_namespace=cli_parser.parse_args()
    if args_namespace.debug:
      logging.basicConfig(level=logging.DEBUG, format=consts.log_format)
    else:
      logging.basicConfig(level=logging.INFO, format=consts.log_format)
    parse_args_actions.run_command(args_namespace)
  except Exception as e:
    print(e)

try: 
  cli_tool=CLIParser(consts.cli_tool_name, None)
  cli_model = model_actions.get_validated_model()
  cli_parser=cli_tool.create_parser(cli_model)
except Exception as e:
  print(e)
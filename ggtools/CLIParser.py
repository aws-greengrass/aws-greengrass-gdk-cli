import argparse

import ggtools.common.parse_args_actions as parse_args_actions
import ggtools.common.consts as consts
import ggtools.common.model_actions as model_actions

class CLIParser:
  def __init__(self, command, top_level_parser):
    self.command = command
    if command != consts.cli_tool_name:
      self.top_level_parser=top_level_parser
      self.parser=self.top_level_parser.add_parser(command, help='{} help'.format(command))
    else:
      self.parser=argparse.ArgumentParser(prog=consts.cli_tool_name)
    self.subparsers=self.parser.add_subparsers(dest=command, help='{} help'.format(command))
    
  def create_parser(self, cli_model):
    if self.command in cli_model:
      self.command_model = cli_model[self.command]
      self._add_arguments()
      self._get_subcommands_from_model(cli_model)
    return self.parser
    
  def _add_arguments(self):
    if "arguments" in self.command_model:
      arguments = self.command_model["arguments"]
      for argument in arguments:
        name, other_args=self._get_arg_from_model(argument)
        if len(name)==2: # For optional args
          self.parser.add_argument(name[0],name[1], **other_args)
        elif len(name) == 1:  # For positional args
          self.parser.add_argument(name[0], **other_args)

  def _get_subcommands_from_model(self, cli_model):
      if "sub-commands" in self.command_model:
        sub_commands=self.command_model["sub-commands"]
        for sub_command in sub_commands:
          CLIParser(sub_command, self.subparsers).create_parser(cli_model)

  def _get_arg_from_model(self,argument):
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
    args=cli_parser.parse_args()
    parse_args_actions.run_command(args)
  else: 
    print("Please provide a valid model to create a CLI parser")
import os
import json
import ggtools as ggt

def is_valid_model(cli_model, command):
  if command not in cli_model:
    return False
  else:
    # Validate args
    if "arguments" in cli_model[command]:
        for argument in cli_model[command]["arguments"]:
            if not is_valid_argument_model(argument):
                return False
                
    # Validate sub-commands
    if "sub-commands" in cli_model[command]:
        if not is_valid_subcommand_model(cli_model, cli_model[command]["sub-commands"]):
            return False
  return True

def is_valid_argument_model(arg):
    if "name" not in arg or "help" not in arg:
        return False
    # Add more custom validation for args 
    return True

def is_valid_subcommand_model(cli_model, subcommands):
    for subc in subcommands:
        if not is_valid_model(cli_model, subc):
            return False
    return True

def get_validated_model():
    cli_model_file = os.path.join(os.path.dirname(ggt.__file__),"static","cli_model.json")
    with open(cli_model_file) as f:
      cli_model = json.loads(f.read())
    if is_valid_model(cli_model, ggt.common.consts.cli_tool_name):
      return cli_model
    else:
      return {}



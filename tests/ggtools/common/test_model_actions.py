
import ggtools.common.model_actions as model_actions
import ggtools.common.consts as consts

def test_model_existence():
    """
    Test for the existence of command model file even before building the cli tool.
    """
    command_model = model_actions.get_validated_model()
    assert type(command_model) == dict # Command model obtained should always be a dictionary
    assert len(command_model)>0 # Command model is never empty
    assert consts.cli_tool_name in command_model # Command model should contain the name of CLI as a key

def test_is_valid_argument_model():

    """
    Case 1: Valid argument
    Case 2: Invalid arg without name
    Case 3: Invalid arg without help
    """
    valid_arg= {
                "name" : ["-l","--lang"],
                "help": "language help",
                "choices": ["p", "j"] }
    invalid_arg_without_name={'names': ['-l', '--lang'], 'help': 'help'}
    invalid_arg_without_help={'name': ['-l', '--lang'], 'helper': 'help'}

    # ## Case 1
    assert model_actions.is_valid_argument_model(valid_arg)

    # ## Case 2
    assert not model_actions.is_valid_model(invalid_arg_without_name, consts.cli_tool_name)

    # ## Case 3
    assert not model_actions.is_valid_model(invalid_arg_without_help, consts.cli_tool_name) 

def test_is_valid_subcommand_model():

    """
    Case 1: Valid subcommand
    Case 2: Invalid subcommand with no key 
    """

    model={'ggt': {'sub-commands': ['component']}, 'component': {'sub-commands': ['init', 'build']}, 'init': {'arguments': [{'name': ['-l', '--lang'], 'help': 'language help', 'choices': ['p', 'j']}, {'name': ['template'], 'help': 'template help'}]}, 'build': {}}
    valid_model_subcommands=['component']
    invalid_model_subcommands=['component','invalid-subcommand-that-is-not-present-as-key']
    
    ## Case 1
    assert model_actions.is_valid_subcommand_model(model, valid_model_subcommands)

    ## Case 2
    assert not model_actions.is_valid_subcommand_model(model, invalid_model_subcommands)

def test_is_valid_model():

    """
    Case 1: Valid model with correct args ang sub-commands
    Case 2: Invalid model with incorrect sub-commands
    Case 3: Invalid model with incorrect arguments
    """

    valid_model={'ggt': {'sub-commands': ['component']}, 'component': {'sub-commands': ['init', 'build']}, 'init': {'arguments': [{'name': ['-l', '--lang'], 'help': 'language help', 'choices': ['p', 'j']}, {'name': ['template'], 'help': 'template help'}]}, 'build': {}}
    invalid_model_subcommands={'ggt': {'sub-commands': ['component','invalid-sub-command']}, 'component': {}}
    invalid_model_args_without_name={'ggt': {'sub-commands': ['component'],'arguments':[{'names': ['-l', '--lang'], 'help': 'help'}]}, 'component': {}}
    invalid_model_args_without_help={'ggt': {'sub-commands': ['component'],'arguments':[{'name': ['-l', '--lang'], 'helper': 'help'}]}, 'component': {}}

    ## Case 1
    assert model_actions.is_valid_model(valid_model, consts.cli_tool_name)

    ## Case 2
    assert not model_actions.is_valid_model(invalid_model_subcommands, consts.cli_tool_name)

    ## Case 3
    assert not model_actions.is_valid_model(invalid_model_args_without_name, consts.cli_tool_name)
    assert not model_actions.is_valid_model(invalid_model_args_without_help, consts.cli_tool_name)
    

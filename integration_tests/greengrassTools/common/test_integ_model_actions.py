import greengrassTools.common.consts as consts
import greengrassTools.common.model_actions as model_actions
import greengrassTools.common.utils as utils


def test_is_valid_model():
    # Integ test for validating the cli model with arguments, commands and sub-commands.
    model = model_actions.get_validated_model()
    assert model_actions.is_valid_model(model, consts.cli_tool_name)


def test_get_static_file_path_cli_model():
    # Integ test for the existence of command model file even before building the cli tool.
    model_file_path = utils.get_static_file_path(consts.cli_model_file)
    assert model_file_path is not None
    assert model_file_path.exists()


def test_model_existence(mocker):
    # Integ test for validating the cli model type
    command_model = model_actions.get_validated_model()
    assert type(command_model) == dict  # Command model obtained should always be a dictionary
    assert len(command_model) > 0  # Command model is never empty
    assert consts.cli_tool_name in command_model  # Command model should contain the name of CLI as a key

from gdk.commands.config import config
from gdk.commands.config.ComponentCommand import ComponentCommand


def test_config_component(mocker):
    mock_config_component = mocker.patch.object(ComponentCommand, "__init__", return_value=None)
    mock_config_component_run = mocker.patch.object(ComponentCommand, "run", return_value=None)
    d_args = {}
    config.component(d_args)
    assert mock_config_component.call_count == 1
    assert mock_config_component_run.call_count == 1
    mock_config_component.assert_called_with(d_args)

import pytest
from gdk.commands.config import config
from gdk.commands.config.UpdateCommand import UpdateCommand


def test_config_update(mocker):
    mock_config_update = mocker.patch.object(UpdateCommand, "__init__", return_value=None)
    mock_config_update_run = mocker.patch.object(UpdateCommand, "run", return_value=None)
    d_args = {}
    config.update(d_args)
    assert mock_config_update.call_count == 1
    assert mock_config_update_run.call_count == 1
    mock_config_update.assert_called_with(d_args)


def test_config_update_exception(mocker):
    mock_config_update = mocker.patch.object(UpdateCommand, "__init__", side_effect=Exception("Error with update command"))
    mock_config_update_run = mocker.patch.object(UpdateCommand, "run", return_value=None)
    d_args = {"wrongargs": None}
    with pytest.raises(Exception) as e:
        config.update(d_args)
    assert "Error with update command" in e.value.args[0]
    assert mock_config_update.call_count == 1
    assert mock_config_update_run.call_count == 0
    mock_config_update.assert_called_with(d_args)

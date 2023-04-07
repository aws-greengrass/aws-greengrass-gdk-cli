import pytest
from gdk.commands.component import component
from gdk.commands.component.BuildCommand import BuildCommand
from gdk.commands.component.InitCommand import InitCommand
from gdk.commands.component.ListCommand import ListCommand
from gdk.commands.component.PublishCommand import PublishCommand
from gdk.common.exceptions.CommandError import ConflictingArgumentsError


def test_component_init(mocker):
    mock_component_init = mocker.patch.object(InitCommand, "__init__", return_value=None)
    mock_component_init_run = mocker.patch.object(InitCommand, "run", return_value=None)
    d_args = {"init": None}
    component.init(d_args)
    assert mock_component_init.call_count == 1
    assert mock_component_init_run.call_count == 1
    mock_component_init.assert_called_with(d_args)


def test_component_init_exception(mocker):
    mock_component_init = mocker.patch.object(InitCommand, "__init__", side_effect=ConflictingArgumentsError("a", "b"))
    mock_component_init_run = mocker.patch.object(InitCommand, "run", return_value=None)
    d_args = {"init": None}
    with pytest.raises(Exception) as e:
        component.init(d_args)
    assert "Arguments 'a' and 'b' are conflicting and cannot be used together in a command." in e.value.args[0]
    assert mock_component_init.call_count == 1
    assert mock_component_init_run.call_count == 0
    mock_component_init.assert_called_with(d_args)


def test_component_build(mocker):
    mock_component_build = mocker.patch.object(BuildCommand, "__init__", return_value=None)
    mock_component_build_run = mocker.patch.object(BuildCommand, "run", return_value=None)
    d_args = {"build": None}
    component.build(d_args)
    assert mock_component_build.call_count == 1
    assert mock_component_build_run.call_count == 1
    mock_component_build.assert_called_with(d_args)


def test_component_build_exception(mocker):
    mock_component_build = mocker.patch.object(BuildCommand, "__init__", side_effect=Exception("Error in build"))
    mock_component_build_run = mocker.patch.object(BuildCommand, "run", return_value=None)
    d_args = {"build": None}
    with pytest.raises(Exception) as e:
        component.build(d_args)
    assert "Error in build" in e.value.args[0]
    assert mock_component_build.call_count == 1
    assert mock_component_build_run.call_count == 0
    mock_component_build.assert_called_with(d_args)


def test_component_publish(mocker):
    mock_component_publish = mocker.patch.object(PublishCommand, "__init__", return_value=None)
    mock_component_publish_run = mocker.patch.object(PublishCommand, "run", return_value=None)
    d_args = {"publish": None}
    component.publish(d_args)
    assert mock_component_publish.call_count == 1
    assert mock_component_publish_run.call_count == 1
    mock_component_publish.assert_called_with(d_args)


def test_component_publish_exception(mocker):
    mock_component_publish = mocker.patch.object(PublishCommand, "__init__", side_effect=Exception("Error in publish"))
    mock_component_publish_run = mocker.patch.object(PublishCommand, "run", return_value=None)
    d_args = {"publish": None}
    with pytest.raises(Exception) as e:
        component.publish(d_args)
    assert "Error in publish" in e.value.args[0]
    assert mock_component_publish.call_count == 1
    assert mock_component_publish_run.call_count == 0
    mock_component_publish.assert_called_with(d_args)


def test_component_list(mocker):
    mock_component_list = mocker.patch.object(ListCommand, "__init__", return_value=None)
    mock_component_list_run = mocker.patch.object(ListCommand, "run", return_value=None)
    d_args = {"list": None}
    component.list(d_args)
    assert mock_component_list.call_count == 1
    assert mock_component_list_run.call_count == 1
    mock_component_list.assert_called_with(d_args)


def test_component_list_exception(mocker):
    mock_component_list = mocker.patch.object(ListCommand, "__init__", side_effect=Exception("Error in list"))
    mock_component_list_run = mocker.patch.object(ListCommand, "run", return_value=None)
    d_args = {"list": None}
    with pytest.raises(Exception) as e:
        component.list(d_args)
    assert "Error in list" in e.value.args[0]
    assert mock_component_list.call_count == 1
    assert mock_component_list_run.call_count == 0
    mock_component_list.assert_called_with(d_args)

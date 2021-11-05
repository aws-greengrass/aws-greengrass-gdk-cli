from greengrassTools.commands.component import component
import greengrassTools.commands.methods as methods

def test_greengrass_tools_component_init(mocker):
    mock_component_init = mocker.patch(
        "greengrassTools.commands.component.component.init", 
        return_value=None)
    methods._greengrass_tools_component_init({})
    assert mock_component_init.call_count == 1

def test_greengrass_tools_component_build(mocker):
    mock_component_build = mocker.patch(
    "greengrassTools.commands.component.component.build", 
    return_value=None)
    methods._greengrass_tools_component_build({})
    assert mock_component_build.call_count == 1

def test_greengrass_tools_component_publish(mocker):
    mock_component_publish = mocker.patch(
    "greengrassTools.commands.component.component.publish", 
    return_value=None)
    methods._greengrass_tools_component_publish({})
    assert mock_component_publish.call_count == 1

def test_greengrass_tools_component_list(mocker):
    mock_component_list = mocker.patch(
        "greengrassTools.commands.component.component.list", 
        return_value=None)
    methods._greengrass_tools_component_list({})
    assert mock_component_list.call_count == 1

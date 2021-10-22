from greengrassTools.commands.component import component
# import greengrassTools.commands.methods as methods

def test_component_init(mocker):
    mock_component_init = mocker.patch(
        "greengrassTools.commands.component.init.run", 
        return_value=None)
    d_args={"init":None}
    component.init(d_args)
    assert mock_component_init.call_count == 1
    mock_component_init.assert_called_with(d_args)

def test_component_build(mocker):
    mock_component_build = mocker.patch(
    "greengrassTools.commands.component.build.run", 
    return_value=None)
    d_args={"init":None}
    component.build(d_args)

    assert mock_component_build.call_count == 1
    mock_component_build.assert_called_with(d_args)

def test_component_publish(mocker):
    mock_component_publish = mocker.patch(
    "greengrassTools.commands.component.publish.run", 
    return_value=None)
    d_args={"init":None}
    component.publish(d_args)
    assert mock_component_publish.call_count == 1
    mock_component_publish.assert_called_with(d_args)
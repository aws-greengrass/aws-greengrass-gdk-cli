import gdk.commands.methods as methods


def test_gdk(mocker):
    mock_component_init = mocker.patch("gdk.CLIParser.cli_parser.print_help", return_value=None)
    methods._gdk({"gdk": None})
    assert mock_component_init.call_count == 1


def test_gdk_component_init(mocker):
    mock_component_init = mocker.patch("gdk.commands.component.component.init", return_value=None)
    methods._gdk_component_init({})
    assert mock_component_init.call_count == 1


def test_gdk_component_build(mocker):
    mock_component_build = mocker.patch("gdk.commands.component.component.build", return_value=None)
    methods._gdk_component_build({})
    assert mock_component_build.call_count == 1


def test_gdk_component_publish(mocker):
    mock_component_publish = mocker.patch("gdk.commands.component.component.publish", return_value=None)
    methods._gdk_component_publish({})
    assert mock_component_publish.call_count == 1


def test_gdk_component_list(mocker):
    mock_component_list = mocker.patch("gdk.commands.component.component.list", return_value=None)
    methods._gdk_component_list({})
    assert mock_component_list.call_count == 1


def test_gdk_config_update(mocker):
    mock_config_update = mocker.patch("gdk.commands.config.config.update", return_value=None)
    methods._gdk_config_update({})
    assert mock_config_update.call_count == 1

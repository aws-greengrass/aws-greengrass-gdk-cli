def test_list_template(gdk_cli):
    check_list_template = gdk_cli.run(["component", "list", "--template"])
    assert "HelloWorld-python" in check_list_template.output
    assert "HelloWorld-java" in check_list_template.output


def test_list_repository(gdk_cli):
    check_list_template = gdk_cli.run(["component", "list", "--repository"])
    assert "aws-greengrass-labs-database-influxdb" in check_list_template.output


def test_list_incomplete_args(gdk_cli):
    check_list_template = gdk_cli.run(["component", "list"])
    assert check_list_template.returncode == 1
    assert "Could not list the components as the command arguments are invalid." in check_list_template.output

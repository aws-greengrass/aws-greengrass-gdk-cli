def test_list_template(gdk_cli):
    check_list_template = gdk_cli.run(["component", "list", "--template"])
    assert "HelloWorld-python" in check_list_template.output
    assert "HelloWorld-java" in check_list_template.output


def test_list_repository(gdk_cli):
    check_list_template = gdk_cli.run(["component", "list", "--repository"])
    assert "aws-greengrass-labs-database-influxdb" in check_list_template.output

import subprocess as sp


def test_list_template():
    check_list_template = sp.run(["gdk", "component", "list", "--template"], check=True, stdout=sp.PIPE)
    assert "HelloWorld-python" in check_list_template.stdout.decode()
    assert "HelloWorld-java" in check_list_template.stdout.decode()


def test_list_repository():
    check_list_template = sp.run(["gdk", "component", "list", "--repository"], check=True, stdout=sp.PIPE)
    assert "aws-greengrass-labs-database-influxdb" in check_list_template.stdout.decode()

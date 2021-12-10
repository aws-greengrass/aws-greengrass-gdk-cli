import os
import subprocess as sp
import tempfile
from pathlib import Path

import gdk.common.exceptions.error_messages as error_messages


def install_cli():
    sp.run(["pip3", "install", "."])
    check_installation = sp.run(["gdk", "--help"], check=True, stdout=sp.PIPE)
    assert "Greengrass development kit - CLI" in check_installation.stdout.decode()


install_cli()


def test_list_template():
    check_list_template = sp.run(["gdk", "component", "list", "--template"], check=True, stdout=sp.PIPE)
    assert "HelloWorld-python" in check_list_template.stdout.decode()
    assert "HelloWorld-java" in check_list_template.stdout.decode()


def test_list_repository():
    check_list_template = sp.run(["gdk", "component", "list", "--repository"], check=True, stdout=sp.PIPE)
    assert "aws-greengrass-labs-database-influxdb" in check_list_template.stdout.decode()


def test_init_template_non_empty_dir():
    check_init_template = sp.run(["gdk", "component", "init", "-t", "HelloWorld", "-l", "python"], stdout=sp.PIPE)
    assert check_init_template.returncode == 1
    assert "Try `gdk component init --help`" in check_init_template.stdout.decode()


def test_init_template():
    dirpath = tempfile.mkdtemp()
    os.chdir(dirpath)
    check_init_template = sp.run(["gdk", "component", "init", "-t", "HelloWorld", "-l", "python"], check=True, stdout=sp.PIPE)
    assert check_init_template.returncode == 0
    assert Path(dirpath).joinpath("recipe.yaml").resolve().exists()
    assert Path(dirpath).joinpath("gdk-config.json").resolve().exists()


def test_init_repository():
    dirpath = tempfile.mkdtemp()
    os.chdir(dirpath)
    check_init_repo = sp.run(
        ["gdk", "component", "init", "-r", "aws-greengrass-labs-database-influxdb"], check=True, stdout=sp.PIPE
    )

    assert check_init_repo.returncode == 0
    assert Path(dirpath).joinpath("recipe.yaml").exists()
    assert Path(dirpath).joinpath("gdk-config.json").exists()

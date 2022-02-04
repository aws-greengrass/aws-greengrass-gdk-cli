import subprocess as sp
from pathlib import Path

import pytest


@pytest.fixture
def change_test_dir(tmpdir, monkeypatch):
    monkeypatch.chdir(tmpdir)
    return tmpdir


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


def test_init_template(change_test_dir):
    dirpath = Path(change_test_dir)
    check_init_template = sp.run(["gdk", "component", "init", "-t", "HelloWorld", "-l", "python"], check=True, stdout=sp.PIPE)
    assert check_init_template.returncode == 0
    assert Path(dirpath).joinpath("recipe.yaml").resolve().exists()
    assert Path(dirpath).joinpath("gdk-config.json").resolve().exists()


def test_init_template_with_new_directory(change_test_dir):
    dir = "test-dir"
    dirpath = Path(change_test_dir).joinpath(dir)
    check_init_template = sp.run(
        ["gdk", "component", "init", "-t", "HelloWorld", "-l", "python", "-n", dir], check=True, stdout=sp.PIPE
    )
    assert check_init_template.returncode == 0
    assert Path(dirpath).joinpath("recipe.yaml").resolve().exists()
    assert Path(dirpath).joinpath("gdk-config.json").resolve().exists()


def test_init_repository(change_test_dir):
    dirpath = Path(change_test_dir)
    check_init_repo = sp.run(
        ["gdk", "component", "init", "-r", "aws-greengrass-labs-database-influxdb"], check=True, stdout=sp.PIPE
    )
    assert check_init_repo.returncode == 0
    assert Path(dirpath).joinpath("recipe.yaml").exists()
    assert Path(dirpath).joinpath("gdk-config.json").exists()


def test_init_repository_with_new_dir(change_test_dir):
    dir = "test-dir"
    dirpath = Path(change_test_dir).joinpath(dir)
    check_init_repo = sp.run(
        ["gdk", "component", "init", "-r", "aws-greengrass-labs-database-influxdb", "-n", dir], check=True, stdout=sp.PIPE
    )
    assert check_init_repo.returncode == 0
    assert Path(dirpath).joinpath("recipe.yaml").exists()
    assert Path(dirpath).joinpath("gdk-config.json").exists()

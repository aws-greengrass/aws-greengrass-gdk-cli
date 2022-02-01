import json
import os
import subprocess as sp
import tempfile
from pathlib import Path


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


def test_build_template_zip():
    dirpath = tempfile.mkdtemp()
    # Recipe contains HelloWorld.zip artifact. So, create HelloWorld directory inside temporary directory.
    path_HelloWorld = Path(dirpath).joinpath("HelloWorld")
    os.mkdir(path_HelloWorld)
    os.chdir(path_HelloWorld)

    # Check if init downloads templates with necessary files.
    check_init_template = sp.run(["gdk", "component", "init", "-t", "HelloWorld", "-l", "python"], check=True, stdout=sp.PIPE)
    assert check_init_template.returncode == 0
    assert Path(path_HelloWorld).joinpath("recipe.yaml").resolve().exists()
    config_file = Path(path_HelloWorld).joinpath("gdk-config.json").resolve()
    assert config_file.exists()

    # Update gdk-config file mandatory field like region.
    with open(str(config_file), "r") as f:
        config = json.loads(f.read())
        config["component"]["com.example.PythonHelloWorld"]["publish"]["region"] = "us-east-1"
    with open(str(config_file), "w") as f:
        f.write(json.dumps(config))

    # Check if build works as expected.
    check_build_template = sp.run(["gdk", "component", "build"], check=True, stdout=sp.PIPE)
    assert check_build_template.returncode == 0
    assert Path(path_HelloWorld).joinpath("zip-build").resolve().exists()
    assert Path(path_HelloWorld).joinpath("greengrass-build").resolve().exists()
    artifact_path = (
        Path(path_HelloWorld)
        .joinpath("greengrass-build")
        .joinpath("artifacts")
        .joinpath("com.example.PythonHelloWorld")
        .joinpath("NEXT_PATCH")
        .joinpath("HelloWorld.zip")
        .resolve()
    )

    assert artifact_path.exists()

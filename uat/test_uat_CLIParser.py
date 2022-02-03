import json
import os
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


def test_build_template_zip(change_test_dir):
    # Recipe contains HelloWorld.zip artifact. So, create HelloWorld directory inside temporary directory.
    path_HelloWorld = Path(change_test_dir).joinpath("HelloWorld")

    # Check if init downloads templates with necessary files.
    check_init_template = sp.run(
        ["gdk", "component", "init", "-t", "HelloWorld", "-l", "python", "-n", "HelloWorld"], check=True, stdout=sp.PIPE
    )
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

    os.chdir(path_HelloWorld)
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


def test_build_template_zip_fail_with_no_artifact(change_test_dir):
    # Recipe contains HelloWorld.zip artifact. So, create HelloWorld directory inside temporary directory.
    dir_path = Path(change_test_dir).joinpath("artifact-not-exists")

    # Check if init downloads templates with necessary files.
    check_init_template = sp.run(
        ["gdk", "component", "init", "-t", "HelloWorld", "-l", "python", "-n", "artifact-not-exists"],
        check=True,
        stdout=sp.PIPE,
    )
    assert check_init_template.returncode == 0
    assert Path(dir_path).joinpath("recipe.yaml").resolve().exists()
    config_file = Path(dir_path).joinpath("gdk-config.json").resolve()
    assert config_file.exists()

    # Update gdk-config file mandatory field like region.
    with open(str(config_file), "r") as f:
        config = json.loads(f.read())
        config["component"]["com.example.PythonHelloWorld"]["publish"]["region"] = "us-east-1"
    with open(str(config_file), "w") as f:
        f.write(json.dumps(config))

    os.chdir(dir_path)
    # Check if build works as expected.
    check_build_template = sp.run(["gdk", "component", "build"], stdout=sp.PIPE)
    output = check_build_template.stdout.decode()
    assert check_build_template.returncode == 1
    assert Path(dir_path).joinpath("zip-build").resolve().exists()
    assert (
        "Could not find artifact with URI 's3://BUCKET_NAME/COMPONENT_NAME/COMPONENT_VERSION/HelloWorld.zip' on s3 or inside"
        " the build folders."
        in output
    )
    assert "Failed to build the component with the given project configuration." in output

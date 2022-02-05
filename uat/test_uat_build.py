import json
import os
import subprocess as sp
from pathlib import Path


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
    # Recipe contains HelloWorld.zip artifact. So, create a directory with different name.
    dir_name = "artifact-not-exists"
    dir_path = Path(change_test_dir).joinpath(dir_name)

    # Check if init downloads templates with necessary files.
    check_init_template = sp.run(
        ["gdk", "component", "init", "-t", "HelloWorld", "-l", "python", "-n", dir_name],
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


def test_build_template_maven(change_test_dir):
    path_HelloWorld = Path(change_test_dir).joinpath("HelloWorld")

    # Check if init downloads templates with necessary files.
    check_init_template = sp.run(
        ["gdk", "component", "init", "-t", "HelloWorld", "-l", "java", "-n", "HelloWorld"], check=True, stdout=sp.PIPE
    )
    assert check_init_template.returncode == 0
    assert Path(path_HelloWorld).joinpath("recipe.yaml").resolve().exists()
    config_file = Path(path_HelloWorld).joinpath("gdk-config.json").resolve()
    assert config_file.exists()

    # Update gdk-config file mandatory field like region.
    with open(str(config_file), "r") as f:
        config = json.loads(f.read())
        config["component"]["com.example.JavaHelloWorld"]["publish"]["region"] = "us-east-1"
    with open(str(config_file), "w") as f:
        f.write(json.dumps(config))

    os.chdir(path_HelloWorld)
    # Check if build works as expected.
    check_build_template = sp.run(["gdk", "component", "build"])
    assert check_build_template.returncode == 0
    assert Path(path_HelloWorld).joinpath("greengrass-build").resolve().exists()

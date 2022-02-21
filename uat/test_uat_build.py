import os
import shutil
from pathlib import Path

import t_utils


def test_build_template_zip(change_test_dir, gdk_cli):
    # Recipe contains HelloWorld.zip artifact. So, create HelloWorld directory inside temporary directory.
    path_HelloWorld = Path(change_test_dir).joinpath("HelloWorld")
    component_name = "com.example.PythonHelloWorld"
    region = "us-east-1"
    # Check if init downloads templates with necessary files.
    check_init_template = gdk_cli.run(
        ["component", "init", "-t", "HelloWorld", "-l", "python", "-n", "HelloWorld"]
    )
    assert check_init_template.returncode == 0
    assert Path(path_HelloWorld).joinpath("recipe.yaml").resolve().exists()
    config_file = Path(path_HelloWorld).joinpath("gdk-config.json").resolve()
    assert config_file.exists()

    # Update gdk-config file mandatory field like region.
    t_utils.update_config(config_file, component_name, region, bucket="", author="")

    os.chdir(path_HelloWorld)
    # Check if build works as expected.
    check_build_template = gdk_cli.run(["component", "build"])
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


def test_build_template_zip_fail_with_no_artifact(change_test_dir, gdk_cli):
    # Recipe contains HelloWorld.zip artifact. So, create a directory with different name.
    dir_name = "artifact-not-exists"
    dir_path = Path(change_test_dir).joinpath(dir_name)
    component_name = "com.example.PythonHelloWorld"
    region = "us-east-1"
    # Check if init downloads templates with necessary files.
    check_init_template = gdk_cli.run(
        ["component", "init", "-t", "HelloWorld", "-l", "python", "-n", dir_name]
    )
    assert check_init_template.returncode == 0
    assert Path(dir_path).joinpath("recipe.yaml").resolve().exists()
    config_file = Path(dir_path).joinpath("gdk-config.json").resolve()
    assert config_file.exists()

    # Update gdk-config file mandatory field like region.
    t_utils.update_config(config_file, component_name, region, bucket="", author="")

    os.chdir(dir_path)
    # Check if build works as expected.
    check_build_template = gdk_cli.run(["component", "build"])
    output = check_build_template.output
    assert check_build_template.returncode == 1
    assert Path(dir_path).joinpath("zip-build").resolve().exists()
    assert (
        "Could not find artifact with URI 's3://BUCKET_NAME/COMPONENT_NAME/COMPONENT_VERSION/HelloWorld.zip' on s3 or inside"
        " the build folders."
        in output
    )
    assert "Failed to build the component with the given project configuration." in output


def test_build_template_maven(change_test_dir, gdk_cli):
    path_HelloWorld = Path(change_test_dir).joinpath("HelloWorld")
    component_name = "com.example.JavaHelloWorld"
    region = "us-east-1"
    # Check if init downloads templates with necessary files.
    check_init_template = gdk_cli.run(
        ["component", "init", "-t", "HelloWorld", "-l", "java", "-n", "HelloWorld"]
    )
    assert check_init_template.returncode == 0
    assert Path(path_HelloWorld).joinpath("recipe.yaml").resolve().exists()
    config_file = Path(path_HelloWorld).joinpath("gdk-config.json").resolve()
    assert config_file.exists()

    t_utils.update_config(config_file, component_name, region, bucket="", author="")

    os.chdir(path_HelloWorld)
    # Check if build works as expected.
    check_build_template = gdk_cli.run(["component", "build"])
    assert check_build_template.returncode == 0
    assert Path(path_HelloWorld).joinpath("greengrass-build").resolve().exists()


def test_build_template_gradle_multi_project(change_test_dir, gdk_cli):
    path_multi_gradle_project = Path(change_test_dir).joinpath("gradle-build-test").resolve()
    zip_file = "gradle-build-test.zip"
    component_name = "com.example.Multi.Gradle"
    region = "us-east-1"
    s3_cl = t_utils.create_s3_client(region)
    account = t_utils.get_acc_num(region)

    s3_cl.download_file(
        f"gdk-cli-uat-{region}-{account}",
        f"do-not-delete-test-data/{zip_file}",
        str(Path(change_test_dir).joinpath(zip_file).resolve()),
    )
    shutil.unpack_archive(
        Path(change_test_dir).joinpath(zip_file),
        path_multi_gradle_project,
        "zip",
    )
    os.remove(Path(change_test_dir).joinpath(zip_file))
    os.chdir(path_multi_gradle_project)
    assert Path(path_multi_gradle_project).joinpath("recipe.yaml").resolve().exists()
    config_file = Path(path_multi_gradle_project).joinpath("gdk-config.json").resolve()
    assert config_file.exists()

    t_utils.update_config(config_file, component_name, region, bucket="", author="")

    # Check if build works as expected.
    check_build_template = gdk_cli.run(["component", "build"])
    assert check_build_template.returncode == 0
    assert Path(path_multi_gradle_project).joinpath("greengrass-build").resolve().exists()


def test_build_template_maven_multi_project(change_test_dir, gdk_cli):
    path_multi_gradle_project = Path(change_test_dir).joinpath("maven-build-test").resolve()
    zip_file = "maven-build-test.zip"
    component_name = "com.example.Multi.Maven"
    region = "us-east-1"
    s3_cl = t_utils.create_s3_client(region)
    account = t_utils.get_acc_num(region)

    s3_cl.download_file(
        f"gdk-cli-uat-{region}-{account}",
        f"do-not-delete-test-data/{zip_file}",
        str(Path(change_test_dir).joinpath(zip_file).resolve()),
    )
    shutil.unpack_archive(
        Path(change_test_dir).joinpath(zip_file),
        path_multi_gradle_project,
        "zip",
    )
    os.remove(Path(change_test_dir).joinpath(zip_file))
    os.chdir(path_multi_gradle_project)
    assert Path(path_multi_gradle_project).joinpath("recipe.yaml").resolve().exists()
    config_file = Path(path_multi_gradle_project).joinpath("gdk-config.json").resolve()
    assert config_file.exists()

    t_utils.update_config(config_file, component_name, region, bucket="", author="")

    # Check if build works as expected.
    check_build_template = gdk_cli.run(["component", "build"])
    assert check_build_template.returncode == 0
    assert Path(path_multi_gradle_project).joinpath("greengrass-build").resolve().exists()

import os
from pathlib import Path

import t_utils


def test_publish_template_zip(change_test_dir, gdk_cli):
    # Recipe contains HelloWorld.zip artifact. So, create HelloWorld directory inside temporary directory.
    path_HelloWorld = Path(change_test_dir).joinpath("HelloWorld")
    component_name = "com.example.PythonHelloWorld"
    region = "us-east-1"
    bucket = "gdk-cli-uat"
    author = "gdk-cli-uat"
    # Check if init downloads templates with necessary files.
    check_init_template = gdk_cli.run(["component", "init", "-t", "HelloWorld", "-l", "python", "-n", "HelloWorld"])
    assert check_init_template.returncode == 0
    assert Path(path_HelloWorld).joinpath("recipe.yaml").resolve().exists()
    config_file = Path(path_HelloWorld).joinpath("gdk-config.json").resolve()
    assert config_file.exists()

    t_utils.update_config(config_file, component_name, region, bucket, author)
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
        .joinpath(component_name)
        .joinpath("NEXT_PATCH")
        .joinpath("HelloWorld.zip")
        .resolve()
    )

    assert artifact_path.exists()
    check_publish_component = gdk_cli.run(["component", "publish"])
    assert check_publish_component.returncode == 0
    recipes_path = Path(path_HelloWorld).joinpath("greengrass-build").joinpath("recipes").resolve()
    t_utils.clean_up_aws_resources(component_name, t_utils.get_version_created(recipes_path, component_name), region)


def test_publish_without_build_template_zip_with_bucket_arg(change_test_dir, gdk_cli):
    # Recipe contains HelloWorld.zip artifact. So, create HelloWorld directory inside temporary directory.
    path_HelloWorld = Path(change_test_dir).joinpath("HelloWorld")
    component_name = "com.example.PythonHelloWorld"
    region = "us-east-1"
    bucket = "gdk-cli-uat"
    author = "gdk-cli-uat"
    # Check if init downloads templates with necessary files.
    check_init_template = gdk_cli.run(["component", "init", "-t", "HelloWorld", "-l", "python", "-n", "HelloWorld"])
    assert check_init_template.returncode == 0
    assert Path(path_HelloWorld).joinpath("recipe.yaml").resolve().exists()
    config_file = Path(path_HelloWorld).joinpath("gdk-config.json").resolve()
    assert config_file.exists()

    # Update gdk-config file mandatory field like region.
    t_utils.update_config(config_file, component_name, region, bucket, author)

    os.chdir(path_HelloWorld)
    # Pass in bucket name as arg
    bucket_arg = "{}-{}-{}".format(bucket, region, t_utils.get_acc_num(region))
    check_publish_component = gdk_cli.run(["component", "publish", "-b", bucket_arg])
    assert check_publish_component.returncode == 0
    assert Path(path_HelloWorld).joinpath("zip-build").resolve().exists()
    assert Path(path_HelloWorld).joinpath("greengrass-build").resolve().exists()
    artifact_path = (
        Path(path_HelloWorld)
        .joinpath("greengrass-build")
        .joinpath("artifacts")
        .joinpath(component_name)
        .joinpath("NEXT_PATCH")
        .joinpath("HelloWorld.zip")
        .resolve()
    )

    assert artifact_path.exists()
    recipes_path = Path(path_HelloWorld).joinpath("greengrass-build").joinpath("recipes").resolve()
    t_utils.clean_up_aws_resources(component_name, t_utils.get_version_created(recipes_path, component_name), region)

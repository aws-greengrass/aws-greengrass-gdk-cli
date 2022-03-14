import os
import shutil
import pytest

from pathlib import Path

import t_utils


@pytest.mark.version(min='1.0.0')
def test_publish_template_zip(change_test_dir, gdk_cli):
    # Recipe contains HelloWorld.zip artifact. So, create HelloWorld directory inside temporary directory.
    path_HelloWorld = Path(change_test_dir).joinpath("helloworld")
    path_HelloWorld.mkdir(parents=True, exist_ok=True)
    os.chdir(str(path_HelloWorld))

    simple_component_name = "com.example.PythonHelloWorld"
    component_name = simple_component_name + "." + t_utils.random_id()
    region = "us-east-1"
    bucket = "gdk-cli-uat"
    author = "gdk-cli-uat"
    # Check if init downloads templates with necessary files.
    check_init_template = gdk_cli.run(["component", "init", "-t", "HelloWorld", "-l", "python"])
    assert check_init_template.returncode == 0
    recipe_file = Path(path_HelloWorld).joinpath("recipe.yaml").resolve()
    assert recipe_file.exists()
    config_file = Path(path_HelloWorld).joinpath("gdk-config.json").resolve()
    assert config_file.exists()

    t_utils.replace_uri_in_recipe(recipe_file, "all", "HelloWorld", "helloworld")
    t_utils.update_config(
        config_file, component_name, region, bucket, author, old_component_name=simple_component_name
    )
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
        .joinpath("helloworld.zip")
        .resolve()
    )

    assert artifact_path.exists()
    check_publish_component = gdk_cli.run(["component", "publish"])
    assert check_publish_component.returncode == 0
    recipes_path = Path(path_HelloWorld).joinpath("greengrass-build").joinpath("recipes").resolve()
    t_utils.clean_up_aws_resources(component_name, t_utils.get_version_created(recipes_path, component_name), region)


@pytest.mark.version(min='1.1.0')
def test_publish_template_zip_with_directory_name(change_test_dir, gdk_cli):
    # Recipe contains HelloWorld.zip artifact. So, create HelloWorld directory inside temporary directory.
    path_HelloWorld = Path(change_test_dir).joinpath("HelloWorld")
    simple_component_name = "com.example.PythonHelloWorld"
    component_name = simple_component_name + "." + t_utils.random_id()
    region = "us-east-1"
    bucket = "gdk-cli-uat"
    author = "gdk-cli-uat"
    # Check if init downloads templates with necessary files.
    check_init_template = gdk_cli.run(["component", "init", "-t", "HelloWorld", "-l", "python", "-n", "HelloWorld"])
    assert check_init_template.returncode == 0
    assert Path(path_HelloWorld).joinpath("recipe.yaml").resolve().exists()
    config_file = Path(path_HelloWorld).joinpath("gdk-config.json").resolve()
    assert config_file.exists()

    t_utils.update_config(
        config_file, component_name, region, bucket, author, old_component_name=simple_component_name
    )
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


@pytest.mark.version(min='1.1.0')
def test_publish_without_build_template_zip_with_bucket_arg(change_test_dir, gdk_cli):
    # Recipe contains HelloWorld.zip artifact. So, create HelloWorld directory inside temporary directory.
    path_HelloWorld = Path(change_test_dir).joinpath("HelloWorld")
    simple_component_name = "com.example.PythonHelloWorld"
    component_name = simple_component_name + "." + t_utils.random_id()
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
    t_utils.update_config(
        config_file, component_name, region, bucket, author, old_component_name=simple_component_name
    )

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


@pytest.mark.version(gt='1.1.0')
def test_build_template_maven_multi_project_mixed_uris(change_test_dir, gdk_cli):
    path_multi_mvn_project = Path(change_test_dir).joinpath("maven-mixed-uris-publish-test").resolve()
    simple_zip_file = "maven-mixed-uris-publish-test.zip"
    simple_component_name = "com.example.Multi.MixUris.Maven"
    component_name = simple_component_name + "." + t_utils.random_id()
    region = "us-east-1"
    s3_cl = t_utils.create_s3_client(region)
    account = t_utils.get_acc_num(region)
    bucket_prefix = "gdk-cli-uat"
    s3_cl.download_file(
        f"gdk-github-workflow-cdk-test-data-{region}-{account}",
        f"{simple_zip_file}",
        str(Path(change_test_dir).joinpath(simple_zip_file).resolve()),
    )
    shutil.unpack_archive(
        Path(change_test_dir).joinpath(simple_zip_file),
        change_test_dir,
        "zip",
    )
    os.remove(Path(change_test_dir).joinpath(simple_zip_file))
    os.chdir(path_multi_mvn_project)
    assert Path(path_multi_mvn_project).joinpath("recipe.yaml").resolve().exists()
    config_file = Path(path_multi_mvn_project).joinpath("gdk-config.json").resolve()
    assert config_file.exists()

    t_utils.update_config(
        config_file, component_name, region, bucket=bucket_prefix, author="Me", old_component_name=simple_component_name
    )

    # Check if publish works as expected.
    check_publish_template = gdk_cli.run(["component", "publish"], capture_output=False)
    assert check_publish_template.returncode == 0
    assert Path(path_multi_mvn_project).joinpath("greengrass-build").resolve().exists()
    recipes_path = Path(path_multi_mvn_project).joinpath("greengrass-build").joinpath("recipes").resolve()
    t_utils.clean_up_aws_resources(component_name, t_utils.get_version_created(recipes_path, component_name), region)

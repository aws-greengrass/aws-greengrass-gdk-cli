import ast
import os
import t_utils
import shutil
from behave import step
from pathlib import Path
from constants import (
    GG_CONFIG_JSON, GG_RECIPE_YAML, GG_BUILD_DIR, GG_BUILD_ZIP_DIR,
    DEFAULT_AWS_REGION, DEFAULT_S3_BUCKET_PREFIX, DEFAULT_ARTIFACT_AUTHOR
)


@step('we verify gdk project files')
def verify_component_files(context):
    cwd = context.cwd if "cwd" in context else os.getcwd()
    assert Path(cwd).joinpath(GG_RECIPE_YAML).resolve().exists(), f"{GG_RECIPE_YAML} does not exist"
    assert Path(cwd).joinpath(GG_CONFIG_JSON).resolve().exists(), f"{GG_CONFIG_JSON} does not exist"


@step("we verify component zip build files")
def verify_component_zip_build_files(context):
    cwd = context.cwd if "cwd" in context else os.getcwd()
    assert Path(cwd).joinpath(GG_BUILD_DIR).resolve().exists()
    assert Path(cwd).joinpath(GG_BUILD_ZIP_DIR).resolve().exists()


@step('we verify component build files')
def verify_component_build_files(context):
    cwd = context.cwd if "cwd" in context else os.getcwd()
    assert Path(cwd).joinpath(GG_BUILD_DIR).resolve().exists()


def context_replace(context, string: str):
    if string.startswith("${context."):
        string = string[len("${context."):]
        idx = string.find("}")
        key = string[0:idx]
        string = getattr(context, key) + string[idx+1:]

    return string


@step('we verify build artifact named {artifact_name}')
def verify_component_build_artifact(context, artifact_name):
    cwd = context.cwd if "cwd" in context else os.getcwd()
    artifact_name = context_replace(context, artifact_name)
    component_name = context.last_component
    artifact_path = (
        Path(cwd)
        .joinpath(GG_BUILD_DIR)
        .joinpath("artifacts")
        .joinpath(component_name)
        .joinpath("NEXT_PATCH")
        .joinpath(artifact_name)
        .resolve()
    )
    assert artifact_path.exists(), f"Artifact {artifact_name} not found at {artifact_path}"


@step('change component name to {component_name}')
def update_component_config(context, component_name):
    cwd = context.cwd if "cwd" in context else os.getcwd()
    config_file = Path(cwd).joinpath(GG_CONFIG_JSON).resolve()
    assert config_file.exists(), f"{GG_CONFIG_JSON} does not exist"

    unique_component_name = f"{component_name}.{t_utils.random_id()}"

    t_utils.update_config(
        config_file, unique_component_name, DEFAULT_AWS_REGION, bucket=DEFAULT_S3_BUCKET_PREFIX,
        author=DEFAULT_ARTIFACT_AUTHOR, old_component_name=component_name
    )
    # for cleanup
    context.last_component = unique_component_name


@step('change build system to {build_system}')
def update_component_config_build_system(context, build_system):
    cwd = context.cwd if "cwd" in context else os.getcwd()
    config_file = Path(cwd).joinpath(GG_CONFIG_JSON).resolve()
    assert config_file.exists(), f"{GG_CONFIG_JSON} does not exist"
    t_utils.update_config_build_sytem(config_file, context.last_component, build_system)


@step("change build options to {build_options}")
def update_component_config_build_options(context, build_options):
    cwd = context.cwd if "cwd" in context else os.getcwd()
    config_file = Path(cwd).joinpath(GG_CONFIG_JSON).resolve()
    assert config_file.exists(), f"{GG_CONFIG_JSON} does not exist"
    t_utils.update_config_build_options(config_file, context.last_component, build_options)


@step('change artifact uri for {platform_type} platform from {search} to {replace}')
def update_artifact_uri(context, platform_type, search, replace):
    cwd = context.cwd if "cwd" in context else os.getcwd()
    recipe_file = Path(cwd).joinpath(GG_RECIPE_YAML).resolve()
    assert recipe_file.exists(), f"{GG_RECIPE_YAML} does not exist"
    t_utils.replace_uri_in_recipe(recipe_file, platform_type, search, context_replace(context, replace))


@step("we verify the following files in {artifact_name}")
def verify_files_in_build_zip_artifact(context, artifact_name):
    cwd = context.cwd if "cwd" in context else os.getcwd()
    component_name = context.last_component
    artifact_name = context_replace(context, artifact_name)
    artifact_path = (
        Path(cwd)
        .joinpath(GG_BUILD_DIR)
        .joinpath("artifacts")
        .joinpath(component_name)
        .joinpath("NEXT_PATCH")
        .joinpath(artifact_name)
        .resolve()
    )
    assert artifact_path.exists(), f"Artifact {artifact_name} not found at {artifact_path}"
    unpack_dir = Path(cwd).joinpath("unarchived-artifact").resolve()
    shutil.unpack_archive(artifact_path, unpack_dir)

    for row in context.table:
        excluded_files = ast.literal_eval(row["excluded"])
        included_files = ast.literal_eval(row["included"])

    for file in excluded_files:
        assert not unpack_dir.joinpath(file).exists(), f"File {file} found at {unpack_dir}"
    for file in included_files:
        assert unpack_dir.joinpath(file).exists(), f"File {file} not found at {unpack_dir}"

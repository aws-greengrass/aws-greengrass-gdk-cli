import os
import t_utils

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


@step('we verify component zip build files')
def verify_component_zip_build_files(context):
    cwd = context.cwd if "cwd" in context else os.getcwd()
    assert Path(cwd).joinpath(GG_BUILD_DIR).resolve().exists()
    assert Path(cwd).joinpath(GG_BUILD_ZIP_DIR).resolve().exists()


@step('we verify component build files')
def verify_component_build_files(context):
    cwd = context.cwd if "cwd" in context else os.getcwd()
    assert Path(cwd).joinpath(GG_BUILD_DIR).resolve().exists()


@step('we verify build artifact named {artifact_name}')
def verify_component_build_artifact(context, artifact_name):
    cwd = context.cwd if "cwd" in context else os.getcwd()
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


@step('change artifact uri for {platform_type} platform from {search} to {replace}')
def update_artifact_uri(context, platform_type, search, replace):
    cwd = context.cwd if "cwd" in context else os.getcwd()
    recipe_file = Path(cwd).joinpath(GG_RECIPE_YAML).resolve()
    assert recipe_file.exists(), f"{GG_RECIPE_YAML} does not exist"
    t_utils.replace_uri_in_recipe(recipe_file, platform_type, search, replace)

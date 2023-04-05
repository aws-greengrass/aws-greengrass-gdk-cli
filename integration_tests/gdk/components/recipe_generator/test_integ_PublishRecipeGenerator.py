import json
from pathlib import Path
from gdk.commands.component.recipe_generator.PublishRecipeGenerator import PublishRecipeGenerator

import pytest
import tempfile
import gdk.common.consts as consts
import gdk.common.utils as utils
import shutil
import yaml


@pytest.fixture()
def supported_build_system(mocker):
    builds_file = utils.get_static_file_path(consts.project_build_system_file)
    with open(builds_file, "r") as f:
        data = json.loads(f.read())
    mock_get_supported_component_builds = mocker.patch(
        "gdk.commands.component.project_utils.get_supported_component_builds", return_value=data
    )
    return mock_get_supported_component_builds


@pytest.fixture()
def rglob_build_file(mocker):
    def search(*args, **kwargs):
        if "build.gradle" in args[0] or "pom.xml" in args[0]:
            return [Path(utils.current_directory).joinpath("build_file")]
        return []

    mock_rglob = mocker.patch("pathlib.Path.rglob", side_effect=search)
    return mock_rglob


def test_generate_publish_recipe_artifact_in_build_json():
    pc = project_config()
    with tempfile.TemporaryDirectory() as newDir:
        pc["component_recipe_file"] = (
            Path(".").joinpath("tests/gdk/static/project_utils").joinpath("valid_component_recipe.json").resolve()
        )
        pc["gg_build_directory"] = Path(newDir).joinpath("greengrass-build").resolve()
        pc["gg_build_component_artifacts_dir"] = (
            pc["gg_build_directory"]
            .joinpath("artifacts")
            .joinpath(pc["component_name"])
            .joinpath(pc["component_version"])
            .resolve()
        )
        pc["gg_build_recipes_dir"] = pc["gg_build_directory"].joinpath("recipes").resolve()
        pc["gg_build_component_artifacts_dir"].mkdir(parents=True)
        pc["gg_build_recipes_dir"].mkdir(parents=True)
        pc["publish_recipe_file"] = pc["gg_build_recipes_dir"].joinpath("com.example.HelloWorld-1.0.0.json")

        shutil.copy(pc["component_recipe_file"], pc["gg_build_recipes_dir"])
        artifact_file = Path(pc["gg_build_component_artifacts_dir"]).joinpath("hello_world.py").resolve()
        artifact_file.touch(exist_ok=True)

        prg = PublishRecipeGenerator(pc)
        prg.generate()

        assert pc["gg_build_recipes_dir"].joinpath("com.example.HelloWorld-1.0.0.json").is_file()

        with open(pc["gg_build_recipes_dir"].joinpath("com.example.HelloWorld-1.0.0.json"), "r") as f:
            recipe = json.loads(f.read())
            assert recipe["Manifests"][0]["Artifacts"][0]["URI"] == "s3://default/com.example.HelloWorld/1.0.0/hello_world.py"


def test_generate_publish_recipe_artifact_in_build_yaml():
    pc = project_config()
    with tempfile.TemporaryDirectory() as newDir:
        pc["component_recipe_file"] = (
            Path(".").joinpath("tests/gdk/static/project_utils").joinpath("valid_component_recipe.yaml").resolve()
        )

        pc["gg_build_directory"] = Path(newDir).joinpath("greengrass-build").resolve()
        pc["gg_build_component_artifacts_dir"] = (
            pc["gg_build_directory"]
            .joinpath("artifacts")
            .joinpath(pc["component_name"])
            .joinpath(pc["component_version"])
            .resolve()
        )
        pc["gg_build_recipes_dir"] = pc["gg_build_directory"].joinpath("recipes").resolve()
        pc["publish_recipe_file"] = pc["gg_build_recipes_dir"].joinpath("com.example.HelloWorld-1.0.0.yaml")
        pc["gg_build_component_artifacts_dir"].mkdir(parents=True)
        pc["gg_build_recipes_dir"].mkdir(parents=True)

        shutil.copy(pc["component_recipe_file"], pc["gg_build_recipes_dir"])
        artifact_file = Path(pc["gg_build_component_artifacts_dir"]).joinpath("hello_world.py").resolve()
        artifact_file.touch(exist_ok=True)

        prg = PublishRecipeGenerator(pc)
        prg.generate()

        assert pc["gg_build_recipes_dir"].joinpath("com.example.HelloWorld-1.0.0.yaml").is_file()

        with open(pc["gg_build_recipes_dir"].joinpath("com.example.HelloWorld-1.0.0.yaml"), "r") as f:
            recipe = yaml.safe_load(f.read())
            assert recipe["Manifests"][0]["Artifacts"][0]["URI"] == "s3://default/com.example.HelloWorld/1.0.0/hello_world.py"


def project_config():
    return {
        "component_name": "com.example.HelloWorld",
        "component_build_config": {"build_system": "zip"},
        "component_version": "1.0.0",
        "component_author": "abc",
        "bucket": "default",
        "region": "us-east-1",
        "gg_build_directory": Path("/src/GDK-CLI-Internal/greengrass-build"),
        "gg_build_artifacts_dir": Path("/src/GDK-CLI-Internal/greengrass-build/artifacts"),
        "gg_build_recipes_dir": Path("/src/GDK-CLI-Internal/greengrass-build/recipes"),
        "gg_build_component_artifacts_dir": Path("/src/GDK-CLI-Internal/greengrass-build/artifacts/component_name/1.0.0"),
        "component_recipe_file": Path("/src/GDK-CLI-Internal/tests/gdk/static/build_command/valid_component_recipe.json"),
    }

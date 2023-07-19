import json
from pathlib import Path
from gdk.commands.component.transformer.BuildRecipeTransformer import (
    BuildRecipeTransformer,
)

import pytest
import tempfile
import gdk.common.consts as consts
import gdk.common.utils as utils
import boto3

gradle_build_command = ["gradle", "clean", "build"]


@pytest.fixture()
def supported_build_system(mocker):
    builds_file = utils.get_static_file_path(consts.project_build_system_file)
    with open(builds_file, "r") as f:
        data = json.loads(f.read())
    mock_get_supported_component_builds = mocker.patch(
        "gdk.commands.component.project_utils.get_supported_component_builds",
        return_value=data,
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


def test_transform_build_recipe_artifact_in_build(mocker):
    pc = project_config()
    with tempfile.TemporaryDirectory() as newDir:
        pc["component_recipe_file"] = (
            Path(".")
            .joinpath("tests/gdk/static/project_utils")
            .joinpath("valid_component_recipe.json")
            .resolve()
        )
        pc["gg_build_directory"] = Path(newDir).joinpath("greengrass-build").resolve()
        pc["gg_build_component_artifacts_dir"] = (
            pc["gg_build_directory"]
            .joinpath("artifacts")
            .joinpath(pc["component_name"])
            .joinpath(pc["component_version"])
            .resolve()
        )
        pc["gg_build_recipes_dir"] = (
            pc["gg_build_directory"].joinpath("recipes").resolve()
        )

        zip_build_directory = Path(newDir).joinpath("zip-build").resolve()
        artifact_file = Path(zip_build_directory).joinpath("hello_world.py").resolve()
        zip_build_directory.mkdir(parents=True)
        artifact_file.touch(exist_ok=True)
        pc["gg_build_component_artifacts_dir"].mkdir(parents=True)
        pc["gg_build_recipes_dir"].mkdir(parents=True)

        brg = BuildRecipeTransformer(pc)
        brg.transform([zip_build_directory])

        assert (
            pc["gg_build_component_artifacts_dir"].joinpath("hello_world.py").is_file()
        )
        assert (
            pc["gg_build_recipes_dir"].joinpath("valid_component_recipe.json").is_file()
        )

        with open(
            pc["gg_build_recipes_dir"].joinpath("valid_component_recipe.json"), "r"
        ) as f:
            recipe = json.loads(f.read())
            # Artifact URI is updated
            assert (
                recipe["Manifests"][0]["Artifacts"][0]["URI"]
                == "s3://BUCKET_NAME/COMPONENT_NAME/COMPONENT_VERSION/hello_world.py"
            )


def test_transform_build_recipe_artifact_in_s3(mocker):
    pc = project_config()

    mocker.patch(
        "gdk.commands.component.project_utils.create_s3_client",
        return_value=mocker.patch("boto3.client", return_value=boto3.client("s3")),
    )
    mock_s3_head_object = mocker.patch(
        "boto3.client.head_object",
        return_value={"ResponseMetadata": {"HTTPStatusCode": 200}},
    )
    with tempfile.TemporaryDirectory() as newDir:
        pc["component_recipe_file"] = (
            Path(".")
            .joinpath("tests/gdk/static/project_utils")
            .joinpath("valid_component_recipe.json")
            .resolve()
        )
        pc["gg_build_directory"] = Path(newDir).joinpath("greengrass-build").resolve()
        pc["gg_build_component_artifacts_dir"] = (
            pc["gg_build_directory"]
            .joinpath("artifacts")
            .joinpath(pc["component_name"])
            .joinpath(pc["component_version"])
            .resolve()
        )
        pc["gg_build_recipes_dir"] = (
            pc["gg_build_directory"].joinpath("recipes").resolve()
        )

        zip_build_directory = Path(newDir).joinpath("zip-build").resolve()
        zip_build_directory.mkdir(parents=True)
        pc["gg_build_component_artifacts_dir"].mkdir(parents=True)
        pc["gg_build_recipes_dir"].mkdir(parents=True)

        brg = BuildRecipeTransformer(pc)
        brg.transform([zip_build_directory])

        assert (
            not pc["gg_build_component_artifacts_dir"]
            .joinpath("hello_world.py")
            .is_file()
        )
        assert (
            pc["gg_build_recipes_dir"].joinpath("valid_component_recipe.json").is_file()
        )
        assert mock_s3_head_object.assert_called_once
        with open(
            pc["gg_build_recipes_dir"].joinpath("valid_component_recipe.json"), "r"
        ) as f:
            recipe = json.loads(f.read())
            # Artifact URI is not updated
            assert (
                recipe["Manifests"][0]["Artifacts"][0]["URI"]
                == "s3://DOC-EXAMPLE-BUCKET/artifacts/com.example.HelloWorld/1.0.0/hello_world.py"
            )


def test_transform_build_recipe_artifact_not_found():
    pc = project_config()
    with tempfile.TemporaryDirectory() as newDir:
        pc["component_recipe_file"] = (
            Path(".")
            .joinpath("tests/gdk/static/project_utils")
            .joinpath("valid_component_recipe.json")
            .resolve()
        )
        pc["gg_build_directory"] = Path(newDir).joinpath("greengrass-build").resolve()
        pc["gg_build_component_artifacts_dir"] = (
            pc["gg_build_directory"]
            .joinpath("artifacts")
            .joinpath(pc["component_name"])
            .joinpath(pc["component_version"])
            .resolve()
        )
        pc["gg_build_recipes_dir"] = (
            pc["gg_build_directory"].joinpath("recipes").resolve()
        )

        zip_build_directory = Path(newDir).joinpath("zip-build").resolve()
        zip_build_directory.mkdir(parents=True)
        pc["gg_build_component_artifacts_dir"].mkdir(parents=True)
        pc["gg_build_recipes_dir"].mkdir(parents=True)

        brg = BuildRecipeTransformer(pc)
        with pytest.raises(Exception) as e:
            brg.transform([zip_build_directory])

        assert (
            "Could not find artifact with URI 's3://DOC-EXAMPLE-BUCKET/artifacts/com.example.HelloWorld/1.0.0/hello_world.py'"
            " on s3 or inside the build folders." in e.value.args[0]
        )


def project_config():
    return {
        "component_name": "component_name",
        "component_build_config": {"build_system": "zip"},
        "component_version": "1.0.0",
        "component_author": "abc",
        "bucket": "default",
        "region": "us-east-1",
        "gg_build_directory": Path("/src/GDK-CLI-Internal/greengrass-build"),
        "gg_build_artifacts_dir": Path(
            "/src/GDK-CLI-Internal/greengrass-build/artifacts"
        ),
        "gg_build_recipes_dir": Path("/src/GDK-CLI-Internal/greengrass-build/recipes"),
        "gg_build_component_artifacts_dir": Path(
            "/src/GDK-CLI-Internal/greengrass-build/artifacts/component_name/1.0.0"
        ),
        "component_recipe_file": Path(
            "/src/GDK-CLI-Internal/tests/gdk/static/build_command/valid_component_recipe.json"
        ),
    }

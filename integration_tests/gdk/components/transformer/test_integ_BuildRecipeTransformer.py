import json
from pathlib import Path
from gdk.commands.component.transformer.BuildRecipeTransformer import BuildRecipeTransformer
from unittest import TestCase

import pytest
import gdk.common.utils as utils
from gdk.commands.component.config.ComponentBuildConfiguration import ComponentBuildConfiguration
import os
import shutil
from gdk.aws_clients.S3Client import S3Client

gradle_build_command = ["gradle", "clean", "build"]


@pytest.fixture()
def rglob_build_file(mocker):
    def search(*args, **kwargs):
        if "build.gradle" in args[0] or "pom.xml" in args[0]:
            return [Path(utils.current_directory).joinpath("build_file")]
        return []

    mock_rglob = mocker.patch("pathlib.Path.rglob", side_effect=search)
    return mock_rglob


class ComponentBuildCommandIntegTest(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker, tmpdir):
        self.mocker = mocker
        self.tmpdir = Path(tmpdir).resolve()
        self.c_dir = Path(".").resolve()
        self.mocker.patch(
            "gdk.common.configuration.get_configuration",
            return_value=config(),
        )
        os.chdir(self.tmpdir)

        yield
        os.chdir(self.c_dir)

    def test_transform_build_recipe_artifact_in_build(self):
        recipe = self.c_dir.joinpath("tests/gdk/static/project_utils").joinpath("valid_component_recipe.json").resolve()
        # with tempfile.TemporaryDirectory() as newDir:
        shutil.copy(recipe, Path(self.tmpdir).joinpath("recipe.json").resolve())
        bconfig = ComponentBuildConfiguration({})
        zip_build_directory = Path(self.tmpdir).joinpath("zip-build").resolve()
        artifact_file = Path(zip_build_directory).joinpath("hello_world.py").resolve()
        zip_build_directory.mkdir(parents=True)
        artifact_file.touch(exist_ok=True)
        bconfig.gg_build_component_artifacts_dir.mkdir(parents=True)
        bconfig.gg_build_recipes_dir.mkdir(parents=True)

        brg = BuildRecipeTransformer(bconfig)
        brg.transform([zip_build_directory])

        assert bconfig.gg_build_component_artifacts_dir.joinpath("hello_world.py").is_file()
        assert bconfig.gg_build_recipes_dir.joinpath("recipe.json").is_file()

        with open(bconfig.gg_build_recipes_dir.joinpath("recipe.json"), "r") as f:
            recipe = json.loads(f.read())
            # Artifact URI is updated
            assert (
                recipe["Manifests"][0]["Artifacts"][0]["URI"]
                == "s3://BUCKET_NAME/COMPONENT_NAME/COMPONENT_VERSION/hello_world.py"
            )

    def test_transform_build_recipe_artifact_in_s3(self):
        recipe = self.c_dir.joinpath("tests/gdk/static/project_utils").joinpath("valid_component_recipe.json").resolve()
        self.mocker.patch.object(
            S3Client,
            "s3_artifact_exists",
            return_value=True,
        )
        shutil.copy(recipe, Path(self.tmpdir).joinpath("recipe.json").resolve())
        bconfig = ComponentBuildConfiguration({})

        zip_build_directory = Path(self.tmpdir).joinpath("zip-build").resolve()
        zip_build_directory.mkdir(parents=True)
        bconfig.gg_build_component_artifacts_dir.mkdir(parents=True)
        bconfig.gg_build_recipes_dir.mkdir(parents=True)

        brg = BuildRecipeTransformer(bconfig)
        brg.transform([zip_build_directory])

        assert not bconfig.gg_build_component_artifacts_dir.joinpath("hello_world.py").is_file()
        assert bconfig.gg_build_recipes_dir.joinpath("recipe.json").is_file()
        with open(bconfig.gg_build_recipes_dir.joinpath("recipe.json"), "r") as f:
            recipe = json.loads(f.read())
            # Artifact URI is not updated
            assert (
                recipe["Manifests"][0]["Artifacts"][0]["URI"]
                == "s3://DOC-EXAMPLE-BUCKET/artifacts/com.example.HelloWorld/1.0.0/hello_world.py"
            )

    def test_transform_build_recipe_artifact_not_found(self):
        recipe = self.c_dir.joinpath("tests/gdk/static/project_utils").joinpath("valid_component_recipe.json").resolve()

        shutil.copy(recipe, Path(self.tmpdir).joinpath("recipe.json").resolve())
        bconfig = ComponentBuildConfiguration({})
        zip_build_directory = Path(self.tmpdir).joinpath("zip-build").resolve()
        zip_build_directory.mkdir(parents=True)
        bconfig.gg_build_component_artifacts_dir.mkdir(parents=True)
        bconfig.gg_build_recipes_dir.mkdir(parents=True)

        brg = BuildRecipeTransformer(bconfig)
        with pytest.raises(Exception) as e:
            brg.transform([zip_build_directory])

        assert (
            "Could not find artifact with URI"
            " 's3://DOC-EXAMPLE-BUCKET/artifacts/com.example.HelloWorld/1.0.0/hello_world.py' on s3 or inside the build"
            " folders."
            in e.value.args[0]
        )


def config():
    return {
        "component": {
            "component_name": {
                "author": "abc",
                "version": "1.0.0",
                "build": {"build_system": "zip"},
                "publish": {"bucket": "default", "region": "us-east-1"},
            }
        },
        "gdk_version": "1.0.0",
    }

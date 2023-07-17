import json
from pathlib import Path
from gdk.commands.component.transformer.PublishRecipeTransformer import PublishRecipeTransformer

import pytest
import yaml
import os

from unittest import TestCase
from gdk.commands.component.config.ComponentPublishConfiguration import ComponentPublishConfiguration

import gdk.common.utils as utils
import boto3
import shutil
from botocore.stub import Stubber

gradle_build_command = ["gradle", "clean", "build"]


@pytest.fixture()
def rglob_build_file(mocker):
    def search(*args, **kwargs):
        if "build.gradle" in args[0] or "pom.xml" in args[0]:
            return [Path(utils.current_directory).joinpath("build_file")]
        return []

    mock_rglob = mocker.patch("pathlib.Path.rglob", side_effect=search)
    return mock_rglob


class ComponentPublishRecipeTransformerIntegTest(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker, tmpdir):
        self.mocker = mocker
        self.tmpdir = Path(tmpdir).resolve()
        self.c_dir = Path(".").resolve()
        self.stub_aws_clients()
        self.mocker.patch(
            "gdk.common.configuration.get_configuration",
            return_value=config(),
        )
        os.chdir(self.tmpdir)

        yield
        os.chdir(self.c_dir)

    def stub_aws_clients(self):
        self.sts_client = boto3.client("sts", region_name="us-east-1")
        self.gg_client = boto3.client("greengrassv2", region_name="us-east-1")
        self.s3_client = boto3.client("s3", region_name="us-east-1")

        def _clients(*args, **kwargs):
            if args[0] == "greengrassv2":
                return self.gg_client
            elif args[0] == "sts":
                return self.sts_client
            elif args[0] == "s3":
                return self.s3_client

        self.mocker.patch("boto3.client", _clients)

        self.gg_client_stub = Stubber(self.gg_client)
        self.sts_client_stub = Stubber(self.sts_client)

        self.gg_client_stub.activate()
        self.sts_client_stub.activate()
        self.sts_client_stub.add_response("get_caller_identity", {"Account": "123456789012"})
        self.gg_client_stub.add_response(
            "list_component_versions",
            {
                "componentVersions": [],
                "nextToken": "string",
            },
        )

    def test_transform_publish_recipe_artifact_in_build_json(self):
        recipe = self.c_dir.joinpath("tests/gdk/static/project_utils").joinpath("valid_component_recipe.json").resolve()
        shutil.copy(recipe, Path(self.tmpdir).joinpath("recipe.json").resolve())
        pconfig = ComponentPublishConfiguration({})
        pconfig.gg_build_component_artifacts_dir.mkdir(parents=True)
        pconfig.gg_build_recipes_dir.mkdir(parents=True)

        shutil.copy(recipe, pconfig.gg_build_recipes_dir.joinpath("recipe.json").resolve())
        artifact_file = pconfig.gg_build_component_artifacts_dir.joinpath("hello_world.py").resolve()
        artifact_file.touch(exist_ok=True)

        prt = PublishRecipeTransformer(pconfig)
        prt.transform()

        assert pconfig.gg_build_component_artifacts_dir.joinpath("hello_world.py").is_file()
        assert pconfig.gg_build_recipes_dir.joinpath("recipe.json").is_file()
        assert pconfig.gg_build_recipes_dir.joinpath("com.example.HelloWorld-1.0.0.json").is_file()
        with open(pconfig.gg_build_recipes_dir.joinpath("com.example.HelloWorld-1.0.0.json"), "r") as f:
            recipe = json.loads(f.read())
            # Artifact URI is updated
            assert (
                recipe["Manifests"][0]["Artifacts"][0]["URI"]
                == "s3://default-us-east-1-123456789012/com.example.HelloWorld/1.0.0/hello_world.py"
            )

    def test_transform_publish_recipe_artifact_in_build_yaml(self):
        recipe = self.c_dir.joinpath("tests/gdk/static/project_utils").joinpath("valid_component_recipe.yaml").resolve()
        shutil.copy(recipe, Path(self.tmpdir).joinpath("recipe.yaml").resolve())
        pconfig = ComponentPublishConfiguration({})
        pconfig.gg_build_component_artifacts_dir.mkdir(parents=True)
        pconfig.gg_build_recipes_dir.mkdir(parents=True)

        shutil.copy(recipe, pconfig.gg_build_recipes_dir.joinpath("recipe.yaml").resolve())
        artifact_file = pconfig.gg_build_component_artifacts_dir.joinpath("hello_world.py").resolve()
        artifact_file.touch(exist_ok=True)

        prt = PublishRecipeTransformer(pconfig)
        prt.transform()

        assert pconfig.gg_build_component_artifacts_dir.joinpath("hello_world.py").is_file()
        assert pconfig.gg_build_recipes_dir.joinpath("recipe.yaml").is_file()
        assert pconfig.gg_build_recipes_dir.joinpath("com.example.HelloWorld-1.0.0.yaml").is_file()
        with open(pconfig.gg_build_recipes_dir.joinpath("com.example.HelloWorld-1.0.0.yaml"), "r") as f:
            recipe = yaml.safe_load(f.read())
            # Artifact URI is updated
            assert (
                recipe["Manifests"][0]["Artifacts"][0]["URI"]
                == "s3://default-us-east-1-123456789012/com.example.HelloWorld/1.0.0/hello_world.py"
            )


def config():
    return {
        "component": {
            "com.example.HelloWorld": {
                "author": "abc",
                "version": "1.0.0",
                "build": {"build_system": "zip"},
                "publish": {"bucket": "default", "region": "us-east-1"},
            }
        },
        "gdk_version": "1.0.0",
    }

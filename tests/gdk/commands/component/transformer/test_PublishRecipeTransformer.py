from pathlib import Path
from unittest import TestCase
from unittest.mock import call, Mock

import pytest

from gdk.commands.component.transformer.PublishRecipeTransformer import PublishRecipeTransformer
from gdk.common.CaseInsensitive import CaseInsensitiveRecipeFile, CaseInsensitiveDict
from gdk.commands.component.config.ComponentPublishConfiguration import ComponentPublishConfiguration
import boto3
from botocore.stub import Stubber
from gdk.common.config.GDKProject import GDKProject


class PublishRecipeTransformerTest(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker):
        self.mocker = mocker
        self.mock_get_proj_config = self.mocker.patch(
            "gdk.common.configuration.get_configuration",
            return_value=config(),
        )
        self.mocker.patch.object(GDKProject, "_get_recipe_file", return_value=Path(".").joinpath("recipe.json").resolve())

        self.case_insensitive_recipe = CaseInsensitiveDict(fake_recipe())
        self.mock_component_recipe = self.mocker.patch.object(
            CaseInsensitiveRecipeFile,
            "read",
            return_value=self.case_insensitive_recipe,
        )
        self.gg_client = boto3.client("greengrassv2", region_name="region")
        self.sts_client = boto3.client("sts", region_name="region")

        def _clients(*args, **kwargs):
            if args[0] == "greengrassv2":
                return self.gg_client
            elif args[0] == "sts":
                return self.sts_client

        self.mocker.patch("boto3.client", side_effect=_clients)
        self.gg_client_stub = Stubber(self.gg_client)
        self.sts_client_stub = Stubber(self.sts_client)
        self.gg_client_stub.activate()
        self.sts_client_stub.activate()
        self.sts_client_stub.add_response("get_caller_identity", {"Account": "123456789012"})
        boto3_ses = Mock()
        boto3_ses.get_partition_for_region.return_value = "aws"
        self.mocker.patch("boto3.Session", return_value=boto3_ses)
        self.gg_client_stub.add_response(
            "list_component_versions",
            {
                "componentVersions": [],
                "nextToken": "string",
            },
        )

    def test_publish_recipe_transformer_instantiate(self):
        pc = ComponentPublishConfiguration({})
        prg = PublishRecipeTransformer(pc)
        assert prg.project_config == pc

    def test_transform(self):
        brg = PublishRecipeTransformer(ComponentPublishConfiguration({}))
        mock_update = self.mocker.patch.object(PublishRecipeTransformer, "update_component_recipe_file", return_value=None)
        mock_create = self.mocker.patch.object(PublishRecipeTransformer, "create_publish_recipe_file", return_value=None)
        brg.transform()

        assert mock_update.call_args_list == [call(self.mock_component_recipe.return_value)]
        assert mock_create.call_args_list == [call(self.mock_component_recipe.return_value)]

    def test_update_component_recipe_file(self):
        recipe = {
            "RecipeFormatVersion": "2020-01-25",
            "ComponentName": "com.example.HelloWorld",
            "ComponentVersion": "1.0.0",
            "ComponentDescription": "My first Greengrass component.",
            "ComponentPublisher": "Amazon",
            "ComponentConfiguration": {"DefaultConfiguration": {"Message": "world"}},
            "Manifests": [
                {
                    "Platform": {"os": "linux"},
                    "Lifecycle": {"Run": "python3 -u {artifacts:path}/hello_world.py '{configuration:/Message}'"},
                    "Artifacts": [{"UrI": "s3://hello_world.py"}],
                }
            ],
        }

        mock_iter_dir_list = [Path("hello_world.py").resolve()]
        mock_glob = self.mocker.patch("pathlib.Path.glob", return_value=mock_iter_dir_list)

        prg = PublishRecipeTransformer(ComponentPublishConfiguration({"bucket": "default"}))
        cis_recipe = CaseInsensitiveDict(recipe)
        prg.update_component_recipe_file(cis_recipe)
        assert mock_glob.call_args_list == [call("hello_world.py")]
        assert cis_recipe["Manifests"][0]["Artifacts"][0]["URI"] == "s3://default/com.example.HelloWorld/1.0.0/hello_world.py"

    def test_update_component_recipe_file_with_docker_uris(self):
        recipe = {
            "RecipeFormatVersion": "2020-01-25",
            "ComponentName": "com.example.HelloWorld",
            "ComponentVersion": "1.0.0",
            "ComponentDescription": "My first Greengrass component.",
            "ComponentPublisher": "Amazon",
            "ComponentConfiguration": {"DefaultConfiguration": {"Message": "world"}},
            "Manifests": [
                {
                    "Platform": {"os": "linux"},
                    "Lifecycle": {"Run": "python3 -u {artifacts:path}/hello_world.py '{configuration:/Message}'"},
                    "Artifacts": [{"UrI": "s3://hello_world.py"}, {"UrI": "docker://hello_world.py"}],
                }
            ],
        }

        mock_iter_dir_list = [Path("hello_world.py").resolve()]
        mock_glob = self.mocker.patch("pathlib.Path.glob", return_value=mock_iter_dir_list)

        prg = PublishRecipeTransformer(ComponentPublishConfiguration({"bucket": "default"}))
        cis_recipe = CaseInsensitiveDict(recipe)
        prg.update_component_recipe_file(cis_recipe)
        assert mock_glob.call_args_list == [call("hello_world.py")]
        assert cis_recipe["Manifests"][0]["Artifacts"][0]["URI"] == "s3://default/com.example.HelloWorld/1.0.0/hello_world.py"

    def test_update_component_recipe_file_not_found(self):
        recipe = {
            "RecipeFormatVersion": "2020-01-25",
            "ComponentName": "com.example.HelloWorld",
            "ComponentVersion": "1.0.0",
            "ComponentDescription": "My first Greengrass component.",
            "ComponentPublisher": "Amazon",
            "ComponentConfiguration": {"DefaultConfiguration": {"Message": "world"}},
            "Manifests": [
                {
                    "Platform": {"os": "linux"},
                    "Lifecycle": {"Run": "python3 -u {artifacts:path}/hello_world.py '{configuration:/Message}'"},
                    "Artifacts": [{"uri": "s3://not-in_build.py"}],
                }
            ],
        }

        mock_iter_dir_list = []
        mock_glob = self.mocker.patch("pathlib.Path.glob", return_value=mock_iter_dir_list)

        prg = PublishRecipeTransformer(ComponentPublishConfiguration({}))
        cis_recipe = CaseInsensitiveDict(recipe)
        prg.update_component_recipe_file(cis_recipe)
        assert mock_glob.call_args_list == [call("not-in_build.py")]
        assert cis_recipe["Manifests"][0]["Artifacts"][0]["URI"] == "s3://not-in_build.py"

    def test_update_component_recipe_file_not_build(self):
        proj_config = ComponentPublishConfiguration({})
        proj_config.component_name = "not-com.example.HelloWorld"
        prg = PublishRecipeTransformer(proj_config)
        cis_recipe = CaseInsensitiveDict(fake_recipe())
        with pytest.raises(Exception) as e:
            prg.update_component_recipe_file(cis_recipe)
        assert "as it is not build.\nBuild the component `gdk component build` before publishing it." in e.value.args[0]

    def test_update_component_recipe_file_not_manifests(self):
        recipe = {
            "RecipeFormatVersion": "2020-01-25",
            "ComponentName": "com.example.HelloWorld",
            "ComponentVersion": "1.0.0",
            "ComponentDescription": "My first Greengrass component.",
            "ComponentPublisher": "Amazon",
            "ComponentConfiguration": {"DefaultConfiguration": {"Message": "world"}},
        }

        mock_iter_dir_list = [Path("hello_world.py").resolve()]
        mock_glob = self.mocker.patch("pathlib.Path.glob", return_value=mock_iter_dir_list)

        prg = PublishRecipeTransformer(ComponentPublishConfiguration({}))
        cis_recipe = CaseInsensitiveDict(recipe)
        prg.update_component_recipe_file(cis_recipe)
        assert not mock_glob.called

    def test_update_component_recipe_file_not_artifacts_in_manifest(self):
        recipe = {
            "RecipeFormatVersion": "2020-01-25",
            "ComponentName": "com.example.HelloWorld",
            "ComponentVersion": "1.0.0",
            "ComponentDescription": "My first Greengrass component.",
            "ComponentPublisher": "Amazon",
            "ComponentConfiguration": {"DefaultConfiguration": {"Message": "world"}},
            "Manifests": [
                {
                    "Platform": {"os": "linux"},
                    "Lifecycle": {"Run": "python3 -u {artifacts:path}/hello_world.py '{configuration:/Message}'"},
                }
            ],
        }

        mock_iter_dir_list = [Path("hello_world.py").resolve()]
        mock_glob = self.mocker.patch("pathlib.Path.glob", return_value=mock_iter_dir_list)

        prg = PublishRecipeTransformer(ComponentPublishConfiguration({}))
        cis_recipe = CaseInsensitiveDict(recipe)
        prg.update_component_recipe_file(cis_recipe)
        assert not mock_glob.called

    def test_update_component_recipe_file_not_uri_in_artifacts(self):
        recipe = {
            "RecipeFormatVersion": "2020-01-25",
            "ComponentName": "com.example.HelloWorld",
            "ComponentVersion": "1.0.0",
            "ComponentDescription": "My first Greengrass component.",
            "ComponentPublisher": "Amazon",
            "ComponentConfiguration": {"DefaultConfiguration": {"Message": "world"}},
            "Manifests": [
                {
                    "Platform": {"os": "linux"},
                    "Lifecycle": {"Run": "python3 -u {artifacts:path}/hello_world.py '{configuration:/Message}'"},
                    "Artifacts": [{}],
                }
            ],
        }

        mock_iter_dir_list = [Path("hello_world.py").resolve()]
        mock_glob = self.mocker.patch("pathlib.Path.glob", return_value=mock_iter_dir_list)

        prg = PublishRecipeTransformer(ComponentPublishConfiguration({}))
        cis_recipe = CaseInsensitiveDict(recipe)
        prg.update_component_recipe_file(cis_recipe)
        assert not mock_glob.called

    def test_create_publish_recipe_file_good_recipe_size(self):
        self.mocker.patch("gdk.common.utils.is_recipe_size_valid", return_value=[True, 1000])
        prg = PublishRecipeTransformer(ComponentPublishConfiguration({}))
        cis_recipe = CaseInsensitiveDict(fake_recipe())
        mocker_recipe_write = self.mocker.patch.object(CaseInsensitiveRecipeFile, "write")
        prg.create_publish_recipe_file(cis_recipe)
        recipe_path = Path(prg.project_config.publish_recipe_file).resolve()
        assert mocker_recipe_write.call_args_list == [call(recipe_path, cis_recipe)]

    def test_create_publish_recipe_file_oversized_recipe(self):
        self.mocker.patch("gdk.common.utils.is_recipe_size_valid", return_value=[False, 17000])
        prg = PublishRecipeTransformer(ComponentPublishConfiguration({}))
        cis_recipe = CaseInsensitiveDict(fake_recipe())
        self.mocker.patch.object(CaseInsensitiveRecipeFile, "write")
        with pytest.raises(Exception) as e:
            prg.create_publish_recipe_file(cis_recipe)
        assert "is too big with a size of 17000 bytes. Component recipes must be 16 kB or smaller" in str(e)


def config():
    return {
        "component": {
            "com.example.HelloWorld": {
                "author": "<PLACEHOLDER_AUTHOR>",
                "version": "1.0.0",
                "build": {"build_system": "zip"},
                "publish": {"bucket": "<PLACEHOLDER_BUCKET>", "region": "region"},
            }
        },
        "gdk_version": "1.0.0",
    }


def fake_recipe():
    return {
        "RecipeFormatVersion": "2020-01-25",
        "ComponentName": "com.example.HelloWorld",
        "ComponentVersion": "1.0.0",
        "ComponentDescription": "My first Greengrass component.",
        "ComponentPublisher": "Amazon",
        "ComponentConfiguration": {"DefaultConfiguration": {"Message": "world"}},
        "Manifests": [
            {
                "Platform": {"os": "linux"},
                "Lifecycle": {"Run": "python3 -u {artifacts:path}/hello_world.py '{configuration:/Message}'"},
                "Artifacts": [{"URI": "s3://DOC-EXAMPLE-BUCKET/artifacts/com.example.HelloWorld/1.0.0/hello_world.py"}],
            }
        ],
    }

from pathlib import Path
from unittest import TestCase
from unittest.mock import call

import pytest
import boto3

from gdk.commands.component.transformer.BuildRecipeTransformer import (
    BuildRecipeTransformer,
)
from gdk.common.CaseInsensitive import CaseInsensitiveRecipeFile, CaseInsensitiveDict


class BuildRecipeTransformerTest(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker):
        self.mocker = mocker
        self.mock_get_proj_config = self.mocker.patch(
            "gdk.commands.component.project_utils.get_project_config_values",
            return_value=project_config(),
        )
        self.case_insensitive_recipe = CaseInsensitiveDict(fake_recipe())
        self.mock_component_recipe = self.mocker.patch.object(
            CaseInsensitiveRecipeFile,
            "read",
            return_value=self.case_insensitive_recipe,
        )

    def test_build_recipe_transformer_instantiate(self):
        pc = project_config()
        brg = BuildRecipeTransformer(pc)
        assert brg.project_config == pc

    def test_transform(self):
        brg = BuildRecipeTransformer(project_config())
        build_folders = [Path("zip-build").resolve()]
        mock_update = self.mocker.patch.object(
            BuildRecipeTransformer, "update_component_recipe_file", return_value=None
        )
        mock_create = self.mocker.patch.object(
            BuildRecipeTransformer, "create_build_recipe_file", return_value=None
        )
        brg.transform(build_folders)

        assert mock_update.call_args_list == [
            call(self.mock_component_recipe.return_value, build_folders)
        ]
        assert mock_create.call_args_list == [
            call(self.mock_component_recipe.return_value)
        ]

    def test_update_component_recipe_file_in_build(self):
        brg = BuildRecipeTransformer(project_config())
        build_folders = [Path("zip-build").resolve()]
        mock_is_artifact_in_s3 = self.mocker.patch.object(
            BuildRecipeTransformer, "is_artifact_in_s3", return_value=False
        )
        mock_is_artifact_in_build = self.mocker.patch.object(
            BuildRecipeTransformer, "is_artifact_in_build", return_value=True
        )
        brg.update_component_recipe_file(self.case_insensitive_recipe, build_folders)
        artifact_uri = {
            "URI": "s3://DOC-EXAMPLE-BUCKET/artifacts/com.example.HelloWorld/1.0.0/hello_world.py"
        }
        assert mock_is_artifact_in_build.call_args_list == [
            call(artifact_uri, build_folders)
        ]
        assert not mock_is_artifact_in_s3.called

    def test_update_component_recipe_file_in_s3(self):
        brg = BuildRecipeTransformer(project_config())
        build_folders = [Path("zip-build").resolve()]
        mock_is_artifact_in_s3 = self.mocker.patch.object(
            BuildRecipeTransformer, "is_artifact_in_s3", return_value=True
        )
        mock_is_artifact_in_build = self.mocker.patch.object(
            BuildRecipeTransformer, "is_artifact_in_build", return_value=False
        )
        brg.update_component_recipe_file(self.case_insensitive_recipe, build_folders)
        artifact_uri = {
            "URI": "s3://DOC-EXAMPLE-BUCKET/artifacts/com.example.HelloWorld/1.0.0/hello_world.py"
        }
        assert mock_is_artifact_in_build.call_args_list == [
            call(artifact_uri, build_folders)
        ]
        assert mock_is_artifact_in_s3.called

    def test_update_component_recipe_file_not_in_s3_not_in_build(self):
        brg = BuildRecipeTransformer(project_config())
        build_folders = [Path("zip-build").resolve()]
        mock_is_artifact_in_s3 = self.mocker.patch.object(
            BuildRecipeTransformer, "is_artifact_in_s3", return_value=False
        )
        mock_is_artifact_in_build = self.mocker.patch.object(
            BuildRecipeTransformer, "is_artifact_in_build", return_value=False
        )
        with pytest.raises(Exception) as e:
            brg.update_component_recipe_file(
                self.case_insensitive_recipe, build_folders
            )
        artifact_uri = {
            "URI": "s3://DOC-EXAMPLE-BUCKET/artifacts/com.example.HelloWorld/1.0.0/hello_world.py"
        }
        assert (
            "Could not find artifact with URI 's3://DOC-EXAMPLE-BUCKET/artifacts/com.example.HelloWorld/1.0.0/hello_world.py'"
            " on s3 or inside the build folders." in e.value.args[0]
        )

        assert mock_is_artifact_in_build.call_args_list == [
            call(artifact_uri, build_folders)
        ]
        assert mock_is_artifact_in_s3.called

    def test_update_component_recipe_file_no_manifest_in_recipe(self):
        mock_is_artifact_in_build = self.mocker.patch.object(
            BuildRecipeTransformer, "is_artifact_in_build", return_value=True
        )
        mock_is_artifact_in_s3 = self.mocker.patch.object(
            BuildRecipeTransformer, "is_artifact_in_s3", return_value=False
        )

        build_folders = [Path("zip-build").resolve()]
        no_manifest_recipe = {
            "RecipeFormatVersion": "2020-01-25",
            "ComponentName": "com.example.HelloWorld",
            "ComponentVersion": "1.0.0",
            "ComponentDescription": "My first Greengrass component.",
            "ComponentPublisher": "Amazon",
            "ComponentConfiguration": {"DefaultConfiguration": {"Message": "world"}},
        }
        brg = BuildRecipeTransformer(project_config())
        brg.update_component_recipe_file(
            CaseInsensitiveDict(no_manifest_recipe), build_folders
        )
        assert not mock_is_artifact_in_build.called
        assert not mock_is_artifact_in_s3.called

    def test_update_component_recipe_file_no_artifacts_in_recipe(self):
        mock_is_artifact_in_build = self.mocker.patch.object(
            BuildRecipeTransformer, "is_artifact_in_build", return_value=True
        )
        mock_is_artifact_in_s3 = self.mocker.patch.object(
            BuildRecipeTransformer, "is_artifact_in_s3", return_value=False
        )

        build_folders = [Path("zip-build").resolve()]

        no_artifacts_in_recipe = {
            "RecipeFormatVersion": "2020-01-25",
            "ComponentName": "com.example.HelloWorld",
            "ComponentVersion": "1.0.0",
            "ComponentDescription": "My first Greengrass component.",
            "ComponentPublisher": "Amazon",
            "ComponentConfiguration": {"DefaultConfiguration": {"Message": "world"}},
            "Manifests": [
                {
                    "Platform": {"os": "linux"},
                    "Lifecycle": {
                        "Run": "python3 -u {artifacts:path}/hello_world.py '{configuration:/Message}'"
                    },
                }
            ],
        }
        brg = BuildRecipeTransformer(project_config())
        brg.update_component_recipe_file(
            CaseInsensitiveDict(no_artifacts_in_recipe), build_folders
        )
        assert not mock_is_artifact_in_build.called
        assert not mock_is_artifact_in_s3.called

    def test_find_artifacts_and_update_uri_no_artifact_uri_in_recipe(self):
        mock_is_artifact_in_build = self.mocker.patch.object(
            BuildRecipeTransformer, "is_artifact_in_build", return_value=True
        )
        mock_is_artifact_in_s3 = self.mocker.patch.object(
            BuildRecipeTransformer, "is_artifact_in_s3", return_value=False
        )

        build_folders = [Path("zip-build").resolve()]

        no_artifacts_in_recipe = {
            "RecipeFormatVersion": "2020-01-25",
            "ComponentName": "com.example.HelloWorld",
            "ComponentVersion": "1.0.0",
            "ComponentDescription": "My first Greengrass component.",
            "ComponentPublisher": "Amazon",
            "ComponentConfiguration": {"DefaultConfiguration": {"Message": "world"}},
            "Manifests": [
                {
                    "Platform": {"os": "linux"},
                    "Lifecycle": {
                        "Run": "python3 -u {artifacts:path}/hello_world.py '{configuration:/Message}'"
                    },
                    "Artifacts": [{}],
                }
            ],
        }
        brg = BuildRecipeTransformer(project_config())
        brg.update_component_recipe_file(
            CaseInsensitiveDict(no_artifacts_in_recipe), build_folders
        )
        assert not mock_is_artifact_in_build.called
        assert not mock_is_artifact_in_s3.called

    def test_is_artifact_in_build(self):
        zip_build_path = [Path("zip-build").resolve()]
        mock_shutil_copy = self.mocker.patch("shutil.copy")
        mock_is_file = self.mocker.patch("pathlib.Path.is_file", return_value=True)
        brg = BuildRecipeTransformer(project_config())
        artifact_uri = CaseInsensitiveDict(
            {
                "uri": "s3://DOC-EXAMPLE-BUCKET/artifacts/com.example.HelloWorld/1.0.0/hello_world.py"
            }
        )
        assert brg.is_artifact_in_build(artifact_uri, zip_build_path)

        assert mock_shutil_copy.called
        assert mock_is_file.assert_called_once
        mock_shutil_copy.assert_called_with(
            Path("zip-build").joinpath("hello_world.py").resolve(),
            self.mock_get_proj_config.return_value["gg_build_component_artifacts_dir"],
        )
        assert artifact_uri.to_dict() == {
            "uri": "s3://BUCKET_NAME/COMPONENT_NAME/COMPONENT_VERSION/hello_world.py"
        }

    def test_is_artifact_in_build_not_exists(self):
        zip_build_path = [Path("zip-build").resolve()]
        mock_shutil_copy = self.mocker.patch("shutil.copy")
        mock_is_file = self.mocker.patch("pathlib.Path.is_file", return_value=False)
        brg = BuildRecipeTransformer(project_config())
        artifact_uri = CaseInsensitiveDict(
            {
                "uri": "s3://DOC-EXAMPLE-BUCKET/artifacts/com.example.HelloWorld/1.0.0/hello_world.py"
            }
        )
        assert not brg.is_artifact_in_build(artifact_uri, zip_build_path)

        assert not mock_shutil_copy.called
        assert mock_is_file.assert_called_once
        assert artifact_uri == {
            "uri": "s3://DOC-EXAMPLE-BUCKET/artifacts/com.example.HelloWorld/1.0.0/hello_world.py"
        }

    def test_is_artifact_in_s3_found(self):
        test_s3_uri = "s3://bucket/object-key.zip"
        mock_client = self.mocker.patch("boto3.client", return_value=None)
        mock_s3_head_object = self.mocker.patch(
            "boto3.client.head_object",
            return_value={"ResponseMetadata": {"HTTPStatusCode": 200}},
        )
        brg = BuildRecipeTransformer(project_config())
        assert brg.is_artifact_in_s3(mock_client, test_s3_uri)
        assert mock_s3_head_object.called
        mock_s3_head_object.assert_called_with(Bucket="bucket", Key="object-key.zip")

    def test_is_artifact_in_s3_not_found(self):
        test_s3_uri = "s3://bucket/object-key.zip"

        mock_client = self.mocker.patch("boto3.client", return_value=None)

        def throw_err(*args, **kwargs):
            ex = boto3.client("s3").exceptions.ClientError(
                {"Error": {"Code": "404", "Message": "Not Found"}}, "HeadObject"
            )
            raise ex

        mock_s3_head_object = self.mocker.patch(
            "boto3.client.head_object",
            side_effect=throw_err,
        )

        brg = BuildRecipeTransformer(project_config())
        assert not brg.is_artifact_in_s3(mock_client, test_s3_uri)
        mock_s3_head_object.assert_called_with(Bucket="bucket", Key="object-key.zip")

    def test_find_artifacts_and_update_uri_mix_uri_in_recipe_call_counts(self):
        build_folders = [Path("zip-build").resolve()]
        recipe_mixed_uris = {
            "RecipeFormatVersion": "2020-01-25",
            "ComponentName": "com.example.HelloWorld",
            "ComponentVersion": "1.0.0",
            "ComponentDescription": "My first Greengrass component.",
            "ComponentPublisher": "Amazon",
            "ComponentConfiguration": {"DefaultConfiguration": {"Message": "world"}},
            "Manifests": [
                {
                    "Platform": {"os": "linux"},
                    "Lifecycle": {
                        "Run": "python3 -u {artifacts:path}/hello_world.py '{configuration:/Message}'"
                    },
                    "Artifacts": [
                        {"URI": "s3://found-in-build.py"},
                        {"URI": "s3://found-1-on-s3.py"},
                        {"URI": "s3://found-2-on-s3.py"},
                        {"URI": "docker://not-s3-uri.py"},
                    ],
                }
            ],
        }

        def artifact_found(*args, **kwargs):
            if args[0] == {"URI": "s3://found-in-build.py"}:
                return True
            else:
                return False

        mock_is_artifact_in_build = self.mocker.patch.object(
            BuildRecipeTransformer, "is_artifact_in_build", side_effect=artifact_found
        )
        mock_client = self.mocker.patch("boto3.client", return_value=None)
        mock_is_artifact_in_s3 = self.mocker.patch.object(
            BuildRecipeTransformer, "is_artifact_in_s3"
        )
        brg = BuildRecipeTransformer(project_config())
        brg.update_component_recipe_file(
            CaseInsensitiveDict(recipe_mixed_uris), build_folders
        )
        assert mock_is_artifact_in_build.call_args_list == [
            call({"URI": "s3://found-in-build.py"}, build_folders),
            call({"URI": "s3://found-1-on-s3.py"}, build_folders),
            call({"URI": "s3://found-2-on-s3.py"}, build_folders),
        ]
        assert mock_is_artifact_in_s3.call_args_list == [
            call(mock_client.return_value, "s3://found-1-on-s3.py"),
            call(mock_client.return_value, "s3://found-2-on-s3.py"),
        ]

    def test_create_recipe_file_json(self):
        pc = project_config()
        brg = BuildRecipeTransformer(pc)
        file_name = (
            Path(pc["gg_build_recipes_dir"])
            .joinpath("valid_component_recipe.json")
            .resolve()
        )

        recipe = CaseInsensitiveDict(fake_recipe())
        mocker_recipe_write = self.mocker.patch.object(
            CaseInsensitiveRecipeFile, "write"
        )
        brg.create_build_recipe_file(recipe)
        assert mocker_recipe_write.call_args_list == [call(file_name, recipe)]

    def test_create_recipe_file_yaml(self):
        pc = project_config()
        brg = BuildRecipeTransformer(pc)
        brg.project_config["component_recipe_file"] = Path("some-yaml.yaml").resolve()
        file_name = (
            Path(pc["gg_build_recipes_dir"]).joinpath("some-yaml.yaml").resolve()
        )

        recipe = CaseInsensitiveDict(fake_recipe())
        mocker_recipe_write = self.mocker.patch.object(
            CaseInsensitiveRecipeFile, "write"
        )
        brg.create_build_recipe_file(recipe)
        assert mocker_recipe_write.call_args_list == [call(file_name, recipe)]


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
            "/src/GDK-CLI-Internal/tests/gdk/static/project_utils/valid_component_recipe.json"
        ),
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
                "Lifecycle": {
                    "Run": "python3 -u {artifacts:path}/hello_world.py '{configuration:/Message}'"
                },
                "Artifacts": [
                    {
                        "URI": "s3://DOC-EXAMPLE-BUCKET/artifacts/com.example.HelloWorld/1.0.0/hello_world.py"
                    }
                ],
            }
        ],
    }

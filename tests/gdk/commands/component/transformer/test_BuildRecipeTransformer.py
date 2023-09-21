from pathlib import Path
from unittest import TestCase
from unittest.mock import call

import pytest

from gdk.commands.component.transformer.BuildRecipeTransformer import BuildRecipeTransformer
from gdk.common.CaseInsensitive import CaseInsensitiveRecipeFile, CaseInsensitiveDict
from gdk.commands.component.config.ComponentBuildConfiguration import ComponentBuildConfiguration
from gdk.common.config.GDKProject import GDKProject
from gdk.aws_clients.S3Client import S3Client


class BuildRecipeTransformerTest(TestCase):
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

    def test_build_recipe_transformer_instantiate(self):
        pc = ComponentBuildConfiguration({})
        brg = BuildRecipeTransformer(pc)
        assert brg.project_config == pc

    def test_transform_good_recipe_size(self):
        self.mocker.patch("gdk.common.utils.is_recipe_size_valid", return_value=[True, 1000])
        brg = BuildRecipeTransformer(ComponentBuildConfiguration({}))
        build_folders = [Path("zip-build").resolve()]
        mock_update = self.mocker.patch.object(BuildRecipeTransformer, "update_component_recipe_file", return_value=None)
        mock_create = self.mocker.patch.object(BuildRecipeTransformer, "create_build_recipe_file", return_value=None)
        brg.transform(build_folders)

        assert mock_update.call_args_list == [call(self.mock_component_recipe.return_value, build_folders)]
        assert mock_create.call_args_list == [call(self.mock_component_recipe.return_value)]

    def test_transform_oversized_recipe(self):
        self.mocker.patch("gdk.common.utils.is_recipe_size_valid", return_value=[False, 17000])
        brg = BuildRecipeTransformer(ComponentBuildConfiguration({}))
        build_folders = [Path("zip-build").resolve()]
        with pytest.raises(Exception) as e:
            brg.transform(build_folders)

        assert "has an invalid size of 17000 bytes. Please make sure it does not exceed 16kB (16000 bytes)" in str(e)

    def test_update_component_recipe_file_in_build(self):
        brg = BuildRecipeTransformer(ComponentBuildConfiguration({}))
        build_folders = [Path("zip-build").resolve()]
        mock_is_artifact_in_s3 = self.mocker.patch.object(S3Client, "s3_artifact_exists", return_value=False)
        mock_is_artifact_in_build = self.mocker.patch.object(BuildRecipeTransformer, "is_artifact_in_build", return_value=True)
        brg.update_component_recipe_file(self.case_insensitive_recipe, build_folders)
        artifact_uri = {"URI": "s3://DOC-EXAMPLE-BUCKET/artifacts/com.example.HelloWorld/1.0.0/hello_world.py"}
        assert mock_is_artifact_in_build.call_args_list == [call(artifact_uri, build_folders)]
        assert not mock_is_artifact_in_s3.called

    def test_update_component_recipe_file_in_s3(self):
        brg = BuildRecipeTransformer(ComponentBuildConfiguration({}))
        build_folders = [Path("zip-build").resolve()]
        mock_is_artifact_in_s3 = self.mocker.patch.object(S3Client, "s3_artifact_exists", return_value=True)
        mock_is_artifact_in_build = self.mocker.patch.object(
            BuildRecipeTransformer, "is_artifact_in_build", return_value=False
        )
        brg.update_component_recipe_file(self.case_insensitive_recipe, build_folders)
        artifact_uri = {"URI": "s3://DOC-EXAMPLE-BUCKET/artifacts/com.example.HelloWorld/1.0.0/hello_world.py"}
        assert mock_is_artifact_in_build.call_args_list == [call(artifact_uri, build_folders)]
        assert mock_is_artifact_in_s3.called

    def test_update_component_recipe_file_not_in_s3_not_in_build(self):
        brg = BuildRecipeTransformer(ComponentBuildConfiguration({}))
        build_folders = [Path("zip-build").resolve()]
        mock_is_artifact_in_s3 = self.mocker.patch.object(S3Client, "s3_artifact_exists", return_value=False)
        mock_is_artifact_in_build = self.mocker.patch.object(
            BuildRecipeTransformer, "is_artifact_in_build", return_value=False
        )
        with pytest.raises(Exception) as e:
            brg.update_component_recipe_file(self.case_insensitive_recipe, build_folders)
        artifact_uri = {"URI": "s3://DOC-EXAMPLE-BUCKET/artifacts/com.example.HelloWorld/1.0.0/hello_world.py"}
        assert (
            "Could not find artifact with URI 's3://DOC-EXAMPLE-BUCKET/artifacts/com.example.HelloWorld/1.0.0/hello_world.py'"
            " on s3 or inside the build folders."
            in e.value.args[0]
        )

        assert mock_is_artifact_in_build.call_args_list == [call(artifact_uri, build_folders)]
        assert mock_is_artifact_in_s3.called

    def test_update_component_recipe_file_no_manifest_in_recipe(self):
        mock_is_artifact_in_build = self.mocker.patch.object(BuildRecipeTransformer, "is_artifact_in_build", return_value=True)
        mock_is_artifact_in_s3 = self.mocker.patch.object(S3Client, "s3_artifact_exists", return_value=False)

        build_folders = [Path("zip-build").resolve()]
        no_manifest_recipe = {
            "RecipeFormatVersion": "2020-01-25",
            "ComponentName": "com.example.HelloWorld",
            "ComponentVersion": "1.0.0",
            "ComponentDescription": "My first Greengrass component.",
            "ComponentPublisher": "Amazon",
            "ComponentConfiguration": {"DefaultConfiguration": {"Message": "world"}},
        }
        brg = BuildRecipeTransformer(ComponentBuildConfiguration({}))
        brg.update_component_recipe_file(CaseInsensitiveDict(no_manifest_recipe), build_folders)
        assert not mock_is_artifact_in_build.called
        assert not mock_is_artifact_in_s3.called

    def test_update_component_recipe_file_no_artifacts_in_recipe(self):
        mock_is_artifact_in_build = self.mocker.patch.object(BuildRecipeTransformer, "is_artifact_in_build", return_value=True)
        mock_is_artifact_in_s3 = self.mocker.patch.object(S3Client, "s3_artifact_exists", return_value=False)

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
                    "Lifecycle": {"Run": "python3 -u {artifacts:path}/hello_world.py '{configuration:/Message}'"},
                }
            ],
        }
        brg = BuildRecipeTransformer(ComponentBuildConfiguration({}))
        brg.update_component_recipe_file(CaseInsensitiveDict(no_artifacts_in_recipe), build_folders)
        assert not mock_is_artifact_in_build.called
        assert not mock_is_artifact_in_s3.called

    def test_find_artifacts_and_update_uri_no_artifact_uri_in_recipe(self):
        mock_is_artifact_in_build = self.mocker.patch.object(BuildRecipeTransformer, "is_artifact_in_build", return_value=True)
        mock_is_artifact_in_s3 = self.mocker.patch.object(S3Client, "s3_artifact_exists", return_value=False)

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
                    "Lifecycle": {"Run": "python3 -u {artifacts:path}/hello_world.py '{configuration:/Message}'"},
                    "Artifacts": [{}],
                }
            ],
        }
        brg = BuildRecipeTransformer(ComponentBuildConfiguration({}))
        brg.update_component_recipe_file(CaseInsensitiveDict(no_artifacts_in_recipe), build_folders)
        assert not mock_is_artifact_in_build.called
        assert not mock_is_artifact_in_s3.called

    def test_is_artifact_in_build(self):
        zip_build_path = [Path("zip-build").resolve()]
        mock_shutil_copy = self.mocker.patch("shutil.copy")
        mock_is_file = self.mocker.patch("pathlib.Path.is_file", return_value=True)
        pc = ComponentBuildConfiguration({})
        brg = BuildRecipeTransformer(pc)
        artifact_uri = CaseInsensitiveDict(
            {"uri": "s3://DOC-EXAMPLE-BUCKET/artifacts/com.example.HelloWorld/1.0.0/hello_world.py"}
        )
        assert brg.is_artifact_in_build(artifact_uri, zip_build_path)

        assert mock_shutil_copy.called
        assert mock_is_file.assert_called_once
        mock_shutil_copy.assert_called_with(
            Path("zip-build").joinpath("hello_world.py").resolve(),
            pc.gg_build_component_artifacts_dir,
        )
        assert artifact_uri.to_dict() == {"uri": "s3://BUCKET_NAME/COMPONENT_NAME/COMPONENT_VERSION/hello_world.py"}

    def test_is_artifact_in_build_not_exists(self):
        zip_build_path = [Path("zip-build").resolve()]
        mock_shutil_copy = self.mocker.patch("shutil.copy")
        mock_is_file = self.mocker.patch("pathlib.Path.is_file", return_value=False)
        brg = BuildRecipeTransformer(ComponentBuildConfiguration({}))
        artifact_uri = CaseInsensitiveDict(
            {"uri": "s3://DOC-EXAMPLE-BUCKET/artifacts/com.example.HelloWorld/1.0.0/hello_world.py"}
        )
        assert not brg.is_artifact_in_build(artifact_uri, zip_build_path)

        assert not mock_shutil_copy.called
        assert mock_is_file.assert_called_once
        assert artifact_uri == {"uri": "s3://DOC-EXAMPLE-BUCKET/artifacts/com.example.HelloWorld/1.0.0/hello_world.py"}

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
                    "Lifecycle": {"Run": "python3 -u {artifacts:path}/hello_world.py '{configuration:/Message}'"},
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
        mock_is_artifact_in_s3 = self.mocker.patch.object(S3Client, "s3_artifact_exists")
        brg = BuildRecipeTransformer(ComponentBuildConfiguration({}))
        brg.update_component_recipe_file(CaseInsensitiveDict(recipe_mixed_uris), build_folders)
        assert mock_is_artifact_in_build.call_args_list == [
            call({"URI": "s3://found-in-build.py"}, build_folders),
            call({"URI": "s3://found-1-on-s3.py"}, build_folders),
            call({"URI": "s3://found-2-on-s3.py"}, build_folders),
        ]
        assert mock_is_artifact_in_s3.call_args_list == [
            call("s3://found-1-on-s3.py"),
            call("s3://found-2-on-s3.py"),
        ]

    def test_create_recipe_file_json(self):
        pc = ComponentBuildConfiguration({})
        brg = BuildRecipeTransformer(pc)
        file_name = pc.gg_build_recipes_dir.joinpath("recipe.json").resolve()

        recipe = CaseInsensitiveDict(fake_recipe())
        mocker_recipe_write = self.mocker.patch.object(CaseInsensitiveRecipeFile, "write")
        brg.create_build_recipe_file(recipe)
        assert mocker_recipe_write.call_args_list == [call(file_name, recipe)]

    def test_create_recipe_file_yaml(self):
        self.mocker.patch.object(GDKProject, "_get_recipe_file", return_value=Path(".").joinpath("recipe.yaml").resolve())
        pc = ComponentBuildConfiguration({})
        brg = BuildRecipeTransformer(pc)
        file_name = pc.gg_build_recipes_dir.joinpath("recipe.yaml").resolve()

        recipe = CaseInsensitiveDict(fake_recipe())
        mocker_recipe_write = self.mocker.patch.object(CaseInsensitiveRecipeFile, "write")
        brg.create_build_recipe_file(recipe)
        assert mocker_recipe_write.call_args_list == [call(file_name, recipe)]


def config():
    return {
        "component": {
            "com.example.PythonLocalPubSub": {
                "author": "<PLACEHOLDER_AUTHOR>",
                "version": "NEXT_PATCH",
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

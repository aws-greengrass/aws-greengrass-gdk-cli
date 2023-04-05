from pathlib import Path
from unittest import TestCase
from unittest.mock import call

import pytest


from gdk.commands.component.transformer.PublishRecipeTransformer import PublishRecipeTransformer
from gdk.common.CaseInsensitive import CaseInsensitiveRecipeFile, CaseInsensitiveDict


class PublishRecipeTransformerTest(TestCase):
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

    def test_publish_recipe_transformer_instantiate(self):
        pc = project_config()
        prg = PublishRecipeTransformer(pc)
        assert prg.project_config == pc

    def test_transform(self):
        brg = PublishRecipeTransformer(project_config())
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

        prg = PublishRecipeTransformer(project_config())
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

        prg = PublishRecipeTransformer(project_config())
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

        prg = PublishRecipeTransformer(project_config())
        cis_recipe = CaseInsensitiveDict(recipe)
        prg.update_component_recipe_file(cis_recipe)
        assert mock_glob.call_args_list == [call("not-in_build.py")]
        assert cis_recipe["Manifests"][0]["Artifacts"][0]["URI"] == "s3://not-in_build.py"

    def test_update_component_recipe_file_not_build(self):
        proj_config = project_config()
        proj_config.update({"component_name": "not-com.example.HelloWorld"})
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

        prg = PublishRecipeTransformer(project_config())
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

        prg = PublishRecipeTransformer(project_config())
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

        prg = PublishRecipeTransformer(project_config())
        cis_recipe = CaseInsensitiveDict(recipe)
        prg.update_component_recipe_file(cis_recipe)
        assert not mock_glob.called

    def test_create_publish_recipe_file(self):
        prg = PublishRecipeTransformer(project_config())
        cis_recipe = CaseInsensitiveDict(fake_recipe())
        mocker_recipe_write = self.mocker.patch.object(CaseInsensitiveRecipeFile, "write")
        prg.create_publish_recipe_file(cis_recipe)
        recipe_path = Path(prg.project_config["publish_recipe_file"]).resolve()
        assert mocker_recipe_write.call_args_list == [call(recipe_path, cis_recipe)]


def project_config():
    return {
        "component_name": "com.example.HelloWorld",
        "component_build_config": {"build_system": "zip"},
        "component_version": "1.0.0",
        "component_author": "abc",
        "bucket": "default",
        "region": "us-east-1",
        "gg_build_directory": Path("/src/GDK-CLI-Internal/greengrass-build"),
        "publish_recipe_file": Path("/src/GDK-CLI-Internal/greengrass-build/recipes/com.example.HelloWorld-1.0.0.json"),
        "gg_build_artifacts_dir": Path("/src/GDK-CLI-Internal/greengrass-build/artifacts"),
        "gg_build_recipes_dir": Path("/src/GDK-CLI-Internal/greengrass-build/recipes"),
        "gg_build_component_artifacts_dir": Path("/src/GDK-CLI-Internal/greengrass-build/artifacts/component_name/1.0.0"),
        "component_recipe_file": Path("/src/GDK-CLI-Internal/tests/gdk/static/project_utils/valid_component_recipe.json"),
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

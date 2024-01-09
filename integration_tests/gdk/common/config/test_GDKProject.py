from pathlib import Path
import pytest
from unittest import TestCase
from gdk.common.config.GDKProject import GDKProject
from gdk.common.GithubUtils import GithubUtils

import gdk.common.exceptions.error_messages as error_messages
import os

import shutil


class GDKProjectTest(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker, tmpdir):
        self.mocker = mocker
        self.mocker.patch.object(GithubUtils, "get_latest_release_name", return_value="1.2.0")
        self.tmpdir = Path(tmpdir).resolve()
        self.c_dir = Path(".").resolve()
        os.chdir(self.tmpdir)

        yield
        os.chdir(self.c_dir)

    def test_GIVEN_project_with_yaml_recipe_WHEN_read_config_THEN_read_default_values(self):
        shutil.copy(
            self.c_dir.joinpath("integration_tests/test_data/config").joinpath("config_without_test.json").resolve(),
            self.tmpdir.joinpath("gdk-config.json"),
        )
        recipe_file = self.tmpdir.joinpath("recipe.yaml")
        recipe_file.touch()

        gdk_config = GDKProject()
        assert gdk_config.component_name == "abc"
        assert gdk_config.test_config.gtf_version == "1.2.0"
        assert gdk_config.test_config.test_build_system == "maven"
        assert gdk_config.test_config.gtf_options == {}

        c_dir = Path(".").resolve()
        assert c_dir.joinpath("greengrass-build") == gdk_config.gg_build_dir
        assert c_dir.joinpath("greengrass-build/artifacts/abc/1.0.0") == gdk_config.gg_build_component_artifacts_dir
        assert c_dir.joinpath("greengrass-build/recipes") == gdk_config.gg_build_recipes_dir
        assert c_dir.joinpath("greengrass-build/artifacts") == gdk_config.gg_build_artifacts_dir
        assert gdk_config.recipe_file == Path(".").joinpath("recipe.yaml").resolve()

    def test_GIVEN_project_with_json_recipe_WHEN_read_test_config_THEN_read_default_values(self):
        shutil.copy(
            self.c_dir.joinpath("integration_tests/test_data/config").joinpath("config.json").resolve(),
            self.tmpdir.joinpath("gdk-config.json"),
        )
        recipe_file = self.tmpdir.joinpath("recipe.json")
        recipe_file.touch()
        gdk_config = GDKProject()
        assert gdk_config.component_name == "abc"
        assert gdk_config.test_config.gtf_version == "1.2.0"
        assert gdk_config.test_config.test_build_system == "maven"
        assert self.tmpdir.joinpath("greengrass-build") == gdk_config.gg_build_dir
        assert self.tmpdir.joinpath("greengrass-build/artifacts/abc/NEXT_PATCH") == gdk_config.gg_build_component_artifacts_dir
        assert self.tmpdir.joinpath("greengrass-build/recipes") == gdk_config.gg_build_recipes_dir
        assert self.tmpdir.joinpath("greengrass-build/artifacts") == gdk_config.gg_build_artifacts_dir
        assert gdk_config.recipe_file == self.tmpdir.joinpath("recipe.json").resolve()

    def test_GIVEN_config_file_with_gtf_test_keys_WHEN_read_test_config_THEN_use_gtf_keys(self):
        shutil.copy(
            self.c_dir.joinpath("integration_tests/test_data/config").joinpath("config_gtf.json").resolve(),
            self.tmpdir.joinpath("gdk-config.json"),
        )
        recipe_file = self.tmpdir.joinpath("recipe.json")
        recipe_file.touch()
        gdk_config = GDKProject()
        assert gdk_config.test_config.gtf_version == "1.2.0"
        assert gdk_config.test_config.gtf_options == {"tags": "testtags"}

    def test_GIVEN_config_file_with_both_gtf_and_otf_test_keys_WHEN_read_test_config_THEN_use_gtf_keys(self):
        shutil.copy(
            self.c_dir.joinpath("integration_tests/test_data/config").joinpath("config_gtf_and_otf.json").resolve(),
            self.tmpdir.joinpath("gdk-config.json"),
        )
        recipe_file = self.tmpdir.joinpath("recipe.json")
        recipe_file.touch()
        gdk_config = GDKProject()
        assert gdk_config.test_config.gtf_version == "1.0.0"
        assert gdk_config.test_config.gtf_options == {"tags": "testtags"}

    def test_GIVEN_project_WHEN_recipe_not_exists_THEN_raise_exception(self):
        # neither recipe.json nor recipe.yaml exists
        shutil.copy(
            self.c_dir.joinpath("integration_tests/test_data/config").joinpath("config.json").resolve(),
            self.tmpdir.joinpath("gdk-config.json"),
        )

        def use_this_for_recipe(*args):
            if args[0] == "recipe.json":
                return []
            elif args[0] == "recipe.yaml":
                return []

        mock_glob = self.mocker.patch("pathlib.Path.glob", side_effect=use_this_for_recipe)
        with pytest.raises(Exception) as e:
            GDKProject()
        assert e.value.args[0] == error_messages.PROJECT_RECIPE_FILE_NOT_FOUND
        # Search for json file and then yaml file.
        assert mock_glob.call_count == 2
        mock_glob.assert_any_call("recipe.json")
        mock_glob.assert_any_call("recipe.yaml")

    def test_GIVEN_project_WHEN_multiple_recipes_exist_THEN_raise_an_exception(self):
        # Both recipe.json and recipe.yaml exists
        shutil.copy(
            self.c_dir.joinpath("integration_tests/test_data/config").joinpath("config.json").resolve(),
            self.tmpdir.joinpath("gdk-config.json"),
        )
        self.tmpdir.joinpath("recipe.json").touch()
        self.tmpdir.joinpath("recipe.yaml").touch()

        with pytest.raises(Exception) as e:
            GDKProject()
        assert error_messages.PROJECT_RECIPE_FILE_NOT_FOUND in e.value.args[0]

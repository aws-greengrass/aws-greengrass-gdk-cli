from pathlib import Path
import pytest
from unittest import TestCase
from gdk.common.config.GDKProject import GDKProject


class GDKProjectTest(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker):
        self.mocker = mocker

    def test_default_values_for_gdk_test_config(self):
        self.mocker.patch(
            "gdk.common.configuration._get_project_config_file",
            return_value=Path(".")
            .joinpath("integration_tests/test_data/config")
            .joinpath("config_without_test.json")
            .resolve(),
        )
        self.mocker.patch("gdk.commands.component.project_utils.get_recipe_file", return_value="recipe.yaml")

        gdk_config = GDKProject()
        assert gdk_config.component_name == "abc"
        assert gdk_config.test_config.otf_version == "1.1.0-SNAPSHOT"
        assert gdk_config.test_config.test_build_system == "maven"
        assert gdk_config.test_config.otf_options == {}

        c_dir = Path(".").resolve()
        assert c_dir.joinpath("greengrass-build") == gdk_config.gg_build_dir
        assert c_dir.joinpath("greengrass-build/artifacts/abc/1.0.0") == gdk_config.gg_build_component_artifacts_dir
        assert c_dir.joinpath("greengrass-build/recipes") == gdk_config.gg_build_recipes_dir
        assert c_dir.joinpath("greengrass-build/artifacts") == gdk_config.gg_build_artifacts_dir
        assert gdk_config.recipe_file == "recipe.yaml"

    def test_values_for_gdk_test_config(self):
        self.mocker.patch(
            "gdk.common.configuration._get_project_config_file",
            return_value=Path(".").joinpath("integration_tests/test_data/config").joinpath("config.json").resolve(),
        )
        self.mocker.patch("gdk.commands.component.project_utils.get_recipe_file", return_value="recipe.json")

        gdk_config = GDKProject()
        assert gdk_config.component_name == "abc"
        assert gdk_config.test_config.otf_version == "1.2.0"
        assert gdk_config.test_config.test_build_system == "maven"
        c_dir = Path(".").resolve()
        assert c_dir.joinpath("greengrass-build") == gdk_config.gg_build_dir
        assert c_dir.joinpath("greengrass-build/artifacts/abc/NEXT_PATCH") == gdk_config.gg_build_component_artifacts_dir
        assert c_dir.joinpath("greengrass-build/recipes") == gdk_config.gg_build_recipes_dir
        assert c_dir.joinpath("greengrass-build/artifacts") == gdk_config.gg_build_artifacts_dir
        assert gdk_config.recipe_file == "recipe.json"

import pytest
from pathlib import Path
from unittest import TestCase

from gdk.build_system.Zip import Zip
from tests.helpers.project_config import arrange_project_config


class ZipTests(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker):
        self.mocker = mocker

    def setUp(self):
        self.build_folder = Path(Path(".").resolve()).joinpath("zip-build")

    def project_config(self, build_options: dict):
        return arrange_project_config(
            {
                "component_build_config": {"build_system": "zip", "options": build_options},
                "component_recipe_file": Path("/src/GDK-CLI-Internal/tests/gdk/static/build_command/recipe.json"),
            }
        )

    def test_zip_ignore_list_with_exclude_option(self):
        # Given
        build_options = {"excludes": [".env"]}
        config = self.project_config(build_options)

        # When
        zip = Zip()

        # Then
        assert ["gdk-config.json", "greengrass-build", "recipe.json", ".env"] == zip.get_ignored_file_patterns(config)

    def test_zip_ignore_list_without_exclude_option(self):
        # Given
        build_options = dict()
        config = self.project_config(build_options)

        # When
        zip = Zip()

        # Then
        assert [
            "gdk-config.json",
            "greengrass-build",
            "recipe.json",
            "test*",
            ".*",
            "node_modules",
        ] == zip.get_ignored_file_patterns(config)

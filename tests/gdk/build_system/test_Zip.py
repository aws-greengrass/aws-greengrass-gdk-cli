import pytest
from pathlib import Path
from unittest import TestCase

from gdk.build_system.Zip import Zip
from gdk.commands.component.config.ComponentBuildConfiguration import ComponentBuildConfiguration


class ZipTests(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker):
        self.mocker = mocker
        self.mock_get_proj_config = self.mocker.patch(
            "gdk.common.configuration.get_configuration",
            return_value=config(),
        )
        self.mock_component_recipe = self.mocker.patch(
            "gdk.commands.component.project_utils.get_recipe_file",
            return_value=Path("recipe.json"),
        )

    def test_zip_ignore_list_with_exclude_option(self):
        # Given
        build_options = {"excludes": [".env"]}
        con = config()
        con["component"]["com.example.PythonLocalPubSub"]["build"] = {"build_system": "zip", "options": build_options}
        self.mock_get_proj_config = self.mocker.patch(
            "gdk.common.configuration.get_configuration",
            return_value=con,
        )
        build_config = ComponentBuildConfiguration({})
        # When
        zip = Zip()

        # Then
        assert ["gdk-config.json", "greengrass-build", "recipe.json", ".env"] == zip.get_ignored_file_patterns(build_config)

    def test_zip_ignore_list_without_exclude_option(self):
        # Given
        config = ComponentBuildConfiguration({})
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

import pytest
from pathlib import Path
from unittest import TestCase

from gdk.build_system.Zip import Zip
from gdk.commands.component.config.ComponentBuildConfiguration import ComponentBuildConfiguration
from gdk.common.config.GDKProject import GDKProject


class ZipTests(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker):
        self.mocker = mocker
        self.mock_get_proj_config = self.mocker.patch(
            "gdk.common.configuration.get_configuration",
            return_value=config(),
        )
        self.mocker.patch.object(GDKProject, "_get_recipe_file", return_value=Path(".").joinpath("recipe.json").resolve())

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
            "**/test*",
            "**/.*",
            "**/node_modules",
        ] == zip.get_ignored_file_patterns(config)

    def test_generate_ignore_list_from_globs(self):
        zip = Zip()
        self.mocker.patch("glob.glob", side_effect=[set(['a']), set(['b', '1']), set(['c'])])
        ignore_set = zip.generate_ignore_list_from_globs("/path/to/root", ["glob", "glob2", "glob3"])
        assert ignore_set == {'a', 'b', '1', 'c'}


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

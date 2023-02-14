from pathlib import Path
from faker import Faker
from faker.providers import color
import pytest
from unittest import TestCase

from gdk.build_system.Zip import Zip
from gdk.common.configuration import validate_configuration


class ZipConfigurationTests(TestCase):

    def configuration_base(self, options: dict):
        base = {
            "component": {
                "com.build.zip": {
                    "author": "abc",
                    "version": "1.0.0",
                    "build": {
                        "build_system": "zip"
                    },
                    "publish": {
                        "bucket": "default",
                        "region": "us-east-1"
                    },
                }
            },
            "gdk_version": "1.0.0",
        }

        if options is not None:
            base["component"]["com.build.zip"]["build"].setdefault("options", options)

        return base

    def test_valid_configuration_options(self):
        options = None
        validate_configuration(self.configuration_base(options))

        options = {"exclude": ["*.ts"]}
        validate_configuration(self.configuration_base(options))

    def test_invalid_configuration_options(self):
        fake = Faker()
        fake.add_provider(color)

        with pytest.raises(Exception):
            options = {"exclude": []}
            validate_configuration(self.configuration_base(options))

        with pytest.raises(Exception):
            options = {}
            validate_configuration(self.configuration_base(options))

        with pytest.raises(Exception):
            options = dict()
            options[fake.color_name] = fake.color_name
            validate_configuration(self.configuration_base(options))

    def test_zip_ignore_list_without_exclude_option(self):
        # When
        recipe_path = Path("/src/GDK-CLI-Internal/tests/gdk/static/build_command/recipe.json")
        zip = Zip({"component_recipe_file": recipe_path}, {Path(".").resolve()})

        # Then
        assert ["gdk-config.json", "greengrass-build", "recipe.json",
                "test*", ".*", "node_modules"] == zip._ignore_files_during_zip(None, None)

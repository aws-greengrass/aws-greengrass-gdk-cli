import pytest
from unittest import TestCase

from gdk.commands.config.update.ConfigData import ConfigData
from gdk.commands.config.update.ConfigEnum import ConfigEnum


class TestConfigModel(TestCase):  # Inherit from unittest.TestCase
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker):
        self.mocker = mocker

        self.field_dict = {
            "component": {
                "1": {
                    "author": "abc",
                    "version": "1.0.0",
                    "build": {"build_system": "zip"},
                    "publish": {"bucket": "default", "region": "us-east-1"},
                }
            },
            "gdk_version": "1.0.0",
        }

    def test_get_component_name(self):
        data = ConfigData(self.field_dict)
        self.assertEqual(data.get_component_name(), "1")

    def test_get_author(self):
        data = ConfigData(self.field_dict)
        self.assertEqual(data.get_field(ConfigEnum.AUTHOR), "abc")

    def test_get_version(self):
        data = ConfigData(self.field_dict)
        self.assertEqual(data.get_field(ConfigEnum.VERSION), "1.0.0")

    def test_get_build_system(self):
        data = ConfigData(self.field_dict)
        self.assertEqual(data.get_field(ConfigEnum.BUILD_SYSTEM), "zip")

    def test_get_custom_build_command(self):
        data = ConfigData(self.field_dict)
        self.assertEqual(data.get_field(ConfigEnum.CUSTOM_BUILD_COMMAND), None)

    def test_get_build_options(self):
        data = ConfigData(self.field_dict)
        self.assertEqual(data.get_field(ConfigEnum.BUILD_OPTIONS), {})

    def test_get_bucket(self):
        data = ConfigData(self.field_dict)
        self.assertEqual(data.get_field(ConfigEnum.BUCKET), "default")

    def test_get_region(self):
        data = ConfigData(self.field_dict)
        self.assertEqual(data.get_field(ConfigEnum.REGION), "us-east-1")

    def test_get_publish_options(self):
        data = ConfigData(self.field_dict)
        self.assertEqual(data.get_field(ConfigEnum.PUBLISH_OPTIONS), {})

    def test_get_gdk_version(self):
        data = ConfigData(self.field_dict)
        self.assertEqual(data.get_field(ConfigEnum.GDK_VERSION), "1.0.0")

    def test_set_component_name(self):
        data = ConfigData(self.field_dict)
        data.set_component_name("2")
        self.assertEqual(data.get_component_name(), "2")

    def test_set_author(self):
        data = ConfigData(self.field_dict)
        data.set_field(ConfigEnum.AUTHOR, "author-author")
        self.assertEqual(data.get_author(), "author-author")

    def test_set_version(self):
        data = ConfigData(self.field_dict)
        data.set_field(ConfigEnum.VERSION, "23.24.25")
        self.assertEqual(data.get_version(), "23.24.25")

    def test_set_build_system(self):
        data = ConfigData(self.field_dict)
        data.set_field(ConfigEnum.BUILD_SYSTEM, "random-build-system")
        self.assertEqual(data.get_build_system(), "random-build-system")

    def test_set_custom_build_command(self):
        data = ConfigData(self.field_dict)
        data.set_field(ConfigEnum.CUSTOM_BUILD_COMMAND, "custom-random-build-command")
        self.assertEqual(data.get_custom_build_command(), "custom-random-build-command")

    def test_set_build_options(self):
        data = ConfigData(self.field_dict)
        data.set_field(ConfigEnum.BUILD_OPTIONS, '{"bar": "foo"}')
        self.assertEqual(data.get_build_options(), {"bar": "foo"})

    def test_set_bucket(self):
        data = ConfigData(self.field_dict)
        data.set_field(ConfigEnum.BUCKET, "random-bucket")
        self.assertEqual(data.get_bucket(), "random-bucket")

    def test_set_region(self):
        data = ConfigData(self.field_dict)
        data.set_field(ConfigEnum.REGION, "random-region123")
        self.assertEqual(data.get_region(), "random-region123")

    def test_set_publish_options_str(self):
        data = ConfigData(self.field_dict)
        data.set_field(ConfigEnum.PUBLISH_OPTIONS, '{"bar": "foo"}')
        self.assertEqual(data.get_publish_options(), {"bar": "foo"})

    def test_set_publish_options_dict(self):
        data = ConfigData(self.field_dict)
        data.set_field(ConfigEnum.PUBLISH_OPTIONS, {"bar": "foo"})
        self.assertEqual(data.get_publish_options(), {"bar": "foo"})

    def test_set_gdk_version(self):
        data = ConfigData(self.field_dict)
        data.set_field(ConfigEnum.GDK_VERSION, "19.20.21")
        self.assertEqual(data.get_gdk_version(), "19.20.21")

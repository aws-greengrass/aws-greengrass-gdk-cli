import pytest
from unittest import TestCase
from gdk.wizard.WizardData import WizardData


class TestWizardModel(TestCase):  # Inherit from unittest.TestCase
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

    def test_get_author(self):
        data = WizardData(self.field_dict)
        self.assertEqual(data.get_author(), "abc")

    def test_get_version(self):
        data = WizardData(self.field_dict)
        self.assertEqual(data.get_version(), "1.0.0")

    def test_get_build_system(self):
        data = WizardData(self.field_dict)
        self.assertEqual(data.get_build_system(), "zip")

    def test_get_custom_build_command(self):
        data = WizardData(self.field_dict)
        self.assertEqual(data.get_custom_build_command(), None)

    def test_get_build_options(self):
        data = WizardData(self.field_dict)
        self.assertEqual(data.get_build_options(), "{}")

    def test_get_bucket(self):
        data = WizardData(self.field_dict)
        self.assertEqual(data.get_bucket(), "default")

    def test_get_region(self):
        data = WizardData(self.field_dict)
        self.assertEqual(data.get_region(), "us-east-1")

    def test_get_publish_options(self):
        data = WizardData(self.field_dict)
        self.assertEqual(data.get_publish_options(), "{}")

    def test_get_gdk_version(self):
        data = WizardData(self.field_dict)
        self.assertEqual(data.get_gdk_version(), "1.0.0")

    def test_set_author(self):
        data = WizardData(self.field_dict)
        data.set_author("author-author")
        self.assertEqual(data.get_author(), "author-author")

    def test_set_version(self):
        data = WizardData(self.field_dict)
        data.set_version("23.24.25")
        self.assertEqual(data.get_version(), "23.24.25")

    def test_set_build_system(self):
        data = WizardData(self.field_dict)
        data.set_version("random-build-system")
        self.assertEqual(data.get_version(), "random-build-system")

    def test_set_custom_build_command(self):
        data = WizardData(self.field_dict)
        data.set_custom_build_command("custom-random-build-command")
        self.assertEqual(data.get_custom_build_command(), "custom-random-build-command")

    def test_set_build_options(self):
        data = WizardData(self.field_dict)
        data.set_build_options({"bar": "foo"})
        self.assertEqual(data.get_build_options(), {"bar": "foo"})

    def test_set_bucket(self):
        data = WizardData(self.field_dict)
        data.set_bucket("random-bucket")
        self.assertEqual(data.get_bucket(), "random-bucket")

    def test_set_region(self):
        data = WizardData(self.field_dict)
        data.set_region("random-region123")
        self.assertEqual(data.get_region(), "random-region123")

    def test_set_publish_options(self):
        data = WizardData(self.field_dict)
        data.set_publish_options({"bar": "foo"})
        self.assertEqual(data.get_publish_options(), {"bar": "foo"})

    def test_set_gdk_version(self):
        data = WizardData(self.field_dict)
        data.set_gdk_version("19.20.21")
        self.assertEqual(data.get_gdk_version(), "19.20.21")

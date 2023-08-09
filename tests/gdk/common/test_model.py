import pytest
from unittest import TestCase
from gdk.wizard.commons.model import WizardModel
from gdk.wizard.commands.data import WizardData
from pathlib import Path


class TestWizardModel(TestCase):  # Inherit from unittest.TestCase
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker):
        self.mocker = mocker
        self.mock_get_project_config_file = self.mocker.patch(
            "gdk.common.configuration._get_project_config_file",
            return_value=Path(".").joinpath("tests/gdk/static").joinpath("config.json"),
        )

    def test_get_author(self):
        data = WizardData()
        model = WizardModel(data)
        assert self.mock_get_project_config_file.called
        self.assertEqual(model.get_author(), "abc")

    def test_get_version(self):
        data = WizardData()
        model = WizardModel(data)
        assert self.mock_get_project_config_file.called
        self.assertEqual(model.get_version(), "1.0.0")

    def test_get_build_system(self):
        data = WizardData()
        model = WizardModel(data)
        assert self.mock_get_project_config_file.called
        self.assertEqual(model.get_build_system(), "zip")

    def test_get_custom_build_command(self):
        data = WizardData()
        model = WizardModel(data)
        assert self.mock_get_project_config_file.called
        self.assertEqual(model.get_custom_build_command(), None)

    def test_get_build_options(self):
        data = WizardData()
        model = WizardModel(data)
        assert self.mock_get_project_config_file.called
        self.assertEqual(model.get_build_options(), "{}")

    def test_get_bucket(self):
        data = WizardData()
        model = WizardModel(data)
        assert self.mock_get_project_config_file.called
        self.assertEqual(model.get_bucket(), "default")

    def test_get_region(self):
        data = WizardData()
        model = WizardModel(data)
        assert self.mock_get_project_config_file.called
        self.assertEqual(model.get_region(), "us-east-1")

    def test_get_publish_options(self):
        data = WizardData()
        model = WizardModel(data)
        assert self.mock_get_project_config_file.called
        self.assertEqual(model.get_publish_options(), "{}")

    def test_get_gdk_version(self):
        data = WizardData()
        model = WizardModel(data)
        assert self.mock_get_project_config_file.called
        self.assertEqual(model.get_gdk_version(), "1.0.0")

    def test_set_author(self):
        data = WizardData()
        model = WizardModel(data)
        assert self.mock_get_project_config_file.called
        model.set_author("author-author")
        self.assertEqual(model.get_author(), "author-author")

    def test_set_version(self):
        data = WizardData()
        model = WizardModel(data)
        assert self.mock_get_project_config_file.called
        model.set_version("23.24.25")
        self.assertEqual(model.get_version(), "23.24.25")

    def test_set_build_system(self):
        data = WizardData()
        model = WizardModel(data)
        assert self.mock_get_project_config_file.called
        model.set_version("random-build-system")
        self.assertEqual(model.get_version(), "random-build-system")

    def test_set_custom_build_command(self):
        data = WizardData()
        model = WizardModel(data)
        assert self.mock_get_project_config_file.called
        model.set_custom_build_command("custom-random-build-command")
        self.assertEqual(
            model.get_custom_build_command(), "custom-random-build-command"
        )

    def test_set_build_options(self):
        data = WizardData()
        model = WizardModel(data)
        assert self.mock_get_project_config_file.called
        model.set_build_options({"bar": "foo"})
        self.assertEqual(model.get_build_options(), {"bar": "foo"})

    def test_set_bucket(self):
        data = WizardData()
        model = WizardModel(data)
        assert self.mock_get_project_config_file.called
        model.set_bucket("random-bucket")
        self.assertEqual(model.get_bucket(), "random-bucket")

    def test_set_region(self):
        data = WizardData()
        model = WizardModel(data)
        assert self.mock_get_project_config_file.called
        model.set_region("random-region123")
        self.assertEqual(model.get_region(), "random-region123")

    def test_set_publish_options(self):
        data = WizardData()
        model = WizardModel(data)
        assert self.mock_get_project_config_file.called
        model.set_publish_options({"bar": "foo"})
        self.assertEqual(model.get_publish_options(), {"bar": "foo"})

    def test_set_gdk_version(self):
        data = WizardData()
        model = WizardModel(data)
        assert self.mock_get_project_config_file.called
        model.set_gdk_version("19.20.21")
        self.assertEqual(model.get_gdk_version(), "19.20.21")

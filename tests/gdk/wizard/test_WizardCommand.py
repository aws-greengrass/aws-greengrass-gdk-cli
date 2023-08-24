from unittest import TestCase
from unittest.mock import Mock
import pytest

from gdk.commands.component.WizardCommand import WizardCommand
from pathlib import Path


class WizardCommandTest(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures__(self, mocker):
        self.mocker = mocker

        self.mock_get_project_config_file = self.mocker.patch(
            "gdk.common.configuration._get_project_config_file",
            return_value=Path(".").joinpath("tests/gdk/static").joinpath("config.json"),
        )

        self.mock_write_to_config_field = self.mocker.patch(
            "gdk.wizard.WizardConfigUtils.WizardConfigUtils.write_to_config_file",
            side_effect=Mock,
        )

    def test_wizard_custom_build_system(self):
        mock_change_configuration = self.mocker.patch(
            "gdk.wizard.Prompter.Prompter.change_configuration",
            side_effect=["yes", "y"],
        )
        test_d_args = {}

        mock_user_input = self.mocker.patch(
            "gdk.wizard.Prompter.Prompter.interactive_prompt",
            side_effect=[
                "test_author",
                "1.0.0",
                "custom",
                "['cmake', '—build', 'build', '—config', 'Release']",
                "S3",
                "us-west-2",
                "{}",
                "1.0.0",
            ],
        )

        WizardCommand(test_d_args).run()

        self.assertEqual(self.mock_get_project_config_file.call_count, 2)
        self.assertEqual(mock_change_configuration.call_count, 2)
        self.assertEqual(mock_user_input.call_count, 8)
        self.assertEqual(self.mock_write_to_config_field.call_count, 1)

    def test_wizard_zip_build_system(self):
        mock_change_configuration = self.mocker.patch(
            "gdk.wizard.Prompter.Prompter.change_configuration",
            side_effect=["yes", "y"],
        )
        test_d_args = {}

        mock_user_input = self.mocker.patch(
            "gdk.wizard.Prompter.Prompter.interactive_prompt",
            side_effect=[
                "test_author",
                "1.0.0",
                "zip",
                '{"file_upload_args": {"bucket": "bucket1"}}',
                "S3",
                "us-west-2",
                "{}",
                "1.0.0",
            ],
        )

        WizardCommand(test_d_args).run()

        self.assertEqual(self.mock_get_project_config_file.call_count, 2)
        self.assertEqual(mock_change_configuration.call_count, 2)
        self.assertEqual(mock_user_input.call_count, 8)
        self.assertEqual(self.mock_write_to_config_field.call_count, 1)

    def test_wizard_invalid_custom_build_command(self):
        mock_change_configuration = self.mocker.patch(
            "gdk.wizard.Prompter.Prompter.change_configuration",
            side_effect=["yes", "no"],
        )
        test_d_args = {}

        mock_user_input = self.mocker.patch(
            "gdk.wizard.Prompter.Prompter.interactive_prompt",
            side_effect=["test_author", "1.0.0", "custom", "None", "{}", "()"],
        )

        with self.assertRaises(SystemExit):
            WizardCommand(test_d_args).run()

        self.assertEqual(self.mock_get_project_config_file.call_count, 2)
        self.assertEqual(mock_change_configuration.call_count, 1)
        self.assertEqual(mock_user_input.call_count, 6)

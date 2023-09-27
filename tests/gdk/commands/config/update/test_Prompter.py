import pytest
from unittest import TestCase
from unittest.mock import patch, Mock
from pathlib import Path

from gdk.commands.config.update.ConfigEnum import ConfigEnum
from gdk.commands.config.update.Prompter import Prompter


class TestPrompter(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker):
        self.mocker = mocker

        self.mock_get_project_config_file = self.mocker.patch(
            "gdk.common.configuration._get_project_config_file",
            return_value=Path(".").joinpath("tests/gdk/static").joinpath("config.json"),
        )

    def test_GIVEN_prompt_for_value_WHEN_new_value_provided_THEN_use_new_value(self):
        prompter = Prompter()
        mock_input = self.mocker.patch("builtins.input", return_value="foo")
        result = prompter.interactive_prompt(ConfigEnum.BUILD, "bar", True)
        self.assertEqual(result, "foo")
        self.assertEqual(mock_input.call_count, 1)
        self.assertEqual(self.mock_get_project_config_file.call_count, 2)

    def test_GIVEN_prompt_for_value_WHEN_no_value_provided_THEN_use_default_value(self):
        prompter = Prompter()
        mock_input = self.mocker.patch("builtins.input", return_value="")
        result = prompter.interactive_prompt(ConfigEnum.BUILD, "foo", True)
        self.assertEqual(result, "foo")
        self.assertEqual(mock_input.call_count, 1)
        self.assertEqual(self.mock_get_project_config_file.call_count, 2)

    @patch("builtins.input", side_effect=["y"])
    def test_change_configuration_positive(self, mock_input):
        prompter = Prompter()
        result = prompter.change_configuration(ConfigEnum.BUILD)
        self.assertTrue(result)
        self.assertEqual(mock_input.call_count, 1)
        self.assertEqual(self.mock_get_project_config_file.call_count, 2)

    @patch("builtins.input", side_effect=["n"])
    def test_change_configuration_negative(self, mock_input):
        prompter = Prompter()
        result = prompter.change_configuration(ConfigEnum.BUILD)
        self.assertFalse(result)
        self.assertEqual(mock_input.call_count, 1)
        self.assertEqual(self.mock_get_project_config_file.call_count, 2)

    @patch("builtins.input", side_effect=["invalid", "y"])
    def test_change_configuration_invalid_then_positive(self, mock_input):
        prompter = Prompter()
        result = prompter.change_configuration(ConfigEnum.PUBLISH)
        self.assertTrue(result)
        self.assertEqual(mock_input.call_count, 2)
        self.assertEqual(self.mock_get_project_config_file.call_count, 2)

    @patch("builtins.input", side_effect=["invalid"] * 3)
    def test_change_configuration_max_attempts_reached(self, mock_input):
        prompter = Prompter()
        result = prompter.change_configuration(ConfigEnum.PUBLISH)
        self.assertFalse(result)
        self.assertEqual(mock_input.call_count, 3)
        self.assertEqual(self.mock_get_project_config_file.call_count, 2)

    def test_prompt_first_try(self):
        mock_user_input = self.mocker.patch(
            "gdk.commands.config.update.Prompter.Prompter.interactive_prompt", return_value="new_value"
        )
        mock_checker = self.mocker.patch(
            "gdk.commands.config.update.ConfigChecker.ConfigChecker.is_valid_input", return_value=True
        )

        prompter = Prompter()
        prompter.add_parser_arguments()
        result = prompter.prompter(ConfigEnum.BUILD_OPTIONS, required=False)

        self.assertEqual(result, "new_value")  # User provided valid input
        self.assertEqual(mock_checker.call_count, 1)
        self.assertEqual(mock_user_input.call_count, 1)
        self.assertEqual(self.mock_get_project_config_file.call_count, 2)

    def test_prompter_second_retry(self):
        mock_user_input = self.mocker.patch(
            "gdk.commands.config.update.Prompter.Prompter.interactive_prompt",
            side_effect=["new_value", "ok"],
        )
        mock_checker = self.mocker.patch(
            "gdk.commands.config.update.ConfigChecker.ConfigChecker.is_valid_input",
            side_effect=[False, True],
        )

        prompter = Prompter()
        prompter.add_parser_arguments()
        result = prompter.prompter(ConfigEnum.BUILD_OPTIONS, required=False)

        self.assertEqual(result, "ok")  # User provided valid input
        self.assertEqual(mock_checker.call_count, 2)
        self.assertEqual(mock_user_input.call_count, 2)
        self.assertEqual(self.mock_get_project_config_file.call_count, 2)

    def test_prompter_third_retry(self):
        mock_user_input = self.mocker.patch(
            "gdk.commands.config.update.Prompter.Prompter.interactive_prompt",
            side_effect=["new_value", "ok", "bar"],
        )
        mock_checker = self.mocker.patch(
            "gdk.commands.config.update.ConfigChecker.ConfigChecker.is_valid_input",
            side_effect=[False, False, True],
        )

        prompter = Prompter()
        prompter.add_parser_arguments()
        result = prompter.prompter(ConfigEnum.BUILD_OPTIONS, required=False)

        self.assertEqual(result, "bar")  # User provided valid input
        self.assertEqual(mock_checker.call_count, 3)
        self.assertEqual(mock_user_input.call_count, 3)
        self.assertEqual(self.mock_get_project_config_file.call_count, 2)

    def test_prompter_invalid_input(self):
        mock_user_input = self.mocker.patch(
            "gdk.commands.config.update.Prompter.Prompter.interactive_prompt",
            side_effect=["invalid"] * 3,
        )
        mock_checker = self.mocker.patch(
            "gdk.commands.config.update.ConfigChecker.ConfigChecker.is_valid_input",
            side_effect=[False] * 3,
        )
        mock_get_field = self.mocker.patch(
            "gdk.commands.config.update.ConfigData.ConfigData.get_field", return_value="old_value"
        )

        prompter = Prompter()
        prompter.add_parser_arguments()
        result = prompter.prompter(ConfigEnum.PUBLISH_OPTIONS, required=False)

        self.assertEqual(result, "old_value")  # User provided valid input
        self.assertEqual(mock_get_field.call_count, 1)
        self.assertEqual(mock_checker.call_count, 3)
        self.assertEqual(mock_user_input.call_count, 3)
        self.assertEqual(self.mock_get_project_config_file.call_count, 2)

    def test_prompter_invalid_input_custom_build_command(self):
        mock_user_input = self.mocker.patch(
            "gdk.commands.config.update.Prompter.Prompter.interactive_prompt",
            side_effect=["invalid"] * 3,
        )
        mock_checker = self.mocker.patch(
            "gdk.commands.config.update.ConfigChecker.ConfigChecker.is_valid_input",
            side_effect=[False] * 3,
        )
        mock_get_field = self.mocker.patch(
            "gdk.commands.config.update.ConfigData.ConfigData.get_field", return_value="old_value"
        )
        mock_write_to_config_field = self.mocker.patch(
            "gdk.commands.config.update.ConfigUtils.ConfigUtils.write_to_config_file",
            side_effect=Mock,
        )
        prompter = Prompter()
        prompter.add_parser_arguments()

        with self.assertRaises(SystemExit):
            prompter.prompter(ConfigEnum.CUSTOM_BUILD_COMMAND, required=False)

        self.assertEqual(mock_write_to_config_field.call_count, 1)
        self.assertEqual(mock_user_input.call_count, 3)
        self.assertEqual(mock_checker.call_count, 3)
        self.assertEqual(mock_get_field.call_count, 1)
        self.assertEqual(self.mock_get_project_config_file.call_count, 2)

    def test_prompt_fields(self):
        # integration testing
        expected_field_dict = {
            "component": {
                "new.component.name": {
                    "author": "test_author",
                    "version": "1.0.0",
                    "build": {"build_system": "zip", "options": {}},
                    "publish": {
                        "bucket": "S3",
                        "region": "us-east-1",
                        "options": {"file_upload_args": {}},
                    },
                }
            },
            "gdk_version": "1.0.0",
        }

        mock_change_configuration = self.mocker.patch(
            "gdk.commands.config.update.Prompter.Prompter.change_configuration",
            side_effect=["yes", "y"],
        )
        mock_user_input = self.mocker.patch(
            "gdk.commands.config.update.Prompter.Prompter.interactive_prompt",
            side_effect=[
                "new.component.name",
                "test_author",
                "random_version",
                "random_version",
                "random_version",
                "zip",
                "{}",
                "S3",
                "us-east-1",
                '{"file_upload_args": {}}',
            ],
        )
        prompter = Prompter()
        prompter.prompt_fields()
        self.assertEqual(mock_change_configuration.call_count, 2)
        self.assertEqual(mock_user_input.call_count, 10)
        self.assertEqual(expected_field_dict, prompter.field_dict)
        self.assertEqual(self.mock_get_project_config_file.call_count, 2)

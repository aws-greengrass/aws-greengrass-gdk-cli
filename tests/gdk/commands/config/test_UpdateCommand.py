import pytest
import logging
from unittest import TestCase
from unittest.mock import Mock
from pathlib import Path

from gdk.commands.config.UpdateCommand import UpdateCommand
from gdk.commands.config.update.Prompter import Prompter
from gdk.commands.config.update.ConfigUtils import ConfigUtils
from gdk.commands.config.update.ConfigData import ConfigData


class UpdateCommandTest(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker):
        self.mocker = mocker

        self.mock_get_project_config_file = self.mocker.patch(
            "gdk.common.configuration._get_project_config_file",
            return_value=Path(".").joinpath("tests/gdk/static").joinpath("config.json"),
        )

        self.mock_write_to_config_field = self.mocker.patch(
            "gdk.commands.config.update.ConfigUtils.ConfigUtils.write_to_config_file",
            side_effect=Mock,
        )

    @pytest.fixture(autouse=True)
    def caplog(self, caplog):
        self.caplog = caplog

    def test_GIVEN_component_arg_WHEN_run_update_command_THEN_log_exiting_statement(self):
        self.caplog.set_level(logging.INFO)
        mock_prompt = self.mocker.patch.object(Prompter, "prompt_fields", return_value=None)
        self.mocker.patch.object(ConfigData, "__init__", return_value=None)

        self.mocker.patch.object(ConfigUtils, "read_from_config_file", return_value=None)
        config_update = UpdateCommand({"component": True})
        config_update.run()
        logs = self.caplog.text
        assert "Config file has been updated. Exiting..." in logs
        assert mock_prompt.call_count == 1
        assert self.mock_write_to_config_field.call_count == 1

    def test_GIVEN_improper_args_WHEN_run_update_command_THEN_raise_exception(self):
        config_update = UpdateCommand({})
        with pytest.raises(Exception) as e:
            config_update.run()
        assert ("Could not start the prompter as the command arguments are invalid. Please supply `--component`" +
                " as an argument to the update command.\nTry `gdk config update --help`") in e.value.args[0]

    def test_prompter_custom_build_system(self):
        mock_change_configuration = self.mocker.patch(
            "gdk.commands.config.update.Prompter.Prompter.change_configuration",
            side_effect=["yes", "y"],
        )
        test_d_args = {"component": True}

        mock_user_input = self.mocker.patch(
            "gdk.commands.config.update.Prompter.Prompter.interactive_prompt",
            side_effect=[
                "1",
                "test_author",
                "1.0.0",
                "custom",
                "['cmake', '—build', 'build', '—config', 'Release']",
                "S3",
                "us-west-2",
                "{}",
            ],
        )

        UpdateCommand(test_d_args).run()

        self.assertEqual(self.mock_get_project_config_file.call_count, 2)
        self.assertEqual(mock_change_configuration.call_count, 2)
        self.assertEqual(mock_user_input.call_count, 8)
        self.assertEqual(self.mock_write_to_config_field.call_count, 1)

    def test_prompter_zip_build_system(self):
        mock_change_configuration = self.mocker.patch(
            "gdk.commands.config.update.Prompter.Prompter.change_configuration",
            side_effect=["yes", "y"],
        )
        test_d_args = {"component": True}

        mock_user_input = self.mocker.patch(
            "gdk.commands.config.update.Prompter.Prompter.interactive_prompt",
            side_effect=[
                "1",
                "test_author",
                "1.0.0",
                "zip",
                '{"file_upload_args": {"bucket": "bucket1"}}',
                "S3",
                "us-west-2",
                "{}",
            ],
        )

        UpdateCommand(test_d_args).run()

        self.assertEqual(self.mock_get_project_config_file.call_count, 2)
        self.assertEqual(mock_change_configuration.call_count, 2)
        self.assertEqual(mock_user_input.call_count, 8)
        self.assertEqual(self.mock_write_to_config_field.call_count, 1)

    def test_prompter_invalid_custom_build_command(self):
        mock_change_configuration = self.mocker.patch(
            "gdk.commands.config.update.Prompter.Prompter.change_configuration",
            side_effect=["yes", "no"],
        )
        test_d_args = {"component": True}

        mock_user_input = self.mocker.patch(
            "gdk.commands.config.update.Prompter.Prompter.interactive_prompt",
            side_effect=["1", "test_author", "1.0.0", "custom", "None", "{}", "()"],
        )

        with self.assertRaises(SystemExit):
            UpdateCommand(test_d_args).run()

        self.assertEqual(self.mock_get_project_config_file.call_count, 2)
        self.assertEqual(mock_change_configuration.call_count, 1)
        self.assertEqual(mock_user_input.call_count, 7)

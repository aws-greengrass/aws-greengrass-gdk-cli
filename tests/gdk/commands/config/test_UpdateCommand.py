import pytest
import logging
from unittest import TestCase

from gdk.commands.config.UpdateCommand import UpdateCommand
from gdk.wizard.Prompter import Prompter
from gdk.wizard.WizardConfigUtils import WizardConfigUtils
from gdk.wizard.WizardData import WizardData
from gdk.wizard.WizardChecker import WizardChecker


class UpdateCommandTest(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker):
        self.mocker = mocker

        self.mocker.patch.object(WizardData, "__init__", return_value=None)
        self.mocker.patch.object(WizardChecker, "__init__", return_value=None)

    @pytest.fixture(autouse=True)
    def caplog(self, caplog):
        self.caplog = caplog

    def test_GIVEN_component_arg_WHEN_run_update_command_THEN_log_exiting_statement(self):
        self.caplog.set_level(logging.INFO)
        mock_prompt = self.mocker.patch.object(Prompter, "prompt_fields", return_value=None)

        self.mocker.patch.object(WizardConfigUtils, "get_project_config_file", return_value=None)
        self.mocker.patch.object(WizardConfigUtils, "read_from_config_file", return_value=None)
        mock_write = self.mocker.patch.object(WizardConfigUtils, "write_to_config_file", return_value=None)
        config_update = UpdateCommand({"component": True})
        config_update.run()
        logs = self.caplog.text
        assert "Config file has been updated. Exiting..." in logs
        assert mock_prompt.call_count == 1
        assert mock_write.call_count == 1

    def test_GIVEN_improper_args_WHEN_run_update_command_THEN_raise_exception(self):
        config_update = UpdateCommand({})
        with pytest.raises(Exception) as e:
            config_update.run()
        assert ("Could not start the prompter as the command arguments are invalid. Please supply `--component`" +
                " as an argument to the update command.\nTry `gdk config update --help`") in e.value.args[0]

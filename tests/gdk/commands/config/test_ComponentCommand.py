import pytest
import logging
from unittest import TestCase

from gdk.commands.config.ComponentCommand import ComponentCommand
from gdk.wizard.Prompter import Prompter
from gdk.wizard.WizardConfigUtils import WizardConfigUtils
from gdk.wizard.WizardData import WizardData
from gdk.wizard.WizardChecker import WizardChecker


class ComponentCommandTest(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker):
        self.mocker = mocker

        self.mocker.patch.object(WizardData, "__init__", return_value=None)
        self.mocker.patch.object(WizardChecker, "__init__", return_value=None)

    @pytest.fixture(autouse=True)
    def caplog(self, caplog):
        self.caplog = caplog

    def test_GIVEN_run_function_called_WHEN_success_THEN_log_exiting_statement(self):
        self.caplog.set_level(logging.INFO)
        self.mocker.patch.object(ComponentCommand, "__init__", return_value=None)
        mock_prompt = self.mocker.patch.object(Prompter, "prompt_fields", return_value=None)

        self.mocker.patch.object(WizardConfigUtils, "get_project_config_file", return_value=None)
        self.mocker.patch.object(WizardConfigUtils, "read_from_config_file", return_value=None)
        mock_write = self.mocker.patch.object(WizardConfigUtils, "write_to_config_file", return_value=None)
        config_component = ComponentCommand({})
        config_component.run()
        logs = self.caplog.text
        assert "Config file has been updated. Exiting..." in logs
        assert mock_prompt.call_count == 1
        assert mock_write.call_count == 1

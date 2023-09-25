import pytest
from unittest import TestCase
from gdk.wizard.ConfigEnum import ConfigEnum
from gdk.wizard.Prompter import Prompter
from pathlib import Path


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

from unittest import TestCase
import pytest
from gdk.wizard.commands.data import Wizard_data as data


def Wizard_dataTest(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker):
        self.mocker = mocker

    def test_init(self):
        # self.project_config_file = _get_project_config_file()
        # self.field_map = get_configuration()
        # self.project_config = self.field_map["component"]
        # self.component_name = next(iter(self.project_config))
        # self.schema = self.get_schema()
        pass

    def test_get_schema():
        pass

    

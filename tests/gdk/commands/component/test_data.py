from unittest import TestCase
import pytest
from gdk.wizard.commands.data import Wizard_data as data


def Wizard_dataTest(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker):
        self.mocker = mocker

    def test_init(self):
        pass

    def test_get_schema():
        pass

    

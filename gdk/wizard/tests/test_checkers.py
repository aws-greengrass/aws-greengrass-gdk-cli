from unittest import TestCase
import pytest
from gdk.wizard.commons.checkers import Wizard_checker

class Wizard_checker_test(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures__(self, mocker):
        self.mocker = mocker


    def test_extract_field_value_from(self):
        pass





    # def test_check_for_empty_string(self):
    #     self.assertEqual(Wizard_checker.check_for_empty_string(""), True)

    # def test_check_for_empty_string_false(self):
    #     self.assertEqual(Wizard_checker.check_for_empty_string("test"), False)

    # def test_check_for_empty_string_false_2(self):
    #     self.assertEqual(Wizard_checker.check_for_empty_string(None), False)

    # def test_check_for_empty_string_false_3(self):
    #     self.assertEqual(Wizard_checker.check_for_empty_string(1), False)

    # def test_check_for_empty_string_false_4(self):
    #     self.assertEqual(Wizard_checker.check_for_empty_string([]), False)

    # def test_check_for_empty_string_false_5(self):
    #     self.assertEqual(Wizard_checker.check_for_empty_string({}), False)
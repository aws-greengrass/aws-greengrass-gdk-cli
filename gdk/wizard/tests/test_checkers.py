from unittest import TestCase
import pytest
from gdk.wizard.commons.checkers import Wizard_checker
from gdk.wizard.commands.data import Wizard_data


class Wizard_checker_test(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures__(self, mocker):
        self.mocker = mocker

    def test_extract_author(self):
        data = Wizard_data()
        checker = Wizard_checker(data)

        expected_author = {
            "description": "Author of the component which is interpolated during build and publish phases.",
            "type": "string",
        }
        self.assertEqual(
            checker.extract_field_value_from_schema("author"), expected_author
        )

    def test_extract_version(self):
        data = Wizard_data()
        checker = Wizard_checker(data)

        expected_version = {
            "description": "Version of the component which is interpolated during build and publish phases. Can be an enum or a semver version.",
            "type": "string",
            "oneOf": [
                {
                    "description": "Exact version of the component to use with cli commands. Must be a semver version.",
                    "pattern": "^(0|[1-9]\\d*)\\.(0|[1-9]\\d*)\\.(0|[1-9]\\d*)(?:-((?:0|[1-9]\\d*|\\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\\.(?:0|[1-9]\\d*|\\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\\+([0-9a-zA-Z-]+(?:\\.[0-9a-zA-Z-]+)*))?",
                },
                {
                    "description": "Enum to dynamically determine the version of the component with cli commands.",
                    "enum": ["NEXT_PATCH"],
                },
            ],
        }
        self.assertEqual(
            checker.extract_field_value_from_schema("version"), expected_version
        )

    def test_extract_custum_build_command(self):
        data = Wizard_data()
        checker = Wizard_checker(data)

        expected_custom_build_command = {
            "description": "Custom command provided as an array of strings to execute with cli build command. Required when the 'build_system' is 'custom'.",
            "type": ["array", "string"],
            "minItems": 1,
            "minLength": 1,
        }
        self.assertEqual(
            checker.extract_field_value_from_schema("custom_build_command"),
            expected_custom_build_command,
        )

    def test_extract_build_system(self):
        data = Wizard_data()
        checker = Wizard_checker(data)

        expected_build_system = {
            "description": "Build system to use with the cli build command. Must be one of the defaults supported by the cli or just 'custom'.",
            "type": "string",
            "enum": ["zip", "maven", "gradle", "gradlew", "custom"],
        }
        self.assertEqual(
            checker.extract_field_value_from_schema("build_system"),
            expected_build_system,
        )

    def test_extract_bucket(self):
        data = Wizard_data()
        checker = Wizard_checker(data)

        expected_bucket = {
            "description": "Prefix of the s3 bucket used during component artifacts upload. Name of the bucket is created by appending account and region to bucket prefix.",
            "type": "string",
        }
        self.assertEqual(
            checker.extract_field_value_from_schema("bucket"), expected_bucket
        )

    def test_extract_region(self):
        data = Wizard_data()
        checker = Wizard_checker(data)

        expected_region = {
            "description": "AWS regions supported by AWS IoT Greengrassv2.",
            "type": "string",
        }

        self.assertEqual(
            checker.extract_field_value_from_schema("region"), expected_region
        )

    def test_extract_options(self):
        data = Wizard_data()
        checker = Wizard_checker(data)

        expected_options = {
            "type": "object",
            "description": "configuration options used during component version creation",
            "properties": {
                "file_upload_args": {
                    "type": "object",
                    "description": "Extra arguments used by S3 client during file transfer.",
                }
            },
        }
        self.assertEqual(
            checker.extract_field_value_from_schema("options"), expected_options
        )

    def test_extract_gdk_version(self):
        data = Wizard_data()
        checker = Wizard_checker(data)

        expected_gdk_version = {
            "description": "Version of the gdk cli tool compatible with the provided configuration.",
            "type": "string",
            "pattern": "^(0|[1-9]\\d*)\\.(0|[1-9]\\d*)\\.(0|[1-9]\\d*)(?:-((?:0|[1-9]\\d*|\\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\\.(?:0|[1-9]\\d*|\\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\\+([0-9a-zA-Z-]+(?:\\.[0-9a-zA-Z-]+)*))?",
        }
        self.assertEqual(
            checker.extract_field_value_from_schema("gdk_version"), expected_gdk_version
        )

    def test_is_valid_input_on_valid_inputs(self):
        data = Wizard_data()
        checker = Wizard_checker(data)

        # author 
        self.assertEqual(checker.is_valid_input("author", "test"), True)

        #version
        self.assertEqual(checker.is_valid_input("version", "1.0.0"), True)

        #custom_build_commands
        self.assertEqual(checker.is_valid_input("custom_build_command", ["test"]), True)

        #build_system
        self.assertEqual(checker.is_valid_input("build_system", "zip"), True)
        self.assertEqual(checker.is_valid_input("build_system", "maven"), True)
        self.assertEqual(checker.is_valid_input("build_system", "gradle"), True)
        self.assertEqual(checker.is_valid_input("build_system", "gradlew"), True)
        self.assertEqual(checker.is_valid_input("build_system", "custom"), True)

        #bucket 
        self.assertEqual(checker.is_valid_input("bucket", "test"), True)

        self.assertEqual(checker.is_valid_input("region", "us-east-1"), True)

        #options
        self.assertEqual(checker.is_valid_input("options", {"file_upload_args": {"test": "test"}}), True)

        #gdk_version
        self.assertEqual(checker.is_valid_input("gdk_version", "1.0.0"), True)



    def test_is_valid_input_on_invalid_inputs(self):
        data = Wizard_data()
        checker = Wizard_checker(data)

        self.assertEqual(checker.is_valid_input("author", 123), False)





    

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

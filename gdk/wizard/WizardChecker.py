from gdk.wizard.ConfigEnum import ConfigEnum
import re
import ast
import json


class WizardChecker:
    def __init__(self):
        self.switch = {
            ConfigEnum.AUTHOR: self.is_valid_author,
            ConfigEnum.VERSION: self.is_valid_version,
            ConfigEnum.CUSTOM_BUILD_COMMAND: self.is_valid_custom_build_command,
            ConfigEnum.BUILD_SYSTEM: self.is_valid_build_system,
            ConfigEnum.BUILD_OPTIONS: self.is_valid_build_options,
            ConfigEnum.BUCKET: self.is_valid_bucket,
            ConfigEnum.REGION: self.is_valid_region,
            ConfigEnum.PUBLISH_OPTIONS: self.is_valid_publish_options,
            ConfigEnum.GDK_VERSION: self.is_valid_gdk_version,
        }

    def is_valid_input(self, input_value, field):
        """
        Prompts the user of all the optional ConfigEnum of the gdk config file and updates the
        field_map if their answer is valid  as the user answers the question to each prompt

        Parameters
        ----------
            input_value(string): The value entered by the user for the field
            field(string): The field name of the field in the gdk config file

        Returns
        -------
            boolean: True if the input value is valid for the field, False otherwise.
        """
        return self.switch.get(field)(input_value)

    def is_valid_author(self, input_value):
        # input must be a non-empty string
        return isinstance(input_value, str) and len(input_value) > 0

    def is_valid_version(self, input_value):
        # input must match the regex or be an allowed enum value
        version_pattern = (
            "^(0|[1-9]\\d*)\\.(0|[1-9]\\d*)\\.(0|[1-9]\\d*)"
            "(?:-((?:0|[1-9]\\d*|\\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\\."
            "(?:0|[1-9]\\d*|\\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
            "(?:\\+([0-9a-zA-Z-]+(?:\\.[0-9a-zA-Z-]+)*))?"
        )
        allowed_enum_values = {"NEXT_PATCH"}

        return (
            re.match(version_pattern, input_value) != None
            or input_value in allowed_enum_values
        )

    def is_valid_build_system(self, input_value):
        # input must be a string and must be one of the allowed build systems
        allowed_build_systems = {"zip", "maven", "gradle", "gradlew", "custom"}
        return isinstance(input_value, str) and input_value in allowed_build_systems

    def is_valid_custom_build_command(self, input_value):
        """
        input must be a non-empty string or a non-empty list of strings

        since input_value will always be a string (b/c its a CLI input), need to try and convert it
        to a list of strings. If it fails, then the input is not valid. Then command_list a non-empty
        list of strings

        required if build_system is custom, exit the wizard with error message
        second approach revert to build_system to zip
        or infinite loop
        """
        try:
            input_list = ast.literal_eval(input_value)
            if isinstance(input_list, list):
                return (
                    all(isinstance(item, str) and item.strip() for item in input_list)
                    and len(input_list) > 0
                )
            else:
                return False
        except (SyntaxError, TypeError, MemoryError, RecursionError):
            return False
        except ValueError:
            return len(input_value) > 0

    def is_valid_build_options(self, input_value):
        # empty dictionary is valid
        if input_value == "{}":
            return True

        try:
            # Convert the input string to a dictionary (object)
            input_obj = json.loads(input_value)
        except json.JSONDecodeError:
            return False

        if not isinstance(input_obj, dict):
            return False

        if "excludes" in input_obj:
            excluded = input_obj.get("excludes")
            if not isinstance(excluded, list) or not all(
                isinstance(item, str) for item in excluded
            ):
                return False

        if "zip_name" in input_obj:
            zip_name = input_obj.get("zip_name")
            if not isinstance(zip_name, str):
                return False

        return True

    def is_valid_bucket(self, input_value):
        # input must be a non-empty string
        return isinstance(input_value, str) and len(input_value) > 0

    def is_valid_region(self, input_value):
        # input must be a non-empty string
        return isinstance(input_value, str) and len(input_value) > 0

    def is_valid_publish_options(self, input_value):
        # input_value will always be a string so must try to convert it to a dict

        try:
            input_object = json.loads(input_value)
        except json.JSONDecodeError:
            return False

        if not isinstance(input_object, dict):
            return False

        _file_upload_args = input_object.get("file_upload_args", {})
        if not isinstance(_file_upload_args, dict):
            return False

        return True

    def is_valid_gdk_version(self, input_value):
        gdk_version_pattern = (
            "^(0|[1-9]\\d*)\\.(0|[1-9]\\d*)\\.(0|[1-9]\\d*)"
            "(?:-((?:0|[1-9]\\d*|\\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\\."
            "(?:0|[1-9]\\d*|\\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
            "(?:\\+([0-9a-zA-Z-]+(?:\\.[0-9a-zA-Z-]+)*))?"
        )
        return re.match(gdk_version_pattern, input_value) != None

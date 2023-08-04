from gdk.wizard.commons.fields import Fields
import re
import json


class Wizard_checker:
    def __init__(self, data):
        self.data = data
        self.schema = self.data.schema

    def is_valid_input(self, input_value, field):
        """
        Prompts the user of all the optional fields of the gdk config file and updates the
        field_map if their answer is valid  as the user answers the question to each prompt

        Parameters
        ----------
            input_value(string): The value entered by the user for the field
            field(string): The field name of the field in the gdk config file

        Returns
        -------
            boolean: True if the input value is valid for the field, False otherwise.
        """

        switch = {
            Fields.AUTHOR: self.check_author,
            Fields.VERSION: self.check_version,
            Fields.CUSTOM_BUILD_COMMAND: self.check_custom_build_command,
            Fields.BUILD_SYSTEM: self.check_build_system,
            Fields.BUILD_OPTIONS: self.check_build_options,
            Fields.BUCKET: self.check_bucket,
            Fields.REGION: self.check_region,
            Fields.PUBLISH_OPTIONS: self.check_publish_options,
            Fields.GDK_VERSION: self.check_gdk_version,
        }
        return switch.get(field)(input_value)

    def check_author(self, input_value):
        # input must be a non-empty string
        return isinstance(input_value, str) and len(input_value) > 0

    def check_version(self, input_value):
        # input must match the regex or be an allowed enum value
        version_pattern = "^(0|[1-9]\\d*)\\.(0|[1-9]\\d*)\\.(0|[1-9]\\d*)(?:-((?:0|[1-9]\\d*|\\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\\.(?:0|[1-9]\\d*|\\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\\+([0-9a-zA-Z-]+(?:\\.[0-9a-zA-Z-]+)*))?"

        allowed_enum_values = {"NEXT_PATCH"}

        if re.match(version_pattern, input_value) or input_value in allowed_enum_values:
            return True

        return False

    def check_build_system(self, input_value):
        # input must be a string and must be one of the allowed build systems
        allowed_build_systems = {"zip", "maven", "gradle", "gradlew", "custom"}
        return isinstance(input_value, str) and input_value in allowed_build_systems

    def check_custom_build_command(self, input_value):
        # input must be a non-empty string or a non-empty list of strings

        # since input_value will always be a string (b/c its a CLI input), need to try and convert it
        # to a list of strings. If it fails, then the input is not valid. Then command_list a non-empty
        # list of strings

        # required if build_system is custom, exit the wizard with error message
        # second approach revert to build_system to zip
        # or infinite loop
        try:
            command_list = json.loads(input_value)
        except json.JSONDecodeError:
            command_list = [input_value]

        if (
            len(command_list) >= 1
            and isinstance(command_list, list)
            and all(isinstance(item, str) and item.strip() for item in command_list)
        ):
            return True

        return False

    def check_build_options(self, input_value):
        try:
            # Convert the input string to a dictionary (object)
            input_obj = json.loads(input_value)
        except json.JSONDecodeError:
            return False

        if not isinstance(input_obj, dict):
            return False

        if len(input_obj) > 2:
            return False

        if "excludes" not in input_obj or "zip_name" not in input_obj:
            return False

        excludes = input_obj.get("excludes")
        if not isinstance(excludes, list) or len(excludes) < 1:
            return False

        zip_name = input_obj.get("zip_name")
        if not isinstance(zip_name, str):
            print("here6")
            return False

        return True

    def check_bucket(self, input_value):
        # input must be a non-empty string
        return isinstance(input_value, str) and len(input_value) > 0

    def check_region(self, input_value):
        # input must be a non-empty string
        return isinstance(input_value, str) and len(input_value) > 0

    def check_publish_options(self, input_value):
        # input_value will always be a string so must try to convert it to a dict

        try:
            input_object = json.loads(input_value)
        except json.JSONDecodeError:
            return False

        if not isinstance(input_object, dict):
            return False

        if "file_upload_args" in input_object and isinstance(
            input_object["file_upload_args"], dict
        ):
            return True

        return False

    def check_gdk_version(self, input_value):
        gdk_version_pattern = "^(0|[1-9]\\d*)\\.(0|[1-9]\\d*)\\.(0|[1-9]\\d*)(?:-((?:0|[1-9]\\d*|\\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\\.(?:0|[1-9]\\d*|\\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\\+([0-9a-zA-Z-]+(?:\\.[0-9a-zA-Z-]+)*))?"
        if re.match(gdk_version_pattern, input_value):
            return True
        return False

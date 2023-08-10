from gdk.wizard.commons.fields import Fields
import re
import ast


class WizardChecker:
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
        version_pattern = (
            "^(0|[1-9]\\d*)\\.(0|[1-9]\\d*)\\.(0|[1-9]\\d*)"
            "(?:-((?:0|[1-9]\\d*|\\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\\."
            "(?:0|[1-9]\\d*|\\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
            "(?:\\+([0-9a-zA-Z-]+(?:\\.[0-9a-zA-Z-]+)*))?"
        )
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

        if not isinstance(input_value, str):
            return False

        try:
            input_list = ast.literal_eval(input_value)
            if isinstance(input_list, list):
                return (
                    all(isinstance(item, str) and item.strip() for item in input_list)
                    and len(input_list) > 0
                )
            else:
                return False
        except (ValueError, SyntaxError):
            return len(input_value) > 0
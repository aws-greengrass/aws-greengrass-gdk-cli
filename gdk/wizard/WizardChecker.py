from gdk.wizard.ConfigEnum import ConfigEnum
import re
import ast


class WizardChecker:
    def __init__(self):
        self.switch = {
            ConfigEnum.AUTHOR: self.is_valid_author,
            ConfigEnum.VERSION: self.is_valid_version,
            ConfigEnum.CUSTOM_BUILD_COMMAND: self.is_valid_custom_build_command,
            ConfigEnum.BUILD_SYSTEM: self.is_valid_build_system,
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

        if re.match(version_pattern, input_value) or input_value in allowed_enum_values:
            return True

        return False

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

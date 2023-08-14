from gdk.wizard.WizardData import WizardData
from gdk.wizard.ConfigEnum import ConfigEnum
from gdk.wizard.WizardChecker import WizardChecker
from gdk.wizard.WizardConfigUtils import WizardConfigUtils
import logging
from PyInquirer import prompt
import argparse
import sys


class Prompter:
    """
    A class used to represent the GDK Startup Wizard
    """

    def __init__(self) -> None:
        """
        Initialize the Wizard object

        Attributes
        ----------
            data: Wizard_data object
            model: Wizard getter and setter object
            checker: Wizard_checker object
            parser: argparse object
        """

        self.utils = WizardConfigUtils()
        self.project_config_file = self.utils.get_project_config_file()
        self.field_dict = self.utils.read_from_config_file()

        self.data = WizardData(self.field_dict)
        self.checker = WizardChecker()
        self.parser = argparse.ArgumentParser()

    def prompter(self, field, required, max_attempts=3):
        """
        Prompts the user for a value of a given field key

        Parameters
        ----------
            field (enum): a field key of the gdk_config file to be changed
            value (string): the current value corresponding the field key to be changed
            required (boolean): if the field is a required field of the gdk config file
            max_attempts (int): the maximum number of attempts to get a valid response from the user

        Returns
        -------
            string: the value for the field key "field"
        """
        current_field_value = self.data.get_field(field)
        require = "REQUIRED " if required else "OPTIONAL "
        for attempt in range(1, max_attempts + 1):
            parser_argument = field.value.key
            if field == ConfigEnum.BUILD_OPTIONS:
                parser_argument = "build_options"
            elif field == ConfigEnum.PUBLISH_OPTIONS:
                parser_argument = "publish_options"

            args = self.parser.parse_args(
                [
                    f"--{parser_argument}",
                    self.interactive_prompt(
                        parser_argument, current_field_value, require
                    ),
                ]
            )
            response = getattr(args, parser_argument).strip()

            """
            only way customer is asked about custom_build_command if they have custom build system
            in which case they must specify a custom build command that is not None or empty
            """
            if self.checker.is_valid_input(response, field):
                return response

            self.retry_messages(field, attempt, max_attempts)

        if field == ConfigEnum.CUSTOM_BUILD_COMMAND:
            self.utils.write_to_config_file(self.field_dict, self.project_config_file)
            sys.exit(
                f"Attempt {attempt}/{max_attempts}: Failed to enter a valid custom build command. Exiting wizard..."
            )

        logging.info(
            f"Attempt {attempt}/{max_attempts}: Exceeded maximum attempts. Assuming current or default response."
        )
        return current_field_value

    def retry_messages(self, field, attempt, max_attempts):
        link = "https://docs.aws.amazon.com/greengrass/v2/developerguide/gdk-cli-configuration-file.html#gdk-config-format"
        default_message = f"Attempt {attempt}/{max_attempts}: Invalid response. Please try again.\nPlease vist: {link}"
        custom_message = f"Attempt {attempt}/{max_attempts}: Must Specify a custum build command.\nPlease vist: {link}"
        if attempt < max_attempts:
            if field == ConfigEnum.CUSTOM_BUILD_COMMAND:
                logging.warning(custom_message)
            else:
                logging.warning(default_message)

    def change_configuration(self, field_key, max_attempts=3):
        """
        Prompts the users to answer if they would like to change the build or publish configurations

        Parameters
        ----------
            build_or_publish(string): takes value "build" or "publish"

        Returns
        -------
            boolean: True if user wants to change the 'build_or_publish' configuration and False otherwise

        """
        self.parser.add_argument(
            f"--change_{field_key}",
            help=f"Change componenet {field_key} configurations",
        )

        for _ in range(max_attempts):
            args = self.parser.parse_args(
                [
                    f"--change_{field_key}",
                    input(
                        f"Do you want to change the {field_key} configurations? (y/n) "
                    ),
                ]
            )
            response = getattr(args, f"change_{field_key}").strip().lower()
            if response in {"y", "yes"}:
                return True
            elif response in {"n", "no"}:
                return False
            logging.warning("Your input was invalid response. Please respond again.")
        return False

    def interactive_prompt(self, field, value, require):
        """
        Prompts the user for a value of a given key through an interactive prompt.

        Parameters
        ----------
            field (string): a field key of the gdk-config file to be changed
            value (string): the current value corresponding the field key to be changed
            require (boolean): if the field is a required field of the gdk config file

        Returns
        -------
            string: the value of field that the user has entered through the interactive prompt
        """
        questions = [
            {
                "type": "input",
                "name": "user_input",
                "message": f"Current value of the {require}{field} is:",
                "default": f"{value}",
            }
        ]
        try:
            answer = prompt(questions)
            return answer["user_input"]
        except (KeyError, TypeError):
            raise Exception("Wizard interrupted. Exiting...")

    def prompt_build_configs(self):
        """
        Asks user if they would like to change build configurations and prompts corresponding ConfigEnum

        Parameters
        ----------
            None

        Returns
        -------
            None

        """
        if self.change_configuration(ConfigEnum.BUILD.value.key):
            response_build_system = self.prompter(
                ConfigEnum.BUILD_SYSTEM, required=True
            )
            self.data.set_field(ConfigEnum.BUILD_SYSTEM, response_build_system)

            # if user has custom build system, then they must supply custom build commands
            if self.data.get_build_system() == "custom":
                response_custom_build_command = self.prompter(
                    ConfigEnum.CUSTOM_BUILD_COMMAND, required=True
                )
                self.data.set_field(
                    ConfigEnum.CUSTOM_BUILD_COMMAND, response_custom_build_command
                )

            elif self.data.get_build_system() == "zip":
                response_build_options = self.prompter(
                    ConfigEnum.BUILD_OPTIONS, required=False
                )
                self.data.set_field(ConfigEnum.BUILD_OPTIONS, response_build_options)

    def prompt_publish_configs(self):
        """
        Asks user if they would like to change publish configurations and prompts corresponding ConfigEnum

        Parameters
        ----------
            None

        Returns
        -------
            None

        """
        if self.change_configuration(ConfigEnum.PUBLISH.value.key):
            response_bucket = self.prompter(ConfigEnum.BUCKET, required=True)
            self.data.set_field(ConfigEnum.BUCKET, response_bucket)

            response_region = self.prompter(ConfigEnum.REGION, required=False)
            self.data.set_field(ConfigEnum.REGION, response_region)

            response_publish_options = self.prompter(
                ConfigEnum.PUBLISH_OPTIONS, required=False
            )
            self.data.set_field(ConfigEnum.PUBLISH_OPTIONS, response_publish_options)

    def add_parser_arguments(self):
        # Add all the optional and required ConfigEnum to the parser
        for field in ConfigEnum:
            parser_argument = field.value.key
            if field == ConfigEnum.BUILD_OPTIONS:
                parser_argument = "build_options"
            elif field == ConfigEnum.PUBLISH_OPTIONS:
                parser_argument = "publish_options"
            self.parser.add_argument(f"--{parser_argument}")

    def prompt_fields(self):
        """
        Wapper method that prompts users for required and optional field values
        for the gdk config file

        Parameters
        ----------
            None

        Returns
        -------
            None
        """

        self.add_parser_arguments()

        response_author = self.prompter(ConfigEnum.AUTHOR, required=True)
        self.data.set_field(ConfigEnum.AUTHOR, response_author)

        response_version = self.prompter(ConfigEnum.VERSION, required=True)
        self.data.set_field(ConfigEnum.VERSION, response_version)

        self.prompt_build_configs()
        self.prompt_publish_configs()

        response_gdk_version = self.prompter(ConfigEnum.GDK_VERSION, required=True)
        self.data.set_field(ConfigEnum.GDK_VERSION, response_gdk_version)

from gdk.wizard.commands.data import WizardData
from gdk.wizard.commons.fields import Fields
from gdk.wizard.commons.checkers import WizardChecker
from gdk.wizard.commons.model import WizardModel
from PyInquirer import prompt
import argparse
import sys


class Wizard:
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

        self.data = WizardData()
        self.model = WizardModel(self.data)
        self.checker = WizardChecker(self.data)
        self.parser = argparse.ArgumentParser()

    def prompter(self, field, value, required, max_attempts=3):
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
        require = "REQUIRED " if required else "OPTIONAL "
        link = "https://docs.aws.amazon.com/greengrass/v2/developerguide/gdk-cli-configuration-file.html#gdk-config-format"
        for attempt in range(1, max_attempts + 1):
            parser_argument = field.value.key
            if field == Fields.BUILD_OPTIONS:
                parser_argument = "build_options"
            elif field == Fields.PUBLISH_OPTIONS:
                parser_argument = "publish_options"

            args = self.parser.parse_args(
                [
                    f"--{parser_argument}",
                    self.interactive_prompt(field.value.key, value, require),
                ]
            )
            response = getattr(args, parser_argument).strip()

            # only way customer is asked about custom_build_command if they have custom build system
            # in which case they must specify a custom build command that is not None
            if field == Fields.CUSTOM_BUILD_COMMAND:
                if response == "None":
                    print(
                        f"Attempt {attempt}/{max_attempts}: Must Specify a custum build command.\nPlease vist: {link}"
                    )
                    continue

            # if customer input response is the default value or the customer input response is
            # the same as the current value, return the current value, then return the same value
            if (
                response == field.value.default
                or response == value
                or self.checker.is_valid_input(response, field)
            ):
                return response
            print(
                f"Attempt {attempt}/{max_attempts}: Invalid response. Please try again.\nPlease vist: {link}"
            )

        if field == Fields.CUSTOM_BUILD_COMMAND:
            self.data.write_to_config_file()
            sys.exit(
                "You have failed to enter a valid custom build command. Exiting wizard..."
            )

        print("Exceeded maximum attempts. Assuming default response.")
        return value

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
            print("Your input was invalid response. Please respond again.")
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
            self.data.write_to_config_file()
            sys.exit("Wizard interrupted. Exiting...")

    def prompt_build_configs(self):
        """
        Asks user if they would like to change build configurations and prompts corresponding fields

        Parameters
        ----------
            None

        Returns
        -------
            None

        """
        if self.change_configuration(Fields.BUILD.value.key):
            response_build_system = self.prompter(
                Fields.BUILD_SYSTEM, self.model.get_build_system(), required=True
            )
            self.model.set_build_system(response_build_system)

            # if user has custom build system, then they must supply custom build commands
            if self.model.get_build_system() == "custom":
                response_custom_build_command = self.prompter(
                    Fields.CUSTOM_BUILD_COMMAND,
                    self.model.get_custom_build_command(),
                    required=True,
                )
                self.model.set_custom_build_command(response_custom_build_command)

            elif self.model.get_build_system() == "zip":
                response_build_options = self.prompter(
                    Fields.BUILD_OPTIONS, self.model.get_build_options(), required=False
                )
                self.model.set_build_options(response_build_options)

    def prompt_publish_configs(self):
        """
        Asks user if they would like to change publish configurations and prompts corresponding fields

        Parameters
        ----------
            None

        Returns
        -------
            None

        """
        if self.change_configuration(Fields.PUBLISH.value.key):
            response_bucket = self.prompter(
                Fields.BUCKET, self.model.get_bucket(), required=True
            )
            self.model.set_bucket(response_bucket)

            response_region = self.prompter(
                Fields.REGION, self.model.get_region(), required=False
            )
            self.model.set_region(response_region)

            response_publish_options = self.prompter(
                Fields.PUBLISH_OPTIONS, self.model.get_publish_options(), required=False
            )
            self.model.set_publish_options(response_publish_options)

    def add_parser_arguments(self):
        # Add all the optional and required fields to the parser
        for field in Fields:
            parser_argument = field.value.key
            if field == Fields.BUILD_OPTIONS:
                parser_argument = "build_options"
            elif field == Fields.PUBLISH_OPTIONS:
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

        response_author = self.prompter(
            Fields.AUTHOR, self.model.get_author(), required=True
        )
        self.model.set_author(response_author)

        response_version = self.prompter(
            Fields.VERSION, self.model.get_version(), required=True
        )
        self.model.set_version(response_version)

        self.prompt_build_configs()
        self.prompt_publish_configs()

        response_gdk_version = self.prompter(
            Fields.GDK_VERSION, self.model.get_gdk_version(), required=True
        )
        self.model.set_gdk_version(response_gdk_version)


def main():
    wizard = Wizard()
    wizard.prompt_fields()
    wizard.data.write_to_config_file()
    sys.exit("Wizard completed. Exiting...")


if __name__ == "__main__":
    main()

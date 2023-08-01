from gdk.wizard.commands.data import Wizard_data
from gdk.wizard.commons.fields import Fields
from gdk.wizard.commons.checkers import Wizard_checker
from gdk.wizard.commons.getters import Wizard_getter
from gdk.wizard.commons.setters import Wizard_setter
import argparse
import json
from PyInquirer import prompt


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
            getter: Wizard_getter object
            setter: Wizard_setter object
            checker: Wizard_checker object
            parser: argparse object
        """

        self.data = Wizard_data()
        self.getter = Wizard_getter(self.data)
        self.setter = Wizard_setter(self.data)
        self.checker = Wizard_checker(self.data)

        self.parser = argparse.ArgumentParser()

    def prompter(self, field, value, required, max_attempts=3):
        """
        Prompts the user for a value of a given field key

        Parameters
        ----------
            field (string): a field key of the gdk-config file to be changed
            value (string): the current value corresponding the field key to be changed
            required (boolean): if the field is a required field of the gdk config file
            max_attempts (int): the maximum number of attempts to get a valid response from the user

        Returns
        -------
            string: the value for the field key "field"
        """
        require = "required " if required else "optional "
        for attempt in range(1, max_attempts + 1):
            args = self.parser.parse_args(
                [f"--{field}", self.interactive_prompt(field, value, require)]
            )

            response = getattr(args, field)
            if self.checker.is_valid_input(response, field):
                return response
            print(
                f"Attempt {attempt}/{max_attempts}: Invalid response. Please try again."
            )

        print("Exceeded maximum attempts. Assuming default response.")
        return value

    def change_build_or_publish(self, build_or_publish, max_attempts=3):
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
            f"--change_{build_or_publish}",
            help=f"Change componenet {build_or_publish} configurations",
        )

        for _ in range(max_attempts):
            args = self.parser.parse_args(
                [
                    f"--change_{build_or_publish}",
                    input(
                        f"Do you want to change the {build_or_publish} configurations? (y/n) "
                    ),
                ]
            )
            response = getattr(args, f"change_{build_or_publish}").strip().lower()
            if response in {"y", "yes"}:
                return True
            elif response in {"n", "no"}:
                return False
            print("Your input was invalid response. Please respond again.")
        return False

    def write_to_config_file(self):
        """
        Writes all the values in field_map to the gdk-config.json file

        Parameters
        ----------
            None

        Returns
        -------
            None
        """
        with open(self.data.project_config_file, "w", encoding="utf-8") as f:
            f.write(json.dumps(self.field_map, indent=4))

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
        answer = prompt(questions)
        return answer["user_input"]

    def prompt_build(self):
        """
        Asks user if they would like to change build configurations and prompts corresponding fields

        Parameters
        ----------
            None

        Returns
        -------
            None

        """
        if self.change_build_or_publish("build"):
            response_custom_build_command = self.prompter(
                "custom_build_command",
                self.getter.get_custom_build_command(),
                required=False,
            )
            self.setter.set_custom_build_command(response_custom_build_command)

            response_build_system = self.prompter(
                "build_system", self.getter.get_build_system(), required=True
            )
            self.setter.set_build_system(response_build_system)

    def prompt_publish(self):
        """
        Asks user if they would like to change publish configurations and prompts corresponding fields

        Parameters
        ----------
            None

        Returns
        -------
            None

        """
        if self.change_build_or_publish("publish"):
            response_bucket = self.prompter(
                "bucket", self.getter.get_bucket(), required=True
            )
            self.setter.set_bucket(response_bucket)

            response_region = self.prompter(
                "region", self.getter.get_region(), required=False
            )
            self.setter.set_region(response_region)

            response_options = self.prompter(
                "options", self.getter.get_options(), required=False
            )
            self.setter.set_options(response_options)

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

        # Add all the optional and required fields to the parser
        for field in Fields:
            self.parser.add_argument(f"--{field.value}")

        response_author = self.prompter(
            "author", self.getter.get_author(), required=True
        )
        self.setter.set_author(response_author)

        response_version = self.prompter(
            "version", self.getter.get_version(), required=True
        )
        self.setter.set_version(response_version)

        self.prompt_build()
        self.prompt_publish()

        response_gdk_version = self.prompter(
            "gdk_version", self.getter.get_gdk_version(), required=True
        )
        self.setter.set_gdk_version(response_gdk_version)

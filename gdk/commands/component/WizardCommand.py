from gdk.wizard.Prompter import Prompter
from gdk.commands.Command import Command
import sys


class WizardCommand(Command):
    def __init__(self, command_args) -> None:
        super().__init__(command_args, "wizard")

    def run(self):
        wizard = Prompter()
        wizard.prompt_fields()
        wizard.utils.write_to_config_file(
            Prompter.field_dict, Prompter.project_config_file
        )
        sys.exit("Wizard completed. Exiting...")

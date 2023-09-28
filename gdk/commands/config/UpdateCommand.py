import logging

from gdk.commands.config.update.Prompter import Prompter
from gdk.commands.Command import Command
import gdk.common.exceptions.error_messages as error_messages


class UpdateCommand(Command):
    def __init__(self, command_args) -> None:
        super().__init__(command_args, "update")

    def run(self):
        if "component" in self.arguments and self.arguments["component"]:
            prompter = Prompter()
            prompter.prompt_fields()
            prompter.utils.write_to_config_file(prompter.field_dict, prompter.project_config_file)
            logging.info("Config file has been updated. Exiting...")
            return
        raise Exception(error_messages.CONFIG_UPDATE_WITH_INVALID_ARGS)

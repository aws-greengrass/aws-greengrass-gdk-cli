import gdk.common.consts as consts
import gdk.common.exceptions.error_messages as error_messages
import gdk.commands.Command as Command
import gdk.commands.component.project_utils as get_project_config_values
import gdk.common.configuration as get_configuration
import gdk.common.configuration as validate_configuration


class Wizard:
    def __init__(self) -> None:
        # self.field_map is a dictionary object
        self.field_map = get_configuration()

    def prompt():
        return
    

    """
    upon exiting the wizard, it will first flush all the values 
    stored in self.field_map to the config file 
    """
    def write_to_config_file():
        pass

    






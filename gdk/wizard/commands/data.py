from gdk.common.configuration import get_configuration, _get_project_config_file
import gdk.common.consts as consts
import gdk.common.utils as utils
import json


class Wizard_data:
    def __init__(self):
        self.project_config_file = _get_project_config_file()
        self.field_map = get_configuration()
        self.project_config = self.field_map["component"]
        self.component_name = next(iter(self.project_config))
        self.schema = self.get_schema()

    def get_schema(self):
        """
        Retrieves the schema of the config file

        Raises an exception if the schema file doesn't exist.

        Parameters
        ----------
            None

        Returns
        -------
            data(dict): config file schema as a python dictionary object
        """

        schema_file = utils.get_static_file_path(consts.config_schema_file)
        with open(schema_file, "r") as schemaFile:
            schema = json.loads(schemaFile.read())
        return schema

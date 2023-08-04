from gdk.common.configuration import get_configuration, _get_project_config_file
import gdk.common.consts as consts
import gdk.common.utils as utils
import json


class Wizard_data:
    def __init__(self):
        self.project_config_file = "/Users/jacksozh/Desktop/aws-greengrass-gdk-cli/gdk/wizard/static/default_config.json"
        with open(self.project_config_file, "r") as config_file:
            config_data = json.loads(config_file.read())
        self.field_map = config_data

        # self.project_config_file = _get_project_config_file()
        # self.field_map = get_configuration()
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
        with open(self.project_config_file, "w", encoding="utf-8") as f:
            f.write(json.dumps(self.field_map, indent=4))

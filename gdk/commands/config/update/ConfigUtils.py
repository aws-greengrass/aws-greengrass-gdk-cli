import gdk.common.configuration as config
import json


class ConfigUtils:
    def get_project_config_file(self):
        return config._get_project_config_file()

    def read_from_config_file(self):
        return config.get_configuration()

    def write_to_config_file(self, field_dict, config_file_path):
        """
        Writes all the values in field_map to the gdk-config.json file

        Parameters
        ----------
            None

        Returns
        -------
            None
        """
        with open(config_file_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(field_dict, indent=4))

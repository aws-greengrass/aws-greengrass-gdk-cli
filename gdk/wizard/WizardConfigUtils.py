import gdk.common.configuration as config
import json


class WizardData:
    def get_project_config_file(self):
        return config._get_project_config_file()

    def read_from_config_file(self):
        return config.get_configuration()

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

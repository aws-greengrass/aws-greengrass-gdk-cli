import gdk.common.configuration as config
import json


class WizardData:
    def __init__(self):
        self.project_config_file = config._get_project_config_file()
        self.field_map = config.get_configuration()
        self.project_config = self.field_map["component"]
        self.component_name = next(iter(self.project_config))

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

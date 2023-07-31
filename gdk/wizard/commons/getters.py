class Wizard_getter:
    def __init__(self, data):
        self.data = data
        self.field_map = self.data.field_map
        self.project_config = self.data.project_config
        self.component_name = self.data.component_name

    def get_author(self):
        try:
            return self.project_config[self.component_name]["author"]
        except KeyError:
            return None

    def get_version(self):
        try:
            return self.project_config[self.component_name]["version"]
        except KeyError:
            return None

    def get_custom_build_command(self):
        try:
            return self.project_config[self.component_name]["build"][
                "custom_build_command"
            ]
        except KeyError:
            return None

    def get_build_system(self):
        try:
            return self.project_config[self.component_name]["build"]["build_system"]
        except KeyError:
            return None

    def get_bucket(self):
        try:
            return self.project_config[self.component_name]["publish"]["bucket"]
        except KeyError:
            return None

    def get_region(self):
        try:
            return self.project_config[self.component_name]["publish"]["region"]
        except KeyError:
            return None

    def get_options(self):
        try:
            return self.project_config[self.component_name]["publish"]["options"]
        except KeyError:
            return None

    def get_gdk_version(self):
        try:
            return self.field_map["gdk_version"]
        except KeyError:
            return None

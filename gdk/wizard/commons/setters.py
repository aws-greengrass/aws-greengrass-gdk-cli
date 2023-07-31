class Wizard_setter:
    def __init__(self, data):
        self.data = data
        self.component_name = self.data.component_name

    def set_author(self, value):
        if value:
            self.data.field_map["component"][self.component_name]["author"] = value

    def set_version(self, value):
        if value:
            self.data.field_map["component"][self.component_name]["version"] = value

    def set_custom_build_command(self, value):
        if value:
            self.data.field_map["component"][self.component_name]["build"][
                "custom_build_command"
            ] = value

    def set_build_system(self, value):
        if value:
            self.data.field_map["component"][self.component_name]["build"][
                "build_system"
            ] = value

    def set_bucket(self, value):
        if value:
            self.data.field_map["component"][self.component_name]["publish"][
                "bucket"
            ] = value

    def set_region(self, value):
        if value:
            self.data.field_map["component"][self.component_name]["publish"][
                "region"
            ] = value

    def set_options(self, value):
        if value:
            self.data.field_map["component"][self.component_name]["publish"][
                "options"
            ] = value

    def set_gdk_version(self, value):
        if value:
            self.data.field_map["gdk_version"] = value

from gdk.wizard.commons.fields import Fields


class Wizard_model:
    def __init__(self, data):
        self.data = data
        self.field_map = self.data.field_map
        self.project_config = self.data.project_config
        self.component_name = self.data.component_name

    def get_author(self):
        try:
            return self.project_config[self.component_name][Fields.AUTHOR.value.key]
        except KeyError:
            return Fields.AUTHOR.value.default

    def get_version(self):
        try:
            return self.project_config[self.component_name][Fields.VERSION.value.key]
        except KeyError:
            return Fields.VERSION.value.default

    def get_custom_build_command(self):
        try:
            return self.project_config[self.component_name][Fields.BUILD.value.key][
                Fields.CUSTOM_BUILD_COMMAND.value.key
            ]
        except KeyError:
            return Fields.CUSTOM_BUILD_COMMAND.value.default

    def get_build_system(self):
        try:
            return self.project_config[self.component_name][Fields.BUILD.value.key][
                Fields.BUILD_SYSTEM.value.key
            ]
        except KeyError:
            return Fields.BUILD_SYSTEM.value.default

    def get_build_options(self):
        try:
            return self.project_config[self.component_name][Fields.BUILD.value.key][
                Fields.BUILD_OPTIONS.value.key
            ]
        except KeyError:
            return Fields.PUBLISH_OPTIONS.value.default

    def get_bucket(self):
        try:
            return self.project_config[self.component_name][Fields.PUBLISH.value.key][
                Fields.BUCKET.value.key
            ]
        except KeyError:
            return Fields.BUCKET.value.default

    def get_region(self):
        try:
            return self.project_config[self.component_name][Fields.PUBLISH.value.key][
                Fields.REGION.value.key
            ]
        except KeyError:
            return Fields.REGION.value.default

    def get_publish_options(self):
        try:
            return self.project_config[self.component_name][Fields.PUBLISH.value.key][
                Fields.PUBLISH_OPTIONS.value.key
            ]
        except KeyError:
            return Fields.PUBLISH_OPTIONS.value.default

    def get_gdk_version(self):
        try:
            return self.field_map[Fields.GDK_VERSION.value.key]
        except KeyError:
            return Fields.GDK_VERSION.value.default

    def set_author(self, value):
        print(value)
        if value:
            self.data.field_map[Fields.COMPONENT.value.key][self.component_name][
                Fields.AUTHOR.value.key
            ] = value

    def set_version(self, value):
        if value:
            self.data.field_map[Fields.COMPONENT.value.key][self.component_name][
                Fields.VERSION.value.key
            ] = value

    def set_build_config_values(self, field, value):
        if value:
            self.data.field_map[Fields.COMPONENT.value.key][self.component_name][
                Fields.BUILD.value.key
            ][field.key] = value

    def set_custom_build_command(self, value):
        self.set_build_config_values(Fields.CUSTOM_BUILD_COMMAND.value, value)

    def set_build_system(self, value):
        self.set_build_config_values(Fields.BUILD_SYSTEM.value, value)

    def set_build_options(self, value):
        self.set_build_config_values(Fields.BUILD_OPTIONS.value, value)

    def set_publish_config_values(self, field, value):
        if value:
            self.data.field_map[Fields.COMPONENT.value.key][self.component_name][
                Fields.PUBLISH.value.key
            ][field.key] = value

    def set_bucket(self, value):
        self.set_publish_config_values(Fields.BUCKET.value, value)

    def set_region(self, value):
        self.set_publish_config_values(Fields.REGION.value, value)

    def set_publish_options(self, value):
        self.set_publish_config_values(Fields.PUBLISH_OPTIONS.value, value)

    def set_gdk_version(self, value):
        if value:
            self.data.field_map[Fields.GDK_VERSION.value.key] = value

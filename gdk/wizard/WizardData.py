from gdk.wizard.ConfigEnum import ConfigEnum


class Model:
    def __init__(self, getter, setter):
        self.getter = getter
        self.setter = setter


class WizardData:
    def __init__(self, field_dict):
        self.field_dict = field_dict
        self.project_config = self.field_dict[ConfigEnum.COMPONENT.value.key]
        self.component_name = next(iter(self.project_config))
        self.component_config = self.project_config.get(
            self.component_name, ConfigEnum.COMPONENT_NAME.value.default
        )

        self.switch = {
            ConfigEnum.AUTHOR: Model(self.get_author, self.set_author),
            ConfigEnum.VERSION: Model(self.get_version, self.set_version),
            ConfigEnum.BUILD_SYSTEM: Model(
                self.get_build_system, self.set_build_system
            ),
            ConfigEnum.CUSTOM_BUILD_COMMAND: Model(
                self.get_custom_build_command, self.set_custom_build_command
            ),
            ConfigEnum.BUILD_OPTIONS: Model(
                self.get_build_options, self.set_build_options
            ),
            ConfigEnum.BUCKET: Model(self.get_bucket, self.set_bucket),
            ConfigEnum.REGION: Model(self.get_region, self.set_region),
            ConfigEnum.PUBLISH_OPTIONS: Model(
                self.get_publish_options, self.set_publish_options
            ),
            ConfigEnum.GDK_VERSION: Model(self.get_gdk_version, self.set_gdk_version),
        }

    def get_field(self, field):
        return self.switch.get(field).getter()

    def set_field(self, field, value):
        self.switch.get(field).setter(value)

    def get_author(self):
        return self.component_config.get(
            ConfigEnum.AUTHOR.value.key, ConfigEnum.AUTHOR.value.default
        )

    def get_version(self):
        return self.component_config.get(
            ConfigEnum.VERSION.value.key, ConfigEnum.VERSION.value.default
        )

    def get_build_system(self):
        return self.component_config.get(
            ConfigEnum.BUILD.value.key, ConfigEnum.BUILD.value.default
        ).get(
            ConfigEnum.BUILD_SYSTEM.value.key,
            ConfigEnum.BUILD_SYSTEM.value.default,
        )

    def get_custom_build_command(self):
        return self.component_config.get(
            ConfigEnum.BUILD.value.key, ConfigEnum.BUILD.value.default
        ).get(
            ConfigEnum.CUSTOM_BUILD_COMMAND.value.key,
            ConfigEnum.CUSTOM_BUILD_COMMAND.value.default,
        )

    def get_build_options(self):
        return self.component_config.get(
            ConfigEnum.BUILD.value.key, ConfigEnum.BUILD.value.default
        ).get(
            ConfigEnum.BUILD_OPTIONS.value.key,
            ConfigEnum.BUILD_OPTIONS.value.default,
        )

    def get_bucket(self):
        return self.component_config.get(
            ConfigEnum.PUBLISH.value.key, ConfigEnum.PUBLISH.value.default
        ).get(
            ConfigEnum.BUCKET.value.key,
            ConfigEnum.BUCKET.value.default,
        )

    def get_region(self):
        return self.component_config.get(
            ConfigEnum.PUBLISH.value.key, ConfigEnum.PUBLISH.value.default
        ).get(
            ConfigEnum.REGION.value.key,
            ConfigEnum.REGION.value.default,
        )

    def get_publish_options(self):
        return self.component_config.get(
            ConfigEnum.PUBLISH.value.key, ConfigEnum.PUBLISH.value.default
        ).get(
            ConfigEnum.PUBLISH_OPTIONS.value.key,
            ConfigEnum.PUBLISH_OPTIONS.value.default,
        )

    def get_gdk_version(self):
        return self.field_dict.get(
            ConfigEnum.GDK_VERSION.value.key, ConfigEnum.GDK_VERSION.value.default
        )

    def set_author(self, value):
        if value:
            self.component_config[ConfigEnum.AUTHOR.value.key] = value

    def set_version(self, value):
        if value:
            self.component_config[ConfigEnum.VERSION.value.key] = value

    def _set_build_config_values(self, field, value):
        if value:
            self.component_config[ConfigEnum.BUILD.value.key][field.key] = value

    def set_build_system(self, value):
        self._set_build_config_values(ConfigEnum.BUILD_SYSTEM.value, value)

    def set_custom_build_command(self, value):
        self._set_build_config_values(ConfigEnum.CUSTOM_BUILD_COMMAND.value, value)

    def set_build_options(self, value):
        self._set_build_config_values(ConfigEnum.BUILD_OPTIONS.value, value)

    def _set_publish_config_values(self, field, value):
        if value:
            self.component_config[ConfigEnum.PUBLISH.value.key][field.key] = value

    def set_bucket(self, value):
        self._set_publish_config_values(ConfigEnum.BUCKET.value, value)

    def set_region(self, value):
        self._set_publish_config_values(ConfigEnum.REGION.value, value)

    def set_publish_options(self, value):
        self._set_publish_config_values(ConfigEnum.PUBLISH_OPTIONS.value, value)

    def set_gdk_version(self, value):
        if value:
            self.field_dict[ConfigEnum.GDK_VERSION.value.key] = value

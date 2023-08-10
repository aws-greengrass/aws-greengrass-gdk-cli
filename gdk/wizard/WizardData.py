from gdk.wizard.ConfigEnum import ConfigEnum


class WizardData:
    def __init__(self, field_dict):
        self.field_dict = field_dict
        self.project_config = self.field_dict[ConfigEnum.COMPONENT.value.key]
        self.component_name = next(iter(self.project_config))
        self.component_config = self.project_config.get(
            self.component_name, ConfigEnum.COMPONENT_NAME.value.default
        )

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

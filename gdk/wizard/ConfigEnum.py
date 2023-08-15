from aenum import Enum, NoAlias


class ConfigEnumDefault:
    def __init__(self, key, default=None):
        self.key = key
        self.default = default


class ConfigEnum(Enum):
    # using NoAlias to avoid hash collisions

    _settings_ = NoAlias
    COMPONENT = ConfigEnumDefault("component")
    COMPONENT_NAME = ConfigEnumDefault("component_name", default="gg-component")
    AUTHOR = ConfigEnumDefault("author", default="gg-customer")
    VERSION = ConfigEnumDefault("version", default="1.0.0")

    BUILD = ConfigEnumDefault("build", default={})
    BUILD_SYSTEM = ConfigEnumDefault("build_system", "zip")
    CUSTOM_BUILD_COMMAND = ConfigEnumDefault("custom_build_command")
    BUILD_OPTIONS = ConfigEnumDefault("options", default={})

    PUBLISH = ConfigEnumDefault("publish", default={})
    BUCKET = ConfigEnumDefault("bucket", default="gg-component-bucket")
    REGION = ConfigEnumDefault("region", default="us-east-1")
    PUBLISH_OPTIONS = ConfigEnumDefault("options", default={})
    GDK_VERSION = ConfigEnumDefault("gdk_version", default="1.0.0")

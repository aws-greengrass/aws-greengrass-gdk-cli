from aenum import Enum, NoAlias


class Field_data:
    def __init__(self, key, default=None):
        self.key = key
        self.default = default


class Fields(Enum):
    # using NoAlias to avoid hash collisions

    _settings_ = NoAlias
    COMPONENT = Field_data("component")
    COMPONENT_NAME = Field_data("component_name", default="gg-component")
    AUTHOR = Field_data("author", default="gg-customer")
    VERSION = Field_data("version", default="1.0.0")

    BUILD = Field_data("build")
    BUILD_SYSTEM = Field_data("build_system", "zip")
    CUSTOM_BUILD_COMMAND = Field_data("custom_build_command")
    BUILD_OPTIONS = Field_data("options", "{}")

    PUBLISH = Field_data("publish")
    BUCKET = Field_data("bucket", default="gg-component-bucket")
    REGION = Field_data("region", default="us-east-1")
    PUBLISH_OPTIONS = Field_data("options", "{}")
    GDK_VERSION = Field_data("gdk_version", default="1.0.0")

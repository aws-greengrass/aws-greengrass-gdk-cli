CONFIG_FILE_NOT_EXISTS = (
    "Config file doesn't exist. Please initialize the project using a template or a repository before using greengrass-tools"
    " commands."
)
CONFIG_SCHEMA_FILE_NOT_EXISTS = "Configuration validation failed. Config schema file doesn't exist."
PROJECT_RECIPE_FILE_NOT_FOUND = (
    "No valid component recipe is found. Please include a valid recipe file of the component to build with default."
)
PROJECT_CONFIG_FILE_INVALID = "Project configuration file '{}' is invalid. Please correct its format and try again. Error: {} "
CLI_MODEL_FILE_NOT_EXISTS = "Model validation failed. CLI model file doesn't exist."
INVALID_CLI_MODEL = "CLI model is invalid. Please provide a valid model to create the CLI parser."
LISTING_COMPONENTS_FAILED = "Failed to list the available components from GitHub. Please try again after sometime."
INIT_FAILS_DURING_COMPONENT_DOWNLOAD = "Failed to download the selected component {{}}. Please try again after sometime."
INIT_WITH_INVALID_ARGS = (
    "Could not initialize the project as the arguments passed are invalid. Please initialize the project with correct"
    " args.\nTry `greengrass-tools component init --help`"
)
INIT_WITH_CONFLICTING_ARGS = (
    "Could not initialize the project as the command args are conflicting. Please initialize the project with correct"
    " args.\nTry `greengrass-tools component init --help` "
)
INIT_NON_EMPTY_DIR_ERROR = (
    "Could not initialize the project as the directory is not empty. Please initialize the project in an empty directory.\nTry"
    " `greengrass-tools component init --help`"
)

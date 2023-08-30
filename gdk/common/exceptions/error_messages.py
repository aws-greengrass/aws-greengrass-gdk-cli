# FILE
CONFIG_FILE_NOT_EXISTS = (
    "Config file doesn't exist. Please initialize the project using a template or a repository before using gdk commands."
)
CONFIG_SCHEMA_FILE_NOT_EXISTS = "Configuration validation failed. Config schema file doesn't exist."
PROJECT_RECIPE_FILE_NOT_FOUND = (
    "No valid component recipe is found. Please include a valid recipe file of the component to build with default."
)
PROJECT_CONFIG_FILE_INVALID = "Project configuration file '{}' is invalid. Please correct its format and try again. Error: {} "
RECIPE_FILE_INVALID = "The input recipe file '{}' is invalid. Please correct its format and try again. Error: {} "
RECIPE_SIZE_INVALID = "The input recipe file '{}' has an invalid size. Please make sure it does not exceed 16KB and try again."
CLI_MODEL_FILE_NOT_EXISTS = "Model validation failed. CLI model file doesn't exist."
USER_INPUT_RECIPE_NOT_EXISTS = (
    "Recipe file not found. "
    "Please ensure that the component's recipe file is initialized as either recipe.json or recipe.yaml."
)
MULTIPLE_INPUT_RECIPES_EXIST = (
    "Both JSON and YAML recipe files found. Only one recipe file (JSON or YAML) should exist."
)

# CLI MODEL
INVALID_CLI_MODEL = "CLI model is invalid. Please provide a valid model to create the CLI parser."

# LIST COMMAND
LISTING_COMPONENTS_FAILED = (
    "Failed to list the available components from Greengrass Software Catalog. Please try again after sometime."
)
LIST_WITH_INVALID_ARGS = (
    "Could not list the components as the command arguments are invalid. Please supply either `--template` or `--repository`"
    " as an argument to the list command.\nTry `gdk component list --help`"
)

# INIT COMMAND
INIT_FAILS_DURING_COMPONENT_DOWNLOAD = "Failed to download the selected component {{}}. Please try again after sometime."
INIT_WITH_INVALID_ARGS = (
    "Could not initialize the project as the arguments passed are invalid. Please initialize the project with correct"
    " arguments.\nTry `gdk component init --help`"
)
INIT_WITH_CONFLICTING_ARGS = (
    "Could not initialize the project as the command arguments are conflicting. Please initialize the project with correct"
    " arguments.\nTry `gdk component init --help` "
)
INIT_NON_EMPTY_DIR_ERROR = (
    "Could not initialize the project as the directory is not empty. Please initialize the project in an empty directory.\nTry"
    " `gdk component init --help`"
)
INIT_DIR_EXISTS_ERROR = (
    "Could not initialize the project as the directory '{}' already exists. Please initialize the project with a new"
    " directory.\nTry `gdk component init --help`"
)
# BUILD COMMAND
BUILD_FAILED = "Failed to build the component with the given project configuration."

# PUBLISH COMMAND
PUBLISH_FAILED = "Failed to publish new version of component with the given configuration."

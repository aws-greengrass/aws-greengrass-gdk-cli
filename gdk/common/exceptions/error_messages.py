# FILE
CONFIG_FILE_NOT_EXISTS = (
    "Config file doesn't exist. Please initialize the project using a template or a repository before using gdk commands."
)
CONFIG_SCHEMA_FILE_NOT_EXISTS = "Configuration validation failed. Config schema file doesn't exist."
PROJECT_RECIPE_FILE_NOT_FOUND = (
    "No valid component recipe is found. Please include a valid recipe file of the component to build with default."
)
PROJECT_CONFIG_FILE_INVALID = "Project configuration file '{}' is invalid. Please correct its format and try again. Error: {} "
CLI_MODEL_FILE_NOT_EXISTS = "Model validation failed. CLI model file doesn't exist."

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

# PUBLISH COMMAND
PUBLISH_FAILED = "Failed to publish new version of component with the given configuration."

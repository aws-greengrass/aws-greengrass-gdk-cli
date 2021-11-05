import greengrassTools.common.consts as consts
# COMMANDS

## INIT
INIT_NON_EMPTY_DIR_ERROR = "Could not initialize the project as the directory is not empty. Please initialize the project in an empty directory.\nTry `greengrass-tools component init --help`"
INIT_WITH_INVALID_ARGS = "Could not initialize the project as the arguments passed are invalid. Please initialize the project with correct args.\nTry `greengrass-tools component init --help`"
INIT_WITH_INVALID_TEMPLATE = "Could not initialize the project as no such template exists. Please initialize the project with correct args.\nTry `greengrass-tools component list --template`"
INIT_WITH_CONFLICTING_ARGS = "Could not initialize the project as the command args are conflicting. Please initialize the project with correct args.\nTry `greengrass-tools component init --help` "
INIT_WITH_INVALID_REPOSITORY = "Could not initialize the project as no such component respository exists. Please initialize the project with correct args.\nTry `greengrass-tools component list --repository`"
INIT_WITH_INVALID_COMPONENT = "Could not initialize the project as no such component {{}} exists. Please initialize the project with correct args. \nTry `greengrass-tools component list --{{}}`"
##BUILD
BUILD_WITH_NO_VALID_RECIPE = "Building the component with 'default' configuration failed as no valid component recipe is found in the project directory."
BUILD_WITH_DEFAULT_FAILED = "Failed to build the component with default configuration."
BUILD_WITH_DEFAULT_COMMAND_FAILED = "Failed to run the build command with default configuration"

## PUBLISH
PUBLISH_FAILED = "Failed to publish new version of component with the given configuration."

# FILES 
CONFIG_FILE_NOT_EXISTS = "Config file doesn't exist. Please initialize the project using a template or a repository before using greengrass-tools commands."
CONFIG_SCHEMA_FILE_NOT_EXISTS = "Configuration validation failed. Config schema file doesn't exist."
PROJECT_RECIPE_FILE_NOT_FOUND = "No valid component recipe is found. Please include a valid recipe file of the component to build with default."
PROJECT_JSON_RECIPE_FILE_NOT_FOUND = "No valid json recipes found for the component."
PROJECT_YAML_RECIPE_FILE_NOT_FOUND = "No valid yaml recipes found for the component."
PROJECT_CONFIG_FILE_INVALID="Invalid project configuration file. Please correct it to use it with {}".format(consts.cli_tool_name)

# EXTERNAL 
INIT_FAILS_DURING_TEMPLATE_DOWNLOAD = "Failed to download the selected component template. Please try again after sometime."
INIT_FAILS_DURING_LISTING_TEMPLATES = "Failed to list the available component templates. Please try again after sometime."
INIT_FAILS_DURING_LISTING_REPOSITORIES = "Failed to list the available component repositories. Please try again after sometime."
LISTING_COMPONENTS_FAILED = "Failed to list the available components from GitHub. Please try again after sometime."
INIT_FAILS_DURING_COMPONENT_DOWNLOAD = "Failed to download the selected component {{}}. Please try again after sometime."

# TOOL - INTERNAL
# CLI_MODEL_FILE_NOT_EXISTS = "Model validation failed. CLI model file doesn't exist."
# INVALID_CLI_MODEL = "CLI model is invalid. Please provide a valid model to create the CLI parser."
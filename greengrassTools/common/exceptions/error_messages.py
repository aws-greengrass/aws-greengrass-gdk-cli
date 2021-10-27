
# COMMANDS
INIT_NON_EMPTY_DIR_ERROR = "Could not init the project as the directory is not empty. Please init the project in an empty directory.\nTry `greengrass-tools component init --help`"
INIT_WITH_INVALID_ARGS = "Could not init the project as the arguments passed are invalid. Please init the project with correct args.\nTry `greengrass-tools component init --help`"
INIT_WITH_INVALID_TEMPLATE = "Could not init the project as no such template exists. Please init the project with correct args.\nTry `greengrass-tools component template list`"
INIT_WITH_CONFLICTING_ARGS = "Could not init the project as the command args are conflicting. Please init the project with correct args.\nTry `greengrass-tools component init --help` "

# FILES 
CONFIG_FILE_NOT_EXISTS = "Config file doesn't exist. Please init the project using a template or a repository before using greengrass-tools commands."
CONFIG_SCHEMA_FILE_NOT_EXISTS = "Configuration validation failed. Config schema file doesn't exist."
PROJECT_RECIPE_FILE_NOT_FOUND = "No valid component recipe is found. Please include a valid recipe file of the component to build with default."
PROJECT_JSON_RECIPE_FILE_NOT_FOUND = "No valid json recipes found for the component."
PROJECT_YAML_RECIPE_FILE_NOT_FOUND = "No valid yaml recipes found for the component."

# EXTERNAL 
INIT_FAILS_DURING_TEMPLATE_DOWNLOAD = "Failed to download the selected component template. Please try again after sometime."
INIT_FAILS_DURING_LISTING_TEMPLATES = "Failed to list the available component templates. Please try again after sometime."

# TOOL - INTERNAL
# CLI_MODEL_FILE_NOT_EXISTS = "Model validation failed. CLI model file doesn't exist."
# INVALID_CLI_MODEL = "CLI model is invalid. Please provide a valid model to create the CLI parser."
# CLI MODEL
cli_tool_name = "gdk"
arg_parameters = [
    "name",
    "action",
    "nargs",
    "const",
    "default",
    "type",
    "choices",
    "required",
    "help",
    "metavar",
    "dest",
]

# MAX RECIPE FILE SIZE
MAX_RECIPE_FILE_SIZE_BYTES = 16000

# FILES
config_schema_file = "config_schema.json"
recipe_schema_file = "recipe_schema.json"
cli_model_file = "cli_model.json"
cli_project_config_file = "gdk-config.json"
greengrass_build_dir = "greengrass-build"
E2E_TESTS_DIR_NAME = "gg-e2e-tests"

# URLS
templates_list_url = (
    "https://raw.githubusercontent.com/aws-greengrass/aws-greengrass-software-catalog/main/cli-components/templates.json"
)
repository_list_url = (
    "https://raw.githubusercontent.com/aws-greengrass/aws-greengrass-software-catalog/main/cli-components/"
    + "community-components.json"
)
DOCS_RECIPE_LINK = "https://docs.aws.amazon.com/greengrass/v2/developerguide/component-recipe-reference.html"
GDK_CONFIG_DOCS_LINK = (
    "https://docs.aws.amazon.com/greengrass/v2/developerguide/gdk-cli-configuration-file.html#gdk-config-format"
)
GTF_REPO_OWNER = "aws-greengrass"
GTF_REPO_NAME = "aws-greengrass-testing"

# DEFAULT LOGGING
log_format = "[%(asctime)s] %(levelname)s - %(message)s"
date_format = "%Y-%m-%d %H:%M:%S"

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

# FILE SIZE
MAX_RECIPE_FILE_SIZE_BYTES = 16000

# FILES
config_schema_file = "config_schema.json"
user_input_recipe_schema_file = "user_input_recipe_schema.json"
cli_model_file = "cli_model.json"
cli_project_config_file = "gdk-config.json"
greengrass_build_dir = "greengrass-build"
E2E_TESTS_DIR_NAME = "gg-e2e-tests"
user_input_recipe_json = "recipe.json"
user_input_recipe_yaml = "recipe.yaml"

# URLS
templates_list_url = (
    "https://raw.githubusercontent.com/aws-greengrass/aws-greengrass-software-catalog/main/cli-components/templates.json"
)
repository_list_url = (
        "https://raw.githubusercontent.com/aws-greengrass/aws-greengrass-software-catalog/main/cli-components/"
        + "community-components.json"
)
recipe_reference_url = ("https://docs.aws.amazon.com/greengrass/v2/developerguide/component-recipe-reference.html")

# DEFAULT LOGGING
log_format = "[%(asctime)s] %(levelname)s - %(message)s"
date_format = "%Y-%m-%d %H:%M:%S"

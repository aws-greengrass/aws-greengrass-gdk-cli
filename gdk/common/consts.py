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
# FILES
config_schema_file = "config_schema.json"
cli_model_file = "cli_model.json"
cli_project_config_file = "gdk-config.json"
greengrass_build_dir = "greengrass-build"
project_build_system_file = "project_build_system.json"
project_build_schema_file = "project_build_schema.json"
E2E_TESTS_DIR_NAME = "gg-e2e-tests"

# URLS
templates_list_url = (
    "https://raw.githubusercontent.com/aws-greengrass/aws-greengrass-software-catalog/main/cli-components/templates.json"
)
repository_list_url = (
    "https://raw.githubusercontent.com/aws-greengrass/aws-greengrass-software-catalog/main/cli-components/"
    + "community-components.json"
)

# DEFAULT LOGGING
log_format = "[%(asctime)s] %(levelname)s - %(message)s"
date_format = "%Y-%m-%d %H:%M:%S"

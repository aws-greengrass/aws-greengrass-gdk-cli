from pathlib import Path

# Names
cli_tool_name = "greengrass-tools"
cli_tool_name_in_method_names = "greengrass_tools"
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

# Files
cli_project_config_file = "greengrass-tools-config.json"
config_schema_file = "config_schema.json"
cli_model_file = "cli_model.json"
supported_component_builds_file = "supported_component_builds.json"
project_build_schema_file = "project_build_schema.json"

# URLS
## TODO: Replace it with main branch
templates_list_url = "https://raw.githubusercontent.com/aws-greengrass/aws-greengrass-community-catalog/list-components/components/templates.json"
repository_list_url = ""

# Frequently used expressions
current_directory = Path('.').resolve()
log_format = "%(asctime)s %(levelname)s %(message)s"



import os

cli_tool_name = "greengrass-tools"
cli_tool_name_in_method_names = "greengrass_tools"
cli_tool_config_file = "greengrass-tools-config.json"
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
config_schema_file = "config_schema.json"
cli_model_file = "cli_model.json"
## Replace it with main branch
templates_list_url = "https://raw.githubusercontent.com/aws-greengrass/aws-greengrass-community-catalog/list-components/components/templates.json"
current_directory = os.path.abspath(os.getcwd())


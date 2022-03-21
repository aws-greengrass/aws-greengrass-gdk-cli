import json
import logging
from pathlib import Path

import boto3
import gdk.common.configuration as config_actions
import gdk.common.consts as consts
import gdk.common.exceptions.error_messages as error_messages
import gdk.common.utils as utils
import yaml


def get_supported_component_builds():
    """
    Reads a json file from static location that contains information related to supported component build systems.

    Parameters
    ----------
        None

    Returns
    -------
      (dict): Returns a dict object with supported component builds information.
    """
    supported_component_builds_file = utils.get_static_file_path(consts.project_build_system_file)
    if supported_component_builds_file:
        with open(supported_component_builds_file, "r") as supported_builds_file:
            logging.debug("Identifying build systems supported by the CLI tool with default configuration.")
            return json.loads(supported_builds_file.read())
    return None


def get_recipe_file():
    """
    Finds recipe file based on component name and its extension.

    Assuming that each component project has a single recipe file, this method looks up for json files first
    and then yaml files in the current project directory with component name in them.
    If none or more than one are found, correct recipe file is not identified.

    Raises an exception if no recipe file is found in the current project directory.

    Parameters
    ----------
        None

    Returns
    -------
        recipe_file(Path): Path of the identified recipe file.
    """
    # Search for json files in current directory that contain component name and ends in .json.
    logging.debug("Looking for recipe file in the project directory.")
    json_file = list(Path(utils.current_directory).glob("recipe.json"))
    yaml_file = list(Path(utils.current_directory).glob("recipe.yaml"))

    if not json_file and not yaml_file:
        logging.error("Could not find 'recipe.json' or 'recipe.yaml' in the project directory.")
        raise Exception(error_messages.PROJECT_RECIPE_FILE_NOT_FOUND)

    if json_file and yaml_file:
        logging.error("Found both 'recipe.json' and 'recipe.yaml' in the given project directory.")
        raise Exception(error_messages.PROJECT_RECIPE_FILE_NOT_FOUND)

    recipe_file = (json_file + yaml_file)[0].resolve()
    logging.info("Found component recipe file '{}' in the  project directory.".format(recipe_file.name))
    return recipe_file


def parse_recipe_file(component_recipe_file):
    """
    Loads recipes file from current project as a json obect.

    Uses yaml or json module to load the recipe file based on its extension.

    Parameters
    ----------
        component_recipe_file(pathlib.Path): Path of the component recipe file.

    Returns
    -------
      (dict): Returns a dict object with the component recipe file.
    """
    logging.debug("Parsing the component recipe file '{}'.".format(component_recipe_file.name))
    with open(component_recipe_file, "r") as r_file:
        recipe = r_file.read()
        try:
            if component_recipe_file.name.endswith(".json"):
                recipe_json = json.loads(recipe)
                return recipe_json
            else:
                recipe_yaml = yaml.safe_load(recipe)
                return recipe_yaml
        except Exception as e:
            raise Exception("""Unable to parse the recipe file - {}.\n{}""".format(component_recipe_file.name, e))


def get_project_config_values():

    # Get component configuration from the greengrass project config file.
    logging.info("Getting project configuration from {}".format(consts.cli_project_config_file))
    project_config = config_actions.get_configuration()["component"]

    # Since there's only one key in the component configuration, use next() instead of looping in.
    component_name = next(iter(project_config))
    component_config = project_config[component_name]
    component_version = component_config["version"]
    component_author = component_config["author"]
    component_build_config = component_config["build"]
    bucket = component_config["publish"]["bucket"]
    region = component_config["publish"]["region"]
    encrypt = component_config["publish"].get("encrypt")
    metadata = component_config["publish"].get("metadata")

    # Build directories
    gg_build_directory = Path(utils.current_directory).joinpath(consts.greengrass_build_dir).resolve()
    gg_build_artifacts_dir = Path(gg_build_directory).joinpath("artifacts").resolve()
    gg_build_recipes_dir = Path(gg_build_directory).joinpath("recipes").resolve()
    gg_build_component_artifacts_dir = Path(gg_build_artifacts_dir).joinpath(component_name, component_version).resolve()

    # Get recipe file
    component_recipe_file = get_recipe_file()

    # Get parsed recipe file
    parsed_component_recipe = parse_recipe_file(component_recipe_file)

    # Create dictionary with all the above values
    vars = {}
    vars["component_name"] = component_name
    vars["component_version"] = component_version
    vars["component_author"] = component_author
    vars["component_build_config"] = component_build_config
    vars["bucket"] = bucket
    vars["region"] = region
    vars["encrypt"] = encrypt
    vars["metadata"] = metadata
    vars["gg_build_directory"] = gg_build_directory
    vars["gg_build_artifacts_dir"] = gg_build_artifacts_dir
    vars["gg_build_recipes_dir"] = gg_build_recipes_dir
    vars["gg_build_component_artifacts_dir"] = gg_build_component_artifacts_dir
    vars["component_recipe_file"] = component_recipe_file
    vars["parsed_component_recipe"] = parsed_component_recipe
    return vars


def get_service_clients(region):
    service_clients = {}
    service_clients["s3_client"] = create_s3_client(region)
    service_clients["sts_client"] = create_sts_client(region)
    service_clients["greengrass_client"] = create_greengrass_client(region)
    return service_clients


def create_s3_client(region=None):
    logging.debug("Creating s3 client")
    return boto3.client("s3", region_name=region)


def create_sts_client(region=None):
    logging.debug("Creating sts client")
    return boto3.client("sts", region_name=region)


def create_greengrass_client(region=None):
    logging.debug("Creating GreengrassV2 client")
    return boto3.client("greengrassv2", region_name=region)

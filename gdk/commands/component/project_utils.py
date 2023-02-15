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

def find_recipe_file_in_path(recipe_name, recipe_path):
    logging.debug("Looking for recipe file into {}".format(recipe_path))

    json_file = list(Path(recipe_path).glob("{}.json".format(recipe_name)))
    yaml_file = list(Path(recipe_path).glob("{}.yaml".format(recipe_name)))

    if not json_file and not yaml_file:
        logging.error("Could not find 'recipe.json' or 'recipe.yaml' into '{}' directory.".format(recipe_path))
        raise Exception(error_messages.PROJECT_RECIPE_FILE_NOT_FOUND)

    if json_file and yaml_file:
        logging.error("Found both 'recipe.json' and 'recipe.yaml' into '{}' directory.".format(recipe_path))
        raise Exception(error_messages.PROJECT_RECIPE_FILE_NOT_FOUND)

    recipe_file = (json_file + yaml_file)[0].resolve()

    return recipe_file

def get_recipe_file(project_recipe_filename, project_recipe_path = utils.current_directory):
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
    
    if project_recipe_filename is None:
        # In case of missing recipe filename as argument, let's look for default ones
        logging.debug("Looking for default recipe file name (recipe.json or recipe.yaml)")

        json_file = list(Path(project_recipe_path).glob("recipe.json"))
        yaml_file = list(Path(project_recipe_path).glob("recipe.yaml"))

        if not json_file and not yaml_file:
            logging.error("Could not find 'recipe.json' or 'recipe.yaml' in the project directory.")
            raise Exception(error_messages.PROJECT_RECIPE_FILE_NOT_FOUND)

        if json_file and yaml_file:
            logging.error("Found both 'recipe.json' and 'recipe.yaml' in the given project directory.")
            raise Exception(error_messages.PROJECT_RECIPE_FILE_NOT_FOUND)

        recipe_file = (json_file + yaml_file)[0].resolve()
    else:
        # Try to use the provided recipe file name
        logging.debug("Using provided recipe file '{}'".format(project_recipe_filename))
        recipe_file = Path(project_recipe_filename).resolve()

    logging.info("Found component recipe file '{}'".format(recipe_file.absolute()))

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

def get_project_recipe_values(project_recipe_filename):
    vars = {}

    # Get parsed recipe file
    parsed_component_recipe = parse_recipe_file(project_recipe_filename)

    vars["component_recipe_file"] = project_recipe_filename
    vars["parsed_component_recipe"] = parsed_component_recipe
    
    return vars

def get_project_config_values(project_config_filename, project_build_directory, custom_component_name = None, custom_component_version = None):

    # Get component configuration from the greengrass project config file.
    logging.info("Getting project configuration from {}".format(project_config_filename))
    project_config = config_actions.get_configuration(project_config_filename)["component"]

    # Since there's only one key in the component configuration, use next() instead of looping in.
    if custom_component_name is not None:
        component_name = custom_component_name
    else:
        component_name = next(iter(project_config))

    component_config = project_config[component_name]

    if custom_component_version is not None:
        component_config["version"] = custom_component_version

    component_version = component_config["version"]
    component_author = component_config["author"]
    component_build_config = component_config["build"]
    bucket = component_config["publish"]["bucket"]
    region = component_config["publish"]["region"]

    # Build directories
    logging.info("Build directory: '{}'".format(project_build_directory))
    gg_build_directory = Path(project_build_directory).resolve()
    gg_build_artifacts_dir = Path(gg_build_directory).joinpath("artifacts").resolve()
    gg_build_recipes_dir = Path(gg_build_directory).joinpath("recipes").resolve()
    gg_build_component_artifacts_dir = Path(gg_build_artifacts_dir).joinpath(component_name, component_version).resolve()

    # # Publish directories
    # gg_publish_directory = Path(gg_build_directory).resolve()
    # logging.info("Publish directory: '{}'".format(gg_publish_directory))
    # gg_publish_artifacts_dir = Path(gg_publish_directory).joinpath("artifacts").resolve()
    # gg_publish_recipes_dir = Path(gg_publish_directory).joinpath("recipes").resolve()
    # gg_publish_component_artifacts_dir = Path(gg_publish_artifacts_dir).joinpath(component_name, component_version).resolve()

    # # Local or remote deployment
    # gg_local_deployment = local_deployment

    # # Get recipe file
    # component_recipe_file = get_recipe_file(project_recipe_filename)

    # # Get parsed recipe file
    # parsed_component_recipe = parse_recipe_file(component_recipe_file)

    # Create dictionary with all the above values
    vars = {}
    vars["project_config_filename"] = project_config_filename
    vars["component_name"] = component_name
    vars["component_version"] = component_version
    vars["component_author"] = component_author
    vars["component_build_config"] = component_build_config
    vars["bucket"] = bucket
    vars["region"] = region
    vars["gg_build_directory"] = gg_build_directory
    vars["gg_build_artifacts_dir"] = gg_build_artifacts_dir
    vars["gg_build_recipes_dir"] = gg_build_recipes_dir
    vars["gg_build_component_artifacts_dir"] = gg_build_component_artifacts_dir
    # vars["gg_publish_directory"] = gg_publish_directory
    # vars["gg_publish_artifacts_dir"] = gg_publish_artifacts_dir
    # vars["gg_publish_recipes_dir"] = gg_publish_recipes_dir
    # vars["gg_publish_component_artifacts_dir"] = gg_publish_component_artifacts_dir
    #vars["gg_local_deployment"] = gg_local_deployment
    #vars["component_recipe_file"] = component_recipe_file
    #vars["parsed_component_recipe"] = parsed_component_recipe
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


def update_and_create_recipe_file(project_config, component_name, component_version):
    """
    Updates recipe with the component version calculated and artifact URIs of the artifacts. This updated recipe is
    used to create a new publish recipe file in build recipes directory.

    Parameters
    ----------
        component_name(string): Name of the component. This is also used in the name of the recipe file.
        component_version(string): Version of the component calculated based on the configuration.

    Returns
    -------
        None
    """
    logging.debug("Updating artifact URIs in the recipe...")
    build_recipe = Path(project_config["gg_build_recipes_dir"]).joinpath(
        project_config["component_recipe_file"].name
    )
    parsed_component_recipe = parse_recipe_file(build_recipe)
    if "ComponentName" in parsed_component_recipe:
        if parsed_component_recipe["ComponentName"] != component_name:
            logging.error("Component '{}' is not build.".format(parsed_component_recipe["ComponentName"]))
            raise Exception(
                "Failed to publish the component '{}' as it is not build.\nBuild the component `gdk component"
                " build` before publishing it.".format(parsed_component_recipe["ComponentName"])
            )
    gg_build_component_artifacts = project_config["gg_build_component_artifacts_dir"]
    bucket = project_config["bucket"]
    artifact_uri = f"{utils.s3_prefix}{bucket}/{component_name}/{component_version}"

    if "Manifests" not in parsed_component_recipe:
        logging.debug("No 'Manifests' key in the recipe.")
        return
    for manifest in parsed_component_recipe["Manifests"]:
        if "Artifacts" not in manifest:
            logging.debug("No 'Artifacts' key in the recipe manifest.")
            continue
        for artifact in manifest["Artifacts"]:
            if "URI" not in artifact:
                logging.debug("No 'URI' found in the recipe artifacts.")
                continue
            # Skip non-s3 URIs in the recipe. Eg docker URIs
            if not artifact["URI"].startswith("s3://"):
                continue
            artifact_file = Path(artifact["URI"]).name
            # For artifact in build component artifacts folder, update its URI
            build_artifact_files = list(gg_build_component_artifacts.glob(artifact_file))
            if len(build_artifact_files) == 1:
                logging.debug("Updating artifact URI of '{}' in the recipe file.".format(artifact_file))
                artifact["URI"] = f"{artifact_uri}/{artifact_file}"
            else:
                raise Exception(
                    f"Could not find the artifact file specified in the recipe '{artifact_file}' inside the build folder"
                    f" '{gg_build_component_artifacts}'."
                )

    # Update the version of the component in the recipe
    parsed_component_recipe["ComponentVersion"] = component_version
    return create_publish_recipe_file(project_config, parsed_component_recipe)

def create_publish_recipe_file(project_config, parsed_component_recipe):
    """
    Creates a new recipe file(json or yaml) with anme `<component_name>-<component_version>.extension` in the component
    recipes build directory.

    This recipe is updated with the component version calculated and artifact URIs of the artifacts.

    Parameters
    ----------
        component_name(string): Name of the component. This is also used in the name of the recipe file.
        component_version(string): Version of the component calculated based on the configuration.
        parsed_component_recipe(dict): Updated publish recipe with component version and s3 artifact uris
    Returns
    -------
        None
    """
    component_name = project_config["component_name"]
    component_version = project_config["component_version"]

    ext = project_config["component_recipe_file"].name.split(".")[-1]  # json or yaml
    publish_recipe_file_name = f"{component_name}-{component_version}.{ext}"  # Eg. HelloWorld-1.0.0.yaml
    publish_recipe_file = Path(project_config["gg_build_recipes_dir"]).joinpath(publish_recipe_file_name).resolve()
    project_config["publish_recipe_file"] = publish_recipe_file
    with open(publish_recipe_file, "w") as prf:
        try:
            logging.debug(
                "Creating component recipe '{}' in '{}'.".format(
                    publish_recipe_file_name, project_config["gg_build_recipes_dir"]
                )
            )

            if publish_recipe_file_name.endswith(".json"):
                prf.write(json.dumps(parsed_component_recipe, indent=4))
            else:
                yaml.dump(parsed_component_recipe, prf)

            return publish_recipe_file_name
        except Exception as e:
            raise Exception("""Failed to create publish recipe file at '{}'.\n{}""".format(publish_recipe_file, e))
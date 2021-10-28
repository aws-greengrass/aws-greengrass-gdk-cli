import greengrassTools.common.configuration as config_actions
import greengrassTools.common.consts as consts
from pathlib import Path
import json
import yaml
import greengrassTools.common.exceptions.error_messages as error_messages
import greengrassTools.common.utils as utils


def get_project_build_info():
    """
    Identifies the build system of the component based on the supported component build file and the files
    in the component project itself. 

    Raises an exception if the build system of the project is not identified. 

    Assuming that each component project corresponds to single build system, this method checks if any of 
    the build identifier files like pom.xml, gradlew, *.py are present in the component project. 

    Parameters
    ----------
        None

    Returns
    -------
        build_file(Path): Path of the config file which determines the build system of the project. 
        build_info(dict): A dictionary object that contains build related information specific to the build 
        type identified by the project. 
    """
    # Get supported component build systems
    supported_builds = get_supported_component_builds()
    if supported_builds:
        for s_file in supported_builds:
            b_files = list(Path(consts.current_directory).glob("*{}".format(s_file)))
            if len(b_files) != 1:
                print("[DEBUG]: No valid files end in {}.".format(s_file))
                # TODO: For python components, if there are multiple ".py" files in project directory,
                # identify the build file based on other artifacts in the recipe? 
            else:
                return b_files[0].resolve(), supported_builds[s_file]
    raise Exception("""Could not use 'default' build as the component build system is not identified. Please provide custom build command in '{}' config file to build the component.""".format(consts.cli_project_config_file))


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
    supported_component_builds_file = utils.get_static_file_path(consts.supported_component_builds_file)
    if supported_component_builds_file:
        with open(supported_component_builds_file, 'r') as supported_builds_file:
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
    json_file = list(Path(consts.current_directory).glob("recipe.json"))
    yaml_file = list(Path(consts.current_directory).glob("recipe.yaml"))

    if not json_file and not yaml_file:
        raise Exception(error_messages.PROJECT_RECIPE_FILE_NOT_FOUND)

    if json_file and yaml_file:
        raise Exception("""Build failed in default mode as no valid component recipe is identified.
        Found both 'recipe.json' and 'recipe.yaml' in the given project.""")

    return (json_file + yaml_file)[0].resolve()

def parse_recipe_file(component_recipe_file):
    """ 
    Loads recipes file from current project as a json obect.

    Uses yaml or json module to load the recipe file based on its extension.

    Parameters
    ----------
        None

    Returns
    -------
      (dict): Returns a dict object with the component recipe file. 
    """   
    with open(component_recipe_file, "r") as r_file:
        recipe=r_file.read()
        try:
            if component_recipe_file.name.endswith(".json"):
                recipe_json=json.loads(recipe)
                return recipe_json    
            else:
                recipe_yaml=yaml.safe_load(recipe)
                return recipe_yaml
        except Exception as e:
            raise Exception("""Unable to parse the recipe file {}. Exception: {}""".format(component_recipe_file.name,e))

def get_project_config_values():
    # Get component configuration from the greengrass project config file.
    project_config = config_actions.get_configuration()["component"]

    # Since there's only one key in the component configuration, use next() instead of looping in. 
    component_name = next(iter(project_config))
    component_config = project_config[component_name]
    component_version = component_config["version"]
    component_author = component_config["author"]
    bucket_name = component_config["publish"]["bucket_name"]

    # Build directories
    gg_build_directory = Path(consts.current_directory).joinpath("greengrass-build").resolve()
    gg_build_artifacts_dir = Path(gg_build_directory).joinpath("artifacts").resolve()
    gg_build_recipes_dir = Path(gg_build_directory).joinpath("recipes").resolve()
    gg_build_component_artifacts_dir = Path(gg_build_artifacts_dir).joinpath(component_name,component_version).resolve()

    # Get recipe file
    component_recipe_file = get_recipe_file()

    # Get parsed recipe file
    parsed_component_recipe = parse_recipe_file(component_recipe_file)

    # Artifact URI
    artifact_uri = f"s3://{bucket_name}/{component_name}/{component_version}"

    # Create dictionary with all the above values
    vars={}
    vars["component_name"] = component_name
    vars["component_config"] = component_config
    vars["component_version"] = component_version
    vars["component_author"] = component_author
    vars["bucket_name"] = bucket_name
    vars["gg_build_directory"] = gg_build_directory
    vars["gg_build_artifacts_dir"] = gg_build_artifacts_dir
    vars["gg_build_recipes_dir"] = gg_build_recipes_dir
    vars["gg_build_component_artifacts_dir"] = gg_build_component_artifacts_dir
    vars["component_recipe_file"] = component_recipe_file
    vars["parsed_component_recipe"] = parsed_component_recipe
    vars["artifact_uri"] = artifact_uri
    return vars
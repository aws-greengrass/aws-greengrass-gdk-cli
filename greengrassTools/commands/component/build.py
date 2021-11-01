import greengrassTools.common.consts as consts
import greengrassTools.common.utils as utils
from pathlib import Path
import shutil 
import json
import subprocess as sp
import yaml
import logging
import greengrassTools.commands.component.project_utils as project_utils
import greengrassTools.common.exceptions.error_messages as error_messages

def run(command_args):
    """ 
    Builds the component based on the command arguments and the project configuration. The build files 
    are created in current directory under "greengrass-build" folder. 

    If the project configuration specifies 'default' build command, the component build system is identified 
    based on some special files in the project. If this build system is supported by the tool, the command 
    builds the component artifacts and recipes. 

    If the project configuration specifies custom build command, the tool executes the command as it is. 

    Parameters
    ----------
        command_args(dict): A dictionary object that contains parsed args namespace of a command.

    Returns
    -------
        None
    """
    component_build_config = project_config["component_build_config"]
    build_command = component_build_config["command"]

    logging.info("Building the component '{}' with the given project configuration.".format(project_config["component_name"]))
    # Create build directories
    create_gg_build_directories()

    if len(build_command) == 1 and build_command[0].lower() == "default":
        logging.info("Using default build configuration to build the component.")
        default_build_component()
    else:
        # Run custom command as is. 
        logging.info("Using custom build configuration to build the component.")
        logging.info("Running the following command\n{}".format(build_command))
        sp.run(build_command)

def create_gg_build_directories():
    """
    Creates "greengrass-build" directory with component artifacts and recipes sub directories. 

    This method removes the "greengrass-build" directory if it already exists.
    
    Parameters
    ----------
        None

    Returns
    -------
        None
    """ 
    # Clean build directory if it exists already.
    utils.clean_dir(project_config["gg_build_directory"])
    
    logging.debug("Creating '{}' directory with artifacts and recipes.".format(consts.greengrass_build_dir))
    # Create build artifacts and recipe directories
    Path.mkdir(project_config["gg_build_recipes_dir"],parents=True,exist_ok=True)
    Path.mkdir(project_config["gg_build_component_artifacts_dir"],parents=True,exist_ok=True)

def default_build_component():
    """ 
    Builds the component artifacts and recipes in default mode if the build system of the component is supported. 

    The build system of the component project is identified based on the keys of the supported builds config file.
    If the build system is supported, build commands are run to build the component artifacts. 

    Based on the artifacts specified in the recipe, the built component artifacts are copied over to greengrass
    component artifacts build folder and the artifact uris in the recipe are updated to reflect the same. 

    Based on the project config file, component recipe is updated and a new recipe file is created in greengrass 
    component recipes build folder.  

    Parameters
    ----------
        None

    Returns
    -------
        None
    """
    try:
        # Identify build info from project
        build_file, build_info = project_utils.get_project_build_info()

        # Build the project with identified the build system
        run_build_command(build_file, build_info)

        # From the recipe, copy necessary artifacts (depends on build system) to the build folder . 
        copy_artifacts_and_update_uris(build_info)

        # Update recipe file with component configuration from project config file.
        create_build_recipe_file() 
    except Exception as e:
        raise Exception("""{}\n{}""".format(error_messages.BUILD_WITH_DEFAULT_FAILED, e))
 
def run_build_command(build_file, build_info):
    """
    Runs the build command based on the component project build info.

    For any build system other than 'zip', the build command obtained as a list from the 
    supported_component_builds.json is passed to the subprocess run command as it is. 
    
    Parameters
    ----------
        build_file(Path): Path of the config file which determines the build system of the project. 
        build_info(dict): A dictionary object that contains build related information specific to the build 
        type identified by the project. 

    Returns
    -------
        None
    """ 
    try:
        build_system = build_info["build_system"]
        build_command = build_info["build_command"]
        logging.warning("""This component is identified as using '{}' build system. If this is incorrect, please exit and specify custom build command in the '{}'.""".format(build_system,consts.cli_project_config_file))

        if build_system == "zip":
            logging.info("Zipping source code files of the component.")
            _build_system_zip(build_file, build_info)
        else:
            logging.info("Running the build command '{}'".format(' '.join(build_command)))
            sp.run(build_command)
    except Exception as e:
        raise Exception("""{}\n{}""".format(error_messages.BUILD_WITH_DEFAULT_COMMAND_FAILED,e))

def _build_system_zip(build_file, build_info):
    """
    Builds the component as a zip file. 

    Copies over necessary files by excluding certain files to a build folder identied for zip build system
    (supported_component_builds.json has the build folder info). 
    This build folder is zipped completely as a component zip artifact.
    Raises an exception if there's an error in the process of zippings. 

    Parameters
    ----------
        build_file(Path): Path of the config file which determines the build system of the project. 
        build_info(dict): A dictionary object that contains build related information specific to the build 
        type identified by the project. 

    Returns
    -------
        None 
    """
    try:
        zip_build = _get_build_folder_by_build_system(build_info)
        utils.clean_dir(zip_build)

        logging.debug("Copying over component files to the '{}' folder.".format(zip_build.name))
        shutil.copytree(utils.current_directory, zip_build, dirs_exist_ok=True, ignore=_ignore_files_during_zip)

        # Get build file name without extension. This will be used as name of the archive. 
        archive_file = build_file.name.split(".py")[0]
        logging.debug("Creating an archive named '{}.zip' in '{}' folder with the files in '{}' folder.".format(archive_file,zip_build.name,zip_build.name))
        archive_file_name = Path(zip_build).joinpath(archive_file).resolve()
        shutil.make_archive(
            archive_file_name, 
            'zip',
            root_dir=zip_build
        )
        logging.debug("Archive complete.")

    except Exception as e:
        raise Exception("""Failed to zip the component in default build mode.\n{}""".format(e))

def _ignore_files_during_zip(path,names):
    """
    Creates a list of files or directories to ignore while copying a directory. 

    Helper function to create custom list of files/directories to ignore. Here, we exclude project config, 
    component recipe and greengrass-build folder.

    Parameters
    ----------
        path,names

    Returns
    -------
        ignore_list(list): List of files or directories to ignore during zip. 
    """
    # TODO: Identify individual files in recipe that are not same as zip and exclude them during zip. 
    ignore_list = [consts.cli_project_config_file, consts.greengrass_build_dir, project_config["component_recipe_file"].name]
    logging.debug("Exclude the following files while zipping the component .\n{}".format(', '.join(ignore_list)))
    return ignore_list

def _get_build_folder_by_build_system(build_info):
    """
    Returns build folder name specific to the build system. This folder contains component artifacts after the build 
    is complete. 

    Parameters
    ----------
        build_info(dict): A dictionary object that contains build related information specific to the build 
        type identified by the project. 

    Returns
    -------
        build_folder(Path): Path to the build folder created by component build system. 
    """
    build_folder = build_info["build_folder"]
    return Path(utils.current_directory).joinpath(*build_folder).resolve()

def copy_artifacts_and_update_uris(build_info):
    """
    Copies over the build artifacts to the greengrass artifacts build folder and update URIs in the recipe.

    The component artifacts created in the build process of the component are identied by the artifact URIs in 
    the recipe and copied over to the greengrass component's artifacts build folder. The parsed component 
    recipe file is also updated with the artifact URIs. 
    
    Parameters
    ----------
        build_info(dict): A dictionary object that contains build related information specific to the build 
        type identified by the project. 

    Returns
    -------
        None
    """ 
    # TODO: Case insenstive recipe keys? 
    logging.info("Copying over the build artifacts to the greengrass component artifacts build folder.")
    logging.info("Updating artifact URIs in the recipe.")
    parsed_component_recipe = project_config["parsed_component_recipe"]
    gg_build_component_artifacts_dir = project_config["gg_build_component_artifacts_dir"]
    artifact_uri = "s3://BUCKET_NAME/COMPONENT_NAME/COMPONENT_VERSION"
    if "Manifests" not in parsed_component_recipe:
        logging.debug("No 'Manifests' key in the recipe.")
        return 
    build_folder = _get_build_folder_by_build_system(build_info)
    build_folder_iterator_list = list(build_folder.iterdir())
    manifests = parsed_component_recipe["Manifests"]
    for manifest in manifests:
        if "Artifacts" not in manifest:
            logging.debug("No 'Artifacts' key in the recipe manifest.")
            continue
        artifacts = manifest["Artifacts"]
        for artifact in artifacts:
            if "URI" not in artifact:
                logging.debug("No 'URI' found in the recipe artifacts.")
                continue
            artifact_file = Path(artifact["URI"]).resolve().name
            
            # If artifact in specific build folder, copy it to artifacts build folder
            for b_file in build_folder_iterator_list:
                if artifact_file == b_file.name:
                    logging.debug("Copying file '{}' from '{}' to '{}'.".format(artifact_file, build_folder, gg_build_component_artifacts_dir ))
                    shutil.copy(b_file, gg_build_component_artifacts_dir)
                    logging.debug("Updating artifact URI of '{}' in the recipe file.".format(artifact_file))
                    artifact["URI"] = f"{artifact_uri}/{artifact_file}"

def create_build_recipe_file():
    """
    Creates a new recipe file(json or yaml) in the component recipes build directory. 
    
    This recipe is updated with the component configuration provided in the project config file.

    Parameters
    ----------
        None

    Returns
    -------
        None
    """
    logging.debug("Updating component recipe with the 'component' configuration provided in '{}'.".format(consts.cli_project_config_file))
    parsed_component_recipe = project_config["parsed_component_recipe"]
    component_recipe_file_name = project_config["component_recipe_file"].name
    parsed_component_recipe["ComponentName"] = project_config["component_name"]
    parsed_component_recipe["ComponentVersion"] = project_config["component_version"]
    parsed_component_recipe["ComponentPublisher"] = project_config["component_author"]
    gg_build_recipe_file = Path(project_config["gg_build_recipes_dir"]).joinpath(component_recipe_file_name).resolve()

    with open(gg_build_recipe_file, 'w') as recipe_file:
        try:
            logging.info("Creating component recipe in '{}'.".format(project_config["gg_build_recipes_dir"]))
            if component_recipe_file_name.endswith(".json"):
                recipe_file.write(json.dumps(parsed_component_recipe, indent=4))
            else:
                yaml.dump(parsed_component_recipe, recipe_file)
        except Exception as e:
            raise Exception("""Failed to create build recipe file at '{}'.\n{}""".format(gg_build_recipe_file,e))

project_config = project_utils.get_project_config_values()

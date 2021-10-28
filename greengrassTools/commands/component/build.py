import greengrassTools.common.consts as consts
import greengrassTools.common.utils as utils
from pathlib import Path
import shutil 
import json
import subprocess as sp
import yaml
import greengrassTools.commands.component.project_utils as project_utils

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
    component_build_config = project_build_config["component_config"]["build"]
    build_command = component_build_config["command"]

    print("Building component:'{}' with build command:'{}'".format(project_build_config["component_name"], build_command))

    # Create build directories
    create_gg_build_directories()

    if len(build_command) == 1 and build_command[0].lower() == "default":
        default_build_component()
    else:
        # Run custom command as is. 
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
    print("[DEBUG]: Cleaning the 'greengrass-build' directory if it exists.")
    utils.clean_dir(project_build_config["gg_build_directory"])
    
    print("[DEBUG]: Creating 'greengrass-build' directory with artifacts and recipes.")
    # Create build artifacts and recipe directories
    Path.mkdir(project_build_config["gg_build_recipes_dir"],parents=True,exist_ok=True)
    Path.mkdir(project_build_config["gg_build_component_artifacts_dir"],parents=True,exist_ok=True)

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
        raise Exception("""Failed to build the component in default mode.\n{}""".format(e))
 
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

        print("""[INFO]: This component is identified as using '{}' build system. If this is incorrect, please exit and specify custom build command in the config file.""".format(build_system))

        if build_system == "zip":
            _build_system_zip(build_file, build_info)
        else:
            print("Running the build command '{}'".format(' '.join(build_command)))
            sp.run(build_command)
    except Exception as e:
        raise Exception("""Failed to run the build command in default build mode.\n{}""".format(e))

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
        print("[DEBUG]: Cleaning the '{}' folder if it exists.".format(zip_build.name))
        utils.clean_dir(zip_build)

        print("[DEBUG]: Copying over component files to the '{}' folder.".format(zip_build.name))
        shutil.copytree(consts.current_directory, zip_build, dirs_exist_ok=True, ignore=_ignore_files_during_zip)

        print("[DEBUG]: Creating an archive in '{}' folder with the files in '{}' folder.".format(zip_build.name,zip_build.name))
        # Get build file name without extension. This will be used as name of the archive. 
        archive_file = build_file.name.split(".py")[0]
        archive_file_name = Path(zip_build).joinpath(archive_file).resolve()
        shutil.make_archive(
            archive_file_name, 
            'zip',
            root_dir=zip_build
        )
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
    ignore_list = [consts.cli_project_config_file, "greengrass-build", project_build_config["component_recipe_file"].name]
    return ignore_list

def _get_build_folder_by_build_system(build_info):
    """
    Builds the component as a zip file. 

    Copies over necessary files by excluding certain files to a build folder identied for zip build system
    (supported_component_builds.json has the build folder info). 
    This build folder is zipped completely as a component zip artifact.

    Parameters
    ----------
        build_info(dict): A dictionary object that contains build related information specific to the build 
        type identified by the project. 

    Returns
    -------
        build_folder(Path): Path to the build folder created by component build system. 
    """
    build_folder = build_info["build_folder"]
    return Path(consts.current_directory).joinpath(*build_folder).resolve()

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
    parsed_component_recipe = project_build_config["parsed_component_recipe"]
    gg_build_component_artifacts_dir = project_build_config["gg_build_component_artifacts_dir"]
    artifact_uri = project_build_config["artifact_uri"]

    if "Manifests" not in parsed_component_recipe:
        print("[DEBUG]: No 'Manifests' found in the recipe.")
        return 
    build_folder_iterator_list = list(_get_build_folder_by_build_system(build_info).iterdir())
    manifests = parsed_component_recipe["Manifests"]
    for manifest in manifests:
        if "Artifacts" not in manifest:
            print("[DEBUG]: No 'Artifacts' found in the recipe manifest.")
            continue
        artifacts = manifest["Artifacts"]
        for artifact in artifacts:
            if "URI" not in artifact:
                print("[DEBUG]: No 'URI' found in the recipe artifacts.")
                continue
            artifact_file = Path(artifact["URI"]).resolve().name
            
            # If artifact in specific build folder, copy it to artifacts build folder
            for b_file in build_folder_iterator_list:
                if artifact_file == b_file.name:
                    shutil.copy(b_file, gg_build_component_artifacts_dir)
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
    parsed_component_recipe = project_build_config["parsed_component_recipe"]
    component_recipe_file_name = project_build_config["component_recipe_file"].name
    parsed_component_recipe["ComponentName"] = project_build_config["component_name"]
    parsed_component_recipe["ComponentVersion"] = project_build_config["component_version"]
    parsed_component_recipe["ComponentPublisher"] = project_build_config["component_author"]
    gg_build_recipe_file = Path(project_build_config["gg_build_recipes_dir"]).joinpath(component_recipe_file_name).resolve()

    with open(gg_build_recipe_file, 'w') as recipe_file:
        try:
            if component_recipe_file_name.endswith(".json"):
                recipe_file.write(json.dumps(parsed_component_recipe, indent=4))
            else:
                yaml.dump(parsed_component_recipe, recipe_file)
        except Exception as e:
            raise Exception("""Could not create a build recipe file for file {}. Exception: {}""".format(component_recipe_file_name,e))

project_build_config = project_utils.get_project_config_values()

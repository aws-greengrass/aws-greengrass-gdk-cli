import json
import logging
import shutil
import subprocess as sp
from pathlib import Path

import gdk.commands.component.project_utils as project_utils
import gdk.common.consts as consts
import gdk.common.exceptions.error_messages as error_messages
import gdk.common.utils as utils
import yaml


def run(command_args):
    """
    Builds the component based on the command arguments and the project configuration. The build files
    are created in current directory under "greengrass-build" folder.

    If this build system specified in the project configuration is supported by the tool, the command
    builds the component artifacts and recipes based on the build system.

    If the project configuration specifies custom build system with a custom build command, then the tool executes
    the command as it is.

    Parameters
    ----------
        command_args(dict): A dictionary object that contains parsed args namespace of a command.

    Returns
    -------
        None
    """
    component_build_config = project_config["component_build_config"]
    build_system = component_build_config["build_system"]

    logging.info("Building the component '{}' with the given project configuration.".format(project_config["component_name"]))
    # Create build directories
    create_gg_build_directories()

    if build_system == "custom":
        # Run custom command as is.
        custom_build_command = component_build_config["custom_build_command"]
        logging.info("Using custom build configuration to build the component.")
        logging.info("Running the following command\n{}".format(custom_build_command))
        sp.run(custom_build_command)
    else:
        logging.info(f"Using '{build_system}' build system to build the component.")
        default_build_component()


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
    Path.mkdir(project_config["gg_build_recipes_dir"], parents=True, exist_ok=True)
    Path.mkdir(project_config["gg_build_component_artifacts_dir"], parents=True, exist_ok=True)


def default_build_component():
    """
    Builds the component artifacts and recipes based on the build system specfied in the project configuration.

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
        # Build the project with specified build system
        run_build_command()

        # From the recipe, copy necessary artifacts (depends on build system) to the build folder .
        copy_artifacts_and_update_uris()

        # Update recipe file with component configuration from project config file.
        create_build_recipe_file()
    except Exception as e:
        raise Exception("""{}\n{}""".format(error_messages.BUILD_FAILED, e))


def run_build_command():
    """
    Runs the build command based on the configuration in 'project_build_system.json' file and component project build
    configuration.

    For any build system other than 'zip', the build command obtained as a list from the
    project_build_system.json is passed to the subprocess run command as it is.

    Parameters
    ----------
        None

    Returns
    -------
        None
    """
    try:
        build_system = project_config["component_build_config"]["build_system"]
        build_command = supported_build_sytems[build_system]["build_command"]
        logging.warning(
            f"This component is identified as using '{build_system}' build system. If this is incorrect, please exit and"
            f" specify custom build command in the '{consts.cli_project_config_file}'."
        )

        if build_system == "zip":
            logging.info("Zipping source code files of the component.")
            _build_system_zip()
        else:
            logging.info("Running the build command '{}'".format(" ".join(build_command)))
            sp.run(build_command)
    except Exception as e:
        raise Exception(f"Error building the component with the given build system.\n{e}")


def _build_system_zip():
    """
    Builds the component as a zip file.

    Copies over necessary files by excluding certain files to a build folder identied for zip build system
    (supported_component_builds.json has the build folder info).
    This build folder is zipped completely as a component zip artifact.
    Raises an exception if there's an error in the process of zippings.

    Parameters
    ----------
        None

    Returns
    -------
        None
    """
    try:
        zip_build = next(iter(_get_build_folder_by_build_system()))  # Only one zip-build folder in the set
        artifacts_zip_build = Path(zip_build).joinpath(utils.current_directory.name).resolve()
        utils.clean_dir(zip_build)
        logging.debug("Copying over component files to the '{}' folder.".format(artifacts_zip_build.name))
        shutil.copytree(utils.current_directory, artifacts_zip_build, dirs_exist_ok=True, ignore=_ignore_files_during_zip)

        # Get build file name without extension. This will be used as name of the archive.
        archive_file = utils.current_directory.name
        logging.debug(
            "Creating an archive named '{}.zip' in '{}' folder with the files in '{}' folder.".format(
                archive_file, zip_build.name, artifacts_zip_build.name
            )
        )
        archive_file_name = Path(zip_build).joinpath(archive_file).resolve()
        shutil.make_archive(archive_file_name, "zip", root_dir=artifacts_zip_build)
        logging.debug("Archive complete.")

    except Exception as e:
        raise Exception("""Failed to zip the component in default build mode.\n{}""".format(e))


def _ignore_files_during_zip(path, names):
    """
    Creates a list of files or directories to ignore while copying a directory.

    Helper function to create custom list of files/directories to ignore. Here, we exclude,
    1. project config file -> gdk-config.json
    2. greengrass-build directory
    3. recipe file
    4. tests folder

    Parameters
    ----------
        path,names

    Returns
    -------
        ignore_list(list): List of files or directories to ignore during zip.
    """
    # TODO: Identify individual files in recipe that are not same as zip and exclude them during zip.

    ignore_list = [
        consts.cli_project_config_file,
        consts.greengrass_build_dir,
        project_config["component_recipe_file"].name,
        "test*",
    ]
    return ignore_list


def _get_build_folder_by_build_system():
    """
    Returns build folder name specific to the build system. This folder contains component artifacts after the build
    is complete.

    If there are multiple modules within the same project, this function recursively identifies all the build folders
    of the modules.

    Parameters
    ----------
        None

    Returns
    -------
        build_folder(Path): Path to the build folder created by component build system.
    """
    build_system = project_config["component_build_config"]["build_system"]
    build_folder = supported_build_sytems[build_system]["build_folder"]
    if build_system == "gradle":
        return get_build_folders(build_folder, "build.gradle")
    elif build_system == "maven":
        return get_build_folders(build_folder, "pom.xml")
    return {Path(utils.current_directory).joinpath(*build_folder).resolve()}


def get_build_folders(build_folder, build_file):
    """
    Recursively identifies build folders in a project.

    This function makes use of build configuration files (such as pom.xml and build.gradle) and build folder
    directories (such as target, build/libs) to identify the module directory.

    Once the module directory is found, its build folder is added to the return list.

    Parameters
    ----------
        build_folder(string): Build foler of a build system(target, build/libs)
        build_file(string): Build configuration file of a build system (pom.xml, build.gradle)

    Returns
    -------
        paths(list): List of build folder paths in a multi-module project.
    """
    set_build_file = set(f.parent for f in Path(utils.current_directory).rglob(build_file))
    set_build_folder = set(f.parent for f in Path(utils.current_directory).rglob(str(Path().joinpath(*build_folder))))
    return set(x.joinpath(*build_folder) for x in (set_build_folder & set_build_file))


def copy_artifacts_and_update_uris():
    """
    Copies over the build artifacts to the greengrass artifacts build folder and update URIs in the recipe.

    The component artifacts created in the build process of the component are identied by the artifact URIs in
    the recipe and copied over to the greengrass component's artifacts build folder. The parsed component
    recipe file is also updated with the artifact URIs.

    Parameters
    ----------
        None

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

    build_folders = _get_build_folder_by_build_system()
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
            # Skip non-s3 URIs in the recipe. Eg docker URIs
            if not artifact["URI"].startswith("s3://"):
                continue
            artifact_file = Path(artifact["URI"]).name
            artifact_found = False
            # If the artifact is present in build system specific build folder, copy it to greengrass artifacts build folder
            for build_folder in build_folders:
                build_files = list(build_folder.glob(artifact_file))
                if len(build_files) == 1:
                    logging.debug(
                        "Copying file '{}' from '{}' to '{}'.".format(
                            artifact_file, build_folder, gg_build_component_artifacts_dir
                        )
                    )
                    shutil.copy(build_files[0], gg_build_component_artifacts_dir)
                    logging.debug("Updating artifact URI of '{}' in the recipe file.".format(artifact_file))
                    artifact["URI"] = f"{artifact_uri}/{artifact_file}"
                    artifact_found = True
                    break
                else:
                    logging.debug(
                        f"Could not find the artifact file specified in the recipe '{artifact_file}' inside the build folder"
                        f" '{build_folder}'."
                    )
            if not artifact_found:
                raise Exception(
                    f"Could not find the artifact file specified in the recipe '{artifact_file}' inside the build folders."
                    f" '{build_folders}'."
                )


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
    logging.debug(
        "Updating component recipe with the 'component' configuration provided in '{}'.".format(consts.cli_project_config_file)
    )
    parsed_component_recipe = project_config["parsed_component_recipe"]
    component_recipe_file_name = project_config["component_recipe_file"].name
    parsed_component_recipe["ComponentName"] = project_config["component_name"]
    parsed_component_recipe["ComponentVersion"] = project_config["component_version"]
    parsed_component_recipe["ComponentPublisher"] = project_config["component_author"]
    gg_build_recipe_file = Path(project_config["gg_build_recipes_dir"]).joinpath(component_recipe_file_name).resolve()

    with open(gg_build_recipe_file, "w") as recipe_file:
        try:
            logging.info("Creating component recipe in '{}'.".format(project_config["gg_build_recipes_dir"]))
            if component_recipe_file_name.endswith(".json"):
                recipe_file.write(json.dumps(parsed_component_recipe, indent=4))
            else:
                yaml.dump(parsed_component_recipe, recipe_file)
        except Exception as e:
            raise Exception("""Failed to create build recipe file at '{}'.\n{}""".format(gg_build_recipe_file, e))


project_config = project_utils.get_project_config_values()

supported_build_sytems = project_utils.get_supported_component_builds()

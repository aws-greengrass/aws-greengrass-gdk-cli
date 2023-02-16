import logging
from pathlib import Path
import shutil
import re
from urllib import parse

import gdk.commands.component.project_utils as project_utils
import gdk.common.exceptions.error_messages as error_messages
from gdk.commands.Command import Command
from gdk.common import utils
from gdk import consts


class PushCommand(Command):
    def __init__(self, command_args) -> None:
        super().__init__(command_args, "push")
        
        logging.debug("Arguments: {}".format(command_args))

        project_config_filename = command_args["gdk_config"] if command_args["gdk_config"] != None else consts.cli_project_config_file
        project_build_directory = command_args["build_dir"] if command_args["build_dir"] != None else consts.greengrass_build_dir
        #project_recipe_filename = "{}/recipes/recipe.json".format(project_build_directory)
        project_recipe_filename = project_utils.find_recipe_file_in_path("recipe", "{}/recipes".format(project_build_directory))

        logging.debug("Project config filename : {}".format(project_config_filename))
        logging.debug("Project build directory : {}".format(project_build_directory))
        logging.debug("Project recipe filename : {}".format(project_recipe_filename))
        logging.debug("Component destination   : {}".format(command_args["destination"]))

        logging.debug("Loading project configuration values")
        self.project_config = project_utils.get_project_config_values(project_config_filename, project_build_directory)

        logging.debug("Loading recipe values")
        recipe_values = project_utils.get_project_recipe_values(project_recipe_filename)

        logging.debug("Merging recipe into project configuration value")
        self.project_config.update(recipe_values)

        self.project_config["component_destination"] = command_args["destination"]
        self.service_clients = project_utils.get_service_clients(self.project_config["region"])

    def run(self):
        component_destination = parse.urlparse(self.project_config["component_destination"])

        logging.info("Pushing component into destination {}".format(component_destination))

        if len(component_destination.path) == 0:
            raise Exception(error_messages.PUSH_INVALID_PATH_VALUE)

        if "s3" == component_destination.scheme:
            self.push_to_s3(component_destination.netloc, component_destination.path)
        elif "file" == component_destination.scheme:
            self.push_to_local("{}/{}".format(component_destination.netloc, component_destination.path))
        else:
            raise Exception(error_messages.PUSH_UNSUPPORTED_LOCATION_TYPE)

    def push_to_s3(self, bucket_name, bucket_path):
        raise RuntimeError("S3 pushing feature to be implemented")

    def push_to_local(self, location):
        logging.info("Local location selected: '{}'".format(location))

        component_name = self.project_config["component_name"]

        # Prepare target location

        location_artifacts_path = Path(location).joinpath("artifacts").resolve()
        location_recipes_path = Path(location).joinpath("recipes").resolve()

        logging.debug("Destination folder for recipe   : {}".format(location_recipes_path))
        logging.debug("Destination folder for artifact : {}".format(location_artifacts_path))

        location_artifacts_path.mkdir(parents=True, exist_ok=True)
        location_recipes_path.mkdir(parents=True, exist_ok=True)
        location_component_artifacts_path = Path(location_artifacts_path).joinpath(component_name).resolve()
        location_component_artifacts_path.mkdir(exist_ok=True)

        build_recipes_directory = Path(self.project_config["gg_build_recipes_dir"])
        build_artifacts_directory = self.project_config["gg_build_component_artifacts_dir"]

        component_version = self.get_component_version_from_local(component_name, location_component_artifacts_path)
        self.project_config["component_version"] = component_version

        logging.info("Pushing artifact '{}' with version '{}' to local location '{}'".format(component_name, component_version, location))
        logging.info("Component recipe build folder   : '{}'".format(build_recipes_directory))
        logging.info("Component artifact build folder : '{}'".format(build_artifacts_directory))

        build_recipe_file_name = project_utils.update_and_create_recipe_file(self.project_config, component_name, component_version)
        build_recipe_file = Path(build_recipes_directory).joinpath(build_recipe_file_name).resolve()

        logging.info("Copying recipe file '{}' into local path '{}'".format(build_recipe_file, location_recipes_path))

        shutil.copy(build_recipe_file.resolve(), location_recipes_path)

        # Clean destination directory, if exists
        location_component_and_version_artifacts_path = Path(location_component_artifacts_path).joinpath(component_version).resolve()
        logging.debug("Artifact target location: '{}'".format(location_component_and_version_artifacts_path))
        if location_component_and_version_artifacts_path.exists():
            logging.debug("Target directory already exists, cleaning its content before copying")
            shutil.rmtree(location_component_and_version_artifacts_path.resolve())
        location_component_and_version_artifacts_path.mkdir(exist_ok=True)

        # Copying artifact content into target directory
        build_component_artifacts = list(build_artifacts_directory.iterdir())
        for file in build_component_artifacts:
            logging.debug("Copying file '{}' into target location '{}'".format(file, location_component_and_version_artifacts_path))
            shutil.copy(file.resolve(), location_component_and_version_artifacts_path)

    def get_component_version_from_local(self, component_name: str, location_component_artifacts_path: Path):
        if self.project_config["component_version"] == "NEXT_PATCH":
            logging.debug("Component version set to 'NEXT_PATCH' in the config file. Calculating next version of the component '{}'".format(component_name))

            if location_component_artifacts_path.exists():
                logging.debug("Target folder exists, let's compute the NEXT_PATCH")

                pattern = re.compile("^[0-9]*\.[0-9]*\.[0-9]*$")

                major = 1
                minor = 0
                patch = -1

                for element in location_component_artifacts_path.iterdir():
                    if element.is_dir() and pattern.match(element.name):
                        ver_split = element.name.split(".")

                        curr_major = int(ver_split[0])
                        curr_minor = int(ver_split[1])
                        curr_patch = int(ver_split[2])

                        logging.debug("{}.{}.{} vs {}.{}.{}".format(major, minor, patch, curr_major, curr_minor, curr_patch))

                        if curr_major > major:
                            major = curr_major
                            minor = curr_minor
                            patch = curr_patch
                        elif curr_major == major:
                            if curr_minor < minor:
                                continue

                            if curr_minor > minor:
                                minor = curr_minor
                                patch = curr_patch
                            elif curr_patch > patch:
                                patch = curr_patch

                        logging.debug("Selected: {}.{}.{}".format(major, minor, patch))

                return "{}.{}.{}".format(major, minor, patch + 1)
            else:
                logging.debug("Target component folder does not exist, return default version")
                return "1.0.0"
        else:
            logging.info("Using the version set for the component '{}' in the config file.".format(component_name))
            return self.project_config["component_version"]
        

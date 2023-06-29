import logging
import subprocess as sp
from pathlib import Path

import gdk.common.consts as consts
import gdk.common.exceptions.error_messages as error_messages
import gdk.common.utils as utils

from gdk.build_system.ComponentBuildSystem import ComponentBuildSystem
from gdk.commands.Command import Command
from gdk.commands.component.transformer.BuildRecipeTransformer import BuildRecipeTransformer
from gdk.commands.component.config.ComponentBuildConfiguration import ComponentBuildConfiguration


class BuildCommand(Command):
    def __init__(self, command_args) -> None:
        super().__init__(command_args, "build")

        self.project_config = ComponentBuildConfiguration(command_args)
        self.build_recipe_transformer = BuildRecipeTransformer(self.project_config)

    def run(self):
        """
        Builds the component based on the command arguments and the project configuration. The build files
        are created in current directory under "greengrass-build" folder.

        If this build system specified in the project configuration is supported by the tool, the command
        builds the component artifacts and recipes based on the build system.

        If the project configuration specifies custom build system with a custom build command, then the tool executes
        the command as it is.

        Parameters
        ----------
            None

        Returns
        -------
            None
        """
        build_system = self.project_config.build_system

        logging.info("Building the component '%s' with the given project configuration.", self.project_config.component_name)

        # Create build directories
        self.create_gg_build_directories()

        if build_system == "custom":
            # Run custom command as is.
            custom_build_command = self.project_config.build_config.get("custom_build_command", [])
            logging.info("Using custom build configuration to build the component.")
            logging.info("Running the following command\n%s", custom_build_command)
            sp.run(custom_build_command, check=True)
        else:
            logging.info("Using '%s' build system to build the component.", build_system)
            self.default_build_component()

    def create_gg_build_directories(self):
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
        utils.clean_dir(self.project_config.gg_build_dir)

        logging.debug("Creating '%s' directory with artifacts and recipes.", consts.greengrass_build_dir)
        # Create build artifacts and recipe directories
        Path.mkdir(self.project_config.gg_build_recipes_dir, parents=True, exist_ok=True)
        Path.mkdir(self.project_config.gg_build_component_artifacts_dir, parents=True, exist_ok=True)

    def default_build_component(self):
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
            self.run_build_command()
            self.build_recipe_transformer.transform(self._get_build_folder_by_build_system())
        except Exception:
            logging.error(error_messages.BUILD_FAILED)
            raise

    def run_build_command(self):
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
            build_system = self.project_config.build_system
            logging.warning(
                f"This component is identified as using '{build_system}' build system. If this is incorrect, please exit and"
                f" specify custom build command in the '{consts.cli_project_config_file}'."
            )
            self.component_build_system = ComponentBuildSystem.get(build_system)
            self.component_build_system.build(project_config=self.project_config)
        except Exception:
            logging.error("Error building the component with the given build system.")
            raise

    def _get_build_folder_by_build_system(self):
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
        build_system_identifiers = self.component_build_system.build_system_identifier
        build_folders = set()
        for identifier in build_system_identifiers:
            build_folders = build_folders.union(self.get_build_folders(self.component_build_system.build_folder, identifier))
        return build_folders

    def get_build_folders(self, build_folder, build_file):
        """
        Recursively identifies build folders in a project.

        This function makes use of build configuration files (such as pom.xml, build.gradle, and build.gradle.kts)
        and build folder directories (such as target, build/libs) to identify the module build directories.

        Once the module directory is found, its build folder is added to the return list.

        Parameters
        ----------
            build_folder(string): Build folder of a build system(target, build/libs)
            build_file(string): Build configuration file of a build system (pom.xml, build.gradle, build.gradle.kts)

        Returns
        -------
            paths(set): Set of build folder paths in a multi-module project.
        """
        # Filter module directories which contain pom.xml, build.gradle, build.gradle.kts build files.
        set_dirs_with_build_file = set(f.parent for f in Path(utils.get_current_directory()).rglob(build_file))
        set_of_module_dirs = set()
        for module_dir in set_dirs_with_build_file:
            module_build_folder = Path(module_dir).joinpath(*build_folder).resolve()
            # Filter module directories that also contain build folders - target/, build/libs/
            if module_build_folder.exists():
                set_of_module_dirs.add(module_build_folder)
        return set_of_module_dirs

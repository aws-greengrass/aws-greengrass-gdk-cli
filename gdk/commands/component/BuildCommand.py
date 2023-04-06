import logging
import platform
import subprocess as sp
from pathlib import Path


import gdk.commands.component.project_utils as project_utils
import gdk.common.consts as consts
import gdk.common.exceptions.error_messages as error_messages
import gdk.common.utils as utils
from gdk.build_system.BuildSystem import BuildSystem
from gdk.build_system.Zip import Zip
from gdk.commands.Command import Command
from gdk.commands.component.transformer.BuildRecipeTransformer import BuildRecipeTransformer


class BuildCommand(Command):
    def __init__(self, command_args) -> None:
        super().__init__(command_args, "build")
        self.project_config = project_utils.get_project_config_values()
        self.supported_build_sytems = project_utils.get_supported_component_builds()
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
        component_build_config = self.project_config["component_build_config"]
        build_system = component_build_config["build_system"]

        logging.info(
            "Building the component '{}' with the given project configuration.".format(self.project_config["component_name"])
        )
        # Create build directories
        self.create_gg_build_directories()

        if build_system == "custom":
            # Run custom command as is.
            custom_build_command = component_build_config["custom_build_command"]
            logging.info("Using custom build configuration to build the component.")
            logging.info("Running the following command\n{}".format(custom_build_command))
            sp.run(custom_build_command, check=True)
        else:
            logging.info(f"Using '{build_system}' build system to build the component.")
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
        utils.clean_dir(self.project_config["gg_build_directory"])

        logging.debug("Creating '{}' directory with artifacts and recipes.".format(consts.greengrass_build_dir))
        # Create build artifacts and recipe directories
        Path.mkdir(self.project_config["gg_build_recipes_dir"], parents=True, exist_ok=True)
        Path.mkdir(self.project_config["gg_build_component_artifacts_dir"], parents=True, exist_ok=True)

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
        except Exception as e:
            raise Exception("""{}\n{}""".format(error_messages.BUILD_FAILED, e))

    def get_build_cmd_from_platform(self, build_system):
        """
        Gets build command of the build system specific to the platform on which the command is running.

        Parameters
        ----------
            build_system(string): build system specified in the gdk config file

        Returns
        -------
            build_command(list): List of build commands of the build system specific to the platform.
        """
        platform_sys = platform.system()
        if platform_sys == "Windows" and "build_command_win" in self.supported_build_sytems[build_system]:
            return self.supported_build_sytems[build_system]["build_command_win"]
        return self.supported_build_sytems[build_system]["build_command"]

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
            build_system = self.project_config["component_build_config"]["build_system"]
            build_command = self.get_build_cmd_from_platform(build_system)
            logging.warning(
                f"This component is identified as using '{build_system}' build system. If this is incorrect, please exit and"
                f" specify custom build command in the '{consts.cli_project_config_file}'."
            )
            if build_system == "zip":
                logging.info("Zipping source code files of the component.")
                self._build_system_zip()
            else:
                logging.info("Running the build command '{}'".format(" ".join(build_command)))
                sp.run(build_command, check=True)
        except Exception as e:
            raise Exception(f"Error building the component with the given build system.\n{e}")

    def _build_system_zip(self):
        # Delegate to avoid breaking tests - TODO: We need to avoid testing private methods
        build_system = BuildSystem()
        build_system.register(Zip(self.project_config, self._get_build_folder_by_build_system()))
        build_system.build("zip")

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
        build_system = self.project_config["component_build_config"]["build_system"]
        build_folder = self.supported_build_sytems[build_system]["build_folder"]
        if build_system == "gradle" or build_system == "gradlew":
            return self.get_build_folders(build_folder, "build.gradle").union(
                self.get_build_folders(build_folder, "build.gradle.kts")
            )
        elif build_system == "maven":
            return self.get_build_folders(build_folder, "pom.xml")
        return {Path(utils.current_directory).joinpath(*build_folder).resolve()}

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
        set_dirs_with_build_file = set(f.parent for f in Path(utils.current_directory).rglob(build_file))
        set_of_module_dirs = set()
        for module_dir in set_dirs_with_build_file:
            module_build_folder = Path(module_dir).joinpath(*build_folder).resolve()
            # Filter module directories that also contain build folders - target/, build/libs/
            if module_build_folder.exists():
                set_of_module_dirs.add(module_build_folder)
        return set_of_module_dirs

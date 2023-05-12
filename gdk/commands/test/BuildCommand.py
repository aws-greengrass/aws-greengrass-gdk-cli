from gdk.commands.Command import Command
from gdk.common.config.GDKProject import GDKProject
from gdk.build_system.UATBuildSystem import UATBuildSystem
from pathlib import Path
import gdk.common.utils as utils
import shutil
import logging


class BuildCommand(Command):
    def __init__(self, command_args) -> None:
        super().__init__(command_args, "build")
        self._gdk_project = GDKProject()
        self._test_config = self._gdk_project.test_config
        self.test_directory = utils.get_current_directory().joinpath("uat-features")
        self.recipe_file_name = self._gdk_project.recipe_file.name
        self._gg_build_uat_dir = self._gdk_project.gg_build_dir.joinpath("uat-features")
        self.should_create_uat_recipe = False

    def run(self):
        """
        This method is called when customer runs the `gdk test build` command.

        1. Remove the UAT module from greengrass-build if it exists.
        2. Copy the UAT folder to the greengrass-build directory and perform the following steps:
        3. Update the feature files with component name and UAT recipe file path.
        4. Create the UAT recipe file in the greengrass-build folder.
        5. Build the UAT module.
        """
        build_recipe_file = self._gdk_project.gg_build_recipes_dir.joinpath(self.recipe_file_name)
        uat_recipe_file = self._gdk_project.gg_build_recipes_dir.joinpath("uat_" + self.recipe_file_name)
        self._clean_uat_build_dir()
        self._copy_uat_dir_to_build()
        self.update_feature_files(build_recipe_file, uat_recipe_file)
        self.create_uat_recipe_file(build_recipe_file, uat_recipe_file)
        self.build_uat_module()

    def _clean_uat_build_dir(self):
        if self._gg_build_uat_dir.exists():
            logging.debug("Removing the UAT module from greengrass-build directory")
            shutil.rmtree(self._gg_build_uat_dir)

    def build_uat_module(self):
        logging.info("Building the UAT module")
        build_system = UATBuildSystem.get(self._test_config.test_build_system)
        build_system.build(self._gg_build_uat_dir)

    def _copy_uat_dir_to_build(self):
        logging.debug("Copying the UAT module to greengrass-build directory")
        shutil.copytree(self.test_directory, self._gg_build_uat_dir)

    def update_feature_files(self, build_recipe_file: Path, uat_recipe_file: Path):
        """
        Update .feature files that have GDK_COMPONENT_NAME and/or GDK_COMPONENT_RECIPE_FILE variables with the component name
        and uat_recipe file path respectively.

        If a feature file contains GDK_COMPONENT_RECIPE_FILE variable, the component must be built before building the test
        module or an exception is thrown.
        """
        feature_files = list(self._gg_build_uat_dir.rglob("*.feature"))
        for feature_file in feature_files:
            with open(feature_file, "r", encoding="utf-8") as f:
                feature_file_content = f.read()

            if "GDK_COMPONENT_NAME" not in feature_file_content and "GDK_COMPONENT_RECIPE_FILE" not in feature_file_content:
                continue

            if "GDK_COMPONENT_NAME" in feature_file_content:
                feature_file_content = feature_file_content.replace("GDK_COMPONENT_NAME", self._gdk_project.component_name)

            if "GDK_COMPONENT_RECIPE_FILE" in feature_file_content:
                if not build_recipe_file.exists():
                    raise Exception(
                        "Component is not built. Build it with `gdk component build` command before building the testing"
                        " module."
                    )
                else:
                    self.should_create_uat_recipe = True
                    feature_file_content = feature_file_content.replace("GDK_COMPONENT_RECIPE_FILE", uat_recipe_file.as_uri())
            logging.info("Updating feature file: %s", feature_file.as_uri())
            with open(feature_file, "w", encoding="utf-8") as f:
                f.write(feature_file_content)

    def create_uat_recipe_file(self, build_recipe_file: Path, uat_recipe_file: Path) -> None:
        """
        When the component is built using `gdk component build` command gdk creates a build recipe file. This method uses that
        build recipe file and creates a uat_recipe file in the greengrass-build/recipes folder by replacing the s3 artifact
        URIs with their absolute file paths.
        """
        if not self.should_create_uat_recipe:
            return

        artifact_uri = f"{utils.s3_prefix}BUCKET_NAME/COMPONENT_NAME/COMPONENT_VERSION"

        with open(build_recipe_file, "r", encoding="utf-8") as f:
            content = f.read()
            content = content.replace(artifact_uri, self._gdk_project.gg_build_component_artifacts_dir.as_uri())

        logging.info("Creating the UAT recipe file: %s", uat_recipe_file.as_uri())
        with open(uat_recipe_file, "w", encoding="utf-8") as f:
            f.write(content)

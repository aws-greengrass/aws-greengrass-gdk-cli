from gdk.commands.Command import Command
from gdk.common.config.GDKProject import GDKProject
from gdk.build_system.E2ETestBuildSystem import E2ETestBuildSystem
from pathlib import Path
import gdk.common.utils as utils
import shutil
import logging
from gdk.common.CaseInsensitive import CaseInsensitiveRecipeFile
import gdk.common.consts as consts


class BuildCommand(Command):
    _test_component_default_v = "1.0.0"

    def __init__(self, command_args) -> None:
        super().__init__(command_args, "build")
        self._gdk_project = GDKProject()
        self._test_config = self._gdk_project.test_config
        self.test_directory = utils.get_current_directory().joinpath(consts.E2E_TESTS_DIR_NAME)
        self.recipe_file_name = self._gdk_project.recipe_file.name
        self._gg_build_e2e_test_dir = self._gdk_project.gg_build_dir.joinpath(consts.E2E_TESTS_DIR_NAME)
        self.should_create_e2e_test_recipe = False

    def run(self):
        """
        This method is called when customer runs the `gdk test build` command.

        1. Remove the e2e module from greengrass-build if it exists.
        2. Copy the e2e folder to the greengrass-build directory and perform the following steps:
        3. Update the feature files with component name and e2e recipe file path.
        4. Create the e2e recipe file in the greengrass-build folder.
        5. Build the e2e test module.
        """
        build_recipe_file = self._gdk_project.gg_build_recipes_dir.joinpath(self.recipe_file_name)
        e2e_test_recipe_file = self._gdk_project.gg_build_recipes_dir.joinpath("e2e_test_" + self.recipe_file_name)
        self._clean_e2e_test_build_dir()
        self._copy_e2e_test_dir_to_build()
        self.update_feature_files(build_recipe_file, e2e_test_recipe_file)
        self.create_e2e_test_recipe_file(build_recipe_file, e2e_test_recipe_file)
        self.build_e2e_test_module()

    def _clean_e2e_test_build_dir(self):
        if self._gg_build_e2e_test_dir.exists():
            logging.debug("Removing the E2E testing module from greengrass-build directory")
            shutil.rmtree(self._gg_build_e2e_test_dir)

    def build_e2e_test_module(self):
        logging.info("Building the E2E testing module")
        build_system = E2ETestBuildSystem.get(self._test_config.test_build_system)
        build_system.build(path=self._gg_build_e2e_test_dir)

    def _copy_e2e_test_dir_to_build(self):
        if not self.test_directory.exists():
            raise Exception(
                "Could not find 'gg-e2e-tests' in the current directory. Please initialize the project with testing module"
                " using `gdk test-e2e init` command before building it."
            )
        logging.debug("Copying the E2E testing module to greengrass-build directory")
        shutil.copytree(self.test_directory, self._gg_build_e2e_test_dir)

    def update_feature_files(self, build_recipe_file: Path, e2e_test_recipe_file: Path):
        """
        Update .feature files that have GDK_COMPONENT_NAME and/or GDK_COMPONENT_RECIPE_FILE variables with the component name
        and e2e_test_recipe file path respectively.

        If a feature file contains GDK_COMPONENT_RECIPE_FILE variable, the component must be built before building the test
        module or an exception is thrown.
        """
        feature_files = list(self._gg_build_e2e_test_dir.rglob("*.feature"))
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
                    self.should_create_e2e_test_recipe = True
                    feature_file_content = feature_file_content.replace(
                        "GDK_COMPONENT_RECIPE_FILE", e2e_test_recipe_file.as_uri()
                    )
            logging.info("Updating feature file: %s", feature_file.as_uri())
            with open(feature_file, "w", encoding="utf-8") as f:
                f.write(feature_file_content)

    def create_e2e_test_recipe_file(self, build_recipe_file: Path, e2e_test_recipe_file: Path) -> None:
        """
        When the component is built using `gdk component build` command gdk creates a build recipe file. This method uses
        that build recipe file and creates a E2E test recipe file in the greengrass-build/recipes folder by replacing the
        s3 artifact URIs with their absolute file paths. It also updates the component version to 1.0.0 if it is set to
        NEXT_PATCH.
        """
        if not self.should_create_e2e_test_recipe:
            return

        _recipe = CaseInsensitiveRecipeFile().read(build_recipe_file)

        # Update component version
        _version = _recipe.get("ComponentVersion", "NEXT_PATCH")
        if _version == "NEXT_PATCH":
            _recipe.update_value("ComponentVersion", self._test_component_default_v)

        # Update artifact URIs
        for manifest in _recipe.get("manifests", []):
            for artifact in manifest.get("artifacts", []):
                artifact_uri = artifact.get("uri", "")
                if not artifact_uri.startswith(utils.s3_prefix):
                    continue
                artifact_path = self._gdk_project.gg_build_component_artifacts_dir.joinpath(Path(artifact_uri).name).resolve()
                if not artifact_path.exists():
                    # TODO: Currently, GTF supports artifacts at local file or class path only.
                    # Raise an exception if the artifact is not found.
                    logging.warning(
                        "Could not update the artifact URI %s as it does not exist in the build directory", artifact_uri
                    )
                    continue
                artifact.update_value("Uri", artifact_path.as_uri())
        logging.info("Creating the E2E testing recipe file: %s", e2e_test_recipe_file.resolve())
        CaseInsensitiveRecipeFile().write(e2e_test_recipe_file, _recipe)

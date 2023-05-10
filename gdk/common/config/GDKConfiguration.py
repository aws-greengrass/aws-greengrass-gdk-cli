import gdk.common.configuration as configuration
from gdk.common.config.TestConfiguration import TestConfiguration
from pathlib import Path
import gdk.common.utils as utils
import gdk.common.consts as consts
import logging

import gdk.common.exceptions.error_messages as error_messages


class GDKConfiguration:
    def __init__(self):
        self._config = configuration.get_configuration()
        self._component = self._config.get("component")
        self._test = self._config.get("test", {})

        self.component_name = next(iter(self._component))
        self.component_config = self._component.get(self.component_name)
        self.test_config = TestConfiguration(self._test)

        component_version = self.component_config.get("version")

        self.gg_build_dir = Path(utils.get_current_directory()).joinpath(consts.greengrass_build_dir).resolve()
        self.gg_build_artifacts_dir = Path(self.gg_build_dir).joinpath("artifacts").resolve()
        self.gg_build_recipes_dir = Path(self.gg_build_dir).joinpath("recipes").resolve()
        self.gg_build_component_artifacts_dir = (
            Path(self.gg_build_artifacts_dir).joinpath(self.component_name, component_version).resolve()
        )
        self.recipe_file = self.get_recipe_file()

    def get_recipe_file():
        # Search for json files in current directory that contain component name and ends in .json.
        logging.debug("Looking for recipe file in the project directory.")
        json_file = list(Path(utils.get_current_directory()).glob("recipe.json"))
        yaml_file = list(Path(utils.get_current_directory()).glob("recipe.yaml"))

        if not json_file and not yaml_file:
            logging.error("Could not find 'recipe.json' or 'recipe.yaml' in the project directory.")
            raise Exception(error_messages.PROJECT_RECIPE_FILE_NOT_FOUND)

        if json_file and yaml_file:
            logging.error("Found both 'recipe.json' and 'recipe.yaml' in the given project directory.")
            raise Exception(error_messages.PROJECT_RECIPE_FILE_NOT_FOUND)

        recipe_file = (json_file + yaml_file)[0].resolve()
        logging.info("Found component recipe file '{}' in the  project directory.".format(recipe_file.name))
        return recipe_file

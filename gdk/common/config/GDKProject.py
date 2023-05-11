import gdk.common.configuration as configuration
from gdk.common.config.TestConfiguration import TestConfiguration
from pathlib import Path
import gdk.common.utils as utils
import gdk.common.consts as consts
import gdk.commands.component.project_utils as project_utils


class GDKProject:
    def __init__(self):
        self._config = configuration.get_configuration()
        self._component = self._config.get("component")
        self._test = self._config.get("test", {})
        self._project_dir = utils.get_current_directory()

        self.component_name = next(iter(self._component))
        self.component_config = self._component.get(self.component_name)
        self.test_config = TestConfiguration(self._test)

        component_version = self.component_config.get("version")

        self.gg_build_dir = Path(self._project_dir).joinpath(consts.greengrass_build_dir).resolve()
        self.gg_build_artifacts_dir = Path(self.gg_build_dir).joinpath("artifacts").resolve()
        self.gg_build_recipes_dir = Path(self.gg_build_dir).joinpath("recipes").resolve()
        self.gg_build_component_artifacts_dir = (
            Path(self.gg_build_artifacts_dir).joinpath(self.component_name, component_version).resolve()
        )

    @property
    def recipe_file(self):
        return project_utils.get_recipe_file()

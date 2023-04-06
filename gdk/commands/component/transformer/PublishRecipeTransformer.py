import logging
from pathlib import Path
from gdk.common.CaseInsensitive import CaseInsensitiveRecipeFile, CaseInsensitiveDict

import gdk.common.consts as consts
import gdk.common.utils as utils


class PublishRecipeTransformer:
    def __init__(self, project_config) -> None:
        self.project_config = project_config

    def transform(self):
        recipe_path = Path(self.project_config["gg_build_recipes_dir"]).joinpath(
            self.project_config["component_recipe_file"].name
        )
        component_recipe = CaseInsensitiveRecipeFile().read(recipe_path)
        self.update_component_recipe_file(component_recipe)
        self.create_publish_recipe_file(component_recipe)

    def update_component_recipe_file(self, parsed_component_recipe):
        logging.debug(
            "Updating component recipe with the 'component' configuration provided in '{}'.".format(
                consts.cli_project_config_file
            )
        )
        parsed_component_recipe.update_value("ComponentVersion", self.project_config["component_version"])
        self._update_artifact_uris(parsed_component_recipe)

    def _update_artifact_uris(self, parsed_component_recipe: CaseInsensitiveDict) -> None:
        """
        Updates recipe with the component version calculated and artifact URIs of the artifacts. This updated recipe is
        used to create a new publish recipe file in build recipes directory.

        """
        logging.debug("Updating artifact URIs in the recipe...")
        component_name = self.project_config["component_name"]
        component_version = self.project_config["component_version"]

        if parsed_component_recipe.get("ComponentName") != component_name:
            logging.error("Component '{}' is not built.".format(parsed_component_recipe["ComponentName"]))
            raise Exception(
                "Failed to publish the component '{}' as it is not build.\nBuild the component `gdk component"
                " build` before publishing it.".format(parsed_component_recipe["ComponentName"])
            )
        gg_build_component_artifacts = self.project_config["gg_build_component_artifacts_dir"]
        bucket = self.project_config["bucket"]
        artifact_uri = f"{utils.s3_prefix}{bucket}/{component_name}/{component_version}"

        if "Manifests" not in parsed_component_recipe:
            logging.debug("No 'Manifests' key in the recipe.")
            return
        for manifest in parsed_component_recipe["Manifests"]:
            if "Artifacts" not in manifest:
                logging.debug("No 'Artifacts' key in the recipe manifest.")
                continue
            for artifact in manifest["Artifacts"]:
                if "URI" not in artifact:
                    logging.debug("No 'URI' found in the recipe artifacts.")
                    continue
                # Skip non-s3 URIs in the recipe. Eg docker URIs
                if not artifact["URI"].startswith("s3://"):
                    continue
                artifact_file = Path(artifact["URI"]).name
                # For artifact in build component artifacts folder, update its URI
                build_artifact_files = list(gg_build_component_artifacts.glob(artifact_file))
                if len(build_artifact_files) == 1:
                    logging.debug("Updating artifact URI of '{}' in the recipe file.".format(artifact_file))
                    artifact.update_value("Uri", f"{artifact_uri}/{artifact_file}")
                else:
                    logging.warning(
                        f"Could not find the artifact file specified in the recipe '{artifact_file}' inside the build folder"
                        f" '{gg_build_component_artifacts}'."
                    )

    def create_publish_recipe_file(self, parsed_component_recipe) -> None:
        """
        Creates a new recipe file(json or yaml) in the component recipes build directory.

        This recipe is updated with the component configuration provided in the project config file.

        Parameters
        ----------
            None

        """
        publish_recipe_file = Path(self.project_config["publish_recipe_file"]).resolve()
        CaseInsensitiveRecipeFile().write(publish_recipe_file, parsed_component_recipe)

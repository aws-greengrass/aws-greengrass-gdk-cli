import jsonschema
import logging
from pathlib import Path
from gdk.commands.component.config.ComponentPublishConfiguration import ComponentPublishConfiguration
from gdk.common.CaseInsensitive import CaseInsensitiveRecipeFile, CaseInsensitiveDict
from gdk.common.RecipeValidator import RecipeValidator

import gdk.common.consts as consts
import gdk.common.utils as utils
from gdk.common.exceptions.error_messages import BUILT_RECIPE_SIZE_INVALID, PROJECT_RECIPE_FILE_INVALID, SCHEMA_FILE_INVALID


class PublishRecipeTransformer:
    def __init__(self, _project_config: ComponentPublishConfiguration) -> None:
        self.project_config = _project_config

    def transform(self):
        recipe_path = Path(self.project_config.gg_build_recipes_dir).joinpath(self.project_config.recipe_file.name)
        component_recipe = CaseInsensitiveRecipeFile().read(recipe_path)
        self.update_component_recipe_file(component_recipe)
        self.create_publish_recipe_file(component_recipe)

    def update_component_recipe_file(self, parsed_component_recipe):
        logging.debug(
            "Updating component recipe with the 'component' configuration provided in '{}'.".format(
                consts.cli_project_config_file
            )
        )
        parsed_component_recipe.update_value("ComponentVersion", self.project_config.component_version)
        self._update_artifact_uris(parsed_component_recipe)

    def _update_artifact_uris(self, parsed_component_recipe: CaseInsensitiveDict) -> None:
        """
        Updates recipe with the component version calculated and artifact URIs of the artifacts. This updated recipe is
        used to create a new publish recipe file in build recipes directory.

        """
        logging.debug("Updating artifact URIs in the recipe...")
        component_name = self.project_config.component_name
        component_version = self.project_config.component_version

        if parsed_component_recipe.get("ComponentName") != component_name:
            logging.error("Component '{}' is not built.".format(parsed_component_recipe["ComponentName"]))
            raise Exception(
                "Failed to publish the component '{}' as it is not build.\nBuild the component `gdk component"
                " build` before publishing it.".format(parsed_component_recipe["ComponentName"])
            )
        gg_build_component_artifacts = self.project_config.gg_build_component_artifacts_dir
        artifact_uri = f"{utils.s3_prefix}{self.project_config.bucket}/{component_name}/{component_version}"

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

        logging.debug("Creating component recipe at '%s'.", self.project_config.publish_recipe_file)
        CaseInsensitiveRecipeFile().write(self.project_config.publish_recipe_file, parsed_component_recipe)

        recipe_path = Path(self.project_config.gg_build_recipes_dir).joinpath(self.project_config.publish_recipe_file)
        logging.info(f"Validating the file size of the built recipe {recipe_path}")
        # Validate the size of the created recipe file so we can raise an exception if it is too big
        valid_file_size, input_recipe_file_size = utils.is_recipe_size_valid(recipe_path)
        if not valid_file_size:
            logging.error(BUILT_RECIPE_SIZE_INVALID.format(input_recipe_file_size))
            raise Exception(BUILT_RECIPE_SIZE_INVALID.format(input_recipe_file_size))

        logging.info("Validating the built recipe against the Greengrass recipe schema.")
        try:
            recipe_schema_path = utils.get_static_file_path(consts.recipe_schema_file)
            validator = RecipeValidator(recipe_schema_path)
            validator.validate_recipe(parsed_component_recipe.to_dict())
        except jsonschema.exceptions.ValidationError as err:
            raise Exception(PROJECT_RECIPE_FILE_INVALID.format(recipe_path, err.message))
        except jsonschema.exceptions.SchemaError as err:
            raise Exception(SCHEMA_FILE_INVALID.format(err.message))

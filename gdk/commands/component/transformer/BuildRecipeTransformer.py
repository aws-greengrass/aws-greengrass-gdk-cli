import jsonschema
import logging
import shutil
from pathlib import Path
from gdk.common.CaseInsensitive import CaseInsensitiveRecipeFile, CaseInsensitiveDict
from gdk.common.RecipeValidator import RecipeValidator

import gdk.common.consts as consts
import gdk.common.utils as utils
from gdk.commands.component.config.ComponentBuildConfiguration import ComponentBuildConfiguration
from gdk.aws_clients.S3Client import S3Client
from gdk.common.exceptions.error_messages import RECIPE_SIZE_INVALID, PROJECT_RECIPE_FILE_INVALID, SCHEMA_FILE_INVALID


class BuildRecipeTransformer:
    def __init__(self, project_config: ComponentBuildConfiguration) -> None:
        self.project_config = project_config
        self._s3_client = None

    def _get_s3_client(self, _region):
        if not _region:
            raise ValueError("Region cannot be empty. Please provide a valid region.")
        if self._s3_client is None:
            self._s3_client = S3Client(_region)
        return self._s3_client

    def transform(self, build_folders):
        logging.info(f"Validating the file size of recipe {self.project_config.recipe_file}")
        # Validate the size of the recipe file before processing its content.
        valid_file_size, input_recipe_file_size = utils.is_recipe_size_valid(self.project_config.recipe_file)
        if not valid_file_size:
            logging.error(RECIPE_SIZE_INVALID.format(self.project_config.recipe_file, input_recipe_file_size))
            raise Exception(RECIPE_SIZE_INVALID.format(self.project_config.recipe_file, input_recipe_file_size))

        component_recipe = CaseInsensitiveRecipeFile().read(self.project_config.recipe_file)
        self.update_component_recipe_file(component_recipe, build_folders)

        logging.info("Validating the recipe against the Greengrass recipe schema.")
        try:
            recipe_schema_path = utils.get_static_file_path(consts.recipe_schema_file)
            validator = RecipeValidator(recipe_schema_path)
            validator.validate_recipe(component_recipe.to_dict())
        except jsonschema.exceptions.ValidationError as err:
            raise Exception(PROJECT_RECIPE_FILE_INVALID.format(self.project_config.recipe_file, err.message))
        except jsonschema.exceptions.SchemaError as err:
            raise Exception(SCHEMA_FILE_INVALID.format(err.message))

        self.create_build_recipe_file(component_recipe)

    def update_component_recipe_file(self, parsed_component_recipe: CaseInsensitiveDict, build_folders):
        logging.debug(
            "Updating component recipe with the 'component' configuration provided in '%s'.", consts.cli_project_config_file
        )
        parsed_component_recipe.update_value("ComponentName", self.project_config.component_name)
        parsed_component_recipe.update_value("ComponentVersion", self.project_config.component_version)
        parsed_component_recipe.update_value("ComponentPublisher", self.project_config.publisher)
        self.update_artifact_uris(parsed_component_recipe, build_folders)

    def update_artifact_uris(self, parsed_component_recipe, build_folders: list) -> None:
        """
        The artifact URIs in the recipe are used to identify the artifacts in local build folders of the component or on s3.

        If the artifact is not found in the local build folders specific to the build system of the component, it is
        searched on S3 with exact URI in the recipe.

        Build command fails when the artifacts are neither not found in local both folders not on s3.
        """
        logging.info("Copying over the build artifacts to the greengrass component artifacts build folder.")
        logging.info("Updating artifact URIs in the recipe.")
        if "Manifests" not in parsed_component_recipe:
            logging.debug("No 'Manifests' key in the recipe.")
            return
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
                if not artifact["URI"].startswith(utils.s3_prefix):
                    continue
                if not self.is_artifact_in_build(artifact, build_folders):
                    if not self._get_s3_client(self.project_config.region).s3_artifact_exists(artifact["URI"]):
                        raise Exception(
                            "Could not find artifact with URI '{}' on s3 or inside the build folders.".format(artifact["URI"])
                        )

    def is_artifact_in_build(self, artifact, build_folders) -> bool:
        """
        Copies over the build artifacts to the greengrass artifacts build folder and update URIs in the recipe.

        The component artifacts in the recipe are looked up in the build folders specific to the build system of the component.
        If the artifact is found, it is copied over to the greengrass artifacts build folder and the URI is updated in the
        recipe and returns True. Otherwise, it returns False.

        Parameters
        ----------
            artifact(dict): The artifact object in the recipe which contains URI and Unarchive type.
            build_folders(list): Build folders specific to the build system of the component

        """
        artifact_uri = f"{utils.s3_prefix}BUCKET_NAME/COMPONENT_NAME/COMPONENT_VERSION"
        gg_build_component_artifacts_dir = self.project_config.gg_build_component_artifacts_dir
        artifact_file_name = Path(artifact["URI"]).name
        # If the artifact is present in build system specific build folder, copy it to greengrass artifacts build folder
        for build_folder in build_folders:
            artifact_file = Path(build_folder).joinpath(artifact_file_name).resolve()
            if artifact_file.is_file():
                logging.debug(
                    "Copying file '%s' from '%s' to '%s'.", artifact_file_name, build_folder, gg_build_component_artifacts_dir
                )

                shutil.copy(artifact_file, gg_build_component_artifacts_dir)
                logging.debug("Updating artifact URI of '%s' in the recipe file.", artifact_file_name)
                artifact.update_value("Uri", f"{artifact_uri}/{artifact_file_name}")
                return True
            else:
                logging.debug(
                    "Could not find the artifact file specified in the recipe '%s' inside the build folder '%s'.",
                    artifact_file_name,
                    build_folder,
                )
        logging.warning("Could not find the artifact file '%s' in the build folder '%s'.", artifact_file_name, build_folders)
        return False

    def create_build_recipe_file(self, parsed_component_recipe) -> None:
        """
        Creates a new recipe file(json or yaml) in the component recipes build directory.

        This recipe is updated with the component configuration provided in the project config file.

        Parameters
        ----------
            None

        """
        gg_build_recipe_file = self.project_config.gg_build_recipes_dir.joinpath(
            self.project_config.recipe_file.name
        ).resolve()
        logging.debug("Creating component recipe at '%s'.", gg_build_recipe_file)
        CaseInsensitiveRecipeFile().write(gg_build_recipe_file, parsed_component_recipe)

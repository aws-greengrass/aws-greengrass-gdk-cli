import logging
import shutil
from pathlib import Path
from gdk.common.CaseInsensitive import CaseInsensitiveRecipeFile, CaseInsensitiveDict

import gdk.commands.component.project_utils as project_utils
import gdk.common.consts as consts
import gdk.common.utils as utils


class BuildRecipeTransformer:
    def __init__(self, project_config) -> None:
        self.project_config = project_config

    def transform(self, build_folders):
        component_recipe = CaseInsensitiveRecipeFile().read(
            self.project_config["component_recipe_file"]
        )
        self.update_component_recipe_file(component_recipe, build_folders)
        self.create_build_recipe_file(component_recipe)

    def update_component_recipe_file(
        self, parsed_component_recipe: CaseInsensitiveDict, build_folders
    ):
        logging.debug(
            "Updating component recipe with the 'component' configuration provided in '{}'.".format(
                consts.cli_project_config_file
            )
        )
        parsed_component_recipe.update_value(
            "ComponentName", self.project_config["component_name"]
        )
        parsed_component_recipe.update_value(
            "ComponentVersion", self.project_config["component_version"]
        )
        parsed_component_recipe.update_value(
            "ComponentPublisher", self.project_config["component_author"]
        )
        self.update_artifact_uris(parsed_component_recipe, build_folders)

    def update_artifact_uris(
        self, parsed_component_recipe, build_folders: list
    ) -> None:
        """
        The artifact URIs in the recipe are used to identify the artifacts in local build folders of the component or on s3.

        If the artifact is not found in the local build folders specific to the build system of the component, it is
        searched on S3 with exact URI in the recipe.

        Build command fails when the artifacts are neither not found in local both folders not on s3.
        """
        logging.info(
            "Copying over the build artifacts to the greengrass component artifacts build folder."
        )
        logging.info("Updating artifact URIs in the recipe.")
        if "Manifests" not in parsed_component_recipe:
            logging.debug("No 'Manifests' key in the recipe.")
            return
        manifests = parsed_component_recipe["Manifests"]
        s3_client = None
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
                    if not s3_client:
                        s3_client = project_utils.create_s3_client(
                            self.project_config["region"]
                        )
                    if not self.is_artifact_in_s3(s3_client, artifact["URI"]):
                        raise Exception(
                            "Could not find artifact with URI '{}' on s3 or inside the build folders.".format(
                                artifact["URI"]
                            )
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
        gg_build_component_artifacts_dir = self.project_config[
            "gg_build_component_artifacts_dir"
        ]
        artifact_file_name = Path(artifact["URI"]).name
        # If the artifact is present in build system specific build folder, copy it to greengrass artifacts build folder
        for build_folder in build_folders:
            artifact_file = Path(build_folder).joinpath(artifact_file_name).resolve()
            if artifact_file.is_file():
                logging.debug(
                    "Copying file '{}' from '{}' to '{}'.".format(
                        artifact_file_name,
                        build_folder,
                        gg_build_component_artifacts_dir,
                    )
                )
                shutil.copy(artifact_file, gg_build_component_artifacts_dir)
                logging.debug(
                    "Updating artifact URI of '{}' in the recipe file.".format(
                        artifact_file_name
                    )
                )
                # artifact["URI"] = f"{artifact_uri}/{artifact_file_name}"
                artifact.update_value("Uri", f"{artifact_uri}/{artifact_file_name}")
                return True
            else:
                logging.debug(
                    f"Could not find the artifact file specified in the recipe '{artifact_file_name}' inside the build folder"
                    f" '{build_folder}'."
                )
        logging.warning(
            f"Could not find the artifact file '{artifact_file_name}' in the build folder '{build_folders}'."
        )
        return False

    def is_artifact_in_s3(self, s3_client, artifact_uri) -> bool:
        """
        Uses exact artifact uri to find the artifact on s3. Returns if the artifact is found in S3 else False.

        Parameters
        ----------
            s3_client(boto3.client): S3 client created specific to the region in the gdk config.
            artifact_uri(string): S3 URI to look up for
        """
        bucket_name, object_key = artifact_uri.replace(utils.s3_prefix, "").split(
            "/", 1
        )
        try:
            response = s3_client.head_object(Bucket=bucket_name, Key=object_key)
            return response["ResponseMetadata"]["HTTPStatusCode"] == 200
        except Exception as e:
            logging.error("Could not find the artifact on S3.\n{}".format(e))
            return False

    def create_build_recipe_file(self, parsed_component_recipe) -> None:
        """
        Creates a new recipe file(json or yaml) in the component recipes build directory.

        This recipe is updated with the component configuration provided in the project config file.

        Parameters
        ----------
            None

        """

        component_recipe_file_name = self.project_config["component_recipe_file"].name
        gg_build_recipe_file = (
            Path(self.project_config["gg_build_recipes_dir"])
            .joinpath(component_recipe_file_name)
            .resolve()
        )
        logging.debug("Creating component recipe at '%s'.", gg_build_recipe_file)
        CaseInsensitiveRecipeFile().write(gg_build_recipe_file, parsed_component_recipe)

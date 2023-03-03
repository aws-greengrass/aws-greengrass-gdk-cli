import json
import logging
from pathlib import Path

import yaml

import gdk.commands.component.component as component
import gdk.commands.component.project_utils as project_utils
import gdk.common.exceptions.error_messages as error_messages
import gdk.common.utils as utils
from gdk.aws_clients.Greengrassv2Client import Greengrassv2Client
from gdk.aws_clients.S3Client import S3Client
from gdk.commands.Command import Command
from gdk.common.exceptions.CommandError import InvalidArgumentsError


class PublishCommand(Command):
    def __init__(self, command_args) -> None:
        super().__init__(command_args, "publish")

        self.project_config = project_utils.get_project_config_values()
        self.service_clients = project_utils.get_service_clients(self._get_region())
        self.s3_client = S3Client(self.project_config, self.service_clients)
        self.greengrass_client = Greengrassv2Client(self.project_config, self.service_clients)

    def run(self):
        try:
            self.try_build()
            self._update_project_config_values()
            component_name = self.project_config["component_name"]
            component_version = self.project_config["component_version"]
            self._publish_component_version(component_name, component_version)
        except Exception as e:
            logging.error("Failed to publish new version of the component '{}'".format(self.project_config["component_name"]))
            raise Exception("{}\n{}".format(error_messages.PUBLISH_FAILED, e))

    def try_build(self):
        # TODO: This method should just warn and proceed. It should not build the component.
        component_name = self.project_config["component_name"]
        logging.debug(f"Checking if the component '{component_name}' is built.")
        if not utils.dir_exists(self.project_config["gg_build_component_artifacts_dir"]):
            logging.warning(
                f"The component '{component_name}' is not built.\nSo, building the component before publishing it."
            )
            component.build({})

    def _update_project_config_values(self):
        """
        Resolve the publish configuration provided in the gdk config file with the CLI arguments passed to the publish command.
        Arguments provided in the `gdk component publish` commands take precedence over the gdk-config values.

        Parameters
        ----------
            None

        Returns
        -------
            None
        """
        self._update_account_number()
        self._override_config_with_command_args()
        self._update_component_version()

    def _update_account_number(self):
        self.project_config["account_number"] = self.get_account_number()

    def _override_config_with_command_args(self):
        logging.debug("Overridig gdk configuration with the command arguments")
        self._update_region()
        self._update_bucket()
        self._update_options()

    def _update_bucket(self):
        if self.arguments.get("bucket"):
            self.project_config["bucket"] = self.arguments["bucket"]
        else:
            self.project_config["bucket"] = "{}-{}-{}".format(
                self.project_config["bucket"], self.project_config["region"], self.project_config["account_number"]
            )

    def _update_options(self):
        if self.arguments.get("options"):
            try:
                self.project_config["options"] = self._read_options(self.arguments["options"])
            except Exception as exc:
                raise Exception(
                    "Please provide a valid json file path or a json string as the options argument.\nError:\t" + str(exc)
                )

    def _read_options(self, options):
        try:
            if not options.endswith(".json"):
                return json.loads(options)
            return self._read_from_file(options)
        except json.decoder.JSONDecodeError as err:
            raise InvalidArgumentsError(
                options,
                "JSON string is incorrectly formatted.\nError:\t" + str(err),
            )

    def _read_from_file(self, options):
        logging.debug("Reading options from the json file provided in the publish command")
        file_path = Path(options).resolve()
        if not utils.file_exists(file_path):
            raise InvalidArgumentsError(
                options,
                "The json file path provided in the command does not exist",
            )
        with open(file_path, "r") as o_file:
            return json.loads(o_file.read())

    def _get_region(self) -> str:
        if self.arguments.get("region"):
            return self.arguments["region"]
        return self.project_config["region"]

    def _update_region(self):
        self.project_config["region"] = self._get_region()

    def _update_component_version(self):
        self.project_config["component_version"] = self.get_component_version_from_config()

    def _publish_component_version(self, component_name, component_version):
        logging.info(f"Publishing the component '{component_name}' with the given project configuration.")
        logging.info("Uploading the component built artifacts to s3 bucket.")
        self.upload_artifacts_s3()

        logging.info(f"Updating the component recipe {component_name}-{component_version}.")
        self.update_and_create_recipe_file(component_name, component_version)

        logging.info(f"Creating a new greengrass component {component_name}-{component_version}")
        self.greengrass_client.create_gg_component()

    def upload_artifacts_s3(self) -> None:
        """
        Uploads all the artifacts from component artifacts build folder to s3 bucket.

        Raises an exception when the request is not successful.
        """
        bucket = self.project_config["bucket"]
        region = self.project_config["region"]
        logging.info(
            f"Uploading component artifacts to S3 bucket: {bucket}. If this is your first time using this bucket, add the"
            " 's3:GetObject' permission to each core device's token exchange role to allow it to download the component"
            f" artifacts. For more information, see {utils.doc_link_device_role}."
        )

        build_component_artifacts = list(self.project_config["gg_build_component_artifacts_dir"].iterdir())

        if len(build_component_artifacts) != 0:
            self.s3_client.create_bucket(bucket, region)
            self.s3_client.upload_artifacts(build_component_artifacts)

    def get_next_version(self):
        """
        Calculates the next patch version of the component if it already exists in the account. Otherwise, it uses 1.0.0 as
        the fallback version.

        Parameters
        ----------
            None

        Returns
        -------
            version(string): Version of the component to create.
        """
        fallback_version = "1.0.0"
        logging.debug("Fetching private components from the account.")
        try:
            c_name = self.project_config["component_name"]
            c_next_patch_version = self.greengrass_client.get_highest_component_version_()
            if not c_next_patch_version:
                logging.info(
                    "No private version of the component '{}' exist in the account. Using '{}' as the next version to create."
                    .format(c_name, fallback_version)
                )
                return fallback_version
            logging.debug(
                "Found latest version '{}' of the component '{}' in the account.".format(c_next_patch_version, c_name)
            )
            next_version = utils.get_next_patch_version(c_next_patch_version)
            logging.info("Using '{}' as the next version of the component '{}' to create.".format(next_version, c_name))
            return next_version
        except Exception as e:
            raise Exception("Failed to calculate the next version of the component during publish.\n{}".format(e))

    def get_account_number(self):
        """
        Uses STS client to get account number from the credentials provided using AWS cli.

        Raises an exception when the request is unsuccessful.

        Parameters
        ----------
            None

        Returns
        -------
            account_num: Returns account number.
        """
        try:
            caller_identity_response = self.service_clients["sts_client"].get_caller_identity()
            account_num = caller_identity_response["Account"]
            logging.debug("Identified account number as '{}'.".format(account_num))
            return account_num
        except Exception as e:
            raise Exception("Error while fetching account number from credentials.\n{}".format(e))

    def get_component_version_from_config(self):
        """
        Returns component version based on the project configuration.

        If component version is set to NEXT_PATCH, patch version of the latest component version is calculated. Otherwise,
        exact version specified will be used as the component version during creation of the component.

        Parameters
        ----------
            None

        Returns
        -------
            None
        """
        try:
            component_name = self.project_config["component_name"]
            if self.project_config["component_version"] == "NEXT_PATCH":
                logging.debug(
                    "Component version set to 'NEXT_PATCH' in the config file. Calculating next version of the component '{}'"
                    .format(self.project_config["component_name"])
                )
                return self.get_next_version()
            logging.info("Using the version set for the component '{}' in the config file.".format(component_name))
            return self.project_config["component_version"]
        except Exception as e:
            logging.error(
                "Failed to calculate the version of component '{}' based on the configuration.".format(component_name)
            )
            raise (e)

    def update_and_create_recipe_file(self, component_name, component_version):
        """
        Updates recipe with the component version calculated and artifact URIs of the artifacts. This updated recipe is
        used to create a new publish recipe file in build recipes directory.

        Parameters
        ----------
            component_name(string): Name of the component. This is also used in the name of the recipe file.
            component_version(string): Version of the component calculated based on the configuration.

        Returns
        -------
            None
        """
        logging.debug("Updating artifact URIs in the recipe...")
        build_recipe = Path(self.project_config["gg_build_recipes_dir"]).joinpath(
            self.project_config["component_recipe_file"].name
        )
        parsed_component_recipe = project_utils.parse_recipe_file(build_recipe)
        if "ComponentName" in parsed_component_recipe:
            if parsed_component_recipe["ComponentName"] != component_name:
                logging.error("Component '{}' is not build.".format(parsed_component_recipe["ComponentName"]))
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
                    artifact["URI"] = f"{artifact_uri}/{artifact_file}"
                else:
                    logging.warning(
                        f"Could not find the artifact file specified in the recipe '{artifact_file}' inside the build folder"
                        f" '{gg_build_component_artifacts}'."
                    )

        # Update the version of the component in the recipe
        parsed_component_recipe["ComponentVersion"] = component_version
        self.create_publish_recipe_file(component_name, component_version, parsed_component_recipe)

    def create_publish_recipe_file(self, component_name, component_version, parsed_component_recipe):
        """
        Creates a new recipe file(json or yaml) with name `<component_name>-<component_version>.extension` in the component
        recipes build directory.

        This recipe is updated with the component version calculated and artifact URIs of the artifacts.

        Parameters
        ----------
            component_name(string): Name of the component. This is also used in the name of the recipe file.
            component_version(string): Version of the component calculated based on the configuration.
            parsed_component_recipe(dict): Updated publish recipe with component version and s3 artifact uris
        Returns
        -------
            None
        """
        ext = self.project_config["component_recipe_file"].name.split(".")[-1]  # json or yaml
        publish_recipe_file_name = f"{component_name}-{component_version}.{ext}"  # Eg. HelloWorld-1.0.0.yaml
        publish_recipe_file = Path(self.project_config["gg_build_recipes_dir"]).joinpath(publish_recipe_file_name).resolve()
        self.project_config["publish_recipe_file"] = publish_recipe_file
        with open(publish_recipe_file, "w") as prf:
            try:
                logging.debug(
                    "Creating component recipe '{}' in '{}'.".format(
                        publish_recipe_file_name, self.project_config["gg_build_recipes_dir"]
                    )
                )
                if publish_recipe_file_name.endswith(".json"):
                    prf.write(json.dumps(parsed_component_recipe, indent=4))
                else:
                    yaml.dump(parsed_component_recipe, prf)
            except Exception as e:
                raise Exception("""Failed to create publish recipe file at '{}'.\n{}""".format(publish_recipe_file, e))

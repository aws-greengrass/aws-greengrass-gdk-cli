import json
import logging
from pathlib import Path

import gdk.commands.component.component as component
import gdk.commands.component.project_utils as project_utils
import gdk.common.exceptions.error_messages as error_messages
import gdk.common.utils as utils
import yaml
from botocore.exceptions import ClientError
from gdk.commands.Command import Command
from gdk.common import consts


class PublishCommand(Command):
    def __init__(self, command_args) -> None:
        super().__init__(command_args, "publish")
        logging.debug("Arguments: {}".format(command_args))

        project_config_filename = command_args["gdk_config"] if command_args["gdk_config"] != None else consts.cli_project_config_file
        project_build_directory = command_args["build_dir"] if command_args["build_dir"] != None else "{}/{}".format(utils.current_directory, consts.greengrass_build_dir)

        component_name = command_args["component_name"]
        component_version = command_args["component_version"]

        logging.debug("Loading project configuration values")
        self.project_config = project_utils.get_project_config_values(project_config_filename, project_build_directory, component_name, component_version)

        if component_name is not None and component_version is not None:
            self.project_config["component_name"] = component_name
            self.project_config["component_version"] = component_version
            project_recipe_filename = project_utils.find_recipe_file_in_path("{}-{}".format(component_name, component_version), "{}/recipes".format(project_build_directory))
        elif component_name is None and component_version is None:
            project_recipe_filename = project_utils.find_recipe_file_in_path("recipe", "{}/recipes".format(project_build_directory))
        else:
            raise RuntimeError("Component name and version must be provided together")

        logging.debug("Project config filename   : {}".format(project_config_filename))
        logging.debug("Project build directory   : {}".format(project_build_directory))
        logging.debug("Project recipe filename   : {}".format(project_recipe_filename))

        logging.debug("Loading recipe values")
        recipe_values = project_utils.get_project_recipe_values(project_recipe_filename)

        logging.debug("Merging recipe into project configuration value")
        self.project_config.update(recipe_values)

        logging.debug("Project configuration: {}".format(self.project_config))

        self.service_clients = project_utils.get_service_clients(self.project_config["region"])

    def run(self):
        try:
            self.project_config["account_number"] = self.get_account_number()
            if self.arguments["bucket"]:
                self.project_config["bucket"] = self.arguments["bucket"]
            else:
                self.project_config["bucket"] = "{}-{}-{}".format(
                    self.project_config["bucket"], self.project_config["region"], self.project_config["account_number"]
                )

            component_name = self.project_config["component_name"]
            component_version = self.get_component_version_from_config()
            logging.debug(f"Checking if the component '{component_name}' is built.")
            if not utils.dir_exists(self.project_config["gg_build_component_artifacts_dir"]):
                logging.warning(
                    f"The component '{component_name}' is not built.\nSo, building the component before publishing it."
                )
                component.build({})
            logging.info(f"Publishing the component '{component_name}' with the given project configuration.")
            logging.info("Uploading the component built artifacts to s3 bucket.")
            self.upload_artifacts_s3(component_name, component_version)

            logging.info(f"Updating the component recipe {component_name}-{component_version}.")
            project_utils.update_and_create_recipe_file(self.project_config, component_name, component_version)

            logging.info(f"Creating a new greengrass component {component_name}-{component_version}")
            self.create_gg_component(component_name, component_version)
        except Exception as e:
            logging.error("Failed to publish new version of the component '{}'".format(self.project_config["component_name"]))
            raise Exception("{}\n{}".format(error_messages.PUBLISH_FAILED, e))

    def upload_artifacts_s3(self, component_name, component_version):
        """
        Uploads all the artifacts from component artifacts build folder to s3 bucket.

        Raises an exception when the request is not successful.

        Parameters
        ----------
            component_name(string): Name of the component to use in the s3 file path.
            component_version(string): Version of the component to use in the s3 file path.

        Returns
        -------
            None
        """
        try:
            bucket = self.project_config["bucket"]
            region = self.project_config["region"]
            logging.info(
                f"Uploading component artifacts to S3 bucket: {bucket}. If this is your first time using this bucket, add the"
                " 's3:GetObject' permission to each core device's token exchange role to allow it to download the component"
                f" artifacts. For more information, see {utils.doc_link_device_role}."
            )

            build_component_artifacts = list(self.project_config["gg_build_component_artifacts_dir"].iterdir())
            # Create bucket only when there's something to upload.
            if len(build_component_artifacts) != 0:
                self.create_bucket(bucket, region)
            for artifact in build_component_artifacts:
                s3_file_path = f"{component_name}/{component_version}/{artifact.name}"
                logging.debug("Uploading artifact '{}' to the bucket '{}'.".format(artifact.resolve(), bucket))
                self.service_clients["s3_client"].upload_file(str(artifact.resolve()), bucket, s3_file_path)
        except Exception as e:
            raise Exception("Error while uploading the artifacts to s3 during publish.\n{}".format(e))

    def create_bucket(self, bucket, region):
        """
        Creates a new s3 bucket for artifacts if it doesn't exist already.

        Raises an exception when the request is not successful.

        Parameters
        ----------
            bucket(string): Name of the bucket to create.
            region(string): Region is which the bucket is created.

        Returns
        -------
            None
        """
        try:
            if region is None or region == "us-east-1":
                self.service_clients["s3_client"].create_bucket(Bucket=bucket)
            else:
                location = {"LocationConstraint": region}
                self.service_clients["s3_client"].create_bucket(Bucket=bucket, CreateBucketConfiguration=location)
        except ClientError as e:
            if e.response["Error"]["Code"] == "BucketAlreadyExists":
                logging.error("Bucket already exists. Please provide a different name for the bucket in the configuration.")
            elif e.response["Error"]["Code"] == "BucketAlreadyOwnedByYou":
                if self.bucket_exists_in_same_region(bucket, region):
                    logging.info("Not creating an artifacts bucket as it already exists.")
                    return
                logging.error(f"Cannot create the artifacts bucket '{bucket}' as it is already owned by you in other region.")
            raise Exception(e)
        except Exception as e:
            logging.error("Failed to create the bucket '{}' in region '{}'".format(bucket, region))
            raise Exception(e)
        logging.info("Successfully created the artifacts bucket '{}' in region '{}'".format(bucket, region))

    def bucket_exists_in_same_region(self, bucket, region):
        """
        Checks if region of the bucket is same as the given region.


        Parameters
        ----------
            bucket(string): Name of the bucket to create.
            region(string): Name of the region to check.

        Returns
        -------
            bool: Returns true if the bucket region is same as the region in check. Else false.
        """
        try:
            response = self.service_clients["s3_client"].get_bucket_location(Bucket=bucket)
            if response["LocationConstraint"] == region:
                return True
            return False
        except Exception as e:
            raise Exception("Unable to fetch the location of the bucket '{}'.\n{}".format(bucket, e))

    def create_gg_component(self, c_name, c_version):
        """
        Creates a GreengrassV2 private component using its recipe.

        Raises an exception if the recipe is invalid or the request is not successful.

        Parameters
        ----------
            c_name(string): Name of the component to create.
            c_version(string): Version of the component to create.

        Returns
        -------
            None
        """
        publish_recipe_file = self.project_config["publish_recipe_file"]
        with open(publish_recipe_file) as f:
            try:
                self.service_clients["greengrass_client"].create_component_version(inlineRecipe=f.read())
            except Exception as e:
                logging.error("Failed to create the component using the recipe at '{}'.".format(publish_recipe_file))
                raise Exception("Creating private version '{}' of the component '{}' failed.\n{}".format(c_version, c_name, e))
            logging.info("Created private version '{}' of the component in the account.'{}'.".format(c_version, c_name))

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
            region = self.project_config["region"]
            account_num = self.project_config["account_number"]
            c_next_patch_version = self.get_next_patch_component_version(c_name, region, account_num)
            if not c_next_patch_version:
                logging.info(
                    "No private version of the component '{}' exist in the account. Using '{}' as the next version to create."
                    .format(c_name, fallback_version)
                )
                return fallback_version
            logging.debug(
                "Found latest version '{}' of the component '{}' in the account.".format(c_next_patch_version, c_name)
            )
            semver_alphanumeric = c_next_patch_version.split("-")
            semver_numeric = semver_alphanumeric[0].split(".")
            major = semver_numeric[0]
            minor = semver_numeric[1]
            patch = semver_numeric[2]
            next_patch_version = int(patch) + 1
            next_version = "{}.{}.{}".format(major, minor, str(next_patch_version))
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

    def get_next_patch_component_version(self, component_name, region, account_num):
        """
        Gets highest version of the component from the sorted order of its versions from an account in a region.

        Makes a boto3 request with greengrass service client to list all versions of a component in an account.
        Parameters
        ----------
            None

        Returns
        -------
            version(string): Highest version of the component if it exists already. Else returns 1.0.0.
        """

        try:
            comp_list_response = self.service_clients["greengrass_client"].list_component_versions(
                arn="arn:aws:greengrass:{}:{}:components:{}".format(region, account_num, component_name)
            )
            component_versions = comp_list_response["componentVersions"]
            if not component_versions:
                return None
            return component_versions[0]["componentVersion"]
        except Exception as e:
            raise Exception(
                "Error while getting the component versions of '{}' in '{}' from the account '{}' during publish.\n{}".format(
                    component_name, region, account_num, e
                )
            )

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
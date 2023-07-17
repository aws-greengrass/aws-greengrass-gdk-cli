from gdk.common.config.GDKProject import GDKProject
import json
from pathlib import Path
from gdk.common.exceptions.CommandError import InvalidArgumentsError
import logging
import gdk.common.utils as utils
from gdk.aws_clients.Greengrassv2Client import Greengrassv2Client
import boto3
from botocore import exceptions


class ComponentPublishConfiguration(GDKProject):
    def __init__(self, _args) -> None:
        super().__init__()
        self._args = _args
        self._gg_client = None
        self._publish_config = self.component_config.get("publish", {})
        self.options = self._get_options()
        self.account_num = self.get_account_number()
        self.region = self._get_region()
        self.bucket = self._get_bucket(self.region, self.account_num)
        self.component_version = self.get_component_version(self.region)
        self.publisher = self.component_config.get("author", "")
        self.publish_recipe_file = self.gg_build_recipes_dir.joinpath(
            f"{self.component_name}-{self.component_version}.{self.recipe_file.name.split('.')[-1]}"
        )

    def gg_client(self, region):
        if not self._gg_client:
            self._gg_client = Greengrassv2Client(region)
        return self._gg_client

    def _get_region(self):
        _region = ""
        _region_args = self._args.get("region")
        if _region_args:
            _region = _region_args
        else:
            _region = self._publish_config.get("region", "")

        return self._validated_region(_region)

    def _validated_region(self, region):
        if region == "":
            raise ValueError("Region cannot be empty. Please provide a valid region.")
        component_arn = self._get_component_arn(region)
        try:
            self.gg_client(region).get_component_version(component_arn)
        except exceptions.EndpointConnectionError:
            raise ValueError("Greengrass does not exist in %s region. Please provide a valid region.", region)
        except Exception as e:
            logging.error("Error occurred while checking Greengrass availability: %s", e)
            raise e
        return region

    def _get_bucket(self, _region, _account):
        _bucket = ""
        _bucket_args = self._args.get("bucket")
        if _bucket_args:
            _bucket = _bucket_args
        else:
            _bucket_config = self._publish_config.get("bucket", "")
            if _bucket_config:
                _bucket = _bucket_config.strip() + "-" + _region + "-" + _account

        if not _bucket:
            raise ValueError("Bucket cannot be empty. Please provide a valid bucket.")

        return _bucket

    def _get_options(self):
        _options_args = self._args.get("options")
        if _options_args:
            return self._read_options_as_dict(_options_args)
        else:
            return self._publish_config.get("options", {})

    def _read_options_as_dict(self, _options: str):
        try:
            if _options.endswith(".json"):
                _options = self._read_from_file(Path(_options))
            else:
                _options = json.loads(_options)
        except json.decoder.JSONDecodeError as err:
            raise InvalidArgumentsError(
                _options,
                "JSON string is incorrectly formatted.\nError:\t" + str(err),
            ) from err
        return _options

    def _read_from_file(self, _opts_path: Path):
        if not _opts_path.is_file():
            raise ValueError("JSON file path provided in the command does not exist. Please provide a valid JSON file.")

        with open(_opts_path.resolve(), "r", encoding="utf-8") as file:
            return json.loads(file.read())

    def get_component_version(self, _region):
        _version = self.component_config.get("version")
        if not _version:
            raise ValueError("Version cannot be empty. Please provide a valid version.")

        if _version == "NEXT_PATCH":
            logging.debug(
                "Component version set to %s in the config file. Calculating next version of the component '%s'",
                _version,
                self.component_name,
            )
            return self._get_next_version(_region)
        logging.info("Using the version %s set for the component '%s' in the config file.", _version, self.component_name)
        return self._validated_version(_region, _version)

    def _validated_version(self, _region, _version):
        component_version_arn = self._get_component_arn(_region) + ":versions:" + _version
        if self.gg_client(_region).component_version_exists(component_version_arn):
            raise ValueError(
                f"Component version {_version} already exists in the {_region} region. Please provide a different version."
            )
        return _version

    def _get_next_version(self, _region) -> str:
        """
        Calculates the next patch version of the component if it already exists in the account. Otherwise, it uses 1.0.0 as
        the fallback version.
        """
        fallback_version = "1.0.0"
        logging.debug("Fetching private components from the account.")
        try:
            c_name = self.component_name
            component_arn = self._get_component_arn(_region)
            c_next_patch_version = self.gg_client(_region).get_highest_cloud_component_version(component_arn)
            if not c_next_patch_version:
                logging.info(
                    "No private version of the component '%s' exist in the account. Using '%s' as the next version to create.",
                    c_name,
                    fallback_version,
                )

                return fallback_version
            logging.debug("Found latest version '%s' of the component '%s' in the account.", c_next_patch_version, c_name)

            next_version = utils.get_next_patch_version(c_next_patch_version)
            logging.info("Using '%s' as the next version of the component '%s' to create.", next_version, c_name)
            return next_version
        except Exception:
            logging.error("Failed to calculate the next version of the component during publish.")
            raise

    def _get_component_arn(self, _region):
        partition = self._get_aws_partition(_region)
        return f"arn:{partition}:greengrass:{_region}:{self.account_num}:components:{self.component_name}"

    def _get_aws_partition(self, _region):
        boto3_session = boto3.Session()
        return boto3_session.get_partition_for_region(region_name=_region)

    def get_account_number(self) -> str:
        """
        Uses STS client to get account number from the credentials provided using AWS cli.
        Raises an exception when the request is unsuccessful.
        """
        try:
            _sts_client = boto3.client("sts")
            account_num = _sts_client.get_caller_identity().get("Account")
            logging.debug("Identified account number as '%s'.", account_num)
            return account_num
        except Exception:
            logging.error("Error while fetching account number from credentials.")
            raise

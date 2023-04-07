import logging

from botocore.exceptions import ClientError


class S3Client:
    """
    S3 client wrapper
    """

    def __init__(self, project_configuration, service_clients):
        self.project_config = project_configuration
        self.s3_client = service_clients["s3_client"]

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
        if self.valid_bucket_for_artifacts_exists(bucket, region):
            logging.info("Not creating an artifacts bucket as it already exists.")
            return

        try:
            if region is None or region == "us-east-1":
                self.s3_client.create_bucket(Bucket=bucket)
            else:
                location = {"LocationConstraint": region}
                self.s3_client.create_bucket(Bucket=bucket, CreateBucketConfiguration=location)
        except Exception:
            logging.error("Failed to create the bucket '%s' in region '%s'", bucket, region)
            raise
        logging.info("Successfully created the artifacts bucket '%s' in region '%s'", bucket, region)

    def upload_artifacts(self, artifacts_to_upload):
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
            component_name = self.project_config["component_name"]
            component_version = self.project_config["component_version"]
            bucket = self.project_config["bucket"]
            options = self.project_config["options"]
            s3_upload_file_args = options.get("file_upload_args", dict())

            for artifact in artifacts_to_upload:
                s3_file_path = f"{component_name}/{component_version}/{artifact.name}"
                logging.debug("Uploading artifact '%s' to the bucket '%s'.", artifact.resolve(), bucket)
                self.s3_client.upload_file(str(artifact.resolve()), bucket, s3_file_path, ExtraArgs=s3_upload_file_args)
        except Exception:
            logging.error("Failed to upload artifacts to s3 during publish.")
            raise

    def valid_bucket_for_artifacts_exists(self, bucket, region) -> bool:
        location_constraint = None if region == "us-east-1" else region
        try:
            response = self.s3_client.get_bucket_location(Bucket=bucket)
            if response["LocationConstraint"] == location_constraint:
                return True
            raise Exception(
                f"Bucket '{bucket}' already exists and is owned by you in another region '{response['LocationConstraint']}'."
                f" Please provide a different name for the bucket in the region '{region}'"
            )
        except ClientError as exc:
            error_code = exc.response["Error"]["Code"]
            if error_code != "403" and error_code != "404":
                logging.error("Could not verify if the bucket '%s' exists in the region '%s'.", bucket, region)
                raise
            elif error_code == "403":
                logging.error(
                    "Bucket '%s' already exists and is not owned by you. Please provide a different name for the"
                    " bucket in the configuration.",
                    bucket,
                )
                raise
            return False
        except Exception:
            logging.error("Could not verify if the bucket '%s' exists in the region '%s'.", bucket, region)
            raise

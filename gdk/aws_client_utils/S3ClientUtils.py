import logging

from botocore.exceptions import ClientError


class S3ClientUtils:
    """
    S3 client utils wrapper
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
        try:
            if region is None or region == "us-east-1":
                self.s3_client.create_bucket(Bucket=bucket)
            else:
                location = {"LocationConstraint": region}
                self.s3_client.create_bucket(Bucket=bucket, CreateBucketConfiguration=location)
        except ClientError as exc:
            if exc.response["Error"]["Code"] == "BucketAlreadyExists":
                logging.error("Bucket already exists. Please provide a different name for the bucket in the configuration.")
            elif exc.response["Error"]["Code"] == "BucketAlreadyOwnedByYou":
                if self.bucket_exists_in_same_region(bucket, region):
                    logging.info("Not creating an artifacts bucket as it already exists.")
                    return
                logging.error("Cannot create the artifacts bucket '%s' as it is already owned by you in other region.", bucket)
            raise Exception(exc) from exc
        except Exception as exc:
            print(exc)
            logging.error("Failed to create the bucket '%s' in region '%s'", bucket, region)
            raise Exception(exc) from exc
        logging.info("Successfully created the artifacts bucket '%s' in region '%s'", bucket, region)

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
            response = self.s3_client.get_bucket_location(Bucket=bucket)
            if response["LocationConstraint"] == region:
                return True
            return False
        except Exception as exc:
            raise Exception(f"Unable to fetch the location of the bucket '{bucket}'.\n{exc}") from exc

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
        except Exception as exc:
            raise Exception(f"Error while uploading the artifacts to s3 during publish.\n{exc}") from exc

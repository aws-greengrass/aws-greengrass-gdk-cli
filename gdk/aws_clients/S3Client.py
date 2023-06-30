import logging
import boto3
from botocore.exceptions import ClientError
import gdk.common.utils as utils


class S3Client:
    """
    S3 client wrapper
    """

    def __init__(self, _region):
        self.s3_client = boto3.client("s3", region_name=_region)
        self._region = _region

    def create_bucket(self, bucket):
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
        region = self._region
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

    def upload_artifact(self, artifact_path, bucket, s3_key_path, extra_args):
        """
        Uploads all the artifacts from component artifacts build folder to s3 bucket.

        Raises an exception when the request is not successful.

        Parameters
        ----------
            component_name(string): Name of the component to use in the s3 file path.
            component_version(string): Version of the component to use in the s3 file path.

        """
        try:
            self.s3_client.upload_file(str(artifact_path.resolve()), bucket, s3_key_path, ExtraArgs=extra_args)
        except Exception:
            logging.error("Failed to upload artifacts to s3 during")
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
            if error_code != "AccessDenied" and error_code != "NoSuchBucket":
                logging.error("Could not verify if the bucket '%s' exists in the region '%s'.", bucket, region)
                raise
            elif error_code == "AccessDenied":
                logging.error(
                    (
                        "Bucket '%s' already exists and is not owned by you. Please provide a different name for the"
                        " bucket in the configuration."
                    ),
                    bucket,
                )
                raise
            return False
        except Exception:
            logging.error("Could not verify if the bucket '%s' exists in the region '%s'.", bucket, region)
            raise

    def s3_artifact_exists(self, artifact_uri) -> bool:
        """
        Uses exact artifact uri to find the artifact on s3. Returns if the artifact is found in S3 else False.

        Parameters
        ----------
            s3_client(boto3.client): S3 client created specific to the region in the gdk config.
            artifact_uri(string): S3 URI to look up for
        """
        bucket_name, object_key = artifact_uri.replace(utils.s3_prefix, "").split("/", 1)
        try:
            response = self.s3_client.head_object(Bucket=bucket_name, Key=object_key)
            return response["ResponseMetadata"]["HTTPStatusCode"] == 200
        except Exception as e:
            logging.error("Could not find the artifact on S3.\n{}".format(e))
            return False

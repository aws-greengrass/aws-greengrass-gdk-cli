from unittest import TestCase
from unittest.mock import call

import boto3
import pytest

from gdk.aws_clients.S3Client import S3Client
from botocore.stub import Stubber


class S3ClientTest(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker):
        self.mocker = mocker
        self.mock_project_config = {}
        self.mock_s3_client = self.mocker.patch("boto3.client", return_value=boto3.client("s3"))
        self.service_clients = {"s3_client": self.mock_s3_client}

        self.client = boto3.client("s3", region_name="region")
        self.mocker.patch("boto3.client", return_value=self.client)
        self.s3_client_stub = Stubber(self.client)
        self.s3_client_stub.activate()

    def test_GIVEN_bucket_does_not_exist_WHEN_create_bucket_THEN_create_us_east_1(self):
        bucket = "test-bucket"
        region = "us-east-1"
        response = {"Location": "us-east-1"}

        mock_valid_bucket_exists = self.mocker.patch.object(S3Client, "valid_bucket_for_artifacts_exists", return_value=False)
        self.s3_client_stub.add_response("create_bucket", response, {"Bucket": "test-bucket"})
        s3_client_utils = S3Client(region)
        s3_client_utils.create_bucket(bucket)
        assert mock_valid_bucket_exists.call_args_list == [call(bucket, region)]
        assert self.s3_client_stub.assert_no_pending_responses

    def test_GIVEN_bucket_does_not_exist_WHEN_create_bucket_THEN_create_non_us_east_1(self):
        bucket = "test-bucket"
        region = "us-west-2"
        response = {"Location": region}
        mock_valid_bucket_exists = self.mocker.patch.object(S3Client, "valid_bucket_for_artifacts_exists", return_value=False)
        s3_client_utils = S3Client(region)
        self.s3_client_stub.add_response(
            "create_bucket",
            response,
            {"Bucket": bucket, "CreateBucketConfiguration": {"LocationConstraint": region}},
        )
        s3_client_utils.create_bucket(bucket)
        assert mock_valid_bucket_exists.call_args_list == [call(bucket, region)]
        assert self.s3_client_stub.assert_no_pending_responses

    def test_GIVEN_bucket_does_not_exist_WHEN_create_bucket_and_exception_THEN_raise_exception(self):
        bucket = "test-bucket"
        region = "region"
        mock_valid_bucket_exists = self.mocker.patch.object(S3Client, "valid_bucket_for_artifacts_exists", return_value=False)
        s3_client_utils = S3Client(region)
        self.s3_client_stub.add_client_error("create_bucket", "some error")
        with pytest.raises(Exception) as e:
            s3_client_utils.create_bucket(bucket)
        assert "An error occurred (some error) when calling the CreateBucket operation:" in e.value.args[0]
        assert mock_valid_bucket_exists.call_args_list == [call("test-bucket", "region")]

    def test_GIVEN_bucket_exists_WHEN_create_bucket_THEN_not_create_bucket(self):
        bucket = "test-bucket"
        region = "region"
        mock_valid_bucket_exists = self.mocker.patch.object(S3Client, "valid_bucket_for_artifacts_exists", return_value=True)
        s3_client_utils = S3Client(region)
        s3_client_utils.create_bucket(bucket)
        assert mock_valid_bucket_exists.call_args_list == [call("test-bucket", "region")]
        assert self.s3_client_stub.assert_no_pending_responses

    def test_GIVEN_bucket_exists_WHEN_check_existence_THEN_return_true_non_us_east_1(self):
        region = "us-west-2"
        s3_client_utils = S3Client(region)

        self.s3_client_stub.add_response("get_bucket_location", {"LocationConstraint": region}, {"Bucket": "bucket"})
        exists = s3_client_utils.valid_bucket_for_artifacts_exists("bucket", region)
        assert exists

    def test_GIVEN_bucket_exists_in_a_region_WHEN_check_existence_in_another_region_THEN_raise_exception(self):
        region = "us-west-2"
        s3_client_utils = S3Client(region)

        self.s3_client_stub.add_response("get_bucket_location", {"LocationConstraint": "us-east-2"}, {"Bucket": "bucket"})
        with pytest.raises(Exception) as e:
            s3_client_utils.valid_bucket_for_artifacts_exists("bucket", region)
        assert (
            "Bucket 'bucket' already exists and is owned by you in another region 'us-east-2'. Please provide a different name"
            " for the bucket in the region 'us-west-2'"
            in e.value.args[0]
        )

    def test_GIVEN_bucket_exists_in_a_region_WHEN_check_existence_and_exception_THEN_raise_exception(self):
        region = "us-west-2"
        s3_client_utils = S3Client(region)

        self.s3_client_stub.add_client_error("get_bucket_location", "some-error")
        with pytest.raises(Exception) as e:
            s3_client_utils.valid_bucket_for_artifacts_exists("bucket", region)
        assert "some-error" in e.value.args[0]
        assert self.s3_client_stub.assert_no_pending_responses

    def test_GIVEN_bucket_owned_by_someone_WHEN_check_existence_THEN_raise_exception(self):
        bucket = "test-bucket"
        region = "region"
        self.s3_client_stub.add_client_error("get_bucket_location", "AccessDenied", {"Bucket": "bucket"})
        s3_client_utils = S3Client("region")

        with pytest.raises(Exception) as e:
            s3_client_utils.valid_bucket_for_artifacts_exists(bucket, region)
        assert "An error occurred (AccessDenied) when calling the GetBucketLocation" in str(e.value.args[0])
        assert self.s3_client_stub.assert_no_pending_responses

    def test_GIVEN_bucket_does_not_exist_WHEN_check_existence_THEN_return_false(self):
        bucket = "test-bucket"
        region = "region"
        self.s3_client_stub.add_client_error("get_bucket_location", "NoSuchBucket", {"Bucket": "bucket"})
        s3_client_utils = S3Client("region")

        assert not s3_client_utils.valid_bucket_for_artifacts_exists(bucket, region)
        assert self.s3_client_stub.assert_no_pending_responses

    def test_WHEN_check_bucket_existence_and_raise_exception_THEN_raise_exception(self):
        bucket = "test-bucket"
        region = "region"
        self.s3_client_stub.add_client_error("get_bucket_location", "400", {"Bucket": "bucket"})
        s3_client_utils = S3Client("region")

        with pytest.raises(Exception) as e:
            s3_client_utils.valid_bucket_for_artifacts_exists(bucket, region)
        assert "An error occurred (400) when calling the GetBucketLocation operation: {'Bucket': 'bucket'}" in e.value.args[0]

    def test_GIVEN_s3_artifact_exists_WHEN_check_for_existence_THEN_return_true(self):
        bucket = "bucket"
        region = "region"
        s3_uri = "s3://bucket/object-key.zip"
        self.s3_client_stub.add_response(
            "head_object",
            {"Metadata": {}, "ResponseMetadata": {"HTTPStatusCode": 200}},
            {"Bucket": bucket, "Key": "object-key.zip"},
        )
        s3_client_utils = S3Client(region)

        assert s3_client_utils.s3_artifact_exists(s3_uri)

    def test_GIVEN_s3_artifact_not_exists_WHEN_check_for_existence_THEN_return_False(self):
        bucket = "test-bucket"
        region = "region"
        s3_uri = "s3://bucket/object-key.zip"
        self.s3_client_stub.add_response(
            "head_object",
            {"Metadata": {}, "ResponseMetadata": {"HTTPStatusCode": 400}},
            {"Bucket": bucket, "Key": "object-key.zip"},
        )
        s3_client_utils = S3Client(region)

        assert not s3_client_utils.s3_artifact_exists(s3_uri)

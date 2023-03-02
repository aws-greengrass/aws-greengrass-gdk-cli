from pathlib import Path
from unittest import TestCase
from unittest.mock import call

import boto3
import pytest
from urllib3.exceptions import HTTPError

from gdk.aws_clients.S3Client import S3Client


class S3ClientTest(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker):
        self.mocker = mocker
        self.mock_project_config = {}
        self.mock_s3_client = self.mocker.patch("boto3.client", return_value=boto3.client("s3"))
        self.service_clients = {"s3_client": self.mock_s3_client}

    def test_create_bucket_us_east_1(self):
        bucket = "test-bucket"
        region = "us-east-1"
        response = {"Buckets": [{"Name": "test-bucket"}]}
        mock_create_bucket = self.mocker.patch("boto3.client.create_bucket", return_value=response)
        s3_client_utils = S3Client(self.mock_project_config, self.service_clients)
        s3_client_utils.create_bucket(bucket, region)
        assert mock_create_bucket.called
        mock_create_bucket.assert_called_with(Bucket="test-bucket")

    def test_create_bucket_non_us_east_1(self):
        bucket = "test-bucket"
        region = "us-west-2"
        response = {"Buckets": [{"Name": "test-bucket"}]}
        mock_create_bucket = self.mocker.patch("boto3.client.create_bucket", return_value=response)
        s3_client_utils = S3Client(self.mock_project_config, self.service_clients)
        s3_client_utils.create_bucket(bucket, region)
        mock_create_bucket.assert_called_with(
            Bucket="test-bucket", CreateBucketConfiguration={"LocationConstraint": "us-west-2"}
        )

    def test_create_bucket_exception(self):
        bucket = "test-bucket"
        region = "region"
        s3_client_utils = S3Client(self.mock_project_config, self.service_clients)
        self.mocker.patch("boto3.client.create_bucket", side_effect=HTTPError("some error"))
        with pytest.raises(Exception) as e:
            s3_client_utils.create_bucket(bucket, region)
        assert type(e.value.args[0]) == HTTPError

    def test_bucket_exists_in_same_region_exists(self):
        s3_client_utils = S3Client({}, self.service_clients)
        mock_get_bucket_location = self.mocker.patch(
            "boto3.client.get_bucket_location", return_value={"LocationConstraint": "us-east-1"}
        )
        exists = s3_client_utils.bucket_exists_in_same_region("bucket", "us-east-1")
        mock_get_bucket_location.assert_called_with(Bucket="bucket")
        assert exists

    def test_bucket_exists_in_same_region_not_exists(self):
        s3_client_utils = S3Client({}, self.service_clients)
        mock_get_bucket_location = self.mocker.patch(
            "boto3.client.get_bucket_location", return_value={"LocationConstraint": "us-west-2"}
        )
        exists = s3_client_utils.bucket_exists_in_same_region("bucket", "us-east-1")
        mock_get_bucket_location.assert_called_with(Bucket="bucket")
        assert not exists

    def test_bucket_exists_in_same_region_exception(self):
        s3_client_utils = S3Client({}, self.service_clients)
        mock_get_bucket_location = self.mocker.patch("boto3.client.get_bucket_location", side_effect=HTTPError("some eror"))
        with pytest.raises(Exception) as e:
            s3_client_utils.bucket_exists_in_same_region("bucket", "us-east-1")
        assert "Unable to fetch the location of the bucket" in e.value.args[0]
        mock_get_bucket_location.assert_called_with(Bucket="bucket")

    def test_create_bucket_exception_bucket_exists(self):
        bucket = "test-bucket"
        region = "region"

        def throw_err(*args, **kwargs):
            ex = boto3.client("s3").exceptions.BucketAlreadyExists(
                {"Error": {"Code": "BucketAlreadyExists", "Message": "fake message"}}, "CreateBucket"
            )
            raise ex

        mock_create_bucket = self.mocker.patch("boto3.client.create_bucket", side_effect=throw_err)
        s3_client_utils = S3Client({}, self.service_clients)

        with pytest.raises(Exception) as e:
            s3_client_utils.create_bucket(bucket, region)
        assert mock_create_bucket.call_count == 1
        assert "An error occurred (BucketAlreadyExists) when calling the CreateBucket operation: fake message" == str(
            e.value.args[0]
        )

    def test_create_bucket_exception_bucket_owned(self):
        bucket = "test-bucket"
        region = "us-west-2"

        def throw_err(*args, **kwargs):
            ex = boto3.client("s3").exceptions.BucketAlreadyOwnedByYou(
                {"Error": {"Code": "BucketAlreadyOwnedByYou", "Message": "fake message"}}, "CreateBucket"
            )
            raise ex

        mock_create_bucket = self.mocker.patch("boto3.client.create_bucket", side_effect=throw_err)
        s3_client_utils = S3Client({}, self.service_clients)

        with pytest.raises(Exception) as e:
            s3_client_utils.create_bucket(bucket, region)
        mock_create_bucket.assert_called_with(
            Bucket="test-bucket", CreateBucketConfiguration={"LocationConstraint": "us-west-2"}
        )
        assert "An error occurred (BucketAlreadyOwnedByYou) when calling the CreateBucket operation: fake message" == str(
            e.value.args[0]
        )

    def test_create_bucket_exception_bucket_owned_not_in_region(self):
        bucket = "test-bucket"
        region = "us-west-2"
        mock_check_in_same_region = self.mocker.patch.object(S3Client, "bucket_exists_in_same_region", return_value=False)

        def throw_err(*args, **kwargs):
            ex = boto3.client("s3").exceptions.BucketAlreadyOwnedByYou(
                {"Error": {"Code": "BucketAlreadyOwnedByYou", "Message": "fake message"}}, "CreateBucket"
            )
            raise ex

        mock_create_bucket = self.mocker.patch("boto3.client.create_bucket", side_effect=throw_err)

        s3_client_utils = S3Client({}, self.service_clients)

        with pytest.raises(Exception) as e:
            s3_client_utils.create_bucket(bucket, region)
        mock_create_bucket.assert_called_with(
            Bucket="test-bucket", CreateBucketConfiguration={"LocationConstraint": "us-west-2"}
        )
        mock_check_in_same_region.assert_called_with("test-bucket", "us-west-2")
        assert "An error occurred (BucketAlreadyOwnedByYou) when calling the CreateBucket operation: fake message" == str(
            e.value.args[0]
        )

    def test_create_bucket_exception_bucket_owned_in_region(self):
        bucket = "test-bucket"
        region = "us-west-2"
        mock_check_in_same_region = self.mocker.patch.object(S3Client, "bucket_exists_in_same_region", return_value=True)

        def throw_err(*args, **kwargs):
            ex = boto3.client("s3").exceptions.BucketAlreadyOwnedByYou(
                {"Error": {"Code": "BucketAlreadyOwnedByYou", "Message": "fake message"}}, "CreateBucket"
            )
            raise ex

        mock_create_bucket = self.mocker.patch("boto3.client.create_bucket", side_effect=throw_err)
        s3_client_utils = S3Client({}, self.service_clients)

        s3_client_utils.create_bucket(bucket, region)
        mock_create_bucket.assert_called_with(
            Bucket="test-bucket", CreateBucketConfiguration={"LocationConstraint": "us-west-2"}
        )
        mock_check_in_same_region.assert_called_with("test-bucket", "us-west-2")

    def test_upload_artifacts(self):
        project_config = {
            "component_name": "test-component",
            "component_version": "1.0.0",
            "bucket": "some-bucket",
            "region": "us-east-1",
            "options": {},
        }
        s3_client_utils = S3Client(project_config, self.service_clients)
        mock_upload_file = self.mocker.patch("boto3.client.upload_file", return_value=None)
        s3_client_utils.upload_artifacts([Path("a.zip"), Path("b.jar"), Path("c.json")])
        assert mock_upload_file.call_count == 3
        assert mock_upload_file.call_args_list == [
            call(
                str(Path("a.zip").resolve()),
                "some-bucket",
                "test-component/1.0.0/a.zip",
                ExtraArgs={},
            ),
            call(
                str(Path("b.jar").resolve()),
                "some-bucket",
                "test-component/1.0.0/b.jar",
                ExtraArgs={},
            ),
            call(
                str(Path("c.json").resolve()),
                "some-bucket",
                "test-component/1.0.0/c.json",
                ExtraArgs={},
            ),
        ]

    def test_upload_artifacts_with_extra_args(self):
        project_config = {
            "component_name": "test-component",
            "component_version": "1.0.0",
            "bucket": "some-bucket",
            "region": "us-east-1",
            "options": {"file_upload_args": {"Metadata": {"key": "value"}}},
        }
        s3_client_utils = S3Client(project_config, self.service_clients)
        mock_upload_file = self.mocker.patch("boto3.client.upload_file", return_value=None)
        s3_client_utils.upload_artifacts([Path("a.zip"), Path("b.jar"), Path("c.json")])
        assert mock_upload_file.call_count == 3
        assert mock_upload_file.call_args_list == [
            call(
                str(Path("a.zip").resolve()),
                "some-bucket",
                "test-component/1.0.0/a.zip",
                ExtraArgs={"Metadata": {"key": "value"}},
            ),
            call(
                str(Path("b.jar").resolve()),
                "some-bucket",
                "test-component/1.0.0/b.jar",
                ExtraArgs={"Metadata": {"key": "value"}},
            ),
            call(
                str(Path("c.json").resolve()),
                "some-bucket",
                "test-component/1.0.0/c.json",
                ExtraArgs={"Metadata": {"key": "value"}},
            ),
        ]

    def test_upload_artifacts_with_exception(self):
        project_config = {
            "component_name": "test-component",
            "component_version": "1.0.0",
            "bucket": "some-bucket",
            "region": "us-east-1",
            "options": {"file_upload_args": {"Metadata": {"key": "value"}}},
        }
        s3_client_utils = S3Client(project_config, self.service_clients)
        mock_upload_file = self.mocker.patch(
            "boto3.client.upload_file", return_value=None, side_effect=HTTPError("some error")
        )

        with pytest.raises(Exception) as e:
            s3_client_utils.upload_artifacts([Path("a.zip"), Path("b.jar"), Path("c.json")])
        assert "some error" in e.value.args[0]
        assert mock_upload_file.called

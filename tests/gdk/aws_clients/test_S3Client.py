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
        mock_valid_bucket_exists = self.mocker.patch.object(S3Client, "valid_bucket_for_artifacts_exists", return_value=False)

        s3_client_utils = S3Client(self.mock_project_config, self.service_clients)
        s3_client_utils.create_bucket(bucket, region)
        assert mock_create_bucket.called
        mock_create_bucket.assert_called_with(Bucket="test-bucket")
        assert mock_valid_bucket_exists.call_args_list == [call(bucket, region)]

    def test_create_bucket_non_us_east_1(self):
        bucket = "test-bucket"
        region = "us-west-2"
        response = {"Buckets": [{"Name": "test-bucket"}]}
        mock_valid_bucket_exists = self.mocker.patch.object(S3Client, "valid_bucket_for_artifacts_exists", return_value=False)
        mock_create_bucket = self.mocker.patch("boto3.client.create_bucket", return_value=response)
        s3_client_utils = S3Client(self.mock_project_config, self.service_clients)
        s3_client_utils.create_bucket(bucket, region)
        mock_create_bucket.assert_called_with(
            Bucket="test-bucket", CreateBucketConfiguration={"LocationConstraint": "us-west-2"}
        )
        assert mock_valid_bucket_exists.call_args_list == [call(bucket, region)]

    def test_create_bucket_exception(self):
        bucket = "test-bucket"
        region = "region"
        mock_valid_bucket_exists = self.mocker.patch.object(S3Client, "valid_bucket_for_artifacts_exists", return_value=False)
        s3_client_utils = S3Client(self.mock_project_config, self.service_clients)
        self.mocker.patch("boto3.client.create_bucket", side_effect=HTTPError("some error"))
        with pytest.raises(Exception) as e:
            s3_client_utils.create_bucket(bucket, region)
        assert "some error" in e.value.args[0]
        assert mock_valid_bucket_exists.call_args_list == [call("test-bucket", "region")]

    def test_create_bucket_valid_bucket_for_artifacts_exists(self):
        bucket = "test-bucket"
        region = "region"
        mock_valid_bucket_exists = self.mocker.patch.object(S3Client, "valid_bucket_for_artifacts_exists", return_value=True)
        mock_create_bucket = self.mocker.patch("boto3.client.create_bucket")
        s3_client_utils = S3Client({}, self.service_clients)
        s3_client_utils.create_bucket(bucket, region)
        assert mock_valid_bucket_exists.call_args_list == [call("test-bucket", "region")]
        assert not mock_create_bucket.called

    def test_create_bucket_valid_bucket_for_artifacts_not_exists(self):
        bucket = "test-bucket"
        region = "region"
        mock_valid_bucket_exists = self.mocker.patch.object(S3Client, "valid_bucket_for_artifacts_exists", return_value=False)
        mock_create_bucket = self.mocker.patch("boto3.client.create_bucket")
        s3_client_utils = S3Client({}, self.service_clients)
        s3_client_utils.create_bucket(bucket, region)
        assert mock_valid_bucket_exists.call_args_list == [call("test-bucket", "region")]
        assert mock_create_bucket.call_args_list == [
            call(Bucket="test-bucket", CreateBucketConfiguration={"LocationConstraint": "region"})
        ]

    def test_create_bucket_exception_in_valid_bucket_for_artifacts_exists(self):
        bucket = "test-bucket"
        region = "region"
        mock_valid_bucket_exists = self.mocker.patch.object(
            S3Client, "valid_bucket_for_artifacts_exists", side_effect=HTTPError("some error")
        )
        s3_client_utils = S3Client({}, self.service_clients)

        with pytest.raises(Exception) as e:
            s3_client_utils.create_bucket(bucket, region)
        assert mock_valid_bucket_exists.call_count == 1
        assert "some error" == str(e.value.args[0])

    def test_valid_bucket_for_artifacts_exists_in_us_east_1(self):
        s3_client_utils = S3Client({}, self.service_clients)
        mock_get_bucket_location = self.mocker.patch(
            "boto3.client.get_bucket_location", return_value={"LocationConstraint": None}
        )
        exists = s3_client_utils.valid_bucket_for_artifacts_exists("bucket", "us-east-1")
        mock_get_bucket_location.assert_called_with(Bucket="bucket")
        assert exists

    def test_valid_bucket_for_artifacts_exists_in_same_region(self):
        s3_client_utils = S3Client({}, self.service_clients)
        mock_get_bucket_location = self.mocker.patch(
            "boto3.client.get_bucket_location", return_value={"LocationConstraint": "us-west-2"}
        )
        exists = s3_client_utils.valid_bucket_for_artifacts_exists("bucket", "us-west-2")
        mock_get_bucket_location.assert_called_with(Bucket="bucket")
        assert exists

    def test_valid_bucket_for_artifacts_exists_in_diff_region_raise_exception(self):
        s3_client_utils = S3Client({}, self.service_clients)
        mock_get_bucket_location = self.mocker.patch(
            "boto3.client.get_bucket_location", return_value={"LocationConstraint": "us-west-2"}
        )
        with pytest.raises(Exception) as e:
            s3_client_utils.valid_bucket_for_artifacts_exists("bucket", "us-east-1")
        mock_get_bucket_location.assert_called_with(Bucket="bucket")
        assert (
            "Bucket 'bucket' already exists and is owned by you in another region 'us-west-2'. Please provide a different name"
            " for the bucket in the region 'us-east-1'"
            in e.value.args[0]
        )

    def test_valid_bucket_for_artifacts_exists_unknown_exception(self):
        s3_client_utils = S3Client({}, self.service_clients)
        mock_get_bucket_location = self.mocker.patch("boto3.client.get_bucket_location", side_effect=HTTPError("some-error"))
        with pytest.raises(Exception) as e:
            s3_client_utils.valid_bucket_for_artifacts_exists("bucket", "us-east-1")
        mock_get_bucket_location.assert_called_with(Bucket="bucket")
        assert "some-error" in e.value.args[0]

    def test_valid_bucket_for_artifacts_exists_owned_by_someone(self):
        bucket = "test-bucket"
        region = "region"

        def throw_err(*args, **kwargs):
            ex = boto3.client("s3").exceptions.ClientError(
                {"Error": {"Code": "403", "Message": "Forbidden"}}, "GetBucketLocation"
            )
            raise ex

        mock_get_bucket_location = self.mocker.patch("boto3.client.get_bucket_location", side_effect=throw_err)
        s3_client_utils = S3Client({}, self.service_clients)

        with pytest.raises(Exception) as e:
            s3_client_utils.valid_bucket_for_artifacts_exists(bucket, region)

        assert mock_get_bucket_location.call_args_list == [call(Bucket=bucket)]
        assert "An error occurred (403) when calling the GetBucketLocation" in str(e.value.args[0])

    def test_valid_bucket_for_artifacts_exists_not_exists(self):
        bucket = "test-bucket"
        region = "region"

        def throw_err(*args, **kwargs):
            ex = boto3.client("s3").exceptions.ClientError(
                {"Error": {"Code": "404", "Message": "Not Found"}}, "GetBucketLocation"
            )
            raise ex

        mock_get_bucket_location = self.mocker.patch("boto3.client.get_bucket_location", side_effect=throw_err)
        s3_client_utils = S3Client({}, self.service_clients)

        assert not s3_client_utils.valid_bucket_for_artifacts_exists(bucket, region)

        assert mock_get_bucket_location.call_args_list == [call(Bucket=bucket)]

    def test_valid_bucket_for_artifacts_exists_bad_request(self):
        bucket = "test-bucket"
        region = "region"

        def throw_err(*args, **kwargs):
            ex = boto3.client("s3").exceptions.ClientError(
                {"Error": {"Code": "400", "Message": "Bad Request"}}, "GetBucketLocation"
            )
            raise ex

        mock_get_bucket_location = self.mocker.patch("boto3.client.get_bucket_location", side_effect=throw_err)
        s3_client_utils = S3Client({}, self.service_clients)

        with pytest.raises(Exception) as e:
            s3_client_utils.valid_bucket_for_artifacts_exists(bucket, region)

        assert mock_get_bucket_location.call_args_list == [call(Bucket=bucket)]
        assert "An error occurred (400) when calling the GetBucketLocation operation: Bad Request" in e.value.args[0]

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

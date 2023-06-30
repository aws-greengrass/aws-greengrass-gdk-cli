from pathlib import Path
from unittest import TestCase
from unittest.mock import call
from gdk.commands.component.transformer.PublishRecipeTransformer import PublishRecipeTransformer

import pytest

from gdk.aws_clients.Greengrassv2Client import Greengrassv2Client
from gdk.aws_clients.S3Client import S3Client
from gdk.commands.component.PublishCommand import PublishCommand
from botocore.stub import Stubber
import boto3


class PublishCommandTest(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker):
        self.mocker = mocker
        self.mock_get_proj_config = self.mocker.patch(
            "gdk.common.configuration.get_configuration",
            return_value=config(),
        )
        self.mock_component_recipe = self.mocker.patch(
            "gdk.commands.component.project_utils.get_recipe_file",
            return_value=Path("some-recipe.json"),
        )
        self.gg_client = boto3.client("greengrassv2", region_name="region")
        self.sts_client = boto3.client("sts", region_name="region")

        def _clients(*args, **kwargs):
            if args[0] == "greengrassv2":
                return self.gg_client
            elif args[0] == "sts":
                return self.sts_client

        self.mocker.patch("boto3.client", side_effect=_clients)
        self.gg_client_stub = Stubber(self.gg_client)
        self.sts_client_stub = Stubber(self.sts_client)
        self.gg_client_stub.activate()
        self.sts_client_stub.activate()
        self.sts_client_stub.add_response("get_caller_identity", {"Account": "123456789012"})

    def test_upload_artifacts_with_no_artifacts(self):
        publish = PublishCommand({})
        publish.service_clients = {"s3_client": self.mocker.patch("boto3.client", return_value=None)}
        publish.s3_client = S3Client("test-region")
        self.mocker.patch("pathlib.Path.iterdir", return_value=[])
        mock_create_bucket = self.mocker.spy(S3Client, "create_bucket")
        publish.upload_artifacts_s3()
        assert not mock_create_bucket.called

    def test_upload_artifacts(self):
        publish = PublishCommand({"bucket": "test-bucket"})
        self.mocker.patch.object(S3Client, "upload_artifact", return_value=None)

        publish.s3_client = S3Client("test-region")
        self.mocker.patch("pathlib.Path.iterdir", return_value=[Path("a.py")])
        mock_create_bucket = self.mocker.patch.object(S3Client, "create_bucket", return_value=None)
        publish.upload_artifacts_s3()
        assert mock_create_bucket.call_args_list == [call("test-bucket")]

    def test_publish_run_not_build(self):
        mock_upload_artifacts_s3 = self.mocker.patch.object(PublishCommand, "upload_artifacts_s3", return_value=None)
        mock_transform = self.mocker.patch.object(PublishRecipeTransformer, "transform")
        mock_dir_exists = self.mocker.patch("gdk.common.utils.dir_exists", return_value=False)
        mock_build = self.mocker.patch("gdk.commands.component.component.build", return_value=None)
        mock_create_gg_component = self.mocker.patch.object(Greengrassv2Client, "create_gg_component", return_value=None)
        publish = PublishCommand(
            {"bucket": None, "region": "us-west-2", "options": '{"file_upload_args":{"Metadata": {"key": "value"}}}'}
        )
        publish.run()
        assert mock_dir_exists.call_count == 1
        assert mock_build.call_count == 1
        assert mock_upload_artifacts_s3.call_count == 1
        assert mock_transform.call_count == 1
        assert mock_create_gg_component.call_count == 1

    def test_publish_run_not_build_command_bucket(self):
        mock_upload_artifacts_s3 = self.mocker.patch.object(PublishCommand, "upload_artifacts_s3", return_value=None)
        mock_transform = self.mocker.patch.object(PublishRecipeTransformer, "transform")
        mock_dir_exists = self.mocker.patch("gdk.common.utils.dir_exists", return_value=False)
        mock_build = self.mocker.patch("gdk.commands.component.component.build", return_value=None)
        mock_create_gg_component = self.mocker.patch.object(Greengrassv2Client, "create_gg_component", return_value=None)
        publish = PublishCommand({"bucket": "exact-bucket", "region": None, "options": None})
        publish.run()
        assert mock_dir_exists.call_count == 1
        assert mock_build.call_count == 1
        assert mock_upload_artifacts_s3.call_count == 1
        assert mock_transform.call_count == 1
        assert mock_create_gg_component.call_count == 1

    def test_publish_run_build(self):
        mock_upload_artifacts_s3 = self.mocker.patch.object(PublishCommand, "upload_artifacts_s3", return_value=None)
        mock_transform = self.mocker.patch.object(PublishRecipeTransformer, "transform")
        mock_dir_exists = self.mocker.patch("gdk.common.utils.dir_exists", return_value=True)
        mock_build = self.mocker.patch("gdk.commands.component.component.build", return_value=None)
        publish = PublishCommand({"bucket": None, "region": None, "options": None})
        mock_create_gg_component = self.mocker.patch.object(Greengrassv2Client, "create_gg_component", return_value=None)
        publish.run()
        assert mock_dir_exists.call_count == 1
        assert not mock_build.called
        assert mock_upload_artifacts_s3.call_count == 1
        assert mock_transform.call_count == 1
        assert mock_create_gg_component.call_count == 1


def config():
    return {
        "component": {
            "com.example.HelloWorld": {
                "author": "<PLACEHOLDER_AUTHOR>",
                "version": "1.0.0",
                "build": {"build_system": "zip"},
                "publish": {"bucket": "default", "region": "region"},
            }
        },
        "gdk_version": "1.0.0",
    }

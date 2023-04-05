from pathlib import Path
from unittest import TestCase
from unittest.mock import call
from gdk.commands.component.recipe_generator.PublishRecipeGenerator import PublishRecipeGenerator

import pytest
from urllib3.exceptions import HTTPError

import gdk.common.exceptions.error_messages as error_messages
from gdk.aws_clients.Greengrassv2Client import Greengrassv2Client
from gdk.aws_clients.S3Client import S3Client
from gdk.commands.component.PublishCommand import PublishCommand


class PublishCommandTest(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker):
        self.mocker = mocker
        self.mock_get_proj_config = self.mocker.patch(
            "gdk.commands.component.project_utils.get_project_config_values",
            return_value=project_config(),
        )

    def test_get_component_version_from_config(self):
        mock_get_next_version = self.mocker.patch.object(PublishCommand, "get_next_version", return_value="")
        publish = PublishCommand({})
        version = publish.get_component_version_from_config()
        assert version == self.mock_get_proj_config.return_value["component_version"]
        assert not mock_get_next_version.called

    def test_get_component_version_from_config_next_patch(self):
        publish = PublishCommand({})
        publish.project_config = {
            "component_name": "component_name",
            "component_version": "NEXT_PATCH",
            "component_author": "abc",
            "bucket": "default",
            "region": "default",
        }
        mock_get_next_version = self.mocker.patch.object(PublishCommand, "get_next_version", return_value="1.0.1")
        version = publish.get_component_version_from_config()
        assert version == mock_get_next_version.return_value
        assert mock_get_next_version.called

    def test_get_component_version_from_config_exception_next_patch(self):
        mock_get_next_version = self.mocker.patch.object(
            PublishCommand, "get_next_version", side_effect=HTTPError("some error")
        )
        publish = PublishCommand({})
        publish.project_config["component_version"] = "NEXT_PATCH"
        publish.project_config["account_number"] = "1234"

        with pytest.raises(Exception) as e:
            publish.get_component_version_from_config()

        assert mock_get_next_version.call_count == 1
        assert e.value.args[0] == "some error"

    def test_get_next_version_component_not_exists(self):

        mock_get_next_patch_component_version = self.mocker.patch.object(
            Greengrassv2Client, "get_highest_component_version_", return_value=None
        )
        publish = PublishCommand({})
        publish.project_config["account_number"] = "1234"
        version = publish.get_next_version()
        assert version == "1.0.0"  # Fallback version
        assert mock_get_next_patch_component_version.call_args_list == [call()]

    def test_get_next_version_component_already_exists(self):
        publish = PublishCommand({})
        mock_get_next_patch_component_version = self.mocker.patch.object(
            Greengrassv2Client, "get_highest_component_version_", return_value="1.0.6"
        )
        publish.project_config["account_number"] = "12345"
        version = publish.get_next_version()
        assert version == "1.0.7"
        assert mock_get_next_patch_component_version.call_count == 1

    def test_client_built_with_correct_region(self):
        self.mocker.patch.object(PublishCommand, "get_account_number", return_value="1234")
        self.mocker.patch.object(PublishCommand, "get_component_version_from_config", return_value=None)
        self.mocker.patch.object(PublishCommand, "upload_artifacts_s3", return_value=None)
        self.mocker.patch.object(PublishRecipeGenerator, "generate")
        self.mocker.patch("gdk.common.utils.dir_exists", return_value=False)
        self.mocker.patch("gdk.commands.component.component.build", return_value=None)
        self.mocker.patch.object(Greengrassv2Client, "create_gg_component", return_value=None)

        publish = PublishCommand({"region": "ca-central-1"})
        publish.run()

        # NOTE: This test is testing implementation details. It should be improved but for now it will
        # give us the confidence that the client is getting created with the correct region
        assert publish.project_config["region"] == "ca-central-1"
        assert publish.service_clients["s3_client"].meta.config.region_name == "ca-central-1"
        assert publish.service_clients["sts_client"].meta.config.region_name == "ca-central-1"
        assert publish.service_clients["greengrass_client"].meta.config.region_name == "ca-central-1"

    def test_get_next_version_component_already_exists_semver(self):
        publish = PublishCommand({})
        publish.project_config["account_number"] = "1234"
        mock_get_next_patch_component_version = self.mocker.patch.object(
            Greengrassv2Client, "get_highest_component_version_", return_value="1.0.6-x-y-z"
        )
        version = publish.get_next_version()
        assert version == "1.0.7"
        assert mock_get_next_patch_component_version.call_count == 1

    def test_get_next_version_component_exception(self):
        publish = PublishCommand({})
        publish.project_config["account_number"] = "1234"
        mock_get_next_patch_component_version = self.mocker.patch.object(
            Greengrassv2Client, "get_highest_component_version_", side_effect=HTTPError("some error")
        )
        with pytest.raises(Exception) as e:
            publish.get_next_version()
        assert mock_get_next_patch_component_version.call_count == 1
        assert e.value.args[0] == "Failed to calculate the next version of the component during publish.\nsome error"

    def test_upload_artifacts_with_no_artifacts(self):
        publish = PublishCommand({})
        publish.project_config = {
            "bucket": "test-bucket",
            "region": "test-region",
            "gg_build_component_artifacts_dir": Path("some-build-dir"),
        }
        publish.service_clients = {"s3_client": self.mocker.patch("boto3.client", return_value=None)}
        publish.s3_client = S3Client(publish.project_config, publish.service_clients)
        self.mocker.patch("pathlib.Path.iterdir", return_value=[])
        mock_create_bucket = self.mocker.spy(S3Client, "create_bucket")
        mock_upload_file = self.mocker.spy(S3Client, "upload_artifacts")
        publish.upload_artifacts_s3()
        assert not mock_create_bucket.called
        assert not mock_upload_file.called

    def test_upload_artifacts(self):
        publish = PublishCommand({})
        publish.project_config = {
            "bucket": "test-bucket",
            "region": "test-region",
            "gg_build_component_artifacts_dir": Path("some-build-dir"),
        }
        publish.service_clients = {"s3_client": self.mocker.patch("boto3.client", return_value=None)}
        publish.s3_client = S3Client(publish.project_config, publish.service_clients)
        self.mocker.patch("pathlib.Path.iterdir", return_value=[Path("a.py")])
        mock_create_bucket = self.mocker.patch.object(S3Client, "create_bucket", return_value=None)
        mock_upload_file = self.mocker.patch.object(S3Client, "upload_artifacts", return_value=None)
        publish.upload_artifacts_s3()
        assert mock_create_bucket.call_args_list == [call("test-bucket", "test-region")]
        assert mock_upload_file.call_args_list == [call([Path("a.py")])]

    def test_publish_run_not_build(self):
        mock_get_account_num = self.mocker.patch.object(PublishCommand, "get_account_number", return_value="1234")
        mock_get_component_version_from_config = self.mocker.patch.object(
            PublishCommand, "get_component_version_from_config", return_value=None
        )
        mock_upload_artifacts_s3 = self.mocker.patch.object(PublishCommand, "upload_artifacts_s3", return_value=None)
        mock_generate = self.mocker.patch.object(PublishRecipeGenerator, "generate")
        mock_dir_exists = self.mocker.patch("gdk.common.utils.dir_exists", return_value=False)
        mock_build = self.mocker.patch("gdk.commands.component.component.build", return_value=None)
        mock_create_gg_component = self.mocker.patch.object(Greengrassv2Client, "create_gg_component", return_value=None)
        publish = PublishCommand(
            {"bucket": None, "region": "us-west-2", "options": '{"file_upload_args":{"Metadata": {"key": "value"}}}'}
        )
        publish.run()
        assert publish.project_config["account_number"] == "1234"
        assert publish.project_config["bucket"] == "default-us-west-2-1234"
        assert publish.project_config["options"] == {"file_upload_args": {"Metadata": {"key": "value"}}}
        assert mock_dir_exists.call_count == 1
        assert mock_build.call_count == 1
        assert mock_get_account_num.call_count == 1
        assert mock_get_component_version_from_config.call_count == 1
        assert mock_upload_artifacts_s3.call_count == 1
        assert mock_generate.call_count == 1
        assert mock_create_gg_component.call_count == 1

    def test_publish_run_not_build_command_bucket(self):
        mock_get_account_num = self.mocker.patch.object(PublishCommand, "get_account_number", return_value="1234")
        mock_get_component_version_from_config = self.mocker.patch.object(
            PublishCommand, "get_component_version_from_config", return_value=None
        )
        mock_upload_artifacts_s3 = self.mocker.patch.object(PublishCommand, "upload_artifacts_s3", return_value=None)
        mock_generate = self.mocker.patch.object(PublishRecipeGenerator, "generate")
        mock_dir_exists = self.mocker.patch("gdk.common.utils.dir_exists", return_value=False)
        mock_build = self.mocker.patch("gdk.commands.component.component.build", return_value=None)
        mock_create_gg_component = self.mocker.patch.object(Greengrassv2Client, "create_gg_component", return_value=None)
        publish = PublishCommand({"bucket": "exact-bucket", "region": None, "options": None})
        publish.run()
        assert publish.project_config["account_number"] == "1234"
        assert publish.project_config["bucket"] == "exact-bucket"
        assert mock_dir_exists.call_count == 1
        assert mock_build.call_count == 1
        assert mock_get_account_num.call_count == 1
        assert mock_get_component_version_from_config.call_count == 1
        assert mock_upload_artifacts_s3.call_count == 1
        assert mock_generate.call_count == 1
        assert mock_create_gg_component.call_count == 1

    def test_publish_run_build(self):
        mock_get_account_num = self.mocker.patch.object(PublishCommand, "get_account_number", return_value="1234")
        mock_get_component_version_from_config = self.mocker.patch.object(
            PublishCommand, "get_component_version_from_config", return_value=None
        )
        mock_upload_artifacts_s3 = self.mocker.patch.object(PublishCommand, "upload_artifacts_s3", return_value=None)
        mock_generate = self.mocker.patch.object(PublishRecipeGenerator, "generate")
        mock_dir_exists = self.mocker.patch("gdk.common.utils.dir_exists", return_value=True)
        mock_build = self.mocker.patch("gdk.commands.component.component.build", return_value=None)
        publish = PublishCommand({"bucket": None, "region": None, "options": None})
        publish.project_config["bucket"] = "default"
        mock_create_gg_component = self.mocker.patch.object(Greengrassv2Client, "create_gg_component", return_value=None)
        publish.run()
        assert publish.project_config["account_number"] == "1234"
        assert publish.project_config["bucket"] == "default-us-east-1-1234"
        assert mock_dir_exists.call_count == 1
        assert not mock_build.called
        assert mock_get_account_num.call_count == 1
        assert mock_get_component_version_from_config.call_count == 1
        assert mock_upload_artifacts_s3.call_count == 1
        assert mock_generate.call_count == 1
        assert mock_create_gg_component.call_count == 1

    def test_publish_run_exception(self):
        mock_get_account_num = self.mocker.patch.object(PublishCommand, "get_account_number", return_value="1234")
        mock_get_component_version_from_config = self.mocker.patch.object(
            PublishCommand,
            "get_component_version_from_config",
            return_value=None,
            side_effect=HTTPError("some error"),
        )
        mock_project_built = self.mocker.patch.object(PublishCommand, "try_build", return_value=None)
        publish = PublishCommand({"bucket": None, "region": None, "options": None})
        publish.project_config["bucket"] = "default"
        with pytest.raises(Exception) as e:
            publish.run()
        assert mock_project_built.call_count == 1
        assert publish.project_config["account_number"] == "1234"
        assert publish.project_config["bucket"] == "default-us-east-1-1234"
        assert e.value.args[0] == "{}\n{}".format(error_messages.PUBLISH_FAILED, "some error")
        assert mock_get_account_num.call_count == 1
        assert mock_get_component_version_from_config.call_count == 1

    def test_get_account_number_exception(self):
        mock_client = self.mocker.patch("boto3.client", return_value=None)
        publish = PublishCommand({})
        publish.service_clients = {"sts_client": mock_client}
        mock_get_caller_identity = self.mocker.patch("boto3.client.get_caller_identity", return_value=None)
        with pytest.raises(Exception) as e:
            publish.get_account_number()
        assert mock_get_caller_identity.call_count == 1
        assert "Error while fetching account number from credentials." in e.value.args[0]

    def test_get_account_number(self):
        mock_client = self.mocker.patch("boto3.client", return_value=None)
        publish = PublishCommand({})
        publish.service_clients = {"sts_client": mock_client}
        mock_get_caller_identity = self.mocker.patch("boto3.client.get_caller_identity", return_value={"Account": 124})
        num = publish.get_account_number()
        assert mock_get_caller_identity.call_count == 1
        assert num == 124


def project_config():
    return {
        "component_name": "component_name",
        "component_build_config": {"build_system": "zip"},
        "component_version": "1.0.0",
        "component_author": "abc",
        "bucket": "default",
        "region": "us-east-1",
        "options": {},
        "gg_build_directory": Path("/src/GDK-CLI-Internal/greengrass-build"),
        "gg_build_artifacts_dir": Path("/src/GDK-CLI-Internal/greengrass-build/artifacts"),
        "gg_build_recipes_dir": Path("/src/GDK-CLI-Internal/greengrass-build/recipes"),
        "gg_build_component_artifacts_dir": Path("/src/GDK-CLI-Internal/greengrass-build/artifacts/component_name/1.0.0"),
        "component_recipe_file": Path("/src/GDK-CLI-Internal/tests/gdk/static/build_command/valid_component_recipe.json"),
    }

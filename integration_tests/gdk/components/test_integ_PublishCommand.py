from pathlib import Path

import boto3
import pytest
from gdk.commands.component.PublishCommand import PublishCommand
import datetime

from unittest import TestCase
import os
import shutil
from gdk.common.CaseInsensitive import CaseInsensitiveRecipeFile
from botocore.stub import Stubber, ANY

from unittest.mock import Mock


class ComponentPublishCommandIntegTest(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker, tmpdir):
        self.mocker = mocker
        self.tmpdir = Path(tmpdir).resolve()
        self.c_dir = Path(".").resolve()
        self.stub_aws_clients()
        os.chdir(self.tmpdir)
        yield
        os.chdir(self.c_dir)

    def stub_aws_clients(self):
        self.sts_client = boto3.client("sts", region_name="us-east-1")
        self.gg_client = boto3.client("greengrassv2", region_name="us-east-1")
        self.s3_client = boto3.client("s3", region_name="us-east-1")

        def _clients(*args, **kwargs):
            if args[0] == "greengrassv2":
                return self.gg_client
            elif args[0] == "sts":
                return self.sts_client
            elif args[0] == "s3":
                return self.s3_client

        self.mocker.patch("boto3.client", _clients)

        self.gg_client_stub = Stubber(self.gg_client)
        self.sts_client_stub = Stubber(self.sts_client)

        self.gg_client_stub.activate()
        self.sts_client_stub.activate()
        self.gg_client_stub.add_response(
            "list_component_versions",
            {
                "componentVersions": [],
                "nextToken": "string",
            },
        )
        boto3_ses = Mock()
        boto3_ses.get_partition_for_region.return_value = "aws"
        self.mocker.patch("boto3.Session", return_value=boto3_ses)

    def test_GIVEN_no_artifacts_and_NEXT_PATCH_WHEN_publish_THEN_create_a_component_with_recipe(self):
        self.zip_test_data()
        account_num = "123456789012"
        self.sts_client_stub.add_response("get_caller_identity", {"Account": account_num}, {})
        self.gg_client_stub.add_response(
            "list_component_versions",
            {
                "componentVersions": [
                    {
                        "componentName": "abc",
                        "componentVersion": "1.1.1",
                        "arn": f"arn:aws:greengrass:us-east-1:{account_num}:components:abc",
                    },
                ],
                "nextToken": "string",
            },
            {"arn": f"arn:aws:greengrass:us-east-1:{account_num}:components:abc"},
        )

        self.gg_client_stub.add_response(
            "create_component_version",
            {
                "componentName": "abc",
                "componentVersion": "1.1.2",
                "creationTimestamp": datetime.datetime.now(),
                "status": {},
            },
            {"inlineRecipe": ANY},
        )

        pc = PublishCommand({})
        pc.run()
        self.gg_client_stub.assert_no_pending_responses()
        self.sts_client_stub.assert_no_pending_responses()
        assert self.tmpdir.joinpath("greengrass-build/recipes/abc-1.1.2.yaml").exists()

    def test_GIVEN_build_artifacts_WHEN_publish_with_args_THEN_upload_artifacts_and_create_a_component(self):
        self.zip_test_data()
        self.tmpdir.joinpath("greengrass-build/artifacts/abc/2.0.0/").mkdir(parents=True, exist_ok=True)
        self.tmpdir.joinpath("greengrass-build/artifacts/abc/2.0.0/hello_world.py").touch()
        self.mocker.patch(
            "gdk.common.configuration.get_configuration",
            return_value={
                "component": {
                    "abc": {
                        "author": "author",
                        "version": "2.0.0",
                        "build": {"build_system": "zip"},
                        "publish": {"bucket": "default", "region": "us-west-2"},
                    }
                }
            },
        )
        self.tmpdir.joinpath("greengrass-build/artifacts/abc/NEXT_PATCH/somefile").touch()
        account_num = "123456789012"
        self.sts_client_stub.add_response("get_caller_identity", {"Account": account_num}, {})
        self.mocker.patch.object(self.s3_client, "get_bucket_location", return_value={"LocationConstraint": "us-east-2"})
        mock_upload_file = self.mocker.patch.object(self.s3_client, "upload_file", return_value=None)

        self.gg_client_stub.add_response(
            "create_component_version",
            {
                "componentName": "abc",
                "componentVersion": "2.0.0",
                "creationTimestamp": datetime.datetime.now(),
                "status": {},
            },
            {"inlineRecipe": ANY},
        )

        pc = PublishCommand({"region": "us-east-2", "bucket": "some-bucket", "options": '{"file_upload_args":{"ACL":"ABC"}}'})
        pc.run()
        self.gg_client_stub.assert_no_pending_responses()
        self.sts_client_stub.assert_no_pending_responses()
        assert self.tmpdir.joinpath("greengrass-build/recipes/abc-2.0.0.yaml").exists()
        mock_upload_file.assert_called_with(
            str(self.tmpdir.joinpath("greengrass-build/artifacts/abc/2.0.0/hello_world.py").resolve()),
            "some-bucket",
            "abc/2.0.0/hello_world.py",
            ExtraArgs={"ACL": "ABC"},
        )

    def test_GIVEN_component_does_not_exist_WHEN_publish_with_NEXT_PATCH_THEN_create_1_0_0_component(self):
        self.zip_test_data()
        account_num = "123456789012"
        self.mocker.patch(
            "gdk.common.configuration.get_configuration",
            return_value={
                "component": {
                    "abc": {
                        "author": "author",
                        "version": "NEXT_PATCH",
                        "build": {"build_system": "zip"},
                        "publish": {"bucket": "default", "region": "us-east-1"},
                    }
                }
            },
        )
        self.sts_client_stub.add_response("get_caller_identity", {"Account": account_num}, {})
        self.gg_client_stub.add_response(
            "list_component_versions",
            {
                "componentVersions": [],
                "nextToken": "string",
            },
            {"arn": f"arn:aws:greengrass:us-east-1:{account_num}:components:abc"},
        )

        self.gg_client_stub.add_response(
            "create_component_version",
            {
                "componentName": "abc",
                "componentVersion": "1.0.0",
                "creationTimestamp": datetime.datetime.now(),
                "status": {},
            },
            {"inlineRecipe": ANY},
        )

        pc = PublishCommand({})
        pc.run()
        self.gg_client_stub.assert_no_pending_responses()
        self.sts_client_stub.assert_no_pending_responses()
        assert self.tmpdir.joinpath("greengrass-build/recipes/abc-1.0.0.yaml").exists()

    def test_GIVEN_artifacts_WHEN_exc_while_fetching_creds_during_publish_THEN_component_is_not_created(self):
        self.zip_test_data()
        self.mocker.patch(
            "gdk.common.configuration.get_configuration",
            return_value={
                "component": {
                    "abc": {
                        "author": "author",
                        "version": "NEXT_PATCH",
                        "build": {"build_system": "zip"},
                        "publish": {"bucket": "default", "region": "us-east-1"},
                    }
                }
            },
        )
        self.sts_client_stub.add_client_error("get_caller_identity", service_error_code="InvalidClientTokenId")

        with pytest.raises(Exception) as e:
            pc = PublishCommand({})
            pc.run()
        assert "InvalidClientTokenId" in str(e)
        self.sts_client_stub.assert_no_pending_responses()
        assert len(list(self.tmpdir.joinpath("greengrass-build/recipes/").iterdir())) == 1

    def test_GIVEN_artifacts_WHEN_exc_while_getting_component_version_during_publish_THEN_component_is_not_created(self):
        self.zip_test_data()
        self.mocker.patch(
            "gdk.common.configuration.get_configuration",
            return_value={
                "component": {
                    "abc": {
                        "author": "author",
                        "version": "NEXT_PATCH",
                        "build": {"build_system": "zip"},
                        "publish": {"bucket": "default", "region": "us-east-1"},
                    }
                }
            },
        )
        self.sts_client_stub.add_response("get_caller_identity", {"Account": "1234"}, {})
        self.gg_client_stub.add_client_error("list_component_versions", service_error_code="AccessDeniedException")
        with pytest.raises(Exception) as e:
            pc = PublishCommand({})
            pc.run()
        assert "AccessDeniedException" in str(e)
        self.sts_client_stub.assert_no_pending_responses()
        self.gg_client_stub.assert_no_pending_responses()
        assert len(list(self.tmpdir.joinpath("greengrass-build/recipes/").iterdir())) == 1

    def test_GIVEN_built_artifacts_WHEN_publish_with_invalid_options_file_THEN_raise_exception(self):
        self.zip_test_data()
        with open(self.tmpdir.joinpath("options.json"), "w") as f:
            f.write('{"file_upload_args:{"missing":"quote"}}')

        self.tmpdir.joinpath("greengrass-build/artifacts/abc/2.0.0/").mkdir(parents=True, exist_ok=True)
        self.tmpdir.joinpath("greengrass-build/artifacts/abc/2.0.0/hello_world.py").touch()
        self.mocker.patch(
            "gdk.common.configuration.get_configuration",
            return_value={
                "component": {
                    "abc": {
                        "author": "author",
                        "version": "2.0.0",
                        "build": {"build_system": "zip"},
                        "publish": {"bucket": "default", "region": "us-west-2"},
                    }
                }
            },
        )
        self.tmpdir.joinpath("greengrass-build/artifacts/abc/NEXT_PATCH/somefile").touch()
        with pytest.raises(Exception) as e:
            PublishCommand({"options": str(self.tmpdir.joinpath("options.json").resolve())})
        assert "JSON string is incorrectly formatted." in e.value.args[0]

    def test_GIVEN_built_artifacts_WHEN_publish_with_oversized_recipe_THEN_raise_exception(self):
        self.zip_test_data_oversized_recipe()

        self.tmpdir.joinpath("greengrass-build/artifacts/abc/2.0.0/").mkdir(parents=True, exist_ok=True)
        self.tmpdir.joinpath("greengrass-build/artifacts/abc/2.0.0/hello_world.py").touch()
        self.mocker.patch(
            "gdk.common.configuration.get_configuration",
            return_value={
                "component": {
                    "abc": {
                        "author": "author",
                        "version": "2.0.0",
                        "build": {"build_system": "zip"},
                        "publish": {"bucket": "default", "region": "us-west-2"},
                    }
                }
            },
        )
        self.tmpdir.joinpath("greengrass-build/artifacts/abc/NEXT_PATCH/somefile").touch()
        account_num = "123456789012"
        self.sts_client_stub.add_response("get_caller_identity", {"Account": account_num}, {})
        self.mocker.patch.object(self.s3_client, "get_bucket_location", return_value={"LocationConstraint": "us-west-2"})
        self.mocker.patch.object(self.s3_client, "upload_file", return_value=None)

        with pytest.raises(Exception) as e:
            pc = PublishCommand({})
            pc.run()
        assert "Component recipes must be 16 kB or smaller. Reduce the size of the recipe and re-build." in str(e)

    def zip_test_data(self):
        shutil.copy(
            self.c_dir.joinpath("integration_tests/test_data/config/config.json"), self.tmpdir.joinpath("gdk-config.json")
        )

        shutil.copy(
            self.c_dir.joinpath("integration_tests/test_data/recipes/build_recipe.yaml"),
            self.tmpdir.joinpath("recipe.yaml"),
        )

        content = CaseInsensitiveRecipeFile().read(self.tmpdir.joinpath("recipe.yaml"))
        content.update_value("componentName", "abc")
        CaseInsensitiveRecipeFile().write(self.tmpdir.joinpath("recipe.yaml"), content)

        self.tmpdir.joinpath("greengrass-build/artifacts/abc/NEXT_PATCH/").mkdir(parents=True, exist_ok=True)
        self.tmpdir.joinpath("greengrass-build/recipes/").mkdir(parents=True, exist_ok=True)
        shutil.copy(
            self.tmpdir.joinpath("recipe.yaml"),
            self.tmpdir.joinpath("greengrass-build/recipes/recipe.yaml"),
        )

    def zip_test_data_oversized_recipe(self):
        shutil.copy(
            self.c_dir.joinpath("integration_tests/test_data/config/config.json"), self.tmpdir.joinpath("gdk-config.json")
        )

        shutil.copy(
            self.c_dir.joinpath("integration_tests/test_data/recipes/build_recipe_really_big.yaml"),
            self.tmpdir.joinpath("recipe.yaml"),
        )

        content = CaseInsensitiveRecipeFile().read(self.tmpdir.joinpath("recipe.yaml"))
        content.update_value("componentName", "abc")
        CaseInsensitiveRecipeFile().write(self.tmpdir.joinpath("recipe.yaml"), content)

        self.tmpdir.joinpath("greengrass-build/artifacts/abc/NEXT_PATCH/").mkdir(parents=True, exist_ok=True)
        self.tmpdir.joinpath("greengrass-build/recipes/").mkdir(parents=True, exist_ok=True)
        shutil.copy(
            self.tmpdir.joinpath("recipe.yaml"),
            self.tmpdir.joinpath("greengrass-build/recipes/recipe.yaml"),
        )

from pathlib import Path
from unittest import TestCase
from unittest.mock import patch, mock_open, Mock
import pytest


from gdk.commands.component.config.ComponentPublishConfiguration import ComponentPublishConfiguration
import boto3
from botocore.stub import Stubber
from gdk.common.config.GDKProject import GDKProject


class ComponentPublishConfigurationTest(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker):
        self.mocker = mocker
        self.mock_get_proj_config = self.mocker.patch(
            "gdk.common.configuration.get_configuration",
            return_value=config(),
        )
        self.mocker.patch.object(GDKProject, "_get_recipe_file", return_value=Path(".").joinpath("recipe.json").resolve())

        self.gg_client = boto3.client("greengrassv2", region_name="region")
        self.sts_client = boto3.client("sts")

        def _clients(*args, **kwargs):
            if args[0] == "greengrassv2":
                return self.gg_client
            elif args[0] == "sts":
                return self.sts_client

        self.client = self.mocker.patch("boto3.client", side_effect=_clients)
        self.gg_client_stub = Stubber(self.gg_client)
        self.sts_client_stub = Stubber(self.sts_client)
        self.gg_client_stub.activate()
        self.sts_client_stub.activate()
        self.sts_client_stub.add_response("get_caller_identity", {"Account": "123456789012"})
        boto3_ses = Mock()
        boto3_ses.get_partition_for_region.return_value = "aws"
        self.mocker.patch("boto3.Session", return_value=boto3_ses)

    def test_GIVEN_config_with_no_arguments_WHEN_read_publish_config_THEN_read_from_config(self):
        self.gg_client_stub.add_response(
            "list_component_versions",
            {"componentVersions": []},
        )
        pconfig = ComponentPublishConfiguration({})
        assert pconfig.publisher == "author"
        assert pconfig.component_version == "1.0.0"
        assert pconfig.bucket == "default-us-east-1-123456789012"

    def test_GIVEN_NEXT_PATCH_for_version_with_no_previous_versions_WHEN_get_next_version_THEN_get_fallback_version(self):
        conf = config()
        conf["component"]["com.example.HelloWorld"]["version"] = "NEXT_PATCH"
        self.mock_get_proj_config = self.mocker.patch(
            "gdk.common.configuration.get_configuration",
            return_value=conf,
        )
        response = {"componentVersions": []}
        self.gg_client_stub.add_response("list_component_versions", response)
        self.gg_client_stub.add_response("list_component_versions", response)
        pconfig = ComponentPublishConfiguration({})
        assert pconfig.publisher == "author"
        assert pconfig.component_version == "1.0.0"
        assert pconfig.bucket == "default-us-east-1-123456789012"

    def test_GIVEN_NEXT_PATCH_for_version_with_previous_versions_WHEN_get_version_THEN_calculate_next_version(self):
        conf = config()
        conf["component"]["com.example.HelloWorld"]["version"] = "NEXT_PATCH"
        self.mock_get_proj_config = self.mocker.patch(
            "gdk.common.configuration.get_configuration",
            return_value=conf,
        )
        response = {"componentVersions": [{"componentVersion": "1.0.4"}, {"componentVersion": "1.0.1"}]}
        self.gg_client_stub.add_response("list_component_versions", response)
        self.gg_client_stub.add_response("list_component_versions", response)
        pconfig = ComponentPublishConfiguration({})
        assert pconfig.publisher == "author"
        assert pconfig.component_version == "1.0.5"
        assert pconfig.bucket == "default-us-east-1-123456789012"

    def test_GIVEN_config_with_bucket_args_WHEN_get_bucket_THEN_get_bucket_from_args(self):
        self.gg_client_stub.add_response(
            "list_component_versions",
            {"componentVersions": []},
        )
        pconfig = ComponentPublishConfiguration({"bucket": "my-bucket"})
        assert pconfig.publisher == "author"
        assert pconfig.component_version == "1.0.0"
        assert pconfig.bucket == "my-bucket"

    def test_GIVEN_config_with_region_args_WHEN_get_region_THEN_get_region_from_args(self):
        self.gg_client_stub.add_response(
            "list_component_versions",
            {"componentVersions": []},
        )
        pconfig = ComponentPublishConfiguration({"region": "us-east-1"})
        assert pconfig.publisher == "author"
        assert pconfig.component_version == "1.0.0"
        assert pconfig.bucket == "default-us-east-1-123456789012"

    def test_GIVEN_config_with_options_args_WHEN_get_options_THEN_get_options_from_args(self):
        opts = '{"metadata": "test"}'
        self.gg_client_stub.add_response(
            "list_component_versions",
            {"componentVersions": []},
        )
        pconfig = ComponentPublishConfiguration({"options": opts})
        assert pconfig.publisher == "author"
        assert pconfig.component_version == "1.0.0"
        assert pconfig.bucket == "default-us-east-1-123456789012"
        assert pconfig.options == {"metadata": "test"}

    def test_GIVEN_config_with_invalid_options_args_WHEN_get_options_THEN_raise_exception(self):
        opts = '{"metadata: "test"}'
        self.gg_client_stub.add_response(
            "list_component_versions",
            {"componentVersions": []},
        )
        with pytest.raises(Exception) as e:
            pconfig = ComponentPublishConfiguration({"options": opts})
            assert pconfig.publisher == "author"
            assert pconfig.component_version == "1.0.0"
            assert pconfig.bucket == "default-us-east-1-123456789012"
            assert pconfig.options == {"metadata": "test"}
        assert "JSON string is incorrectly formatted." in e.value.args[0]

    def test_GIVEN_config_with_file_options_args_and_path_not_exists_WHEN_get_options_THEN_raise_exception(self):
        opts = "file_does_not_exist.json"
        self.gg_client_stub.add_response(
            "list_component_versions",
            {"componentVersions": []},
        )
        with pytest.raises(Exception) as e:
            pconfig = ComponentPublishConfiguration({"options": opts})
            assert pconfig.publisher == "author"
            assert pconfig.component_version == "1.0.0"
            assert pconfig.bucket == "default-us-east-1-123456789012"
        assert "JSON file path provided in the command does not exist. Please provide a valid JSON file." in e.value.args[0]

    def test_GIVEN_config_with_file_options_args_WHEN_get_options_THEN_read_opts_from_file(self):
        opts = "some_file.json"
        valid_json_string = '{"metadata": "test"}'
        self.mocker.patch("pathlib.Path.is_file", return_value=True)
        self.gg_client_stub.add_response(
            "list_component_versions",
            {"componentVersions": []},
        )
        with patch("builtins.open", mock_open(read_data=valid_json_string)):
            pconfig = ComponentPublishConfiguration({"options": opts})
            assert pconfig.publisher == "author"
            assert pconfig.component_version == "1.0.0"
            assert pconfig.bucket == "default-us-east-1-123456789012"
            assert pconfig.options == {"metadata": "test"}

    def test_GIVEN_config_with_invalid_file_options_args_WHEN_get_options_THEN_raise_exception(self):
        opts = "some_file.json"
        invalid_json_string = "invalid_json"
        self.mocker.patch("pathlib.Path.is_file", return_value=True)
        self.gg_client_stub.add_response(
            "list_component_versions",
            {"componentVersions": []},
        )
        with patch("builtins.open", mock_open(read_data=invalid_json_string)):
            with pytest.raises(Exception) as e:
                ComponentPublishConfiguration({"options": opts})
        assert "JSON string is incorrectly formatted." in e.value.args[0]

    def test_GIVEN_config_with_no_region_WHEN_get_config_THEN_raise_exception(self):
        conf = config()
        conf["component"]["com.example.HelloWorld"]["publish"]["region"] = ""
        self.mock_get_proj_config = self.mocker.patch(
            "gdk.common.configuration.get_configuration",
            return_value=conf,
        )
        with pytest.raises(Exception) as e:
            ComponentPublishConfiguration({})
        assert "Region cannot be empty. Please provide a valid region." in str(e)


def config():
    return {
        "component": {
            "com.example.HelloWorld": {
                "author": "author",
                "version": "1.0.0",
                "build": {"build_system": "zip"},
                "publish": {"bucket": "default", "region": "us-east-1"},
            }
        },
        "gdk_version": "1.0.0",
    }

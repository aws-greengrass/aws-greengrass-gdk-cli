from pathlib import Path
from unittest import TestCase, mock
from unittest.mock import call

import pytest

from gdk.aws_clients.Greengrassv2Client import Greengrassv2Client
from botocore.stub import Stubber
import boto3


class Greengrassv2ClientTest(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker):
        self.mocker = mocker
        self.project_config = {
            "account_number": "1234",
            "component_name": "c_name",
            "region": "test-region",
            "publish_recipe_file": Path("some-recipe.yaml"),
            "component_version": "1.0.0",
        }
        self.client = boto3.client("greengrassv2", region_name="region")
        self.mocker.patch("boto3.client", return_value=self.client)
        self.mock_ggv2_client = Stubber(self.client)
        self.mock_ggv2_client.activate()

    def test_get_next_patch_component_version(self):
        response = {"componentVersions": [{"componentVersion": "1.0.4"}, {"componentVersion": "1.0.1"}]}
        ggv2 = Greengrassv2Client("region")
        c_arn = "arn:aws:greengrass:test-region:1234:components:c_name"
        self.mock_ggv2_client.add_response("list_component_versions", response, {"arn": c_arn})

        highest_component_version = ggv2.get_highest_cloud_component_version(c_arn)
        assert highest_component_version == "1.0.4"

    def test_get_next_patch_component_version_no_components(self):
        ggv2 = Greengrassv2Client("region")
        c_arn = "arn:aws:greengrass:test-region:1234:components:c_name"
        self.mock_ggv2_client.add_response("list_component_versions", {"componentVersions": []}, {"arn": c_arn})

        highest_component_version = ggv2.get_highest_cloud_component_version(c_arn)
        assert highest_component_version is None

    def test_get_next_patch_component_version_exception(self):
        ggv2 = Greengrassv2Client("_region")
        c_arn = "arn:aws:greengrass:test-region:1234:components:c_name"
        self.mock_ggv2_client.add_client_error("list_component_versions", service_error_code="500")
        with pytest.raises(Exception) as e:
            ggv2.get_highest_cloud_component_version(c_arn)
        assert "An error occurred (500) when calling the ListComponentVersions operation" in e.value.args[0]

    def test_create_gg_component(self):
        ggv2 = Greengrassv2Client("region")
        response = {
            "componentName": "some",
            "componentVersion": "1.0.0",
            "creationTimestamp": "2023-10-10",
            "status": {"componentState": "DEPLOYABLE"},
        }
        self.mock_ggv2_client.add_response("create_component_version", response, {"inlineRecipe": "some-recipe-content"})

        with mock.patch("builtins.open", mock.mock_open(read_data="some-recipe-content")) as mock_file:
            ggv2.create_gg_component(Path("some-recipe.yaml"))
            assert mock_file.call_args_list == [call(Path("some-recipe.yaml"), "r", encoding="utf-8")]

        self.mock_ggv2_client.assert_no_pending_responses()

    def test_create_gg_component_exception(self):
        greengrass_client = Greengrassv2Client("region")
        self.mock_ggv2_client.add_client_error("create_component_version", service_error_code="400")

        with mock.patch("builtins.open", mock.mock_open(read_data="some-recipe-content")):
            with pytest.raises(Exception) as e:
                greengrass_client.create_gg_component(Path("some-recipe.yaml"))
            assert "An error occurred (400) when calling the CreateComponentVersion operation" in e.value.args[0]

        self.mock_ggv2_client.assert_no_pending_responses()

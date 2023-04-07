from pathlib import Path
from unittest import TestCase, mock
from unittest.mock import call

import pytest
from urllib3.exceptions import HTTPError

from gdk.aws_clients.Greengrassv2Client import Greengrassv2Client


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
        self.mock_ggv2_client = self.mocker.patch("boto3.client", return_value=None)
        self.service_clients = {"greengrass_client": self.mock_ggv2_client}

    def test_get_next_patch_component_version(self):
        greengrass_client = Greengrassv2Client(self.project_config, self.service_clients)
        response = {"componentVersions": [{"componentVersion": "1.0.4"}, {"componentVersion": "1.0.1"}]}
        mock_get_next_patch_component_version = self.mocker.patch(
            "boto3.client.list_component_versions", return_value=response
        )
        c_arn = "arn:aws:greengrass:test-region:1234:components:c_name"
        highest_component_version = greengrass_client.get_highest_component_version_()
        assert mock_get_next_patch_component_version.call_args_list == [call(arn=c_arn)]
        assert highest_component_version == "1.0.4"

    def test_get_next_patch_component_version_no_components(self):
        greengrass_client = Greengrassv2Client(self.project_config, self.service_clients)
        mock_get_next_patch_component_version = self.mocker.patch(
            "boto3.client.list_component_versions", return_value={"componentVersions": []}
        )
        c_arn = "arn:aws:greengrass:test-region:1234:components:c_name"
        highest_component_version = greengrass_client.get_highest_component_version_()
        assert mock_get_next_patch_component_version.call_args_list == [call(arn=c_arn)]
        assert highest_component_version is None

    def test_get_next_patch_component_version_exception(self):
        greengrass_client = Greengrassv2Client(self.project_config, self.service_clients)
        mock_get_next_patch_component_version = self.mocker.patch(
            "boto3.client.list_component_versions", side_effect=HTTPError("listing error")
        )
        c_arn = "arn:aws:greengrass:test-region:1234:components:c_name"
        with pytest.raises(Exception) as e:
            greengrass_client.get_highest_component_version_()
        assert mock_get_next_patch_component_version.call_args_list == [call(arn=c_arn)]
        assert (
            "listing error"
            == e.value.args[0]
        )

    def test_create_gg_component(self):
        greengrass_client = Greengrassv2Client(self.project_config, self.service_clients)
        mock_create_component = self.mocker.patch("boto3.client.create_component_version", return_value=None)

        with mock.patch("builtins.open", mock.mock_open(read_data="some-recipe-content")) as mock_file:
            greengrass_client.create_gg_component()
            assert mock_file.call_args_list == [call(Path("some-recipe.yaml"))]
            assert mock_create_component.call_args_list == [call(inlineRecipe="some-recipe-content")]

    def test_create_gg_component_exception(self):
        greengrass_client = Greengrassv2Client(self.project_config, self.service_clients)
        mock_create_component = self.mocker.patch(
            "boto3.client.create_component_version", return_value=None, side_effect=HTTPError("gg error")
        )
        greengrass_client.project_config["publish_recipe_file"] = Path("some-recipe.yaml")

        with mock.patch("builtins.open", mock.mock_open(read_data="some-recipe-content")) as mock_file:
            with pytest.raises(Exception) as e:
                greengrass_client.create_gg_component()
            assert "gg error" in e.value.args[0]
            assert mock_file.call_args_list == [call(Path("some-recipe.yaml"))]
            assert mock_create_component.call_args_list == [call(inlineRecipe="some-recipe-content")]

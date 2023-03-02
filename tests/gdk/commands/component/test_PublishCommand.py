import logging
from pathlib import Path
from unittest import TestCase, mock
from unittest.mock import call

import pytest
from urllib3.exceptions import HTTPError

import gdk.common.exceptions.error_messages as error_messages
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

    def test_create_publish_recipe_file_json(self):
        component_name = "component_name"
        component_version = "1.0.0"
        parsed_recipe_file = {"componentName": component_name, "componentVersion": component_version}

        file_name = (
            Path(self.mock_get_proj_config.return_value["gg_build_recipes_dir"])
            .joinpath("component_name-1.0.0.json")
            .resolve()
        )
        mock_json_dump = self.mocker.patch("json.dumps")
        mock_yaml_dump = self.mocker.patch("yaml.dump")
        publish = PublishCommand({})
        with mock.patch("builtins.open", mock.mock_open()) as mock_file:
            publish.create_publish_recipe_file(component_name, component_version, parsed_recipe_file)
            mock_file.assert_any_call(file_name, "w")
            mock_json_dump.call_count == 1
            assert not mock_yaml_dump.called
        assert "publish_recipe_file" in publish.project_config

    def test_create_publish_recipe_file_yaml(self):
        component_name = "component_name"
        component_version = "1.0.0"
        parsed_recipe_file = {"componentName": component_name, "componentVersion": component_version}
        publish = PublishCommand({})
        publish.project_config["component_recipe_file"] = Path("some-yaml.yaml").resolve()
        file_name = (
            Path(self.mock_get_proj_config.return_value["gg_build_recipes_dir"])
            .joinpath("component_name-1.0.0.yaml")
            .resolve()
        )
        mock_json_dump = self.mocker.patch("json.dumps")
        mock_yaml_dump = self.mocker.patch("yaml.dump")
        with mock.patch("builtins.open", mock.mock_open()) as mock_file:
            publish.create_publish_recipe_file(component_name, component_version, parsed_recipe_file)
            mock_file.assert_any_call(file_name, "w")
            mock_yaml_dump.call_count == 1
            assert not mock_json_dump.called
        assert "publish_recipe_file" in publish.project_config

    def test_create_recipe_file_json_invalid(self):
        # Raise exception for when creating recipe failed due to invalid json
        component_name = "component_name"
        component_version = "1.0.0"
        parsed_recipe_file = {"componentName": component_name, "componentVersion": component_version}
        publish = PublishCommand({})
        publish.project_config["component_recipe_file"] = Path("some-json.json").resolve()
        file_name = (
            Path(self.mock_get_proj_config.return_value["gg_build_recipes_dir"])
            .joinpath("component_name-1.0.0.json")
            .resolve()
        )

        def throw_error(*args, **kwargs):
            if args[0] == parsed_recipe_file:
                raise TypeError("I mock json error")

        mock_json_dump = self.mocker.patch("json.dumps", side_effect=throw_error)
        mock_yaml_dump = self.mocker.patch("yaml.dump")
        with mock.patch("builtins.open", mock.mock_open()) as mock_file:
            with pytest.raises(Exception) as e:
                publish.create_publish_recipe_file(component_name, component_version, parsed_recipe_file)
            assert "Failed to create publish recipe file at" in e.value.args[0]
            mock_file.assert_called_once_with(file_name, "w")
            mock_json_dump.call_count == 1
            assert not mock_yaml_dump.called
        assert "publish_recipe_file" in publish.project_config

    def test_create_recipe_file_yaml_invalid(self):
        # Raise exception for when creating recipe failed due to invalid yaml
        component_name = "component_name"
        component_version = "1.0.0"
        parsed_recipe_file = {"componentName": component_name, "componentVersion": component_version}
        publish = PublishCommand({})
        publish.project_config["component_recipe_file"] = Path("some-yaml.yaml").resolve()
        file_name = (
            Path(self.mock_get_proj_config.return_value["gg_build_recipes_dir"])
            .joinpath("component_name-1.0.0.yaml")
            .resolve()
        )

        def throw_error(*args, **kwargs):
            if args[0] == parsed_recipe_file:
                raise TypeError("I mock yaml error")

        mock_json_dump = self.mocker.patch("json.dumps")
        mock_yaml_dump = self.mocker.patch("yaml.dump", side_effect=throw_error)
        with mock.patch("builtins.open", mock.mock_open()) as mock_file:
            with pytest.raises(Exception) as e:
                publish.create_publish_recipe_file(component_name, component_version, parsed_recipe_file)
            assert "Failed to create publish recipe file at" in e.value.args[0]
            mock_file.assert_called_once_with(file_name, "w")
            mock_json_dump.call_count == 1
            assert mock_yaml_dump.called
        assert "publish_recipe_file" in publish.project_config

    def test_update_and_create_recipe_file_no_manifests(self):
        self.mocker.patch("gdk.commands.component.project_utils.parse_recipe_file", return_value={})
        mock_create_publish_recipe = self.mocker.patch.object(PublishCommand, "create_publish_recipe_file", return_value=None)

        component_name = "component_name"
        component_version = "1.0.0"
        publish = PublishCommand({})
        publish.update_and_create_recipe_file(component_name, component_version)
        assert not mock_create_publish_recipe.called  # No 'Manifests' in recipe

    def test_update_and_create_recipe_file_manifests_build(self):
        self.mocker.patch(
            "gdk.commands.component.project_utils.parse_recipe_file",
            return_value=self.mock_get_proj_config.return_value["parsed_component_recipe"],
        )
        mock_glob = self.mocker.patch("pathlib.Path.glob", return_value=[Path("hello_world.py")])
        mock_create_publish_recipe = self.mocker.patch.object(PublishCommand, "create_publish_recipe_file", return_value=None)

        component_name = "com.example.HelloWorld"
        component_version = "1.0.0"
        publish = PublishCommand({})
        publish.update_and_create_recipe_file(component_name, component_version)
        publish_component_recipe = self.mock_get_proj_config.return_value["parsed_component_recipe"]
        assert mock_glob.call_count == 1
        assert mock_create_publish_recipe.call_count == 1
        mock_create_publish_recipe.assert_any_call(component_name, component_version, publish_component_recipe)
        assert publish_component_recipe["ComponentVersion"] == component_version
        assert (
            publish_component_recipe["Manifests"][0]["Artifacts"][0]["URI"]
            == f"s3://default/{component_name}/{component_version}/hello_world.py"
        )

    def test_update_and_create_recipe_file_manifests_not_build(self):
        self.mocker.patch(
            "gdk.commands.component.project_utils.parse_recipe_file",
            return_value=self.mock_get_proj_config.return_value["parsed_component_recipe"],
        )
        mock_create_publish_recipe = self.mocker.patch.object(PublishCommand, "create_publish_recipe_file", return_value=None)

        component_name = "component_name"
        component_version = "1.0.0"
        publish = PublishCommand({})
        with pytest.raises(Exception) as e:
            publish.update_and_create_recipe_file(component_name, component_version)
        assert "as it is not build.\nBuild the component `gdk component build` before publishing it." in e.value.args[0]
        assert mock_create_publish_recipe.call_count == 0

    def test_update_and_create_recipe_file_uri_not_matches(self):
        self.mocker.patch(
            "gdk.commands.component.project_utils.parse_recipe_file",
            return_value=self.mock_get_proj_config.return_value["parsed_component_recipe"],
        )
        mock_glob = self.mocker.patch("pathlib.Path.glob", return_value=[Path("hello_world.py")])
        mock_create_publish_recipe = self.mocker.patch.object(PublishCommand, "create_publish_recipe_file", return_value=None)

        component_name = "com.example.HelloWorld"
        component_version = "1.0.0"
        publish = PublishCommand({})
        publish.update_and_create_recipe_file(component_name, component_version)
        publish_component_recipe = self.mock_get_proj_config.return_value["parsed_component_recipe"]
        assert mock_glob.call_count == 1
        assert mock_create_publish_recipe.call_count == 1
        mock_create_publish_recipe.assert_any_call(component_name, component_version, publish_component_recipe)
        assert publish_component_recipe["ComponentVersion"] == component_version

    def test_update_and_create_recipe_file_artifact_file_not_exists(self):
        self.mocker.patch(
            "gdk.commands.component.project_utils.parse_recipe_file",
            return_value=self.mock_get_proj_config.return_value["parsed_component_recipe"],
        )
        mock_glob = self.mocker.patch("pathlib.Path.glob", return_value=[])
        mock_create_publish_recipe = self.mocker.patch.object(PublishCommand, "create_publish_recipe_file", return_value=None)
        spy_logging_warning = self.mocker.spy(logging, "warning")
        component_name = "com.example.HelloWorld"
        component_version = "1.0.0"
        publish = PublishCommand({})
        publish.update_and_create_recipe_file(component_name, component_version)
        assert spy_logging_warning.call_count == 1
        assert mock_glob.call_count == 1
        assert mock_create_publish_recipe.called

    def test_update_and_create_recipe_file_no_artifacts(self):
        no_artifacts_key = {
            "RecipeFormatVersion": "2020-01-25",
            "ComponentName": "com.example.HelloWorld",
            "ComponentVersion": "1.0.0",
            "ComponentDescription": "My first Greengrass component.",
            "ComponentPublisher": "Amazon",
            "ComponentConfiguration": {"DefaultConfiguration": {"Message": "world"}},
            "Manifests": [
                {
                    "Platform": {"os": "linux"},
                    "Lifecycle": {"Run": "python3 -u {artifacts:path}/hello_world.py '{configuration:/Message}'"},
                }
            ],
        }
        self.mocker.patch("gdk.commands.component.project_utils.parse_recipe_file", return_value=no_artifacts_key)
        mock_create_publish_recipe = self.mocker.patch.object(PublishCommand, "create_publish_recipe_file", return_value=None)

        component_name = "com.example.HelloWorld"
        component_version = "1.0.0"
        publish = PublishCommand({})
        publish.update_and_create_recipe_file(component_name, component_version)
        assert mock_create_publish_recipe.call_count == 1
        mock_create_publish_recipe.assert_any_call(component_name, component_version, no_artifacts_key)
        assert no_artifacts_key["ComponentVersion"] == component_version

    def test_update_and_create_recipe_file_no_artifacts_uri(self):
        no_artifacts_uri_key = {
            "RecipeFormatVersion": "2020-01-25",
            "ComponentName": "com.example.HelloWorld",
            "ComponentVersion": "1.0.0",
            "ComponentDescription": "My first Greengrass component.",
            "ComponentPublisher": "Amazon",
            "ComponentConfiguration": {"DefaultConfiguration": {"Message": "world"}},
            "Manifests": [
                {
                    "Platform": {"os": "linux"},
                    "Lifecycle": {"Run": "python3 -u {artifacts:path}/hello_world.py '{configuration:/Message}'"},
                    "Artifacts": [{}],
                }
            ],
        }
        self.mocker.patch("gdk.commands.component.project_utils.parse_recipe_file", return_value=no_artifacts_uri_key)
        mock_create_publish_recipe = self.mocker.patch.object(PublishCommand, "create_publish_recipe_file", return_value=None)

        component_name = "com.example.HelloWorld"
        component_version = "1.0.0"
        publish = PublishCommand({})
        publish.update_and_create_recipe_file(component_name, component_version)
        assert mock_create_publish_recipe.call_count == 1
        mock_create_publish_recipe.assert_any_call(component_name, component_version, no_artifacts_uri_key)
        assert no_artifacts_uri_key["ComponentVersion"] == component_version

    def test_update_and_create_recipe_file_docker_artifacts_uri(self):
        no_artifacts_uri_key = {
            "RecipeFormatVersion": "2020-01-25",
            "ComponentName": "com.example.HelloWorld",
            "ComponentVersion": "1.0.0",
            "ComponentDescription": "My first Greengrass component.",
            "ComponentPublisher": "Amazon",
            "ComponentConfiguration": {"DefaultConfiguration": {"Message": "world"}},
            "Manifests": [
                {
                    "Platform": {"os": "linux"},
                    "Lifecycle": {"Run": "python3 -u {artifacts:path}/hello_world.py '{configuration:/Message}'"},
                    "Artifacts": [{"URI": "docker:uri"}],
                }
            ],
        }
        self.mocker.patch("gdk.commands.component.project_utils.parse_recipe_file", return_value=no_artifacts_uri_key)
        mock_create_publish_recipe = self.mocker.patch.object(PublishCommand, "create_publish_recipe_file", return_value=None)

        component_name = "com.example.HelloWorld"
        component_version = "1.0.0"
        publish = PublishCommand({})
        publish.update_and_create_recipe_file(component_name, component_version)
        assert mock_create_publish_recipe.call_count == 1
        mock_create_publish_recipe.assert_any_call(component_name, component_version, no_artifacts_uri_key)
        assert no_artifacts_uri_key["ComponentVersion"] == component_version

    def test_update_and_create_recipe_file_mix_uri_in_recipe(self):
        # Nothing to copy if artifact uri don't exist in the recipe.

        mock_iter_dir_list = [Path("hello_world.py").resolve()]
        mock_glob = self.mocker.patch("pathlib.Path.glob", return_value=mock_iter_dir_list)

        docker_artifacts_uri_key = {
            "RecipeFormatVersion": "2020-01-25",
            "ComponentName": "com.example.HelloWorld",
            "ComponentVersion": "1.0.0",
            "ComponentDescription": "My first Greengrass component.",
            "ComponentPublisher": "Amazon",
            "ComponentConfiguration": {"DefaultConfiguration": {"Message": "world"}},
            "Manifests": [
                {
                    "Platform": {"os": "linux"},
                    "Lifecycle": {"Run": "python3 -u {artifacts:path}/hello_world.py '{configuration:/Message}'"},
                    "Artifacts": [{"URI": "docker:uri"}, {"URI": "s3://hello_world.py"}],
                }
            ],
        }
        mock_create_publish_recipe = self.mocker.patch.object(PublishCommand, "create_publish_recipe_file", return_value=None)
        self.mocker.patch("gdk.commands.component.project_utils.parse_recipe_file", return_value=docker_artifacts_uri_key)
        component_name = "com.example.HelloWorld"
        component_version = "1.0.0"
        publish = PublishCommand({})
        publish.update_and_create_recipe_file(component_name, component_version)
        mock_glob.assert_called_with("hello_world.py")
        assert mock_create_publish_recipe.call_count == 1
        mock_create_publish_recipe.assert_any_call(component_name, component_version, docker_artifacts_uri_key)
        assert docker_artifacts_uri_key["ComponentVersion"] == component_version

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
            PublishCommand, "get_next_patch_component_version", return_value=None
        )
        publish = PublishCommand({})
        publish.project_config["account_number"] = "1234"
        version = publish.get_next_version()
        assert version == "1.0.0"  # Fallback version
        assert mock_get_next_patch_component_version.call_count == 1
        mock_get_next_patch_component_version.assert_any_call("component_name", "us-east-1", "1234")

    def test_get_next_version_component_already_exists(self):
        publish = PublishCommand({})
        mock_get_next_patch_component_version = self.mocker.patch.object(
            PublishCommand, "get_next_patch_component_version", return_value="1.0.6"
        )
        publish.project_config["account_number"] = "12345"
        version = publish.get_next_version()
        assert version == "1.0.7"
        assert mock_get_next_patch_component_version.call_count == 1

    def test_client_built_with_correct_region(self):
        self.mocker.patch.object(PublishCommand, "get_account_number", return_value="1234")
        self.mocker.patch.object(PublishCommand, "get_component_version_from_config", return_value=None)
        self.mocker.patch.object(PublishCommand, "upload_artifacts_s3", return_value=None)
        self.mocker.patch.object(PublishCommand, "update_and_create_recipe_file", return_value=None)
        self.mocker.patch("gdk.common.utils.dir_exists", return_value=False)
        self.mocker.patch("gdk.commands.component.component.build", return_value=None)
        self.mocker.patch.object(PublishCommand, "create_gg_component", return_value=None)

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
            PublishCommand, "get_next_patch_component_version", return_value="1.0.6-x-y-z"
        )
        version = publish.get_next_version()
        assert version == "1.0.7"
        assert mock_get_next_patch_component_version.call_count == 1

    def test_get_next_version_component_exception(self):
        publish = PublishCommand({})
        publish.project_config["account_number"] = "1234"
        mock_get_next_patch_component_version = self.mocker.patch.object(
            PublishCommand, "get_next_patch_component_version", side_effect=HTTPError("some error")
        )
        with pytest.raises(Exception) as e:
            publish.get_next_version()
        assert mock_get_next_patch_component_version.call_count == 1
        assert e.value.args[0] == "Failed to calculate the next version of the component during publish.\nsome error"

    def test_get_next_patch_component_version(self):
        publish = PublishCommand({})
        publish.project_config["account_number"] = "1234"
        mock_client = self.mocker.patch("boto3.client", return_value=None)
        publish.service_clients = {"greengrass_client": mock_client}
        response = {"componentVersions": [{"componentVersion": "1.0.4"}, {"componentVersion": "1.0.1"}]}
        mock_get_next_patch_component_version = self.mocker.patch(
            "boto3.client.list_component_versions", return_value=response
        )
        li = publish.get_next_patch_component_version("c_name", "region", "1234")
        assert mock_get_next_patch_component_version.call_count == 1
        assert li == "1.0.4"

    def test_get_next_patch_component_version_no_components(self):
        publish = PublishCommand({})
        mock_client = self.mocker.patch("boto3.client", return_value=None)
        publish.service_clients = {"greengrass_client": mock_client}
        mock_get_next_patch_component_version = self.mocker.patch(
            "boto3.client.list_component_versions", return_value={"componentVersions": []}
        )
        li = publish.get_next_patch_component_version("c_name", "region", "1234")
        assert mock_get_next_patch_component_version.call_count == 1
        assert not li

    def test_get_next_patch_component_version_exception(self):
        publish = PublishCommand({})
        mock_client = self.mocker.patch("boto3.client", return_value=None)
        publish.service_clients = {"greengrass_client": mock_client}
        mock_get_next_patch_component_version = self.mocker.patch(
            "boto3.client.list_component_versions", side_effect=HTTPError("listing error")
        )
        with pytest.raises(Exception) as e:
            publish.get_next_patch_component_version("c_name", "region", "1234")
        assert mock_get_next_patch_component_version.call_count == 1
        assert (
            "Error while getting the component versions of 'c_name' in 'region' from the account '1234' during"
            " publish.\nlisting error"
            == e.value.args[0]
        )

    def test_create_gg_component(self):
        publish = PublishCommand({})
        mock_client = self.mocker.patch("boto3.client", return_value=None)
        publish.service_clients = {"greengrass_client": mock_client}
        mock_create_component = self.mocker.patch("boto3.client.create_component_version", return_value=None)
        publish.project_config["publish_recipe_file"] = Path("some-recipe.yaml")
        component_name = "component_name"
        component_version = "1.0.0"

        with mock.patch("builtins.open", mock.mock_open()) as mock_file:
            publish.create_gg_component(component_name, component_version)
            mock_file.assert_any_call(publish.project_config["publish_recipe_file"])
            assert mock_create_component.call_count == 1

    def test_create_gg_component_exception(self):
        publish = PublishCommand({})
        mock_client = self.mocker.patch("boto3.client", return_value=None)
        publish.service_clients = {"greengrass_client": mock_client}
        mock_create_component = self.mocker.patch(
            "boto3.client.create_component_version", return_value=None, side_effect=HTTPError("error")
        )
        publish.project_config["publish_recipe_file"] = Path("some-recipe.yaml")
        component_name = "component_name"
        component_version = "1.0.0"

        with mock.patch("builtins.open", mock.mock_open()) as mock_file:
            with pytest.raises(Exception) as e:
                publish.create_gg_component(component_name, component_version)
            assert "Creating private version '1.0.0' of the component 'component_name' failed." in e.value.args[0]
            mock_file.assert_any_call(publish.project_config["publish_recipe_file"])
            assert mock_create_component.call_count == 1

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
        mock_update_and_create_recipe_file = self.mocker.patch.object(
            PublishCommand, "update_and_create_recipe_file", return_value=None
        )
        mock_dir_exists = self.mocker.patch("gdk.common.utils.dir_exists", return_value=False)
        mock_build = self.mocker.patch("gdk.commands.component.component.build", return_value=None)
        mock_create_gg_component = self.mocker.patch.object(PublishCommand, "create_gg_component", return_value=None)
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
        assert mock_update_and_create_recipe_file.call_count == 1
        assert mock_create_gg_component.call_count == 1

    def test_publish_run_not_build_command_bucket(self):
        mock_get_account_num = self.mocker.patch.object(PublishCommand, "get_account_number", return_value="1234")
        mock_get_component_version_from_config = self.mocker.patch.object(
            PublishCommand, "get_component_version_from_config", return_value=None
        )
        mock_upload_artifacts_s3 = self.mocker.patch.object(PublishCommand, "upload_artifacts_s3", return_value=None)
        mock_update_and_create_recipe_file = self.mocker.patch.object(
            PublishCommand, "update_and_create_recipe_file", return_value=None
        )
        mock_dir_exists = self.mocker.patch("gdk.common.utils.dir_exists", return_value=False)
        mock_build = self.mocker.patch("gdk.commands.component.component.build", return_value=None)
        mock_create_gg_component = self.mocker.patch.object(PublishCommand, "create_gg_component", return_value=None)
        publish = PublishCommand({"bucket": "exact-bucket", "region": None, "options": None})
        publish.run()
        assert publish.project_config["account_number"] == "1234"
        assert publish.project_config["bucket"] == "exact-bucket"
        assert mock_dir_exists.call_count == 1
        assert mock_build.call_count == 1
        assert mock_get_account_num.call_count == 1
        assert mock_get_component_version_from_config.call_count == 1
        assert mock_upload_artifacts_s3.call_count == 1
        assert mock_update_and_create_recipe_file.call_count == 1
        assert mock_create_gg_component.call_count == 1

    def test_publish_run_build(self):
        mock_get_account_num = self.mocker.patch.object(PublishCommand, "get_account_number", return_value="1234")
        mock_get_component_version_from_config = self.mocker.patch.object(
            PublishCommand, "get_component_version_from_config", return_value=None
        )
        mock_upload_artifacts_s3 = self.mocker.patch.object(PublishCommand, "upload_artifacts_s3", return_value=None)
        mock_update_and_create_recipe_file = self.mocker.patch.object(
            PublishCommand, "update_and_create_recipe_file", return_value=None
        )
        mock_dir_exists = self.mocker.patch("gdk.common.utils.dir_exists", return_value=True)
        mock_build = self.mocker.patch("gdk.commands.component.component.build", return_value=None)
        publish = PublishCommand({"bucket": None, "region": None, "options": None})
        publish.project_config["bucket"] = "default"
        mock_create_gg_component = self.mocker.patch.object(PublishCommand, "create_gg_component", return_value=None)
        publish.run()
        assert publish.project_config["account_number"] == "1234"
        assert publish.project_config["bucket"] == "default-us-east-1-1234"
        assert mock_dir_exists.call_count == 1
        assert not mock_build.called
        assert mock_get_account_num.call_count == 1
        assert mock_get_component_version_from_config.call_count == 1
        assert mock_upload_artifacts_s3.call_count == 1
        assert mock_update_and_create_recipe_file.call_count == 1
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
        "parsed_component_recipe": {
            "RecipeFormatVersion": "2020-01-25",
            "ComponentName": "com.example.HelloWorld",
            "ComponentVersion": "1.0.0",
            "ComponentDescription": "My first Greengrass component.",
            "ComponentPublisher": "Amazon",
            "ComponentConfiguration": {"DefaultConfiguration": {"Message": "world"}},
            "Manifests": [
                {
                    "Platform": {"os": "linux"},
                    "Lifecycle": {"Run": "python3 -u {artifacts:path}/hello_world.py '{configuration:/Message}'"},
                    "Artifacts": [{"URI": "s3://DOC-EXAMPLE-BUCKET/artifacts/com.example.HelloWorld/1.0.0/hello_world.py"}],
                }
            ],
        },
    }

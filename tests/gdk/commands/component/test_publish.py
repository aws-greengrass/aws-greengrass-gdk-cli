from pathlib import Path
from unittest import mock

import boto3
import pytest
from gdk.common.exceptions import error_messages
from urllib3.exceptions import HTTPError

json_values = {
    "component_name": "component_name",
    "component_config": {
        "author": "abc",
        "version": "1.0.0",
        "build": {"build_system": "zip"},
        "publish": {"bucket": "default"},
    },
    "component_version": "1.0.0",
    "component_author": "abc",
    "bucket": "default",
    "region": "default",
    "gg_build_directory": Path("/src/GDK-CLI-Internal/greengrass-build"),
    "gg_build_artifacts_dir": Path("/src/GDK-CLI-Internal/greengrass-build/artifacts"),
    "gg_build_recipes_dir": Path("/src/GDK-CLI-Internal/greengrass-build/recipes"),
    "gg_build_component_artifacts_dir": Path("/src/GDK-CLI-Internal/greengrass-build/artifacts/component_name/1.0.0"),
    "component_recipe_file": Path("/src/GDK-CLI-Internal/tests/gdk/static/build_command/recipe.json"),
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
    "artifact_uri": "s3://default/component_name/1.0.0",
}

with mock.patch("gdk.commands.component.project_utils.get_project_config_values", return_value=json_values) as mock_method:
    mock_client = mock.patch("boto3.client", return_value=None)
    mock.patch("gdk.commands.component.project_utils.get_service_clients", return_value={})
    import gdk.commands.component.publish as publish


def test_create_publish_recipe_file_json(mocker):
    component_name = "component_name"
    component_version = "1.0.0"
    parsed_recipe_file = {"componentName": component_name, "componentVersion": component_version}

    file_name = Path(json_values["gg_build_recipes_dir"]).joinpath("component_name-1.0.0.json").resolve()
    mock_json_dump = mocker.patch("json.dumps")
    mock_yaml_dump = mocker.patch("yaml.dump")
    with mock.patch("builtins.open", mock.mock_open()) as mock_file:
        publish.create_publish_recipe_file(component_name, component_version, parsed_recipe_file)
        mock_file.assert_any_call(file_name, "w")
        mock_json_dump.call_count == 1
        assert not mock_yaml_dump.called
    assert "publish_recipe_file" in publish.project_config


def test_create_publish_recipe_file_yaml(mocker):
    component_name = "component_name"
    component_version = "1.0.0"
    parsed_recipe_file = {"componentName": component_name, "componentVersion": component_version}
    publish.project_config["component_recipe_file"] = Path("some-yaml.yaml").resolve()
    file_name = Path(json_values["gg_build_recipes_dir"]).joinpath("component_name-1.0.0.yaml").resolve()
    mock_json_dump = mocker.patch("json.dumps")
    mock_yaml_dump = mocker.patch("yaml.dump")
    with mock.patch("builtins.open", mock.mock_open()) as mock_file:
        publish.create_publish_recipe_file(component_name, component_version, parsed_recipe_file)
        mock_file.assert_any_call(file_name, "w")
        mock_yaml_dump.call_count == 1
        assert not mock_json_dump.called
    assert "publish_recipe_file" in publish.project_config


def test_create_recipe_file_json_invalid(mocker):
    # Raise exception for when creating recipe failed due to invalid json
    component_name = "component_name"
    component_version = "1.0.0"
    parsed_recipe_file = {"componentName": component_name, "componentVersion": component_version}
    publish.project_config["component_recipe_file"] = Path("some-json.json").resolve()
    file_name = Path(json_values["gg_build_recipes_dir"]).joinpath("component_name-1.0.0.json").resolve()

    def throw_error(*args, **kwargs):
        if args[0] == parsed_recipe_file:
            raise TypeError("I mock json error")

    mock_json_dump = mocker.patch("json.dumps", side_effect=throw_error)
    mock_yaml_dump = mocker.patch("yaml.dump")
    with mock.patch("builtins.open", mock.mock_open()) as mock_file:
        with pytest.raises(Exception) as e:
            publish.create_publish_recipe_file(component_name, component_version, parsed_recipe_file)
        assert "Failed to create publish recipe file at" in e.value.args[0]
        mock_file.assert_called_once_with(file_name, "w")
        mock_json_dump.call_count == 1
        assert not mock_yaml_dump.called
    assert "publish_recipe_file" in publish.project_config


def test_create_recipe_file_yaml_invalid(mocker):
    # Raise exception for when creating recipe failed due to invalid yaml
    component_name = "component_name"
    component_version = "1.0.0"
    parsed_recipe_file = {"componentName": component_name, "componentVersion": component_version}
    publish.project_config["component_recipe_file"] = Path("some-yaml.yaml").resolve()
    file_name = Path(json_values["gg_build_recipes_dir"]).joinpath("component_name-1.0.0.yaml").resolve()

    def throw_error(*args, **kwargs):
        if args[0] == parsed_recipe_file:
            raise TypeError("I mock yaml error")

    mock_json_dump = mocker.patch("json.dumps")
    mock_yaml_dump = mocker.patch("yaml.dump", side_effect=throw_error)
    with mock.patch("builtins.open", mock.mock_open()) as mock_file:
        with pytest.raises(Exception) as e:
            publish.create_publish_recipe_file(component_name, component_version, parsed_recipe_file)
        assert "Failed to create publish recipe file at" in e.value.args[0]
        mock_file.assert_called_once_with(file_name, "w")
        mock_json_dump.call_count == 1
        assert mock_yaml_dump.called
    assert "publish_recipe_file" in publish.project_config


def test_update_and_create_recipe_file_no_manifests(mocker):
    mocker.patch("gdk.commands.component.project_utils.parse_recipe_file", return_value={})
    mock_create_publish_recipe = mocker.patch("gdk.commands.component.publish.create_publish_recipe_file", return_value=None)

    component_name = "component_name"
    component_version = "1.0.0"
    publish.update_and_create_recipe_file(component_name, component_version)
    assert not mock_create_publish_recipe.called  # No 'Manifests' in recipe


def test_update_and_create_recipe_file_manifests_build(mocker):
    mocker.patch(
        "gdk.commands.component.project_utils.parse_recipe_file",
        return_value=json_values["parsed_component_recipe"],
    )
    mock_glob = mocker.patch("pathlib.Path.glob", return_value=[Path("hello_world.py")])
    mock_create_publish_recipe = mocker.patch("gdk.commands.component.publish.create_publish_recipe_file", return_value=None)

    component_name = "com.example.HelloWorld"
    component_version = "1.0.0"
    publish.update_and_create_recipe_file(component_name, component_version)
    publish_component_recipe = json_values["parsed_component_recipe"]
    assert mock_glob.call_count == 1
    assert mock_create_publish_recipe.call_count == 1
    mock_create_publish_recipe.assert_any_call(component_name, component_version, publish_component_recipe)
    assert publish_component_recipe["ComponentVersion"] == component_version
    assert (
        publish_component_recipe["Manifests"][0]["Artifacts"][0]["URI"]
        == f"s3://default/{component_name}/{component_version}/hello_world.py"
    )


def test_update_and_create_recipe_file_manifests_not_build(mocker):
    mocker.patch(
        "gdk.commands.component.project_utils.parse_recipe_file",
        return_value=json_values["parsed_component_recipe"],
    )
    mock_create_publish_recipe = mocker.patch("gdk.commands.component.publish.create_publish_recipe_file", return_value=None)

    component_name = "component_name"
    component_version = "1.0.0"

    with pytest.raises(Exception) as e:
        publish.update_and_create_recipe_file(component_name, component_version)
    assert "as it is not build.\nBuild the component `gdk component build` before publishing it." in e.value.args[0]
    assert mock_create_publish_recipe.call_count == 0


def test_update_and_create_recipe_file_uri_not_matches(mocker):
    mocker.patch(
        "gdk.commands.component.project_utils.parse_recipe_file",
        return_value=json_values["parsed_component_recipe"],
    )
    mock_glob = mocker.patch("pathlib.Path.glob", return_value=[Path("hello_world.py")])
    mock_create_publish_recipe = mocker.patch("gdk.commands.component.publish.create_publish_recipe_file", return_value=None)

    component_name = "com.example.HelloWorld"
    component_version = "1.0.0"
    publish.update_and_create_recipe_file(component_name, component_version)
    publish_component_recipe = json_values["parsed_component_recipe"]
    assert mock_glob.call_count == 1
    assert mock_create_publish_recipe.call_count == 1
    mock_create_publish_recipe.assert_any_call(component_name, component_version, publish_component_recipe)
    assert publish_component_recipe["ComponentVersion"] == component_version


def test_update_and_create_recipe_file_artifact_file_not_exists(mocker):
    mocker.patch(
        "gdk.commands.component.project_utils.parse_recipe_file",
        return_value=json_values["parsed_component_recipe"],
    )
    mock_glob = mocker.patch("pathlib.Path.glob", return_value=[])
    mock_create_publish_recipe = mocker.patch("gdk.commands.component.publish.create_publish_recipe_file", return_value=None)

    component_name = "com.example.HelloWorld"
    component_version = "1.0.0"
    with pytest.raises(Exception) as e:
        publish.update_and_create_recipe_file(component_name, component_version)
    assert (
        "Could not find the artifact file specified in the recipe 'hello_world.py' inside the build folder" in e.value.args[0]
    )
    assert mock_glob.call_count == 1
    assert not mock_create_publish_recipe.called


def test_update_and_create_recipe_file_no_artifacts(mocker):
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
    mocker.patch("gdk.commands.component.project_utils.parse_recipe_file", return_value=no_artifacts_key)
    mock_create_publish_recipe = mocker.patch("gdk.commands.component.publish.create_publish_recipe_file", return_value=None)

    component_name = "com.example.HelloWorld"
    component_version = "1.0.0"
    publish.update_and_create_recipe_file(component_name, component_version)
    assert mock_create_publish_recipe.call_count == 1
    mock_create_publish_recipe.assert_any_call(component_name, component_version, no_artifacts_key)
    assert no_artifacts_key["ComponentVersion"] == component_version


def test_update_and_create_recipe_file_no_artifacts_uri(mocker):
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
    mocker.patch("gdk.commands.component.project_utils.parse_recipe_file", return_value=no_artifacts_uri_key)
    mock_create_publish_recipe = mocker.patch("gdk.commands.component.publish.create_publish_recipe_file", return_value=None)

    component_name = "com.example.HelloWorld"
    component_version = "1.0.0"
    publish.update_and_create_recipe_file(component_name, component_version)
    assert mock_create_publish_recipe.call_count == 1
    mock_create_publish_recipe.assert_any_call(component_name, component_version, no_artifacts_uri_key)
    assert no_artifacts_uri_key["ComponentVersion"] == component_version


def test_update_and_create_recipe_file_docker_artifacts_uri(mocker):
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
    mocker.patch("gdk.commands.component.project_utils.parse_recipe_file", return_value=no_artifacts_uri_key)
    mock_create_publish_recipe = mocker.patch("gdk.commands.component.publish.create_publish_recipe_file", return_value=None)

    component_name = "com.example.HelloWorld"
    component_version = "1.0.0"
    publish.update_and_create_recipe_file(component_name, component_version)
    assert mock_create_publish_recipe.call_count == 1
    mock_create_publish_recipe.assert_any_call(component_name, component_version, no_artifacts_uri_key)
    assert no_artifacts_uri_key["ComponentVersion"] == component_version


def test_update_and_create_recipe_file_mix_uri_in_recipe(mocker):
    # Nothing to copy if artifact uri don't exist in the recipe.

    mock_iter_dir_list = [Path("hello_world.py").resolve()]
    mock_glob = mocker.patch("pathlib.Path.glob", return_value=mock_iter_dir_list)

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
    mock_create_publish_recipe = mocker.patch("gdk.commands.component.publish.create_publish_recipe_file", return_value=None)
    mocker.patch("gdk.commands.component.project_utils.parse_recipe_file", return_value=docker_artifacts_uri_key)
    component_name = "com.example.HelloWorld"
    component_version = "1.0.0"
    publish.update_and_create_recipe_file(component_name, component_version)
    mock_glob.assert_called_with("hello_world.py")
    assert mock_create_publish_recipe.call_count == 1
    mock_create_publish_recipe.assert_any_call(component_name, component_version, docker_artifacts_uri_key)
    assert docker_artifacts_uri_key["ComponentVersion"] == component_version


def test_get_component_version_from_config(mocker):
    mock_get_next_version = mocker.patch("gdk.commands.component.publish.get_next_version", return_value="")
    version = publish.get_component_version_from_config()
    assert version == json_values["component_version"]
    assert not mock_get_next_version.called


def test_get_component_version_from_config_latest(mocker):
    publish.project_config = {
        "component_name": "component_name",
        "component_version": "LATEST",
        "component_author": "abc",
        "bucket": "default",
        "region": "default",
    }
    mock_get_next_version = mocker.patch("gdk.commands.component.publish.get_next_version", return_value="1.0.1")
    version = publish.get_component_version_from_config()
    assert version == mock_get_next_version.return_value
    assert mock_get_next_version.called


def test_get_component_version_from_config_exception(mocker):
    mock_get_next_version = mocker.patch(
        "gdk.commands.component.publish.get_next_version", return_value="", side_effect=HTTPError("some error")
    )
    with pytest.raises(Exception) as e:
        publish.get_component_version_from_config()
        assert mock_get_next_version.call_count == 1
    assert e.value.args[0] == "some error"


def test_get_next_version_component_not_exists(mocker):
    publish.project_config["account_number"] = "1234"
    mock_get_latest_component_version = mocker.patch(
        "gdk.commands.component.publish.get_latest_component_version", return_value=None
    )
    version = publish.get_next_version()
    assert version == "1.0.0"  # Fallback version
    assert mock_get_latest_component_version.call_count == 1
    mock_get_latest_component_version.assert_any_call("component_name", "default", "1234")


def test_get_next_version_component_already_exists(mocker):
    mock_get_latest_component_version = mocker.patch(
        "gdk.commands.component.publish.get_latest_component_version", return_value="1.0.6"
    )

    version = publish.get_next_version()
    assert version == "1.0.7"
    assert mock_get_latest_component_version.call_count == 1


def test_get_next_version_component_already_exists_semver(mocker):
    mock_get_latest_component_version = mocker.patch(
        "gdk.commands.component.publish.get_latest_component_version", return_value="1.0.6-x-y-z"
    )
    version = publish.get_next_version()
    assert version == "1.0.7"
    assert mock_get_latest_component_version.call_count == 1


def test_get_next_version_component_exception(mocker):
    publish.project_config["account_number"] = "1234"
    mock_get_latest_component_version = mocker.patch(
        "gdk.commands.component.publish.get_latest_component_version", side_effect=HTTPError("some error")
    )
    with pytest.raises(Exception) as e:
        publish.get_next_version()
    assert mock_get_latest_component_version.call_count == 1
    assert e.value.args[0] == "Failed to calculate the next version of the component during publish.\nsome error"


def test_get_latest_component_version(mocker):
    publish.project_config["account_number"] = "1234"
    mock_client = mocker.patch("boto3.client", return_value=None)
    publish.service_clients = {"greengrass_client": mock_client}
    response = {"componentVersions": [{"componentVersion": "1.0.4"}, {"componentVersion": "1.0.1"}]}
    mock_get_latest_component_version = mocker.patch("boto3.client.list_component_versions", return_value=response)
    li = publish.get_latest_component_version("c_name", "region", "1234")
    assert mock_get_latest_component_version.call_count == 1
    assert li == "1.0.4"


def test_get_latest_component_version_no_components(mocker):
    mock_client = mocker.patch("boto3.client", return_value=None)
    publish.service_clients = {"greengrass_client": mock_client}
    mock_get_latest_component_version = mocker.patch(
        "boto3.client.list_component_versions", return_value={"componentVersions": []}
    )
    li = publish.get_latest_component_version("c_name", "region", "1234")
    assert mock_get_latest_component_version.call_count == 1
    assert not li


def test_get_latest_component_version_exception(mocker):
    mock_client = mocker.patch("boto3.client", return_value=None)
    publish.service_clients = {"greengrass_client": mock_client}
    mock_get_latest_component_version = mocker.patch(
        "boto3.client.list_component_versions", side_effect=HTTPError("listing error")
    )
    with pytest.raises(Exception) as e:
        publish.get_latest_component_version("c_name", "region", "1234")
    assert mock_get_latest_component_version.call_count == 1
    assert (
        e.value.args[0]
        == "Error while getting the component versions of 'c_name' in 'region' from the account '1234' during publish.\nlisting error"
    )


def test_create_gg_component(mocker):
    mock_client = mocker.patch("boto3.client", return_value=None)
    publish.service_clients = {"greengrass_client": mock_client}
    mock_create_component = mocker.patch("boto3.client.create_component_version", return_value=None)
    publish.project_config["publish_recipe_file"] = Path("some-recipe.yaml")
    component_name = "component_name"
    component_version = "1.0.0"

    with mock.patch("builtins.open", mock.mock_open()) as mock_file:
        publish.create_gg_component(component_name, component_version)
        mock_file.assert_any_call(publish.project_config["publish_recipe_file"])
        assert mock_create_component.call_count == 1


def test_create_gg_component_exception(mocker):
    mock_client = mocker.patch("boto3.client", return_value=None)
    publish.service_clients = {"greengrass_client": mock_client}
    mock_create_component = mocker.patch(
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


def test_create_bucket_exists(mocker):
    bucket = "test-bucket"
    region = "region"
    mock_client = mocker.patch("boto3.client", return_value=None)
    publish.service_clients = {"s3_client": mock_client}
    response = {"Buckets": [{"Name": "test-bucket"}]}
    mock_create_bucket = mocker.patch("boto3.client.create_bucket", return_value=response)
    publish.create_bucket(bucket, region)
    assert mock_create_bucket.called


def test_create_bucket_exception(mocker):
    bucket = "test-bucket"
    region = "region"
    mock_client = mocker.patch("boto3.client", return_value=None)
    publish.service_clients = {"s3_client": mock_client}
    response = {"Buckets": [{"Name": "test-bucket"}]}
    mock_create_bucket = mocker.patch("boto3.client.create_bucket", return_value=response, side_effect=HTTPError("some error"))
    with pytest.raises(Exception) as e:
        publish.create_bucket(bucket, region)
    assert mock_create_bucket.call_count == 1
    assert type(e.value.args[0]) == HTTPError


def test_upload_artifacts_no_artifacts_not_build(mocker):
    publish.project_config = json_values
    mock_client = mocker.patch("boto3.client", return_value=None)
    publish.service_clients = {"s3_client": mock_client}
    response = {"Buckets": [{"Name": "test-bucket"}]}
    mock_iter_dir = mocker.patch("pathlib.Path.iterdir", return_value=[])
    mock_create_bucket = mocker.patch("boto3.client.create_bucket", return_value=response)
    mock_upload_file = mocker.patch("boto3.client.upload_file", return_value=response)
    mock_dir_exists = mocker.patch("gdk.common.utils.dir_exists", return_value=False)
    with pytest.raises(Exception) as e:
        publish.upload_artifacts_s3("name", "version")
    assert "as it is not build.\nBuild the component `gdk component build` before publishing it." in e.value.args[0]
    assert mock_dir_exists.call_count == 1
    assert mock_iter_dir.call_count == 0
    assert mock_create_bucket.call_count == 0
    assert not mock_upload_file.called


def test_upload_artifacts_no_artifacts(mocker):
    publish.project_config = json_values
    mock_client = mocker.patch("boto3.client", return_value=None)
    publish.service_clients = {"s3_client": mock_client}
    response = {"Buckets": [{"Name": "test-bucket"}]}
    mock_iter_dir = mocker.patch("pathlib.Path.iterdir", return_value=[])
    mock_create_bucket = mocker.patch("boto3.client.create_bucket", return_value=response)
    mock_upload_file = mocker.patch("boto3.client.upload_file", return_value=response)
    mock_dir_exists = mocker.patch("gdk.common.utils.dir_exists", return_value=True)
    publish.upload_artifacts_s3("name", "version")
    assert mock_iter_dir.call_count == 1
    assert mock_create_bucket.call_count == 1
    assert not mock_upload_file.called
    assert mock_dir_exists.call_count == 1


def test_upload_artifacts(mocker):
    publish.project_config = json_values
    mock_client = mocker.patch("boto3.client", return_value=None)
    publish.service_clients = {"s3_client": mock_client}
    mock_iter_dir = mocker.patch("pathlib.Path.iterdir", return_value=[Path("hello.py")])
    mock_create_bucket = mocker.patch("boto3.client.create_bucket", return_value=None)
    mock_upload_file = mocker.patch("boto3.client.upload_file", return_value=None)
    mock_dir_exists = mocker.patch("gdk.common.utils.dir_exists", return_value=True)
    publish.upload_artifacts_s3("name", "1.0.0")
    assert mock_dir_exists.call_count == 1
    assert mock_iter_dir.call_count == 1
    assert mock_create_bucket.call_count == 1
    assert mock_upload_file.call_count == 1
    s3_file_path = "name/1.0.0/hello.py"
    mock_upload_file.assert_any_call(str(Path("hello.py").resolve()), json_values["bucket"], s3_file_path)


def test_upload_artifacts_region_us_east_1(mocker):
    publish.project_config = json_values
    publish.project_config["region"] = "us-east-1"
    mock_client = mocker.patch("boto3.client", return_value=None)
    publish.service_clients = {"s3_client": mock_client}
    mock_iter_dir = mocker.patch("pathlib.Path.iterdir", return_value=[Path("hello.py")])
    mock_create_bucket = mocker.patch("boto3.client.create_bucket", return_value=None)
    mock_upload_file = mocker.patch("boto3.client.upload_file", return_value=None)
    mock_dir_exists = mocker.patch("gdk.common.utils.dir_exists", return_value=True)
    publish.upload_artifacts_s3("name", "1.0.0")
    assert mock_dir_exists.call_count == 1
    assert mock_iter_dir.call_count == 1
    assert mock_create_bucket.call_count == 1
    assert mock_upload_file.call_count == 1
    s3_file_path = "name/1.0.0/hello.py"
    mock_upload_file.assert_any_call(str(Path("hello.py").resolve()), json_values["bucket"], s3_file_path)


def test_upload_artifacts_exception(mocker):
    publish.project_config = json_values
    mock_client = mocker.patch("boto3.client", return_value=None)
    publish.service_clients = {"s3_client": mock_client}
    mock_iter_dir = mocker.patch("pathlib.Path.iterdir", return_value=[Path("hello.py")])
    mock_create_bucket = mocker.patch("boto3.client.create_bucket", return_value=None)
    mock_dir_exists = mocker.patch("gdk.common.utils.dir_exists", return_value=True)
    mock_upload_file = mocker.patch("boto3.client.upload_file", return_value=None, side_effect=HTTPError("some error"))
    with pytest.raises(Exception) as e:
        publish.upload_artifacts_s3("name", "1.0.0")
    assert "some error" in e.value.args[0]
    assert mock_dir_exists.call_count == 1
    assert mock_iter_dir.call_count == 1
    assert mock_create_bucket.call_count == 1
    assert mock_upload_file.call_count == 1
    s3_file_path = "name/1.0.0/hello.py"
    mock_upload_file.assert_any_call(str(Path("hello.py").resolve()), json_values["bucket"], s3_file_path)


def test_publish_run(mocker):
    mock_get_account_num = mocker.patch("gdk.commands.component.publish.get_account_number", return_value="1234")
    mock_get_component_version_from_config = mocker.patch(
        "gdk.commands.component.publish.get_component_version_from_config", return_value=None
    )
    mock_upload_artifacts_s3 = mocker.patch("gdk.commands.component.publish.upload_artifacts_s3", return_value=None)
    mock_update_and_create_recipe_file = mocker.patch(
        "gdk.commands.component.publish.update_and_create_recipe_file", return_value=None
    )
    mock_create_gg_component = mocker.patch("gdk.commands.component.publish.create_gg_component", return_value=None)
    publish.run({})
    assert publish.project_config["account_number"] == "1234"
    assert publish.project_config["bucket"] == "default-us-east-1-1234"
    assert mock_get_account_num.call_count == 1
    assert mock_get_component_version_from_config.call_count == 1
    assert mock_upload_artifacts_s3.call_count == 1
    assert mock_update_and_create_recipe_file.call_count == 1
    assert mock_create_gg_component.call_count == 1


def test_publish_run_exception(mocker):
    mock_get_account_num = mocker.patch("gdk.commands.component.publish.get_account_number", return_value="1234")
    mock_get_component_version_from_config = mocker.patch(
        "gdk.commands.component.publish.get_component_version_from_config",
        return_value=None,
        side_effect=HTTPError("some error"),
    )
    mock_upload_artifacts_s3 = mocker.patch("gdk.commands.component.publish.upload_artifacts_s3", return_value=None)
    mock_update_and_create_recipe_file = mocker.patch(
        "gdk.commands.component.publish.update_and_create_recipe_file", return_value=None
    )
    mock_create_gg_component = mocker.patch("gdk.commands.component.publish.create_gg_component", return_value=None)
    publish.project_config["bucket"] = "default"
    with pytest.raises(Exception) as e:
        publish.run({})
    assert publish.project_config["account_number"] == "1234"
    assert publish.project_config["bucket"] == "default-us-east-1-1234"
    assert e.value.args[0] == "{}\n{}".format(error_messages.PUBLISH_FAILED, "some error")
    assert mock_get_account_num.call_count == 1
    assert mock_get_component_version_from_config.call_count == 1
    assert mock_upload_artifacts_s3.call_count == 0
    assert mock_update_and_create_recipe_file.call_count == 0
    assert mock_create_gg_component.call_count == 0


def test_create_bucket_exception_bucket_exists(mocker):
    bucket = "test-bucket"
    region = "region"

    def throw_err(*args, **kwargs):
        ex = boto3.client("s3").exceptions.BucketAlreadyExists(
            {"Error": {"Code": "BucketAlreadyExists", "Message": "fake message"}}, "CreateBucket"
        )
        raise ex

    mock_client = mocker.patch("boto3.client", return_value=boto3.client("s3"))
    mock_create_bucket = mocker.patch("boto3.client.create_bucket", side_effect=throw_err)
    publish.service_clients = {"s3_client": mock_client}

    with pytest.raises(Exception) as e:
        publish.create_bucket(bucket, region)
    assert mock_create_bucket.call_count == 1
    assert "An error occurred (BucketAlreadyExists) when calling the CreateBucket operation: fake message" == str(
        e.value.args[0]
    )


def test_create_bucket_exception_bucket_owned(mocker):
    bucket = "test-bucket"
    region = "region"

    def throw_err(*args, **kwargs):
        ex = boto3.client("s3").exceptions.BucketAlreadyOwnedByYou(
            {"Error": {"Code": "BucketAlreadyOwnedByYou", "Message": "fake message"}}, "CreateBucket"
        )
        raise ex

    mock_client = mocker.patch("boto3.client", return_value=boto3.client("s3"))
    mock_create_bucket = mocker.patch("boto3.client.create_bucket", side_effect=throw_err)
    publish.service_clients = {"s3_client": mock_client}

    with pytest.raises(Exception) as e:
        publish.create_bucket(bucket, region)
    assert mock_create_bucket.call_count == 1
    assert "An error occurred (BucketAlreadyOwnedByYou) when calling the CreateBucket operation: fake message" == str(
        e.value.args[0]
    )


def test_create_bucket_exception_bucket_owned_not_in_region(mocker):
    bucket = "test-bucket"
    region = "region"
    mock_check_in_same_region = mocker.patch("gdk.commands.component.publish.bucket_exists_in_same_region", return_value=False)

    def throw_err(*args, **kwargs):
        ex = boto3.client("s3").exceptions.BucketAlreadyOwnedByYou(
            {"Error": {"Code": "BucketAlreadyOwnedByYou", "Message": "fake message"}}, "CreateBucket"
        )
        raise ex

    mock_client = mocker.patch("boto3.client", return_value=boto3.client("s3"))
    mock_create_bucket = mocker.patch("boto3.client.create_bucket", side_effect=throw_err)
    publish.service_clients = {"s3_client": mock_client}

    with pytest.raises(Exception) as e:
        publish.create_bucket(bucket, region)
    assert mock_create_bucket.call_count == 1
    assert mock_check_in_same_region.called
    print(e.value.args[0])
    assert "An error occurred (BucketAlreadyOwnedByYou) when calling the CreateBucket operation: fake message" == str(
        e.value.args[0]
    )


def test_create_bucket_exception_bucket_owned_in_region(mocker):
    bucket = "test-bucket"
    region = "region"
    mock_check_in_same_region = mocker.patch("gdk.commands.component.publish.bucket_exists_in_same_region", return_value=True)

    def throw_err(*args, **kwargs):
        ex = boto3.client("s3").exceptions.BucketAlreadyOwnedByYou(
            {"Error": {"Code": "BucketAlreadyOwnedByYou", "Message": "fake message"}}, "CreateBucket"
        )
        raise ex

    mock_client = mocker.patch("boto3.client", return_value=boto3.client("s3"))
    mock_create_bucket = mocker.patch("boto3.client.create_bucket", side_effect=throw_err)
    publish.service_clients = {"s3_client": mock_client}

    publish.create_bucket(bucket, region)
    assert mock_create_bucket.call_count == 1
    assert mock_check_in_same_region.called


def test_get_account_number_exception(mocker):
    mock_client = mocker.patch("boto3.client", return_value=None)
    publish.service_clients = {"sts_client": mock_client}
    mock_get_caller_identity = mocker.patch("boto3.client.get_caller_identity", return_value=None)
    with pytest.raises(Exception) as e:
        publish.get_account_number()
    assert mock_get_caller_identity.call_count == 1
    assert "Error while fetching account number from credentials." in e.value.args[0]


def test_get_account_number(mocker):
    mock_client = mocker.patch("boto3.client", return_value=None)
    publish.service_clients = {"sts_client": mock_client}
    mock_get_caller_identity = mocker.patch("boto3.client.get_caller_identity", return_value={"Account": 124})
    num = publish.get_account_number()
    assert mock_get_caller_identity.call_count == 1
    assert num == 124


def test_bucket_exists_in_same_region_exists(mocker):
    mock_client = mocker.patch("boto3.client", return_value=None)
    publish.service_clients = {"s3_client": mock_client}
    mock_get_bucket_location = mocker.patch(
        "boto3.client.get_bucket_location", return_value={"LocationConstraint": "us-east-1"}
    )
    exists = publish.bucket_exists_in_same_region("bucket", "us-east-1")
    assert mock_get_bucket_location.call_count == 1
    assert exists


def test_bucket_exists_in_same_region_not_exists(mocker):
    mock_client = mocker.patch("boto3.client", return_value=None)
    publish.service_clients = {"s3_client": mock_client}
    mock_get_bucket_location = mocker.patch(
        "boto3.client.get_bucket_location", return_value={"LocationConstraint": "us-west-2"}
    )
    exists = publish.bucket_exists_in_same_region("bucket", "us-east-1")
    assert mock_get_bucket_location.call_count == 1
    assert not exists


def test_bucket_exists_in_same_region_exception(mocker):
    mock_client = mocker.patch("boto3.client", return_value=None)
    publish.service_clients = {"s3_client": mock_client}
    mock_get_bucket_location = mocker.patch("boto3.client.get_bucket_location", side_effect=HTTPError("some eror"))
    with pytest.raises(Exception) as e:
        publish.bucket_exists_in_same_region("bucket", "us-east-1")
    assert "Unable to fetch the location of the bucket" in e.value.args[0]
    assert mock_get_bucket_location.call_count == 1

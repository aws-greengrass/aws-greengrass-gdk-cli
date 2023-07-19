from pathlib import Path
from unittest.mock import ANY, mock_open, patch

import boto3
from gdk.commands.component.transformer.PublishRecipeTransformer import (
    PublishRecipeTransformer,
)
import pytest

import gdk.CLIParser as CLIParser
import gdk.common.parse_args_actions as parse_args_actions
from gdk.aws_clients.S3Client import S3Client
from gdk.commands.component.PublishCommand import PublishCommand


@pytest.fixture()
def mock_project_config(mocker):
    mock_get_proj_config = mocker.patch(
        "gdk.commands.component.project_utils.get_project_config_values",
        return_value=project_config(),
    )
    return mock_get_proj_config


@pytest.fixture()
def get_service_clients(mocker):
    region = project_config()["region"]
    service_clients = {}
    service_clients["sts_client"] = boto3.client("sts", region_name=region)
    service_clients["s3_client"] = boto3.client("s3", region_name=region)
    service_clients["greengrass_client"] = boto3.client(
        "greengrassv2", region_name=region
    )
    mocker.patch(
        "gdk.commands.component.project_utils.get_service_clients",
        return_value=service_clients,
    )
    mocker.patch.object(
        service_clients["sts_client"],
        "get_caller_identity",
        return_value={"Account": 1234},
    )
    mocker.patch.object(
        service_clients["s3_client"], "create_bucket", return_value=None
    )
    mocker.patch.object(service_clients["s3_client"], "upload_file", return_value=None)
    mocker.patch.object(
        service_clients["greengrass_client"],
        "create_component_version",
        return_value=None,
    )
    mocker.patch.object(
        service_clients["greengrass_client"],
        "list_component_versions",
        return_value={
            "componentVersions": [
                {"componentVersion": "1.0.4"},
                {"componentVersion": "1.0.1"},
            ]
        },
    )
    return service_clients


def test_publish_command_instantiation(mocker, mock_project_config):
    mock_check_if_arguments_conflict = mocker.patch.object(
        PublishCommand, "check_if_arguments_conflict", return_value=None
    )
    mock_run = mocker.patch.object(PublishCommand, "run", return_value=None)
    mock_get_service_clients = mocker.patch(
        "gdk.commands.component.project_utils.get_service_clients",
        return_value={"s3_client": None, "greengrass_client": None},
    )
    parse_args_actions.run_command(
        CLIParser.cli_parser.parse_args(["component", "publish"])
    )

    assert mock_project_config.call_count == 1
    assert mock_check_if_arguments_conflict.call_count == 1
    assert mock_run.call_count == 1
    assert mock_get_service_clients.call_count == 1


def test_publish_run_already_built(mocker, get_service_clients, mock_project_config):
    mock_build_dir_exists = mocker.patch(
        "gdk.common.utils.dir_exists",
        return_value=True,
    )
    pc = mock_project_config.return_value
    mock_iter_dir = mocker.patch(
        "pathlib.Path.iterdir", return_value=[Path("hello_world.py")]
    )
    file_name = (
        Path(pc["gg_build_recipes_dir"])
        .joinpath("{}-{}.json".format(pc["component_name"], pc["component_version"]))
        .resolve()
    )
    mock_transform = mocker.patch.object(PublishRecipeTransformer, "transform")
    spy_get_caller_identity = mocker.spy(
        get_service_clients["sts_client"], "get_caller_identity"
    )
    spy_create_bucket = mocker.patch.object(S3Client, "create_bucket")
    spy_upload_file = mocker.patch.object(
        get_service_clients["s3_client"], "upload_file"
    )
    spy_create_component = mocker.patch.object(
        get_service_clients["greengrass_client"], "create_component_version"
    )
    with patch("builtins.open", mock_open()) as mock_file:
        parse_args_actions.run_command(
            CLIParser.cli_parser.parse_args(["component", "publish"])
        )
        mock_file.assert_any_call(file_name)
    assert mock_build_dir_exists.call_count == 1  # Checks if build directory exists
    assert (
        mock_iter_dir.call_count == 1
    )  # Checks if there is at least one artifact to upload
    assert (
        mock_transform.call_count == 1
    )  # Checks if artifact in the recipe exist in the build directory

    # Assert cloud calls
    assert (
        spy_create_bucket.call_count == 1
    )  # Tries to create a bucket if at least one artifact needs to be uploaded
    spy_create_bucket.assert_called_with("default-us-east-1-1234", "us-east-1")
    assert spy_upload_file.call_count == 1  # Only one file to upload
    assert spy_create_component.call_count == 1  # Create gg private component
    assert spy_get_caller_identity.call_count == 1  # Get account number


def test_publish_run_with_bucket_argument(
    mocker, get_service_clients, mock_project_config
):
    mock_build_dir_exists = mocker.patch(
        "gdk.common.utils.dir_exists",
        return_value=True,
    )
    pc = mock_project_config.return_value
    mock_iter_dir = mocker.patch(
        "pathlib.Path.iterdir", return_value=[Path("hello_world.py")]
    )

    file_name = (
        Path(pc["gg_build_recipes_dir"])
        .joinpath("{}-{}.json".format(pc["component_name"], pc["component_version"]))
        .resolve()
    )
    mock_transform = mocker.patch.object(PublishRecipeTransformer, "transform")
    spy_get_caller_identity = mocker.spy(
        get_service_clients["sts_client"], "get_caller_identity"
    )
    spy_create_bucket = mocker.patch.object(S3Client, "create_bucket")
    spy_upload_file = mocker.patch.object(
        get_service_clients["s3_client"], "upload_file"
    )
    spy_create_component = mocker.patch.object(
        get_service_clients["greengrass_client"], "create_component_version"
    )
    with patch("builtins.open", mock_open()) as mock_file:
        parse_args_actions.run_command(
            CLIParser.cli_parser.parse_args(
                ["component", "publish", "-b", "new-bucket-arg"]
            )
        )
        mock_file.assert_any_call(file_name)
    assert mock_build_dir_exists.call_count == 1  # Checks if build directory exists
    assert (
        mock_iter_dir.call_count == 1
    )  # Checks if there is at least one artifact to upload
    assert (
        mock_transform.call_count == 1
    )  # Checks if artifact in the recipe exist in the build directory

    # Assert cloud calls
    assert (
        spy_create_bucket.call_count == 1
    )  # Tries to create a bucket if at least one artifact needs to be uploaded
    spy_create_bucket.assert_called_with(
        "new-bucket-arg", "us-east-1"
    )  # Use exact bucket arg
    assert spy_upload_file.call_count == 1  # Only one file to upload
    assert spy_create_component.call_count == 1  # Create gg private component
    assert spy_get_caller_identity.call_count == 1  # Get account number


def test_publish_run_with_all_arguments(
    mocker, get_service_clients, mock_project_config
):
    mock_build_dir_exists = mocker.patch(
        "gdk.common.utils.dir_exists",
        return_value=True,
    )
    pc = mock_project_config.return_value
    mock_iter_dir = mocker.patch(
        "pathlib.Path.iterdir", return_value=[Path("hello_world.py")]
    )
    mock_transform = mocker.patch.object(PublishRecipeTransformer, "transform")
    file_name = (
        Path(pc["gg_build_recipes_dir"])
        .joinpath("{}-{}.json".format(pc["component_name"], pc["component_version"]))
        .resolve()
    )

    spy_get_caller_identity = mocker.spy(
        get_service_clients["sts_client"], "get_caller_identity"
    )
    spy_create_bucket = mocker.patch.object(S3Client, "create_bucket")
    spy_upload_file = mocker.spy(get_service_clients["s3_client"], "upload_file")
    spy_create_component = mocker.spy(
        get_service_clients["greengrass_client"], "create_component_version"
    )
    with patch("builtins.open", mock_open()) as mock_file:
        parse_args_actions.run_command(
            CLIParser.cli_parser.parse_args(
                [
                    "component",
                    "publish",
                    "-b",
                    "new-bucket-arg",
                    "-r",
                    "us-west-2",
                    "-o",
                    '{"file_upload_args":{"ACL":"ABC"}}',
                ]
            )
        )
        mock_file.assert_any_call(file_name)
    assert mock_build_dir_exists.call_count == 1  # Checks if build directory exists
    assert (
        mock_iter_dir.call_count == 1
    )  # Checks if there is at least one artifact to upload
    assert (
        mock_transform.call_count == 1
    )  # Checks if artifact in the recipe exist in the build directory

    # Assert cloud calls
    assert (
        spy_create_bucket.call_count == 1
    )  # Tries to create a bucket if at least one artifact needs to be uploaded
    spy_create_bucket.assert_called_with(
        "new-bucket-arg", "us-west-2"
    )  # Use exact bucket arg
    spy_upload_file.assert_called_with(
        ANY,
        "new-bucket-arg",
        "component_name/1.0.0/hello_world.py",
        ExtraArgs={"ACL": "ABC"},
    )
    assert spy_upload_file.call_count == 1  # Only one file to upload
    assert spy_create_component.call_count == 1  # Create gg private component
    assert spy_get_caller_identity.call_count == 1  # Get account number


@pytest.mark.parametrize(
    "options_arg",
    ["file/path/not_exists.json"],
)
def test_publish_with_invalid_options_file_not_exists(
    mocker, options_arg, get_service_clients, mock_project_config
):
    mocker.patch(
        "gdk.common.utils.dir_exists",
        return_value=True,
    )
    if options_arg == "file_exists.json":
        mocker.patch(
            "gdk.common.utils.file_exists",
            return_value=True,
        )

    with pytest.raises(Exception) as e:
        with patch("builtins.open", mock_open()):
            parse_args_actions.run_command(
                CLIParser.cli_parser.parse_args(
                    [
                        "component",
                        "publish",
                        "-d",
                        "-b",
                        "new-bucket-arg",
                        "-r",
                        "us-west-2",
                        "-o",
                        options_arg,
                    ]
                )
            )
    assert (
        "The json file path provided in the command does not exist" in e.value.args[0]
    )


@pytest.mark.parametrize(
    "options_arg",
    ['{"missing":quotes"}'],
)
def test_publish_with_invalid_options(
    mocker, options_arg, get_service_clients, mock_project_config
):
    mocker.patch(
        "gdk.common.utils.dir_exists",
        return_value=True,
    )
    if options_arg == "file_exists.json":
        mocker.patch(
            "gdk.common.utils.file_exists",
            return_value=True,
        )

    with pytest.raises(Exception) as e:
        with patch("builtins.open", mock_open()):
            parse_args_actions.run_command(
                CLIParser.cli_parser.parse_args(
                    [
                        "component",
                        "publish",
                        "-d",
                        "-b",
                        "new-bucket-arg",
                        "-r",
                        "us-west-2",
                        "-o",
                        options_arg,
                    ]
                )
            )
    assert "JSON string is incorrectly formatted." in e.value.args[0]


@pytest.mark.parametrize(
    "options_arg_file_contents",
    ['{"missing""colon"}', '{"invalid_json_string":{"missing":quotes"}}'],
)
def test_publish_with_invalid_options_file(
    mocker, options_arg_file_contents, get_service_clients, mock_project_config
):
    mocker.patch(
        "gdk.common.utils.dir_exists",
        return_value=True,
    )
    mocker.patch(
        "gdk.common.utils.file_exists",
        return_value=True,
    )
    with pytest.raises(Exception) as e:
        with patch("builtins.open", mock_open(read_data=options_arg_file_contents)):
            parse_args_actions.run_command(
                CLIParser.cli_parser.parse_args(
                    [
                        "component",
                        "publish",
                        "-d",
                        "-b",
                        "new-bucket-arg",
                        "-r",
                        "us-west-2",
                        "-o",
                        "options_arg_file_contents.json",
                    ]
                )
            )
    assert "JSON string is incorrectly formatted." in e.value.args[0]


def test_publish_run_next_patch(mocker, get_service_clients, mock_project_config):
    mock_build_dir_exists = mocker.patch(
        "gdk.common.utils.dir_exists",
        return_value=True,
    )
    pc = mock_project_config.return_value
    pc["component_version"] = "NEXT_PATCH"
    mock_iter_dir = mocker.patch(
        "pathlib.Path.iterdir", return_value=[Path("hello_world.py")]
    )
    mock_transform = mocker.patch.object(PublishRecipeTransformer, "transform")
    # Next patch version based on test data
    file_name = (
        Path(pc["gg_build_recipes_dir"])
        .joinpath("{}-{}.json".format(pc["component_name"], "1.0.5"))
        .resolve()
    )

    spy_get_caller_identity = mocker.spy(
        get_service_clients["sts_client"], "get_caller_identity"
    )
    spy_create_bucket = mocker.patch.object(S3Client, "create_bucket")
    spy_upload_file = mocker.patch.object(
        get_service_clients["s3_client"], "upload_file"
    )
    spy_create_component = mocker.patch.object(
        get_service_clients["greengrass_client"], "create_component_version"
    )
    with patch("builtins.open", mock_open()) as mock_file:
        parse_args_actions.run_command(
            CLIParser.cli_parser.parse_args(["component", "publish"])
        )
        mock_file.assert_any_call(file_name)
    assert mock_build_dir_exists.call_count == 1  # Checks if build directory exists
    assert (
        mock_iter_dir.call_count == 1
    )  # Checks if there is at least one artifact to upload
    assert (
        mock_transform.call_count == 1
    )  # Checks if artifact in the recipe exist in the build directory

    # Assert cloud calls
    assert (
        spy_create_bucket.call_count == 1
    )  # Tries to create a bucket if at least one artifact needs to be uploaded
    spy_create_bucket.assert_called_with("default-us-east-1-1234", "us-east-1")
    assert spy_upload_file.call_count == 1  # Only one file to upload
    assert spy_create_component.call_count == 1  # Create gg private component
    assert spy_get_caller_identity.call_count == 1  # Get account number


def test_publish_run_next_patch_doesnt_exist(
    mocker, get_service_clients, mock_project_config
):
    mock_build_dir_exists = mocker.patch(
        "gdk.common.utils.dir_exists",
        return_value=True,
    )
    pc = mock_project_config.return_value
    pc["component_version"] = "NEXT_PATCH"
    mock_iter_dir = mocker.patch(
        "pathlib.Path.iterdir", return_value=[Path("hello_world.py")]
    )
    mock_transform = mocker.patch.object(PublishRecipeTransformer, "transform")
    # Next patch version based on test data
    file_name = (
        Path(pc["gg_build_recipes_dir"])
        .joinpath("{}-{}.json".format(pc["component_name"], "1.0.0"))
        .resolve()
    )
    mocker.patch.object(
        get_service_clients["greengrass_client"],
        "list_component_versions",
        return_value={"componentVersions": []},
    )
    spy_get_caller_identity = mocker.spy(
        get_service_clients["sts_client"], "get_caller_identity"
    )
    spy_create_bucket = mocker.patch.object(S3Client, "create_bucket")
    spy_upload_file = mocker.patch.object(
        get_service_clients["s3_client"], "upload_file"
    )
    spy_create_component = mocker.patch.object(
        get_service_clients["greengrass_client"], "create_component_version"
    )
    with patch("builtins.open", mock_open()) as mock_file:
        parse_args_actions.run_command(
            CLIParser.cli_parser.parse_args(["component", "publish"])
        )
        mock_file.assert_any_call(file_name)
    assert mock_build_dir_exists.call_count == 1  # Checks if build directory exists
    assert (
        mock_iter_dir.call_count == 1
    )  # Checks if there is at least one artifact to upload
    assert (
        mock_transform.call_count == 1
    )  # Checks if artifact in the recipe exist in the build directory

    # Assert cloud calls
    assert (
        spy_create_bucket.call_count == 1
    )  # Tries to create a bucket if at least one artifact needs to be uploaded
    spy_create_bucket.assert_called_with("default-us-east-1-1234", "us-east-1")
    assert spy_upload_file.call_count == 1  # Only one file to upload
    assert spy_create_component.call_count == 1  # Create gg private component
    assert spy_get_caller_identity.call_count == 1  # Get account number


def test_publish_run_not_built(mocker, get_service_clients, mock_project_config):
    mock_build_dir_exists = mocker.patch(
        "gdk.common.utils.dir_exists",
        return_value=False,
    )
    mock_build = mocker.patch(
        "gdk.commands.component.component.build", return_value=None
    )

    pc = mock_project_config.return_value
    mock_iter_dir = mocker.patch(
        "pathlib.Path.iterdir", return_value=[Path("hello_world.py")]
    )
    mock_transform = mocker.patch.object(PublishRecipeTransformer, "transform")
    file_name = (
        Path(pc["gg_build_recipes_dir"])
        .joinpath("{}-{}.json".format(pc["component_name"], pc["component_version"]))
        .resolve()
    )

    spy_get_caller_identity = mocker.spy(
        get_service_clients["sts_client"], "get_caller_identity"
    )
    spy_create_bucket = mocker.patch.object(S3Client, "create_bucket")
    spy_upload_file = mocker.patch.object(
        get_service_clients["s3_client"], "upload_file"
    )
    spy_create_component = mocker.patch.object(
        get_service_clients["greengrass_client"], "create_component_version"
    )
    with patch("builtins.open", mock_open()) as mock_file:
        parse_args_actions.run_command(
            CLIParser.cli_parser.parse_args(["component", "publish"])
        )
        mock_file.assert_any_call(file_name)
    assert mock_build_dir_exists.call_count == 1  # Checks if build directory exists
    assert mock_build.call_count == 1  # build the component first
    assert (
        mock_iter_dir.call_count == 1
    )  # Checks if there is at least one artifact to upload
    assert (
        mock_transform.call_count == 1
    )  # Checks if artifact in the recipe exist in the build directory

    # Assert cloud calls
    assert (
        spy_create_bucket.call_count == 1
    )  # Tries to create a bucket if at least one artifact needs to be uploaded
    assert spy_upload_file.call_count == 1  # Only one file to upload
    assert spy_create_component.call_count == 1  # Create gg private component
    assert spy_get_caller_identity.call_count == 1  # Get account number


def test_publish_run_error_during_upload(
    mocker, get_service_clients, mock_project_config
):
    mock_build_dir_exists = mocker.patch(
        "gdk.common.utils.dir_exists",
        return_value=True,
    )
    pc = mock_project_config.return_value
    mock_iter_dir = mocker.patch(
        "pathlib.Path.iterdir", return_value=[Path("hello_world.py")]
    )

    mock_glob = mocker.patch("pathlib.Path.glob", return_value=[Path("hello_world.py")])
    file_name = (
        Path(pc["gg_build_recipes_dir"])
        .joinpath("{}-{}.json".format(pc["component_name"], "1.0.0"))
        .resolve()
    )

    spy_get_caller_identity = mocker.spy(
        get_service_clients["sts_client"], "get_caller_identity"
    )
    spy_create_bucket = mocker.patch.object(S3Client, "create_bucket")
    spy_create_component = mocker.patch.object(
        get_service_clients["greengrass_client"], "create_component_version"
    )

    mocker.patch.object(
        get_service_clients["s3_client"],
        "upload_file",
        side_effect=Exception("Error in upload"),
    )
    with pytest.raises(Exception) as e:
        with patch("builtins.open", mock_open()) as mock_file:
            parse_args_actions.run_command(
                CLIParser.cli_parser.parse_args(["component", "publish"])
            )
            mock_file.assert_any_call(file_name, "w")
        assert "Error in upload" in e.args.value[0]
    assert mock_build_dir_exists.call_count == 1  # Checks if build directory exists
    assert (
        mock_iter_dir.call_count == 1
    )  # Checks if there is at least one artifact to upload
    assert mock_glob.call_count == 0  # Recipe is not updated

    # Assert cloud calls
    assert (
        spy_create_bucket.call_count == 1
    )  # Tries to create a bucket if at least one artifact needs to be uploaded
    spy_create_bucket.assert_called_with("default-us-east-1-1234", "us-east-1")
    assert spy_create_component.call_count == 0  # GG component is not created
    assert spy_get_caller_identity.call_count == 1  # Get account number


def test_publish_run_bucket_exists_owned_by_someone(
    mocker, get_service_clients, mock_project_config
):
    mock_build_dir_exists = mocker.patch(
        "gdk.common.utils.dir_exists",
        return_value=True,
    )
    pc = mock_project_config.return_value
    mock_iter_dir = mocker.patch(
        "pathlib.Path.iterdir", return_value=[Path("hello_world.py")]
    )

    mock_glob = mocker.patch("pathlib.Path.glob", return_value=[Path("hello_world.py")])
    # Next patch version based on test data
    file_name = (
        Path(pc["gg_build_recipes_dir"])
        .joinpath("{}-{}.json".format(pc["component_name"], "1.0.0"))
        .resolve()
    )

    spy_get_caller_identity = mocker.spy(
        get_service_clients["sts_client"], "get_caller_identity"
    )

    def throw_err(*args, **kwargs):
        ex = boto3.client("s3").exceptions.ClientError(
            {"Error": {"Code": "403", "Message": "Forbidden"}}, "GetBucketLocation"
        )
        raise ex

    mock_get_bucket_location = mocker.patch.object(
        S3Client, "valid_bucket_for_artifacts_exists", side_effect=throw_err
    )
    mock_create_bucket = mocker.patch.object(
        get_service_clients["s3_client"], "create_bucket"
    )
    spy_create_component = mocker.patch.object(
        get_service_clients["greengrass_client"], "create_component_version"
    )
    mocker.patch.object(
        get_service_clients["s3_client"], "upload_file", return_value=None
    )
    with pytest.raises(Exception) as e:
        with patch("builtins.open", mock_open()) as mock_file:
            parse_args_actions.run_command(
                CLIParser.cli_parser.parse_args(["component", "publish"])
            )
            mock_file.assert_any_call(file_name, "w")
        assert (
            "An error occurred (BucketAlreadyExists) when calling the CreateBucket operation: fake message"
            in e.value.args[0]
        )
    assert mock_build_dir_exists.call_count == 1  # Checks if build directory exists
    assert (
        mock_iter_dir.call_count == 1
    )  # Checks if there is at least one artifact to upload
    assert mock_glob.call_count == 0  # Recipe is not updated

    # Assert cloud calls
    assert (
        not mock_create_bucket.called
    )  # Tries to create a bucket if at least one artifact needs to be uploaded
    mock_get_bucket_location.assert_called_with("default-us-east-1-1234", "us-east-1")
    assert not spy_create_component.called  # GG component is not created
    assert spy_get_caller_identity.call_count == 1  # Get account number


def test_publish_run_bucket_already_owned_in_same_region(
    mocker, get_service_clients, mock_project_config
):
    mock_build_dir_exists = mocker.patch(
        "gdk.common.utils.dir_exists",
        return_value=True,
    )
    pc = mock_project_config.return_value
    mock_iter_dir = mocker.patch(
        "pathlib.Path.iterdir", return_value=[Path("hello_world.py")]
    )
    mock_transform = mocker.patch.object(PublishRecipeTransformer, "transform")
    file_name = (
        Path(pc["gg_build_recipes_dir"])
        .joinpath("{}-{}.json".format(pc["component_name"], "1.0.0"))
        .resolve()
    )

    spy_get_caller_identity = mocker.spy(
        get_service_clients["sts_client"], "get_caller_identity"
    )

    mock_get_bucket_location = mocker.patch.object(
        S3Client, "valid_bucket_for_artifacts_exists", return_value=True
    )
    mock_create_bucket = mocker.patch.object(
        get_service_clients["s3_client"], "create_bucket"
    )
    spy_create_component = mocker.patch.object(
        get_service_clients["greengrass_client"], "create_component_version"
    )

    with patch("builtins.open", mock_open()) as mock_file:
        parse_args_actions.run_command(
            CLIParser.cli_parser.parse_args(["component", "publish", "-d"])
        )
        mock_file.assert_any_call(file_name)
    assert mock_build_dir_exists.call_count == 1  # Checks if build directory exists
    assert (
        mock_iter_dir.call_count == 1
    )  # Checks if there is at least one artifact to upload
    assert mock_transform.call_count == 1  # Recipe is not updated

    # Assert cloud calls
    assert (
        not mock_create_bucket.called
    )  # Tries to create a bucket if at least one artifact needs to be uploaded
    assert spy_create_component.call_count == 1  # GG component is not created
    assert spy_get_caller_identity.call_count == 1  # Get account number
    mock_get_bucket_location.assert_called_with("default-us-east-1-1234", "us-east-1")


def project_config():
    return {
        "component_name": "component_name",
        "component_build_config": {"build_system": "zip"},
        "component_version": "1.0.0",
        "component_author": "abc",
        "bucket": "default",
        "region": "us-east-1",
        "options": {"what": "is"},
        "gg_build_directory": Path("/src/GDK-CLI-Internal/greengrass-build"),
        "gg_build_artifacts_dir": Path(
            "/src/GDK-CLI-Internal/greengrass-build/artifacts"
        ),
        "gg_build_recipes_dir": Path("/src/GDK-CLI-Internal/greengrass-build/recipes"),
        "gg_build_component_artifacts_dir": Path(
            "/src/GDK-CLI-Internal/greengrass-build/artifacts/component_name/1.0.0"
        ),
        "component_recipe_file": Path(
            "/src/GDK-CLI-Internal/tests/gdk/static/build_command/valid_component_recipe.json"
        ),
    }

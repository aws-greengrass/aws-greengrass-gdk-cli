import json
from pathlib import Path

import pytest

import gdk.common.validate_user_input_recipe as recipe
from gdk.common.exceptions import error_messages


def test_get_recipe_valid_recipe_found(mocker):
    expected_recipe = {
        "RecipeFormatVersion": "2020-01-25",
        "ComponentName": "com.example.HelloWorld",
        "ComponentVersion": "1.0.0",
        "ComponentDescription": "My first Greengrass component.",
        "ComponentPublisher": "Amazon",
        "ComponentConfiguration": {
            "DefaultConfiguration": {
                "Message": "world",
                "SampleList": [
                    "1",
                    "2",
                    "3"
                ],
                "SampleNestedList": [
                    [
                        "1"
                    ],
                    [
                        "2"
                    ],
                    [
                        "3"
                    ]
                ],
                "SampleMap": {
                    "key1": "value1",
                    "key2": {
                        "key3": [
                            "value2",
                            "value3"
                        ],
                        "key4": {
                            "key41": "value4"
                        }
                    }
                }
            }
        },
        "Manifests": [
            {
                "Platform": {
                    "os": "linux"
                },
                "Lifecycle": {
                    "Run": "python3 -u {artifacts:path}/hello_world.py '{configuration:/Message}'"
                },
                "Artifacts": [
                    {
                        "URI": "s3://DOC-EXAMPLE-BUCKET/artifacts/com.example.HelloWorld/1.0.0/hello_world.py"
                    }
                ]
            }
        ]
    }

    mock_get_recipe_file = mocker.patch(
        "gdk.common.validate_user_input_recipe.get_user_input_recipe_file",
        return_value=Path(".").joinpath("tests/gdk/static/project_utils").joinpath("valid_component_recipe.json"),
    )

    assert recipe.get_recipe() == expected_recipe
    assert mock_get_recipe_file.called


def test_get_recipe_invalid_recipe_file(mocker):
    mock_get_recipe_file = mocker.patch(
        "gdk.common.validate_user_input_recipe.get_user_input_recipe_file",
        return_value=Path(".").joinpath("tests/gdk/static/project_utils").joinpath("invalid_component_recipe.json"),
    )

    with pytest.raises(SystemExit) as exit_info:
        recipe.get_recipe()

    assert mock_get_recipe_file.called
    # Assert that the exit code is 1
    assert exit_info.type == SystemExit
    assert exit_info.value.code == 1


def test_no_recipe_file_exists(mocker):
    mock_file_exists = mocker.patch("gdk.common.utils.file_exists", return_value=False)

    with pytest.raises(Exception) as err:
        recipe.get_user_input_recipe_file()
        assert err.value.args[0] == error_messages.USER_INPUT_RECIPE_NOT_EXISTS
        assert mock_file_exists.called


def test_both_recipe_file_exists(mocker):
    mock_file_exists = mocker.patch("gdk.common.utils.file_exists", return_value=True)

    with pytest.raises(Exception) as err:
        recipe.get_user_input_recipe_file()
        assert err.value.args[0] == error_messages.MULTIPLE_INPUT_RECIPES_EXIST
        assert mock_file_exists.called


# Mock the open function and its return value
@pytest.fixture
def mock_open(mocker):
    m = mocker.mock_open()
    m.return_value.__iter__ = lambda self: self
    m.return_value.__next__ = lambda self: self.readline()
    return m


def test_validate_recipe_syntax_invalid_json(mocker, mock_open):
    invalid_json_content = '{"key": "value"'
    mock_open(invalid_json_content)
    mocker.patch("builtins.open", mock_open)

    with pytest.raises(SystemExit) as e:
        recipe.validate_recipe_syntax("invalid_recipe.json")

    assert e.type == SystemExit
    assert e.value.code == 1


def test_parse_json_error(caplog):
    error_message = "Expecting property name enclosed in double quotes: line 1 column 3 (char 2)"
    recipe.parse_json_error(json.JSONDecodeError(error_message, "", 1))
    assert "Expecting property name enclosed in double quotes" in caplog.text
    assert "line 1" in caplog.text
    assert "If none of the above is the cause, please review the overall JSON syntax and resolve any issues." in caplog.text

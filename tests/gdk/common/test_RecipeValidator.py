from pathlib import Path
from unittest import TestCase, mock

import pytest
import yaml
import json
import os

from jsonschema import validate, exceptions

from gdk.common.CaseInsensitive import CaseInsensitiveDict
from gdk.common.RecipeValidator import RecipeValidator


class RecipeValidatorTest(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker):
        self.mocker = mocker

    def test_validate_missing_recipe_format_version_expect_exception(self):
        mock_logging_error = self.mocker.patch('logging.error')
        invalid_recipe = CaseInsensitiveDict({})
        validator = RecipeValidator(invalid_recipe)
        with pytest.raises(Exception) as e:
            validator.validate_recipe_format_version()
        self.assertEqual(str(e.value), "The recipe file is invalid. The 'RecipeFormatVersion' field is mandatory in "
                                       "the recipe.")
        mock_logging_error.assert_called_with("Recipe validation failed for 'RecipeFormatVersion'. This field is "
                                              "required but missing from the recipe. Please correct it and try again.")

    def test_validate_invalid_recipe_format_version_expect_exception(self):
        mock_logging_error = self.mocker.patch('logging.error')
        invalid_recipe = CaseInsensitiveDict({"RecipeFormatVersion": "99999"})
        validator = RecipeValidator(invalid_recipe)
        with pytest.raises(Exception) as e:
            validator.validate_recipe_format_version()
        self.assertEqual(str(e.value), "The provided RecipeFormatVersion in the recipe is invalid. Please ensure that "
                                       "it follows the correct format and matches one of the supported versions.")
        mock_logging_error.assert_called_with("The provided RecipeFormatVersion '99999' is not supported in this gdk "
                                              "version. Please ensure that it is a valid RecipeFormatVersion "
                                              "compatible with the gdk, and refer to the list of supported "
                                              "RecipeFormatVersion: ['2020-01-25'].")

    def test_validate_semantics_valid_recipe(self):
        valid_recipe = CaseInsensitiveDict({
            "manifests": [{"artifacts": [{"uri": "example"}]}],
            "componentconfiguration": {"defaultconfiguration": {"message": "Hello"}}
        })
        validator = RecipeValidator(valid_recipe)
        with mock.patch('gdk.common.RecipeValidator.jsonschema.validate') as mock_validate:
            validator.validate_semantics()
        mock_validate.assert_called_once()

    def test_validate_semantics_invalid_recipe(self):
        invalid_recipe = CaseInsensitiveDict({
            "manifests": [{"artifacts": [{"uri": "example"}]}],
            "componentconfiguration": {"defaultconfiguration": {"message": 123}}
        })
        validator = RecipeValidator(invalid_recipe)
        with pytest.raises(exceptions.ValidationError):
            validator.validate_semantics()

    def test_validate_input_specify_component_type_expect_warning(self):
        recipe_data = CaseInsensitiveDict({
            "ComponentName": "example",
            "RecipeFormatVersion": "2020-01-25",
            "ComponentType": "aws.greengrass.generic"
        })
        validator = RecipeValidator(recipe_data)
        with mock.patch('gdk.common.RecipeValidator.logging') as mock_logging:
            validator.validate_input()
        assert mock_logging.warning.call_count == 1
        warnings = mock_logging.warning.call_args[0]
        expected_warnings = "It's not recommended to specify the component type in a recipe. " \
                            "AWS IoT Greengrass sets the type for you when you create a component."
        assert any(expected_warnings in arg for arg in warnings)

    def test_validate_input_specify_component_source_expect_warning(self):
        recipe_data = CaseInsensitiveDict({
            "ComponentName": "example",
            "RecipeFormatVersion": "2020-01-25",
            "ComponentSource": "arn:aws:lambda:us-east-1:123456789012:function:example-function"
        })
        validator = RecipeValidator(recipe_data)
        with mock.patch('gdk.common.RecipeValidator.logging') as mock_logging:
            validator.validate_input()
        assert mock_logging.warning.call_count == 1
        warnings = mock_logging.warning.call_args[0]
        expected_warnings = "It's not recommended to specify the component source in a recipe. " \
                            "AWS IoT Greengrass sets this parameter for you when you create a " \
                            "component from a Lambda function."
        assert any(expected_warnings in arg for arg in warnings)

    def test_validate_input_specify_both_startup_and_run_expect_warning(self):
        recipe_data = CaseInsensitiveDict({
            "ComponentName": "example",
            "RecipeFormatVersion": "2020-01-25",
            "lifecycle": {
                "startup": {},
                "run": {}
            }
        })
        validator = RecipeValidator(recipe_data)
        with mock.patch('gdk.common.RecipeValidator.logging') as mock_logging:
            validator.validate_input()
        assert mock_logging.warning.call_count == 1
        warnings = mock_logging.warning.call_args[0]
        expected_warnings = "You can define only one startup or run lifecycle in a recipe. " \
                            "Defining both may lead to unexpected behavior."
        assert any(expected_warnings in arg for arg in warnings)

    def test_validate_input_non_s3_uri_expect_warning(self):
        recipe_data = CaseInsensitiveDict({
            "ComponentName": "example",
            "RecipeFormatVersion": "2020-01-25",
            "Manifests": [{
                "Artifacts": [
                    {
                        "URI": "https://example.com/file.txt"
                    }
                ]
            }]
        })
        validator = RecipeValidator(recipe_data)
        with mock.patch('gdk.common.RecipeValidator.logging') as mock_logging:
            validator.validate_input()
        assert mock_logging.warning.call_count == 1
        warnings = mock_logging.warning.call_args[0]
        expected_warnings = "The provided URI 'https://example.com/file.txt' in the recipe is not an S3 bucket."
        assert any(expected_warnings in arg for arg in warnings)

    def test_validate_input_script_does_not_match_artifact_uri_expect_warning(self):
        recipe_data = CaseInsensitiveDict({
            "ComponentName": "example",
            "RecipeFormatVersion": "2020-01-25",
            "Manifests": [{
                "Artifacts": [
                    {
                        "URI": "s3://greengrasscomponent/sample.py"
                    }
                ],
                "LifeCycle": {
                    "Run": "python3 {artifacts:path}/sample555.py '{configuration:/Message}'"
                }
            }]
        })
        validator = RecipeValidator(recipe_data)
        with mock.patch('gdk.common.RecipeValidator.logging') as mock_logging:
            validator.validate_input()
        assert mock_logging.warning.call_count == 1
        warnings = mock_logging.warning.call_args[0]
        expected_warnings = "The filename in the script does not match the artifact names in the URI provided in the " \
                            "recipe. If this is inaccurate, please exit and verify that both the artifacts and the " \
                            "script are correct."
        assert any(expected_warnings in arg for arg in warnings)

    def test_validate_input_script_in_run_does_not_match_artifact_uri_expect_warning(self):
        recipe_data = CaseInsensitiveDict({
            "ComponentName": "example",
            "RecipeFormatVersion": "2020-01-25",
            "Manifests": [{
                "Artifacts": [
                    {
                        "URI": "s3://greengrasscomponent/sample.py"
                    }
                ],
                "LifeCycle": {
                    "Run": {
                        "Script": "python3 {artifacts:path}/sample555.py '{configuration:/Message}'"
                    }
                }
            }]
        })
        validator = RecipeValidator(recipe_data)
        with mock.patch('gdk.common.RecipeValidator.logging') as mock_logging:
            validator.validate_input()
        assert mock_logging.warning.call_count == 1
        warnings = mock_logging.warning.call_args[0]
        expected_warnings = "The filename in the script does not match the artifact names in the URI provided in the " \
                            "recipe. If this is inaccurate, please exit and verify that both the artifacts and the " \
                            "script are correct."
        assert any(expected_warnings in arg for arg in warnings)

    def test_validate_input_mismatched_platform_architecture_expect_warning(self):
        recipe_data = CaseInsensitiveDict({
            "ComponentName": "example",
            "RecipeFormatVersion": "2020-01-25",
            "Manifests": [{
                "Platform": {
                    "os": "linux",
                    "architecture": "unknown_architecture"
                }
            }]
        })
        validator = RecipeValidator(recipe_data)
        with mock.patch('gdk.common.RecipeValidator.logging') as mock_logging:
            validator.validate_input()
        assert mock_logging.warning.call_count == 1
        warnings = mock_logging.warning.call_args[0]
        expected_warnings = "The specified architecture 'unknown_architecture' may not be supported by the os " \
                            "'linux' as provided in the recipe."
        assert any(expected_warnings in arg for arg in warnings)

    def test_validate_input_specify_both_startup_and_run_in_manifests_lifecycle_expect_warning(self):
        recipe_data = CaseInsensitiveDict({
            "ComponentName": "example",
            "RecipeFormatVersion": "2020-01-25",
            "Manifests": [{
                "Platform": {
                    "os": "linux",
                    "architecture": "x86"
                },
                "LifeCycle": {
                    "Startup": {},
                    "Run": {}
                }
            }]
        })
        validator = RecipeValidator(recipe_data)
        with mock.patch('gdk.common.RecipeValidator.logging') as mock_logging:
            validator.validate_input()
        assert mock_logging.warning.call_count == 1
        warnings = mock_logging.warning.call_args[0]
        expected_warnings = "You can define only one startup or run lifecycle in the recipe manifest. " \
                            "Defining both may result in unexpected behavior."
        assert any(expected_warnings in arg for arg in warnings)

    def test_validate_input_expect_multiple_warnings(self):
        recipe_data = CaseInsensitiveDict({
            "ComponentType": "aws.greengrass.generic",
            "ComponentSource": "arn:aws:lambda:us-east-1:123456789012:function:example-function",
            "LifeCycle": {
                "startup": {},
                "run": {}
            },
            "Manifests": [
                {
                    "Platform": {
                        "os": "linux",
                        "architecture": "unknown"
                    },
                    "Artifacts": [
                        {"uri": "s3://example-bucket/file.txt"},
                        {"uri": "s4://example-bucket/file.txt"}],
                    "LifeCycle": {
                        "Run": {
                            "Script": "python3 -u {artifacts:decompressedPath}/HelloWorld/hello_world.py"
                        }
                    }
                },
                {
                    "Platform": {
                        "os": "macos",
                        "architecture": "x86"
                    },
                }
            ]
        })
        validator = RecipeValidator(recipe_data)
        with mock.patch('gdk.common.RecipeValidator.logging') as mock_logging:
            validator.validate_input()
        assert mock_logging.warning.call_count == 7
        warning_list = mock_logging.warning.call_args_list
        expected_warnings = [
            "It's not recommended to specify the component type in a recipe.",
            "It's not recommended to specify the component source in a recipe.",
            "You can define only one startup or run lifecycle in a recipe.",
            "The provided URI 's4://example-bucket/file.txt' in the recipe is not an S3 bucket.",
            "The filename in the script does not match the artifact names in the URI provided in the recipe.",
            "The specified architecture 'x86' may not be supported by the os 'macos' as provided in the recipe.",
            "The specified architecture 'unknown' may not be supported by the os 'linux' as provided in the recipe."
        ]
        for expected_warning in expected_warnings:
            assert any(expected_warning in str(arg) for arg in warning_list)

    def test_validate_input_expect_no_warnings(self):
        recipe_data = CaseInsensitiveDict({
            "RecipeFormatVersion": "2020-01-25",
            "ComponentName": "{COMPONENT_NAME}",
            "ComponentVersion": "{COMPONENT_VERSION}",
            "Manifests": [
                {
                    "Platform": {
                        "os": "*",
                        "architecture": "arm"
                    },
                    "Lifecycle": {
                        "Run": "java -jar {artifacts:path}/aws.greengrass.example.jar"
                    },
                    "Artifacts": [
                        {
                            "URI": "s3://aws.greengrass.example.jar"
                        }
                    ]
                }
            ]
        })
        validator = RecipeValidator(recipe_data)
        with mock.patch('gdk.common.RecipeValidator.logging') as mock_logging:
            validator.validate_input()
        assert mock_logging.warning.call_count == 0

    def test_convert_keys_to_lowercase_dict(self):
        input_dict = CaseInsensitiveDict({
            "Key1": "Value1",
            "Key2": {
                "SubKey1": "SubValue1",
                "SubKey2": "SubValue2"
            }
        })
        expected_output = {
            "key1": "Value1",
            "key2": {
                "subkey1": "SubValue1",
                "subkey2": "SubValue2"
            }
        }
        validator = RecipeValidator(CaseInsensitiveDict())
        output = validator._convert_keys_to_lowercase(input_dict)
        assert output == expected_output

    def test_convert_keys_to_lowercase_list(self):
        input_list = [
            CaseInsensitiveDict({"Key1": "Value1"}),
            CaseInsensitiveDict({"Key2": "Value2"})
        ]
        expected_output = [
            {"key1": "Value1"},
            {"key2": "Value2"}
        ]
        validator = RecipeValidator(CaseInsensitiveDict())
        output = validator._convert_keys_to_lowercase(input_list)
        assert output == expected_output

    def test_convert_keys_to_lowercase_mixed(self):
        input_mixed = CaseInsensitiveDict({
            "Key1": [
                {"SubKey1": "SubValue1"},
                {"SubKey2": "SubValue2"}
            ],
            "Key2": "Value2"
        })
        expected_output = {
            "key1": [
                {"subkey1": "SubValue1"},
                {"subkey2": "SubValue2"}
            ],
            "key2": "Value2"
        }
        validator = RecipeValidator(CaseInsensitiveDict())
        output = validator._convert_keys_to_lowercase(input_mixed)
        assert output == expected_output

    def test_load_from_file_json(self):
        json_file = Path(".").joinpath("tests/gdk/static/project_utils").joinpath(
            "valid_component_recipe.json").resolve()
        validator = RecipeValidator(json_file)
        recipe_data = validator._load_recipe()
        assert isinstance(recipe_data, CaseInsensitiveDict)
        assert "manifests" in recipe_data
        assert "artifacts" in recipe_data["manifests"][0]

    def test_load_from_file_invalid_json(self):
        json_file = Path(".").joinpath("tests/gdk/static/project_utils").joinpath(
            "invalid_component_recipe.json").resolve()

        with pytest.raises(json.JSONDecodeError) as e:
            RecipeValidator(json_file)

        assert isinstance(e.value, json.JSONDecodeError)

    def test_load_from_yaml(self):
        yaml_file = Path(".").joinpath("tests/gdk/static/project_utils").joinpath(
            "valid_component_recipe.yaml"
        ).resolve()
        validator = RecipeValidator(yaml_file)
        recipe_data = validator._load_recipe()
        assert isinstance(recipe_data, CaseInsensitiveDict)
        assert "componentconfiguration" in recipe_data
        assert "defaultconfiguration" in recipe_data["componentconfiguration"]
        assert "message" in recipe_data["componentconfiguration"]["defaultconfiguration"]

    def test_load_from_invalid_yaml(self):
        yaml_file = Path(".").joinpath("tests/gdk/static/project_utils").joinpath(
            "invalid_component_recipe.yaml"
        ).resolve()

        with pytest.raises(yaml.YAMLError) as e:
            RecipeValidator(yaml_file)

        assert isinstance(e.value, yaml.YAMLError)

    def test_load_from_file_invalid_format(self):
        invalid_file = Path(".").joinpath("tests/gdk/static/project_utils").joinpath("not_exists.txt").resolve()

        with pytest.raises(Exception) as e:
            RecipeValidator(invalid_file)
        assert "Recipe file must be in json or yaml format" in e.value.args[0]

    def test_load_from_dict(self):
        recipe_data = CaseInsensitiveDict({
            "manifests": [{"artifacts": [{"uri": "example"}]}]
        })
        validator = RecipeValidator(recipe_data)
        loaded_data = validator._load_recipe()
        assert loaded_data == recipe_data

    def test_load_from_invalid_type(self):
        invalid_data = "invalid_data"

        with pytest.raises(ValueError) as e:
            RecipeValidator(invalid_data)
        assert "Invalid recipe source type" in e.value.args[0]


# =========================== Tests for recipe schema ===========================

# Load the JSON schema
with open('gdk/static/user_input_recipe_schema.json', 'r') as schema_file:
    schema = json.load(schema_file)

# Get the list of valid recipe files
valid_recipe_files_json = [
    os.path.join('tests/gdk/static/sample_recipes', filename)
    for filename in os.listdir('tests/gdk/static/sample_recipes')
    if filename.startswith('recipe') and filename.endswith('.json')
]
valid_recipe_files_yaml = [
    os.path.join('tests/gdk/static/sample_recipes', filename)
    for filename in os.listdir('tests/gdk/static/sample_recipes')
    if filename.startswith('recipe') and filename.endswith('.yaml')
]
# Get the list of invalid recipe files
invalid_recipe_files = [
    os.path.join('tests/gdk/static/sample_recipes', filename)
    for filename in os.listdir('tests/gdk/static/sample_recipes')
    if filename.startswith('invalid') and filename.endswith('.json')
]


# Function to recursively convert keys to lowercase
def convert_keys_to_lowercase(input_dict):
    if isinstance(input_dict, dict):
        return {key.lower(): convert_keys_to_lowercase(value) for key, value in input_dict.items()}
    elif isinstance(input_dict, list):
        return [convert_keys_to_lowercase(item) for item in input_dict]
    else:
        return input_dict


# Define the test function
@pytest.mark.parametrize("recipe_file", valid_recipe_files_json)
def test_valid_recipes_json(recipe_file):
    with open(recipe_file, 'r') as recipe_file:
        recipe_data = json.load(recipe_file)
        validate(instance=convert_keys_to_lowercase(recipe_data), schema=schema)


@pytest.mark.parametrize("recipe_file", valid_recipe_files_yaml)
def test_valid_recipes_yaml(recipe_file):
    with open(recipe_file, 'r') as recipe_file:
        recipe_data = yaml.safe_load(recipe_file)
        validate(instance=convert_keys_to_lowercase(recipe_data), schema=schema)


@pytest.mark.parametrize("recipe_file", invalid_recipe_files)
def test_invalid_recipes_raise_error(recipe_file):
    with open(recipe_file, 'r') as recipe_file:
        recipe_data = json.load(recipe_file)
        with pytest.raises(exceptions.ValidationError):
            validate(instance=convert_keys_to_lowercase(recipe_data), schema=schema)

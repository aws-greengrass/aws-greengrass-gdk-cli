from pathlib import Path
from unittest import TestCase

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
        validator = RecipeValidator(json_file)
        with pytest.raises(SystemExit) as e:
            validator._load_recipe()

        assert e.type == SystemExit
        assert e.value.code == 1

    def test_load_from_file_invalid_format(self):
        invalid_file = Path(".").joinpath("tests/gdk/static/project_utils").joinpath("not_exists.txt").resolve()
        validator = RecipeValidator(invalid_file)
        with pytest.raises(Exception) as e:
            validator._load_recipe()
        assert "Recipe file must be in json or yaml format" in e.value.args[0]

    def test_load_from_dict(self):
        recipe_data = {
            "manifests": [{"artifacts": [{"uri": "example"}]}]
        }
        validator = RecipeValidator(recipe_data)
        loaded_data = validator._load_recipe()
        assert loaded_data == recipe_data

    def test_load_from_invalid_type(self):
        invalid_data = "invalid_data"
        validator = RecipeValidator(invalid_data)
        with pytest.raises(ValueError) as e:
            validator._load_recipe()
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

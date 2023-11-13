from unittest import TestCase

import pytest

import gdk.common.consts as consts
import gdk.common.utils as utils
from gdk.common.RecipeValidator import RecipeValidator


class RecipeValidatorTest(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker):
        self.mocker = mocker

    def test_GIVEN_valid_recipe_WHEN_validate_recipe_THEN_no_exceptions(self):
        valid_recipe_object = {
            "recipeformatversion": "2020-01-25",
            "componentname": "com.example.hello",
            "componentpublisher": "Me",
            "componentversion": "1.0.0",
            "manifests": [
                {
                    "Lifecycle": {
                      "run": "echo Hello"
                    }
                }
            ]
        }
        schema = utils.get_static_file_path(consts.recipe_schema_file)
        validator = RecipeValidator(schema)
        validator.validate_recipe(valid_recipe_object)

    def test_GIVEN_invalid_recipe_WHEN_validate_recipe_THEN_raise_exception(self):
        invalid_recipe_object = {
            "recipeformatversion": "202-01-25",
            "componentname": "com.example.hello",
            "componentpublisher": "Me",
            "componentversion": "1.0.0",
            "manifests": [
                {
                    "Lifecycle": {
                      "run": "echo Hello"
                    }
                }
            ]
        }
        schema = utils.get_static_file_path(consts.recipe_schema_file)
        validator = RecipeValidator(schema)
        with pytest.raises(Exception) as e:
            validator.validate_recipe(invalid_recipe_object)
        assert "ValidationError" in str(e)

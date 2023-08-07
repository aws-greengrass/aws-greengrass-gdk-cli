from pathlib import Path
from unittest import TestCase

import pytest

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
        print(recipe_data)
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

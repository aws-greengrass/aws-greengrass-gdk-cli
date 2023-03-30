from pathlib import Path
from unittest import TestCase
import tempfile
import pytest

from gdk.common.recipe_file.Recipe import Recipe


class RecipeTest(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker):
        self.mocker = mocker

    def test_read_json(self):
        json_file = Path(".").joinpath("tests/gdk/static/project_utils").joinpath("valid_component_recipe.json").resolve()
        assert isinstance(Recipe().read(json_file), dict)

    def test_read_yaml(self):
        yaml_file = Path(".").joinpath("tests/gdk/static/project_utils").joinpath("valid_component_recipe.yaml").resolve()
        assert isinstance(Recipe().read(yaml_file), dict)

    def test_read_invalid_format(self):
        invalid_file = Path(".").joinpath("tests/gdk/static/project_utils").joinpath("not_exists.txt").resolve()
        with pytest.raises(Exception) as e:
            Recipe().read(invalid_file)
        assert "Recipe file must be in json or yaml format" in e.value.args[0]

    def test_write_json(self):
        json_file = Path(".").joinpath("tests/gdk/static/project_utils").joinpath("valid_component_recipe.json").resolve()
        with tempfile.TemporaryDirectory() as newDir:
            tmp_path = Path(newDir).joinpath("valid.json").resolve()
            Recipe().write(tmp_path, Recipe().read(json_file))
            assert Recipe().read(json_file) == Recipe().read(tmp_path)

    def test_write_yaml(self):
        yaml_file = Path(".").joinpath("tests/gdk/static/project_utils").joinpath("valid_component_recipe.yaml").resolve()
        with tempfile.TemporaryDirectory() as newDir:
            tmp_path = Path(newDir).joinpath("valid.yaml").resolve()
            Recipe().write(tmp_path, Recipe().read(yaml_file))
            assert Recipe().read(yaml_file) == Recipe().read(tmp_path)

    def test_write_invalid_format(self):
        with tempfile.TemporaryDirectory() as newDir:
            yaml_file = Path(".").joinpath("tests/gdk/static/project_utils").joinpath("valid_component_recipe.yaml").resolve()
            contents = Recipe().read(yaml_file)
            tmp_path = Path(newDir).joinpath("invalid.txt").resolve()
            with pytest.raises(Exception) as e:
                Recipe().write(tmp_path, contents)
            assert "Recipe file must be in json or yaml format" in e.value.args[0]

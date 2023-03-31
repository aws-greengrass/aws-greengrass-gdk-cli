from pathlib import Path
from unittest import TestCase
import tempfile
import pytest

from gdk.common.recipe_file.CaseInsensitiveRecipeFile import CaseInsensitiveRecipeFile

from requests.structures import CaseInsensitiveDict


class CaseInsensitiveRecipeFileTest(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker):
        self.mocker = mocker

    def test_read_json(self):
        json_file = Path(".").joinpath("tests/gdk/static/project_utils").joinpath("valid_component_recipe.json").resolve()
        case_insensitive_recipe = CaseInsensitiveRecipeFile().read(json_file)
        assert isinstance(CaseInsensitiveRecipeFile().read(json_file), CaseInsensitiveDict)
        assert "manifests" in case_insensitive_recipe
        assert "MANIFESTS" in case_insensitive_recipe
        assert "artifacts" in case_insensitive_recipe["manifests"][0]
        assert "ARTIFACTS" in case_insensitive_recipe["manifests"][0]
        assert "uri" in case_insensitive_recipe["Manifests"][0]["Artifacts"][0]
        assert "URI" in case_insensitive_recipe["Manifests"][0]["Artifacts"][0]

    def test_read_yaml(self):
        yaml_file = Path(".").joinpath("tests/gdk/static/project_utils").joinpath("valid_component_recipe.yaml").resolve()
        case_insensitive_recipe = CaseInsensitiveRecipeFile().read(yaml_file)
        assert isinstance(case_insensitive_recipe, CaseInsensitiveDict)
        assert "manifests" in case_insensitive_recipe
        assert "MANIFESTS" in case_insensitive_recipe
        assert "artifacts" in case_insensitive_recipe["manifests"][0]
        assert "ARTIFACTS" in case_insensitive_recipe["manifests"][0]
        assert "uri" in case_insensitive_recipe["Manifests"][0]["Artifacts"][0]
        assert "URI" in case_insensitive_recipe["Manifests"][0]["Artifacts"][0]

    def test_read_invalid_format(self):
        invalid_file = Path(".").joinpath("tests/gdk/static/project_utils").joinpath("not_exists.txt").resolve()
        with pytest.raises(Exception) as e:
            CaseInsensitiveRecipeFile().read(invalid_file)
        assert "Recipe file must be in json or yaml format" in e.value.args[0]

    def test_write_json(self):
        json_file = Path(".").joinpath("tests/gdk/static/project_utils").joinpath("valid_component_recipe.json").resolve()
        with tempfile.TemporaryDirectory() as newDir:
            tmp_path = Path(newDir).joinpath("valid.json").resolve()
            CaseInsensitiveRecipeFile().write(tmp_path, CaseInsensitiveRecipeFile().read(json_file))

    def test_write_yaml(self):
        yaml_file = Path(".").joinpath("tests/gdk/static/project_utils").joinpath("valid_component_recipe.yaml").resolve()
        with tempfile.TemporaryDirectory() as newDir:
            tmp_path = Path(newDir).joinpath("valid.yaml").resolve()
            CaseInsensitiveRecipeFile().write(tmp_path, CaseInsensitiveRecipeFile().read(yaml_file))

    def test_write_invalid_format(self):
        with tempfile.TemporaryDirectory() as newDir:
            yaml_file = Path(".").joinpath("tests/gdk/static/project_utils").joinpath("valid_component_recipe.yaml").resolve()
            contents = CaseInsensitiveRecipeFile().read(yaml_file)
            tmp_path = Path(newDir).joinpath("invalid.txt").resolve()
            with pytest.raises(Exception) as e:
                CaseInsensitiveRecipeFile().write(tmp_path, contents)
            assert "Recipe file must be in json or yaml format" in e.value.args[0]

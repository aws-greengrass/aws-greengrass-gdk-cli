import json
import logging
import tempfile
from pathlib import Path
from unittest import TestCase

import pytest
import yaml

from gdk.common.CaseInsensitive import (CaseInsensitiveDict,
                                        CaseInsensitiveRecipeFile)


class CaseInsensitiveRecipeFileTest(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker):
        self.mocker = mocker

    @pytest.fixture(autouse=True)
    def caplog(self, caplog):
        self.caplog = caplog

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

    def test_GIVEN_json_recipe_file_with_syntax_err_WHEN_read_recipe_THEN_throw_err_logging_and_exception(self):
        self.caplog.set_level(logging.ERROR)
        json_file = Path(".").joinpath("tests/gdk/static/project_utils").joinpath("recipe_missing_comma.json").resolve()
        with pytest.raises(Exception) as e:
            CaseInsensitiveRecipeFile().read(json_file)
        logs = self.caplog.text
        assert "For information and examples regarding component recipes refer to the docs here" in logs
        assert "Expecting ',' delimiter: line 6 column 3" in str(e)

    def test_GIVEN_yaml_recipe_file_with_syntax_err_WHEN_read_recipe_THEN_throw_err_logging_and_exception(self):
        self.caplog.set_level(logging.ERROR)
        yaml_file = Path(".").joinpath("tests/gdk/static/project_utils").joinpath("invalid_component_recipe.yaml").resolve()
        with pytest.raises(Exception) as e:
            CaseInsensitiveRecipeFile().read(yaml_file)
        logs = self.caplog.text
        assert "For information and examples regarding component recipes refer to the docs here" in logs
        assert "expected <block end>, but found '<block mapping start>'" in str(e)

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
            with open(json_file, "r") as original_yaml:
                with open(tmp_path, "r") as updated_yaml:
                    assert json.loads(original_yaml.read()) == json.loads(updated_yaml.read())

    def test_write_yaml(self):
        yaml_file = Path(".").joinpath("tests/gdk/static/project_utils").joinpath("valid_component_recipe.yaml").resolve()
        with tempfile.TemporaryDirectory() as newDir:
            tmp_path = Path(newDir).joinpath("valid.yaml").resolve()
            CaseInsensitiveRecipeFile().write(tmp_path, CaseInsensitiveRecipeFile().read(yaml_file))
            with open(yaml_file, "r") as original_yaml:
                with open(tmp_path, "r") as updated_yaml:
                    assert yaml.safe_load(original_yaml.read()) == yaml.safe_load(updated_yaml.read())

    def test_write_invalid_format(self):
        with tempfile.TemporaryDirectory() as newDir:
            yaml_file = Path(".").joinpath("tests/gdk/static/project_utils").joinpath("valid_component_recipe.yaml").resolve()
            contents = CaseInsensitiveRecipeFile().read(yaml_file)
            tmp_path = Path(newDir).joinpath("invalid.txt").resolve()
            with pytest.raises(Exception) as e:
                CaseInsensitiveRecipeFile().write(tmp_path, contents)
            assert "Recipe file must be in json or yaml format" in e.value.args[0]


class CaseInsensitiveDictTest(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker):
        self.mocker = mocker

    def test_convert_dict_to_CaseInsensitiveDict(self):
        dictionary = {
            "key1": "value1",
            "key2": [{"key21": "value21"}, {"key22": "value22"}],
            "key3": {"key31": {"key311": "key312"}},
            "key4": ["entry1", "entry2"]
        }
        cis = CaseInsensitiveDict(dictionary)
        assert "KEY1" in cis
        assert cis["KEY2"][0]["KEy21"] == "value21"
        assert cis["KEy3"]["key31"]["KeY311"] == "key312"
        assert len(cis["key4"]) == 2
        assert cis.to_dict() == dictionary

    def test_when_update_value_then_key_not_changed(self):
        dictionary = {
            "key1": "value1",
            "key2": [{"key21": "value21"}, {"key22": "value22"}],
            "key3": {"key31": {"key311": "key312"}},
        }
        cis = CaseInsensitiveDict(dictionary)
        cis.update_value("KEY1", "updated-value")
        cis["keY2"][0].update_value("KEY21", "updated-value21")

        assert cis["KEY1"] == "updated-value"
        assert cis.to_dict() == {
            "key1": "updated-value",
            "key2": [{"key21": "updated-value21"}, {"key22": "value22"}],
            "key3": {"key31": {"key311": "key312"}},
        }

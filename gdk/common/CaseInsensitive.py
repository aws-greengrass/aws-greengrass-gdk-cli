import json
import logging
from pathlib import Path

import yaml
from requests.structures import CaseInsensitiveDict as _CaseInsensitiveDict
from gdk.common.consts import DOCS_RECIPE_LINK


class CaseInsensitiveDict(_CaseInsensitiveDict):
    def __init__(self, data=None, **kwargs):
        super().__init__(data, **kwargs)
        _dict = _CaseInsensitiveDict(data)
        self._convert_nested_dict(_dict)
        self.update(_dict)

    def to_dict(self):
        _dict = dict(self)
        self._convert_nested_case_insensitive_dict(_dict)
        return _dict

    def update_value(self, key, value):
        if key.lower() in self._store:
            key = self._store[key.lower()][0]
        self._store[key.lower()] = (key, value)

    def _convert_nested_dict(self, case_insensitive_dict: _CaseInsensitiveDict) -> None:
        for key, value in case_insensitive_dict.items():
            if isinstance(value, dict):
                case_insensitive_dict.update({key: CaseInsensitiveDict(value)})
            elif isinstance(value, list):
                case_insensitive_dict.update(
                    {key: [CaseInsensitiveDict(val) if isinstance(val, dict) else val for val in value]}
                )

    def _convert_nested_case_insensitive_dict(self, dictObj: dict) -> dict:
        for key, value in dictObj.items():
            if isinstance(value, CaseInsensitiveDict):
                dictObj.update({key: self._convert_nested_case_insensitive_dict(dict(value))})
            elif isinstance(value, list):
                dictObj.update(
                    {
                        key: [
                            self._convert_nested_case_insensitive_dict(dict(val))
                            if isinstance(val, CaseInsensitiveDict)
                            else val
                            for val in value
                        ]
                    }
                )
        return dictObj


class CaseInsensitiveRecipeFile:
    def write(self, file_path: Path, content: CaseInsensitiveDict) -> None:
        """
        Writes CaseInsensitiveDict contents to a JSON or a YAML file based on the file path.
        """
        if not self._is_json(file_path) and not self._is_yaml(file_path):
            raise Exception(f"Invalid recipe file : {file_path}. Recipe file must be in json or yaml format.")
        self._write(file_path, content.to_dict())

    def read(self, file_path: Path) -> CaseInsensitiveDict:
        """
        Reads a JSON or a YAMl file contents as a CaseInsensitiveDict and returns it.
        """
        if not self._is_json(file_path) and not self._is_yaml(file_path):
            raise Exception(f"Invalid recipe file : {file_path}. Recipe file must be in json or yaml format.")
        return CaseInsensitiveDict(self._read(file_path))

    def _write(self, file_path, content):
        if self._is_json(file_path):
            self._write_to_json(file_path, content)
        else:
            self._write_to_yaml(file_path, content)

    def _read(self, file_path):
        if self._is_json(file_path):
            return self._read_from_json(file_path)
        else:
            return self._read_from_yaml(file_path)

    def _read_from_yaml(self, file_path: Path) -> dict:
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                return yaml.safe_load(f.read())
            except yaml.YAMLError as err:
                logging.error(f"Syntax error when parsing the recipe file: {file_path}. For information and examples" +
                              f" regarding component recipes refer to the docs here: {DOCS_RECIPE_LINK}")
                raise err

    def _read_from_json(self, file_path: Path) -> dict:
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                return json.loads(f.read())
            except json.JSONDecodeError as err:
                logging.error(f"Syntax error when parsing the recipe file: {file_path}. For information and examples" +
                              f" regarding component recipes refer to the docs here: {DOCS_RECIPE_LINK}")
                raise err

    def _write_to_json(self, file_path: Path, content: dict) -> None:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(content, indent=4))

    def _write_to_yaml(self, file_path: Path, content: dict) -> None:
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(content, f, sort_keys=False)

    def _is_json(self, file_path: Path) -> bool:
        return file_path.name.endswith(".json")

    def _is_yaml(self, file_path: Path) -> bool:
        return file_path.name.endswith(".yaml") or file_path.name.endswith(".yml")

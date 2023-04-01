import json
import yaml
from pathlib import Path
from requests.structures import CaseInsensitiveDict


class CaseInsensitiveRecipeFile:
    def write(self, file_path: Path, content: CaseInsensitiveDict) -> None:
        """
        Writes CaseInsensitiveDict contents to a JSON or a YAML file based on the file path.
        """
        if not self._is_json(file_path) and not self._is_yaml(file_path):
            raise Exception(f"Invalid recipe file : {file_path}. Recipe file must be in json or yaml format.")
        self._write(file_path, self._to_dict(content))

    def read(self, file_path: Path) -> CaseInsensitiveDict:
        """
        Reads a JSON or a YAMl file contents as a CaseInsensitiveDict and returns it.
        """
        if not self._is_json(file_path) and not self._is_yaml(file_path):
            raise Exception(f"Invalid recipe file : {file_path}. Recipe file must be in json or yaml format.")
        return self._from_dict(self._read(file_path))

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
            return yaml.safe_load(f.read())

    def _read_from_json(self, file_path: Path) -> dict:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.loads(f.read())

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

    def _convert_nested_dict(self, case_insensitive_dict: CaseInsensitiveDict) -> CaseInsensitiveDict:
        for key, value in case_insensitive_dict.items():
            if isinstance(value, dict):
                case_insensitive_dict.update({key: self._convert_nested_dict(CaseInsensitiveDict(value))})
            elif isinstance(value, list):
                case_insensitive_dict.update(
                    {key: [self._convert_nested_dict(CaseInsensitiveDict(val)) for val in value if isinstance(val, dict)]}
                )
        return case_insensitive_dict

    def _convert_nested_case_insensitive_dict(self, dictObj: dict) -> dict:
        for key, value in dictObj.items():
            if isinstance(value, CaseInsensitiveDict):
                dictObj.update({key: self._convert_nested_case_insensitive_dict(dict(value))})
            elif isinstance(value, list):
                dictObj.update(
                    {
                        key: [
                            self._convert_nested_case_insensitive_dict(dict(val))
                            for val in value
                            if isinstance(val, CaseInsensitiveDict)
                        ]
                    }
                )
        return dictObj

    def _from_dict(self, original: dict) -> CaseInsensitiveDict:
        _dict = CaseInsensitiveDict(original)
        self._convert_nested_dict(_dict)
        return _dict

    def _to_dict(self, cir: CaseInsensitiveDict) -> dict:
        __dict = dict(cir)
        self._convert_nested_case_insensitive_dict(__dict)
        return __dict

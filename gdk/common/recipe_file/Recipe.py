import json
import yaml
from pathlib import Path


class Recipe:
    def write(self, file_path: Path, content: dict) -> None:
        """
        Writes python dictionary contents to a JSON or a YAML file based on the file path.
        """
        if self._is_json(file_path):
            self._write_to_json(file_path, content)
        elif self._is_yaml(file_path):
            self._write_to_yaml(file_path, content)
        else:
            raise Exception(f"Invalid recipe file : {file_path}. Recipe file must be in json or yaml format.")

    def read(self, file_path: Path) -> dict:
        """
        Reads a JSON or a YAMl file contents as a dictionary and returns it.
        """
        if self._is_json(file_path):
            return self._read_from_json(file_path)
        elif self._is_yaml(file_path):
            return self._read_from_yaml(file_path)
        else:
            raise Exception(f"Invalid recipe file - {file_path}. Recipe file must be in json or yaml format.")

    def _read_from_yaml(self, file_path: Path) -> dict:
        with open(file_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f.read())

    def _read_from_json(self, file_path: Path) -> dict:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.loads(f.read())

    def _write_to_json(self, file_path: Path, content: dict) -> None:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(content))

    def _write_to_yaml(self, file_path: Path, content: dict) -> None:
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(content, f)

    def _is_json(self, file_path: Path) -> bool:
        return file_path.name.endswith(".json")

    def _is_yaml(self, file_path: Path) -> bool:
        return file_path.name.endswith(".yaml")

from gdk.common.config.GDKProject import GDKProject
from pathlib import Path
import json
import logging


class RunConfiguration(GDKProject):
    def __init__(self, _args) -> None:
        super().__init__()
        self._args = _args
        self._test_options_from_config = self.test_config.gtf_options
        self._default_tags = "Sample"
        self.default_nucleus_archive_path = self.gg_build_dir.joinpath("greengrass-nucleus-latest.zip").resolve()
        self.options = self._get_options()

    def _get_options_from_config(self) -> dict:
        """
        Read gtf_options provided in the gdk-config.json. Validate and update only `tags` and `ggc-archive` for now as these
        are required options. Use rest of the options as they're provided in the test config.
        """
        options = self._test_options_from_config.copy()
        options["ggc-archive"] = str(self._get_archive_path())
        options["tags"] = self._get_tags()
        return options

    def _get_archive_path(self) -> Path:
        """
        Read and validate `ggc-archive` provided in the gdk-config.json. Raise an exception if the archive doesn't exist at
        the given path.

        If no `ggc-archive` is provided, then use default nucleus archive path - greengrass-build/greengrass-nucleus-latest.zip
        """
        _nucleus_archive = self._test_options_from_config.get("ggc-archive", None)
        if not _nucleus_archive:
            return self.default_nucleus_archive_path

        _nucleus_archive_path = Path(_nucleus_archive).resolve()
        if not _nucleus_archive_path.exists():
            raise ValueError(
                f"Cannot find nucleus archive at path {_nucleus_archive}. Please check 'ggc-archive' in the test config"
            )
        return _nucleus_archive_path

    def _get_tags(self) -> str:
        """
        Read and validate `tags` provided in the gdk-config.json. If no tags are provided, then use default `Sample` tag.
        """
        tags = self._test_options_from_config.get("tags", self._default_tags)
        if not tags:
            raise ValueError("Test tags provided in the config are invalid. Please check 'tags' in the test config")
        return tags

    def _get_options(self) -> dict:
        _options_args = self._args.get("gtf_options", "")
        if _options_args == "":
            _options_args = self._args.get("otf_options", "")
        _options_from_config = self._get_options_from_config()
        if not _options_args:
            return _options_from_config
        try:
            if _options_args.endswith(".json"):
                _options_args_json = self._read_options_from_file(_options_args)
            else:
                _options_args_json = json.loads(_options_args)
        except json.decoder.JSONDecodeError as err:
            raise ValueError(
                "JSON string provided in the test command is incorrectly formatted.\nError:\t" + str(err),
            ) from err
        # Merge the options provided in the gdk-config.json with the ones provided as args in test command.
        # Options in args override the config.
        logging.info("Overriding the E2E testing options provided in the config with the ones provided as args")
        _merged_dict = {**_options_from_config, **_options_args_json}
        return _merged_dict

    def _read_options_from_file(self, file: str) -> str:
        file_path = Path(file).resolve()
        if not file_path.exists():
            raise ValueError(f"Cannot find the E2E testing options file at the given path {file}.")

        logging.debug("Reading E2E testing options from file %s", file)
        with open(file_path, "r", encoding="utf-8") as f:
            return json.loads(f.read())

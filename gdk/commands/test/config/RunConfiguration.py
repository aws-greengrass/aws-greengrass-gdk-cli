from gdk.common.config.GDKProject import GDKProject
from pathlib import Path


class RunConfiguration:
    def __init__(self, _gdk_project: GDKProject, _args) -> None:
        self._args = _args
        self._gdk_project = _gdk_project
        self._test_options_from_config = self._gdk_project.test_config.otf_options
        self._default_tags = "Sample"
        self.default_nucleus_archive_path = self._gdk_project.gg_build_dir.joinpath("greengrass-nucleus-latest.zip").resolve()
        self.options = {}
        self._update_options()

    def _update_options(self) -> None:
        """
        Read otf_options provided in the gdk-config.json. Validate and update only `tags` and `ggc-archive` for now as these
        are required options. Use rest of the options as they're provided in the test config.
        """
        self.options = self._test_options_from_config.copy()
        self.options["ggc-archive"] = str(self._get_archive_path())
        self.options["tags"] = self._get_tags()

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
            raise Exception(
                f"Cannot find nucleus archive at path {_nucleus_archive}. Please check 'ggc-archive' in the test config"
            )
        return _nucleus_archive_path

    def _get_tags(self) -> str:
        """
        Read and validate `tags` provided in the gdk-config.json. If no tags are provided, then use default `Sample` tag.
        """
        tags = self._test_options_from_config.get("tags", self._default_tags)
        if not tags:
            raise Exception("Test tags provided in the config are invalid. Please check 'tags' in the test config")
        return tags

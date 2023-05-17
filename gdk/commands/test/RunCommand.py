from gdk.commands.Command import Command
from gdk.common.config.GDKProject import GDKProject
from gdk.build_system.UATBuildSystem import UATBuildSystem
from gdk.commands.test.config.RunConfiguration import RunConfiguration
from pathlib import Path
from gdk.common.URLDownloader import URLDownloader
import logging


class RunCommand(Command):
    def __init__(self, command_args) -> None:
        super().__init__(command_args, "run")
        self._gdk_project = GDKProject()
        self._test_directory = self._gdk_project.gg_build_dir.joinpath("uat-features").resolve()
        self._test_build_system = self._gdk_project.test_config.test_build_system
        self._config = RunConfiguration(self._gdk_project, command_args)
        self._nucleus_archive_link = "https://d2s8p88vqu9w66.cloudfront.net/releases/greengrass-latest.zip"

    def run(self):
        """
        This method is called when customer runs the `gdk test run` command

        1. Check if the test module is built. Otherwise, raise an exception.
        2. If 'ggc-archive' path is set to default, then download the latest nucleus archive from url if it doesn't exist.
        3. TODO: Run the test module jar with configured options.
        """
        if not self._is_test_module_built():
            raise Exception(
                "UAT module is not built. Please build the test module using `gdk test build`command before running the tests."
            )

        _nucleus_path = Path(self._config.options.get("ggc-archive"))
        if self._should_download_nucleus_archive(_nucleus_path):
            logging.info("Downloading latest nucleus archive from url %s", self._nucleus_archive_link)
            URLDownloader(self._nucleus_archive_link).download(_nucleus_path)

    def _is_test_module_built(self) -> bool:
        """
        Return true if the test module build folder exists
        """
        uat_build_system = UATBuildSystem.get(self._test_build_system)
        test_build_folder = self._test_directory.joinpath(*uat_build_system.build_folder).resolve()

        return test_build_folder.exists()

    def _should_download_nucleus_archive(self, _nucleus_path: Path) -> bool:
        """
        If ggc-archive path is set to default path and if it doesn't already exist at this path, then download the latest
        nucleus archive from url.
        """
        return _nucleus_path == Path(self._config.default_nucleus_archive_path).resolve() and not _nucleus_path.exists()

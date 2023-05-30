from gdk.commands.Command import Command
from gdk.build_system.E2ETestBuildSystem import E2ETestBuildSystem
from gdk.commands.test.config.RunConfiguration import RunConfiguration
from pathlib import Path
from gdk.common.URLDownloader import URLDownloader
import logging
import subprocess as sp
import gdk.common.consts as consts


class RunCommand(Command):
    def __init__(self, command_args) -> None:
        super().__init__(command_args, "run")
        self._run_config = RunConfiguration(command_args)
        self._test_directory = self._run_config.gg_build_dir.joinpath(consts.E2E_TESTS_DIR_NAME).resolve()
        self._test_build_system = self._run_config.test_config.test_build_system
        self._nucleus_archive_link = "https://d2s8p88vqu9w66.cloudfront.net/releases/greengrass-latest.zip"

    def run(self):
        """
        This method is called when customer runs the `gdk test run` command

        1. Check if the test module is built. Otherwise, raise an exception.
        2. If 'ggc-archive' path is set to default, then download the latest nucleus archive from url if it doesn't exist.
        3. Run the test module jar with configured options.
        """
        if not self._is_test_module_built():
            raise Exception(
                "E2E testing module is not built. Please build the test module using `gdk test build`command before running"
                " the tests."
            )

        _nucleus_path = Path(self._run_config.options.get("ggc-archive"))
        if self._should_download_nucleus_archive(_nucleus_path):
            logging.info("Downloading latest nucleus archive from url %s", self._nucleus_archive_link)
            URLDownloader(self._nucleus_archive_link).download(_nucleus_path)

        self.run_testing_jar()

    def _is_test_module_built(self) -> bool:
        """
        Return true if the test module build folder exists
        """
        return self._test_build_directory().exists()

    def _test_build_directory(self) -> Path:
        """
        Return the test build directory
        """
        e2e_test_build_system = E2ETestBuildSystem.get(self._test_build_system)
        return self._test_directory.joinpath(*e2e_test_build_system.build_folder).resolve()

    def _should_download_nucleus_archive(self, _nucleus_path: Path) -> bool:
        """
        If ggc-archive path is set to default path and if it doesn't already exist at this path, then download the latest
        nucleus archive from url.
        """
        return _nucleus_path == Path(self._run_config.default_nucleus_archive_path).resolve() and not _nucleus_path.exists()

    def run_testing_jar(self) -> None:
        """
        Run the testing jar from the build folder using the configured options.
        """
        _jar_path = self._identify_testing_jar().__str__()
        logging.debug("Identified %s in the build folder as the testing jar", _jar_path)
        _commands = ["java", "-jar", _jar_path]
        _commands.extend(self._get_options_as_list())
        logging.info("Running test jar with command %s", " ".join(_commands))

        sp.run(_commands, check=True)

    def _identify_testing_jar(self) -> Path:
        """
        Identify testing jar from the build folder.

        If gg-e2e-tests-1.0.0.jar is in the build folder and is a testing jar, then return it.
        Otherwise, find all the *.jar files in the build folder and return the first one that is a testing jar.
        If nothing is found, an exception in thrown.
        """
        _test_build_dir = self._test_build_directory()
        default_jar_path = _test_build_dir.joinpath(f"{consts.E2E_TESTS_DIR_NAME}-1.0.0.jar").resolve()

        if default_jar_path.exists() and self._is_testing_jar(default_jar_path):
            return default_jar_path

        jar_list = list(Path(_test_build_dir).glob("*.jar"))
        for jar in jar_list:
            if self._is_testing_jar(jar):
                return jar
        raise Exception("Unable to find testing jar in the build folder")

    def _is_testing_jar(self, _jar_path: Path):
        """
        Run java -jar /path/to/jar --help. If the command succeeds and has "gg-test" in its output, then it could be the
        testing jar.
        """
        completed_proc = sp.run(["java", "-jar", str(_jar_path), "--help"], check=False, stderr=sp.STDOUT, stdout=sp.PIPE)
        _cmd_successful = completed_proc.returncode != 1
        _cmd_output = ""
        if _cmd_successful:
            _cmd_output = completed_proc.stdout.decode("utf-8")

        return _cmd_successful and "gg-test" in _cmd_output

    def _get_options_as_list(self) -> list:
        """
        Return options as list of arguments to the jar
        """
        return [f"--{opt}={val}" for opt, val in self._run_config.options.items()]

import logging
from pathlib import Path

from gdk.commands.test.config.InitConfiguration import InitConfiguration
import gdk.common.utils as utils
from gdk.commands.Command import Command
from gdk.build_system.E2ETestBuildSystem import E2ETestBuildSystem
from gdk.common.URLDownloader import URLDownloader
import gdk.common.consts as consts


class InitCommand(Command):
    def __init__(self, command_args) -> None:
        super().__init__(command_args, "init")
        self.template_name = "TestTemplateForCLI"
        self.test_directory = Path(utils.get_current_directory()).joinpath(consts.E2E_TESTS_DIR_NAME).resolve()
        self._init_config = InitConfiguration(command_args)
        self._test_config = self._init_config.test_config

    @property
    def template_url(self):
        return (
            "https://github.com/aws-greengrass/aws-greengrass-component-templates/releases/download/v1.0/"
            + f"{self.template_name}.zip"
        )

    def run(self):
        if self.test_directory.exists() and len(list(self.test_directory.iterdir())) > 0:
            logging.warning(
                "Not downloading the E2E testing template as '%s' already exists in the current directory and is not empty.",
                consts.E2E_TESTS_DIR_NAME,
            )
            return

        logging.info("Downloading the E2E testing template from GitHub into %s directory...", consts.E2E_TESTS_DIR_NAME)

        URLDownloader(self.template_url).download_and_extract(self.test_directory)
        self.update_testing_module_build_identifiers(self._test_config.test_build_system, self._init_config.gtf_version)

    def update_testing_module_build_identifiers(self, build_system_str, gtf_version):
        build_system = E2ETestBuildSystem.get(build_system_str)
        for identifier in build_system.build_system_identifier:
            build_file = self.test_directory.joinpath(identifier)

            if not build_file.exists():
                continue

            logging.debug("Updating the testing jar version used in the E2E testing module '%s'", identifier)
            with open(build_file, "r", encoding="utf-8") as f:
                build_file_content = f.read()

            build_file_content = build_file_content.replace("GDK_TESTING_VERSION", gtf_version + "-SNAPSHOT")

            with open(build_file, "w", encoding="utf-8") as f:
                f.write(build_file_content)

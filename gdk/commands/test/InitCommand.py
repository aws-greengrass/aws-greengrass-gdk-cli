import logging
import tempfile
import zipfile
from io import BytesIO
from pathlib import Path

import requests
from gdk.common.config.GDKProject import GDKProject

import gdk.common.utils as utils
from gdk.commands.Command import Command
from gdk.build_system.UATBuildSystem import UATBuildSystem


class InitCommand(Command):
    def __init__(self, command_args) -> None:
        super().__init__(command_args, "run")
        self.template_name = "TestTemplateForCLI"
        self.test_directory = Path(utils.get_current_directory()).joinpath("uat-features").resolve()
        self._gdk_project = GDKProject()
        self._test_config = self._gdk_project.test_config

    @property
    def template_url(self):
        return (
            "https://github.com/aws-greengrass/aws-greengrass-component-templates/releases/download/v1.0/"
            + f"{self.template_name}.zip"
        )

    def run(self):
        if self.test_directory.exists():
            logging.warning("Not downloading the uat template as 'uat-features' already exists in the current directory.")
            return
        self.download_template()
        self.update_testing_module_build_identifiers(self._test_config.test_build_system, self._test_config.otf_version)

    def download_template(self):
        download_response = requests.get(self.template_url, stream=True, timeout=30)
        if download_response.status_code != 200:
            try:
                download_response.raise_for_status()
            except Exception:
                logging.error("Failed to download the uat template from GitHub")
                raise

        logging.info("Downloading the UAT module from GitHub")
        with zipfile.ZipFile(BytesIO(download_response.content)) as zfile:
            with tempfile.TemporaryDirectory() as tmpdirname:
                zfile.extractall(tmpdirname)
                Path(tmpdirname).joinpath(self.template_name).rename(self.test_directory)

    def update_testing_module_build_identifiers(self, build_system_str, otf_version):
        build_system = UATBuildSystem.get(build_system_str)
        for identifier in build_system.build_system_identifier:
            build_file = self.test_directory.joinpath(identifier)

            if not build_file.exists():
                continue

            logging.debug("Updating the testing jar version used in the UAT module '%s'", identifier)
            with open(build_file, "r", encoding="utf-8") as f:
                build_file_content = f.read()

            build_file_content = build_file_content.replace("GDK_TESTING_VERSION", otf_version)

            with open(build_file, "w", encoding="utf-8") as f:
                f.write(build_file_content)

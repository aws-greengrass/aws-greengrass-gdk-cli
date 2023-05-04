import logging
import tempfile
import zipfile
from io import BytesIO
from pathlib import Path

import requests

import gdk.common.utils as utils
from gdk.commands.Command import Command


class InitCommand(Command):
    def __init__(self, command_args) -> None:
        super().__init__(command_args, "run")
        self.template_name = "TestTemplateForCLI"
        self.test_directory = Path(utils.get_current_directory()).joinpath("uat-features").resolve()

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

    def download_template(self):
        download_response = requests.get(self.template_url, stream=True)
        if download_response.status_code != 200:
            try:
                download_response.raise_for_status()
            except Exception:
                logging.error("Failed to download the uat template from GitHub")
                raise

        logging.info("Downloading the uat template from GitHub")
        with zipfile.ZipFile(BytesIO(download_response.content)) as zfile:
            with tempfile.TemporaryDirectory() as tmpdirname:
                zfile.extractall(tmpdirname)
                Path(tmpdirname).joinpath(self.template_name).rename(self.test_directory)

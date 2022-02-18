import logging
import shutil
import tempfile
import zipfile
from io import BytesIO
from pathlib import Path

import gdk.common.consts as consts
import gdk.common.exceptions.error_messages as error_messages
import gdk.common.utils as utils
import requests
from gdk.commands.Command import Command
from gdk.commands.component.ListCommand import ListCommand


class InitCommand(Command):
    def __init__(self, command_args) -> None:
        super().__init__(command_args, "init")

    def run(self):
        """
        Initializes the current directory in which the command runs based on the command arguments.

        This function creates a new directory if name argument is passed in the command and initializes the project inside it.
        Errors out if the directory already exists.

        If no name argument is passed, then it checks if the current directory is empty before initiating the project.
        Raises an exception otherwise.

        Parameters
        ----------
          command_args(dict): A dictionary object that contains parsed args namespace of a command.

        Returns
        -------
            None
        """
        project_dir = utils.current_directory
        if not self.arguments["name"]:
            # Check if directory is not empty
            if not utils.is_directory_empty(project_dir):
                raise Exception(error_messages.INIT_NON_EMPTY_DIR_ERROR)
        else:
            # Create a new directory with name.
            project_dir = Path(project_dir).joinpath(self.arguments["name"]).resolve()
            try:
                logging.debug("Creating new project directory '{}' in the current directory.".format(project_dir.name))
                Path(project_dir).mkdir(exist_ok=False)
            except FileExistsError:
                raise Exception(error_messages.INIT_DIR_EXISTS_ERROR.format(project_dir.name))

        # Choose appropriate action based on commands
        if self.arguments["template"] and self.arguments["language"]:
            template = self.arguments["template"]
            language = self.arguments["language"]
            if template and language:
                logging.info(
                    "Initializing the project directory with a {} component template - '{}'.".format(language, template)
                )
                self.init_with_template(template, language, project_dir)
                return
        elif self.arguments["repository"]:
            repository = self.arguments["repository"]
            if repository:
                logging.info(
                    "Initializing the project directory with a component from repository catalog - '{}'.".format(repository)
                )
                self.init_with_repository(repository, project_dir)
                return
        raise Exception(error_messages.INIT_WITH_INVALID_ARGS)

    def init_with_template(self, template, language, project_dir):
        try:
            template_name = "{}-{}".format(template, language)
            logging.info("Fetching the component template '{}' from Greengrass Software Catalog.".format(template_name))
            self.download_and_clean(template_name, "template", project_dir)
        except Exception as e:
            raise Exception("Could not initialize the project with component template '{}'.\n{}".format(template, e))

    def init_with_repository(self, repository, project_dir):
        try:
            logging.info("Fetching the component repository '{}' from Greengrass Software Catalog.".format(repository))
            self.download_and_clean(repository, "repository", project_dir)
        except Exception as e:
            raise Exception("Could not initialize the project with component repository '{}'.\n{}".format(repository, e))

    def download_and_clean(self, comp_name, comp_type, project_dir):
        """
        Downloads component zip file file from GitHub and unarchives it in current directory.

        Extracts the contents of the zip file into a temporary diretory and moves over them to the current directory.

        Parameters
        ----------
          comp_name(string): Name of the component.
          comp_type(string): Type of the component(template or repository).

        Returns
        -------
            None
        """
        comp_url = self.get_download_url(comp_name, comp_type)

        download_response = requests.get(comp_url, stream=True)
        if download_response.status_code != 200:
            try:
                download_response.raise_for_status()
            except Exception as e:
                logging.error(e)
                raise e
            finally:
                raise Exception(error_messages.INIT_FAILS_DURING_COMPONENT_DOWNLOAD.format(comp_type))

        logging.debug("Downloading the component {}...".format(comp_type))
        with zipfile.ZipFile(BytesIO(download_response.content)) as zfile:
            with tempfile.TemporaryDirectory() as tmpdirname:
                # Extracts the zip file into temporary directory - /some-temp-dir/downloaded-zip-folder/
                zfile.extractall(tmpdirname)
                # Moves the unarchived contents from temporary folder (downloaded-zip-folder) to current directory.
                for f in Path(tmpdirname).joinpath(zfile.namelist()[0]).iterdir():
                    shutil.move(str(f), project_dir)

    def get_download_url(self, comp_name, comp_type):
        if comp_type == "template":
            url = consts.templates_list_url
        elif comp_type == "repository":
            url = consts.repository_list_url
        available_components = ListCommand({}).get_component_list_from_github(url)
        if comp_name in available_components:
            logging.debug("Component {} '{}' is available in Greengrass Software Catalog.".format(comp_type, comp_name))
            return available_components[comp_name]
        else:
            raise Exception(
                "Could not find the component {} '{}' in Greengrass Software Catalog.".format(comp_type, comp_name)
            )

import logging

import gdk.common.consts as consts
import gdk.common.exceptions.error_messages as error_messages
import gdk.common.utils as utils
from gdk.commands.Command import Command
from gdk.commands.component.ListCommand import ListCommand
from gdk.common.URLDownloader import URLDownloader


class InitCommand(Command):
    def __init__(self, command_args) -> None:
        super().__init__(command_args, "init")

    def run(self) -> None:
        """
        Initializes the current directory in which the command runs based on the command arguments.

        This function creates a new directory if name argument is passed in the command and initializes the project inside it.
        Errors out if the directory is not empty.

        If no name argument is passed, then it checks if the current directory is empty before initiating the project.
        Raises an exception otherwise.

        Parameters
        ----------
          command_args(dict): A dictionary object that contains parsed args namespace of a command.
        """
        _name = self.arguments.get("name")
        project_dir = utils.get_current_directory()
        if _name:
            project_dir = project_dir.joinpath(_name).resolve()

        if project_dir.exists() and not utils.is_directory_empty(project_dir):
            raise Exception(error_messages.INIT_NON_EMPTY_DIR_ERROR)

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
        except Exception:
            logging.error("Could not initialize the project with component template '%s'.", template)
            raise

    def init_with_repository(self, repository, project_dir):
        try:
            logging.info("Fetching the component repository '{}' from Greengrass Software Catalog.".format(repository))
            self.download_and_clean(repository, "repository", project_dir)
        except Exception:
            logging.error("Could not initialize the project with component repository '%s'.", repository)
            raise

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
        URLDownloader(comp_url).download_and_extract(project_dir)

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

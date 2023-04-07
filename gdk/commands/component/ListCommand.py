import re
import logging
from typing import Iterable

import gdk.common.consts as consts
import gdk.common.exceptions.error_messages as error_messages
import requests
from gdk.commands.Command import Command


class ListCommand(Command):
    def __init__(self, command_args) -> None:
        super().__init__(command_args, "list")

    def run(self):
        if "template" in self.arguments and self.arguments["template"]:
            logging.info("Listing all the available component templates from Greengrass Software Catalog.")
            li = self.get_component_list_from_github(consts.templates_list_url)
            logging.info("Found '{}' component templates to display.".format(len(li)))
            self.display_list(li, transform=self._map_template_name)
            return
        elif "repository" in self.arguments and self.arguments["repository"]:
            logging.info("Listing all the available component repositories from Greengrass Software Catalog.")
            li = self.get_component_list_from_github(consts.repository_list_url)
            logging.info("Found '{}' component repositories to display.".format(len(li)))
            self.display_list(li)
            return
        raise Exception(error_messages.LIST_WITH_INVALID_ARGS)

    def get_component_list_from_github(self, url) -> list:
        response = requests.get(url)
        try:
            response.raise_for_status()
        except Exception:
            logging.error(error_messages.LISTING_COMPONENTS_FAILED)
            raise

        try:
            return response.json()
        except Exception as e:
            logging.error(e, exc_info=True)
            return []

    def _map_template_name(self, template_name: str) -> str:
        """
        Maps the raw name into the <name> (language) format.

        Repository template names are postfixed by the `-<programming-language>`. For example
        HelloWorld-python, HelloWorld-java.
        """
        try:
            language = re.search(r"\b(java|python)\b", template_name).group(1)
            template_name = re.sub(r"\b\-(java|python)\b", "", template_name)
            return f"{template_name} ({language})"
        except Exception:
            return template_name

    def display_list(self, component_names: Iterable[str], transform=lambda x: x):
        # TODO: Add short description of what each component is for?
        for count, component_name in enumerate(component_names):
            # Do not use logging here.
            print(f"{count + 1}. {transform(component_name)}")

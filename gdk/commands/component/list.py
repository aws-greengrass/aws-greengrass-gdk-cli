import logging

import gdk.common.consts as consts
import gdk.common.exceptions.error_messages as error_messages
import requests


def run(command_args):
    if "template" in command_args and command_args["template"]:
        logging.info("Listing all the available component templates from Greengrass Software Catalog.")
        li = get_component_list_from_github(consts.templates_list_url)
        logging.info("Found '{}' component templates to display.".format(len(li)))
        display_list(li)
        return
    elif "repository" in command_args and command_args["repository"]:
        logging.info("Listing all the available component repositories from Greengrass Software Catalog.")
        li = get_component_list_from_github(consts.repository_list_url)
        logging.info("Found '{}' component repositories to display.".format(len(li)))
        display_list(li)
        return
    raise Exception(error_messages.LIST_WITH_INVALID_ARGS)


def get_component_list_from_github(url):
    comp_list_response = requests.get(url)
    if comp_list_response.status_code != 200:
        try:
            comp_list_response.raise_for_status()
        except Exception as e:
            logging.error(e)
            raise e
        finally:
            raise Exception(error_messages.LISTING_COMPONENTS_FAILED)
    try:
        comp_list = comp_list_response.json()
        return comp_list
    except Exception as e:
        logging.error(e)
        return []


def display_list(components):
    # TODO: Add short description of what each component is for?
    i = 1
    for component in components:
        # Do not use logging here.
        print(f"{i}. {component}")
        i += 1

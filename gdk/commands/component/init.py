import logging
import os
import shutil

import gdk.commands.component.list as list
import gdk.common.consts as consts
import gdk.common.exceptions.error_messages as error_messages
import gdk.common.parse_args_actions as parse_args_actions
import gdk.common.utils as utils
import requests


def run(command_args):
    """
    Initializes the current directory in which the command runs based on the command arguments.

    This function checks if the current directory is empty before initiating the project. Raises an
    exception otherwise.

    Parameters
    ----------
      command_args(dict): A dictionary object that contains parsed args namespace of a command.

    Returns
    -------
        None
    """
    # Check if directory is not empty
    if not utils.is_directory_empty(utils.current_directory):
        raise Exception(error_messages.INIT_NON_EMPTY_DIR_ERROR)

    # Check if the command args are conflicting
    if parse_args_actions.conflicting_arg_groups(command_args, "init"):
        raise Exception(error_messages.INIT_WITH_CONFLICTING_ARGS)

    # Choose appropriate action based on commands
    if "template" in command_args and "language" in command_args:
        template = command_args["template"]
        language = command_args["language"]
        if template and language:
            logging.info("Initializing the project directory with a {} component template - '{}'.".format(language, template))
            init_with_template(template, language)
            return
    elif "repository" in command_args:
        repository = command_args["repository"]
        if repository:
            logging.info(
                "Initializing the project directory with a component from repository catalog - '{}'.".format(repository)
            )
            init_with_repository(repository)
            return
    raise Exception(error_messages.INIT_WITH_INVALID_ARGS)


def init_with_template(template, language):
    try:
        template_name = "{}-{}".format(template, language)
        logging.info("Fetching the component template '{}' from Greengrass Software Catalog.".format(template_name))
        download_and_clean(template_name, "template")
    except Exception as e:
        raise Exception("Could not initialize the project with component template '{}'.\n{}".format(template, e))


def init_with_repository(repository):
    try:
        logging.info("Fetching the component repository '{}' from Greengrass Software Catalog.".format(repository))
        download_and_clean(repository, "repository")
    except Exception as e:
        raise Exception("Could not initialize the project with component repository '{}'.\n{}".format(repository, e))


def download_and_clean(comp_name, comp_type):
    comp_url = get_download_url(comp_name, comp_type)

    download_request = requests.get(comp_url, stream=True)
    if download_request.status_code != 200:
        try:
            download_request.raise_for_status()
        except Exception as e:
            logging.error(e)
            raise e
        finally:
            raise Exception(error_messages.INIT_FAILS_DURING_COMPONENT_DOWNLOAD.format(comp_type))

    zip_comp_name = "{}.zip".format(comp_name)
    with open(zip_comp_name, "wb") as f:
        logging.debug("Downloading the component {}...".format(comp_type))
        f.write(download_request.content)
        logging.debug("Download complete.")

    # unzip the template
    logging.debug("Unzipping the downloaded component {}...".format(comp_type))
    shutil.unpack_archive(zip_comp_name, utils.current_directory)
    logging.debug("Unzip complete.")

    # Delete the downloaded zip template
    logging.debug("Deleting the downloaded zip component {}.".format(comp_type))
    os.remove(zip_comp_name)
    logging.debug("Delete complete.")


def get_download_url(comp_name, comp_type):
    if comp_type == "template":
        url = consts.templates_list_url
    elif comp_type == "repository":
        url = consts.repository_list_url
    available_components = list.get_component_list_from_github(url)
    if comp_name in available_components:
        logging.debug("Component {} '{}' is available in Greengrass Software Catalog.".format(comp_type, comp_name))
        return available_components[comp_name]
    else:
        raise Exception("Could not find the component {} '{}' in Greengrass Software Catalog.".format(comp_type, comp_name))

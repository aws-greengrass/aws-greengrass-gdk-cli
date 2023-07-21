import json
import logging
from pathlib import Path

import gdk.common.consts as consts
import gdk.common.exceptions.error_messages as error_messages
import gdk.common.utils as utils
import jsonschema
from packaging.version import Version


def get_configuration():
    """
    Loads the configuration from the greengrass project config file as a json object.

    Throws ValidationError if the config file not valid as per schema.

    Parameters
    ----------
        None

    Returns
    -------
       config_data(dict): Greengrass project configuration as a dictionary object if the config is valid.
    """
    project_config_file = _get_project_config_file()
    with open(project_config_file, "r") as config_file:
        config_data = json.loads(config_file.read())
    try:
        validate_cli_version(config_data)
        validate_configuration(config_data)

        return config_data
    except jsonschema.exceptions.ValidationError as err:
        raise Exception(error_messages.PROJECT_CONFIG_FILE_INVALID.format(project_config_file.name, err.message))


def validate_configuration(data):
    """
    Validates the greengrass project configuration object against json schema.

    Raises an exception if the schema file doesn't exist.
    Throws ValidationError if configuration is invalid as per the schema.

    Parameters
    ----------
        data(dict): A dictionary object containing the configuration from greengrass project config file.

    Returns
    -------
      None
    """

    config_schema_file = utils.get_static_file_path(consts.config_schema_file)
    with open(config_schema_file, "r") as schemaFile:
        schema = json.loads(schemaFile.read())
    logging.debug("Validating the configuration file.")
    jsonschema.validate(data, schema)


def validate_cli_version(config_data):
    cli_version = utils.cli_version
    config_version = config_data.get("gdk_version")
    if not config_version:
        return
    if Version(cli_version) < Version(config_version):
        update_command = f"pip3 install git+https://github.com/aws-greengrass/aws-greengrass-gdk-cli.git@v{config_version}"
        raise Exception(
            f"This gdk project requires gdk cli version '{config_version}' or above. Please update the cli using the command"
            f" `{update_command}` before proceeding."
        )
    logging.debug(
        f"This gdk project configuration (gdk-{config_version}) is compatible with the existing gdk cli version"
        f" (gdk-{cli_version})."
    )


def _get_project_config_file():
    """
    Returns path of the config file present in the greengrass project directory.

    Looks for certain config file in the current work directory of the command.

    Raises an exception if the config file is not present.

    Parameters
    ----------
        None

    Returns
    -------
       config_file(pathlib.Path): Path of the config file.
    """
    config_file = Path(utils.get_current_directory()).joinpath(consts.cli_project_config_file).resolve()
    if not utils.file_exists(config_file):
        raise Exception(error_messages.CONFIG_FILE_NOT_EXISTS)
    return config_file

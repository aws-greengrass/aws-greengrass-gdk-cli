import json
import logging
import sys
from pathlib import Path

import gdk.common.consts as consts
import gdk.common.exceptions.error_messages as error_messages
import gdk.common.utils as utils


def get_recipe():
    """
    Loads the component's recipe from the user-input recipe file as a python object.

    Parameters
    ----------
        None

    Returns
    -------
        recipe_data: component's recipe as a dictionary object if the user-input recipe file is valid.
    """
    user_recipe_file = get_user_input_recipe_file()

    # validate the json recipe syntax
    recipe_data = validate_recipe_syntax(user_recipe_file)

    # TODO: validate the user-input recipe file

    return recipe_data


def get_user_input_recipe_file():
    """
    Returns the path of the user-input recipe file present in the greengrass project directory.

    Looks for user input-recipe file in the current work directory of the command.

    Raises an exception if the recipe file is not present.

    Parameters
    ----------
        None

    Returns
    -------
       recipe_file(pathlib.Path): Path of the recipe file.
    """
    recipe_file_json = Path(utils.get_current_directory()).joinpath(consts.user_input_recipe_json).resolve()
    if not utils.file_exists(recipe_file_json):
        recipe_file_yaml = Path(utils.get_current_directory()).joinpath(consts.user_input_recipe_yaml).resolve()
        if not utils.file_exists(recipe_file_yaml):
            raise Exception(error_messages.USER_INPUT_RECIPE_NOT_EXISTS)
        return recipe_file_yaml
    return recipe_file_json


def validate_recipe_syntax(recipe_file):
    with open(recipe_file, "r") as recipe:
        try:
            recipe_data = json.loads(recipe.read())
            return recipe_data
        except json.JSONDecodeError as err:
            logging.error(f"Syntax error when parsing the recipe file: {recipe_file}")
            parse_json_error(err)
            sys.exit(1)


def parse_json_error(err):
    lines = err.doc.split('\n')
    logging.error(f"{err.args[0]}")
    logging.info(f"The error occurs around line {err.lineno}: " + lines[err.lineno - 1].lstrip())

    logging.info("This might be caused by one of the following reasons: ")
    msg = err.msg

    for err_msg, causes in error_messages.JSON_LIBRARY_ERROR_MESSAGES.items():
        if msg in err_msg:
            for cause in causes:
                logging.info("\t " + cause)
            break

    logging.info("If none of the above is the cause, please review the overall JSON syntax and resolve any issues.")

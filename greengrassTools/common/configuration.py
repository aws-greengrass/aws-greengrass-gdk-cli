import json
import jsonschema
import greengrassTools.common.consts as consts
import greengrassTools.common.utils as utils
import greengrassTools.common.exceptions.error_messages as error_messages
from pathlib import Path

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
    with open(project_config_file, 'r') as config_file:
        data = config_file.read()
    try:
        config_data = json.loads(data)
        validate_configuration(config_data)
        return config_data
    except jsonschema.exceptions.ValidationError as err:
        print("Configuration file provide {0} is not in correct format, details of error {1}".format(project_config_file, err))
        raise err

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

    config_schema_file=utils.get_static_file_path(consts.config_schema_file)
    if config_schema_file:
        with open(config_schema_file, 'r') as schemaFile:
            schema = json.loads(schemaFile.read())
        jsonschema.validate(data, schema)
    else:
        raise Exception(error_messages.CONFIG_SCHEMA_FILE_NOT_EXISTS)
    
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
    config_file = Path(consts.current_directory).joinpath(consts.cli_project_config_file).resolve()
    if not utils.is_file_exists(config_file):
      raise Exception(error_messages.CONFIG_FILE_NOT_EXISTS)
    return config_file
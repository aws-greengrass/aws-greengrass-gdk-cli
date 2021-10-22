import json
import jsonschema
import greengrassTools.common.consts as consts
import greengrassTools.common.utils as utils
import greengrassTools.common.exceptions.error_messages as error_messages
def get_configuration(file_name, component_name):
    """
     This method returns component configuration from the given file name.
     If configuration in file, is not valid per defined schema it will throw ValidationError error.
     If component configuration doesn't exists, then it will return None
    :param file_name: file name for configuration file to read. This needs to be valid & absolute path.
    :param component_name: name of the component
    :return: Json object representing to component configuration
    """
    with open(file_name, 'r') as config_file:
        data = config_file.read()
    try:
        validate_configuration(json.loads(data))
    except jsonschema.exceptions.ValidationError as err:
        print("Configuration file provide {0} is not in correct format, details of error {1}".format(file_name, err))
        raise err
    config_data = json.loads(data)
    try:
        return config_data["component"][component_name]
    except:
        return None

def validate_configuration(data):
    """
    This method validates the Json configuration object against json schema. It throws error if data is invalid.
    :param data: Json configuration object
    :return:
    """
    config_schema_file=utils.get_static_file_path(consts.config_schema_file)
    if config_schema_file:
        with open(config_schema_file, 'r') as schemaFile:
            schema = json.loads(schemaFile.read())
        jsonschema.validate(data, schema)
    else:
        raise Exception(error_messages.CONFIG_SCHEMA_FILE_NOT_EXISTS)
    
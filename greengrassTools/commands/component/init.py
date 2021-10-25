import requests
import os
import shutil
import greengrassTools.common.utils as utils
import greengrassTools.common.model_actions as model_actions
import greengrassTools.common.parse_args_actions as parse_args_actions
import greengrassTools.common.consts as consts
import greengrassTools.common.exceptions.error_messages as error_messages

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
    if not utils.is_directory_empty(current_directory):
        raise Exception(error_messages.INIT_NON_EMPTY_DIR_ERROR)

    # Check if the command args are conflicting
    if parse_args_actions.conflicting_arg_groups(command_args, "init"):
        raise Exception(error_messages.INIT_WITH_CONFLICTING_ARGS)
    
    # Choose appropriate action based on commands
    if "template" in command_args and "language" in command_args:
        template = command_args["template"]
        language = command_args["language"]
        if template and language:
            init_with_template(template,language)
            return 
    elif "repository" in command_args:
        repository = command_args["repository"]
        if repository:
            init_with_repository(repository)
            return
    raise Exception(error_messages.INIT_WITH_INVALID_ARGS)

def init_with_template(template, language):
    """    
    Initializes the directory with a greengrass component template in choosen programming language. 

    This function downloads specified component template by language from github. Raises an exception 
    if the template doesn't exist in that language.
    
    Parameters
    ----------
        template(string): A template name that is used to pull the template by the choosen language.

    Returns
    -------
        None
    """
    template_name = "{}-{}".format(template, language)
    template_url = get_template_url(template_name)
    zip_template_name = "{}.zip".format(template_name)
    
    print("Downloading the template '{}'...".format(template_name))
    
    download_request = requests.get(template_url, stream = True) 
    if download_request.status_code != 200:
        try:
            download_request.raise_for_status()
        except Exception as e:
            print(e)
        finally:
            raise Exception(error_messages.INIT_FAILS_DURING_TEMPLATE_DOWNLOAD)

    with open(zip_template_name, 'wb') as f:
        f.write(download_request.content)

    # unzip the template
    shutil.unpack_archive(zip_template_name, current_directory)

    # Delete the downloaded zip template
    os.remove(zip_template_name)

def init_with_repository(repository):
    """    
    Initializes the directory with a component from greengrass repository catalog. 
    """
    print(" I init with repository")

def get_template_url(template_name):
    """    
    Forms the downloadable url of the template. 

    This functions builds the url by using the greengrass components github repo and its releases.

    Parameters
    ----------
        template_name(string): Template name concatenated with programming language provided in the args.

    Returns
    -------
       template_url(string): URL of the template which will be used for downloading. 
    """ 
    available_templates = get_available_templates_from_github()
    if template_name in available_templates:
        return available_templates[template_name]
    else: 
        raise Exception(error_messages.INIT_WITH_INVALID_TEMPLATE)

def get_available_templates_from_github():
    """    
    Retrieves full list of greengrass component templates that can be used with the cli tool.

    This function lists the templates provided as a json file in the greengrass repository catalog.

    Parameters
    ----------
        None

    Returns
    -------
       template_list(list): List of all the available templates in the greengrass component templates repo.
    """ 
    template_list_response=requests.get(consts.templates_list_url)
    
    if template_list_response.status_code != 200:
        try:
            template_list_response.raise_for_status()
        except Exception as e:
            print(e)
        finally:
            raise Exception(error_messages.INIT_FAILS_DURING_LISTING_TEMPLATES)

    try: 
        template_list = template_list_response.json()
        return template_list
    except Exception as e:
        print(e)
        return []
 
current_directory=os.path.abspath(os.getcwd())

import urllib.request
import ssl
import os
import shutil
import greengrassTools.common.utils as utils
import greengrassTools.common.model_actions as model_actions
import greengrassTools.common.parse_args_actions as parse_args_actions
import greengrassTools.common.consts as consts
import greengrassTools.common.exceptions.error_messages as error_messages
ssl._create_default_https_context = ssl._create_unverified_context

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
    if template in get_available_templates_from_github(): # If template exists in the list? or just try to download and catch error
        # Download from github as a zip. Unzip in the current directory and delete the zip. 

        zip_template_name = "{}.zip".format(template)
        template_url = get_template_url(template,language)
        print("Downloading the template '{}'...".format(template))
        urllib.request.urlretrieve(template_url, zip_template_name)

        # unzip the template
        shutil.unpack_archive(zip_template_name, current_directory)

        # Delete the downloaded zip template
        os.remove(zip_template_name)
    else:
        raise Exception(error_messages.INIT_WITH_INVALID_TEMPLATE)

def init_with_repository(repository):
    """    
    Initializes the directory with a component from greengrass repository catalog. 
    """
    print(" I init with repository")

def get_template_url(template, language):
    """    
    Forms the downloadable url of the template. 

    This functions builds the url by using the greengrass components github repo and its releases.

    Parameters
    ----------
        template(string): Template name provided in the args.
        language(string): Language provided in the args

    Returns
    -------
       template_url(string): URL of the template which will be used for downloading. 
    """ 
    template_url="{}archive/refs/tags/v1.1.0.zip".format(consts.templates_github_url)
    return template_url

def get_available_templates_from_github():
    """    
    Retrieves full list of greengrass component templates that can be used with the cli tool.

    This functions list template releases from the greengrass component templates github repository.

    Parameters
    ----------
        None

    Returns
    -------
       template_list(list): List of all the available templates in the greengrass component templates repo.
    """ 
    template_list = ['HelloWorld-python', 'HelloWorld-java']
    return template_list
   
current_directory=os.path.abspath(os.getcwd())

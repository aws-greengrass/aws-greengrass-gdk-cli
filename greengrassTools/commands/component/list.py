import requests
import logging
import greengrassTools.common.consts as consts
import greengrassTools.common.exceptions.error_messages as error_messages

def run(command_args):
    if "template" in command_args and command_args["template"]:
        logging.info("Listing all the available component templates from GitHub.")
        li = get_component_list_from_github(consts.templates_list_url)
        logging.info("Found '{}' component templates to display.".format(len(li)))
        display_list(li)
    elif "repository" in command_args and command_args["repository"]:
        logging.info("Listing all the available component repositories from GitHub.")
        li = get_component_list_from_github(consts.repository_list_url)
        logging.info("Found '{}' component repositories to display.".format(len(li)))
        display_list(li)
        
def get_component_list_from_github(url):
    comp_list_response=requests.get(url)
    if comp_list_response.status_code != 200:
        try:
            comp_list_response.raise_for_status()
        except Exception as e:
            logging.error(e)
            raise e
        finally:
            raise Exception(error_messages.LISTING_COMPONENTS_FAILED)
    try: 
        # TODO: Integ test for checking if the github file is always a valid json file.
        # TODO: GitHub Workflow of repository catalog should check for this. 
        comp_list = comp_list_response.json()
        return comp_list
    except Exception as e:
        logging.error(e)
        return []

def display_list(components):
    # TODO: Short description of what each component is for??
    i = 1
    for component in components:
        print(f"{i}. {component}")
        i+=1
        

 

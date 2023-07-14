import gdk.common.consts as consts
import gdk.common.exceptions.error_messages as error_messages
import gdk.commands.Command as Command
import gdk.commands.component.project_utils as get_project_config_values
from gdk.common.configuration import get_configuration
from gdk.common.configuration import validate_configuration
import gdk.common.utils as utils
import argparse
import json  


class Wizard:
    """
    A class used to represent the GDK Startup Wizard

    Methods: 
    -----------
    prompt_required_fields()
        prompts the user of all the required fields in the gdk config file
    prompt_optional_fields()
        prompts the user of all the optional fields in the gdk config file 
    check_input(input)
    """

    def __init__(self) -> None:
        """
        Initialize the Wizard object

        Attributes
        ----------
        field_map : data(dict)
            A dictionary object containing the configuration from greengrass project config file.

        """
        self.field_map = get_configuration()

    def prompt_required_fields(self):
        """
        Prompts the user of all the required fields in the gdk config file
        and updates the field_map if their answer is valid  as the user 
        answers the question to each prompt 

        Parameters
        ----------
            None
        
        Returns
        -------
            None
        """
        project_config = self.field_map["component"]
        component_name = next(iter(project_config))
        
        # parser for commandline options: https://docs.python.org/3/library/argparse.html
        parser = argparse.ArgumentParser()

        parser.add_argument('--author', help='Author of the component')
        parser.add_argument('--version', help='Version of the component')
        parser.add_argument('--build_system', help='Build system to use')
        parser.add_argument('--bucket', help='Prefix of the S3 bucket')
        parser.add_argument('--region', help='AWS region')
        parser.add_argument('--gdk_version', help='Version of the gdk cli tool compatible with the provided configuration')
        parser.add_argument('--change_value', help='Change the value of a component field')

        # later PRs will include a helper method to remove repetitive code
        component_author = project_config[component_name]['author']
        if self.change_value(parser, field='author', value=component_author):
            while True:
                args = parser.parse_args(['--author', input('Enter the author of the component: ')])
                if self.check_input(args.author):
                    self.field_map['component'][component_name]['author'] = args.author
                    break
                print('Invalid author name. Please input again.')

    
        component_version = project_config[component_name]['version']
        if self.change_value(parser, field='version', value=component_version):
            while True: 
                args = parser.parse_args(['--version', input('Enter the version of the component: ')])
                if self.check_input(args.version):
                    self.field_map['component'][component_name]['version'] = args.version
                    break
                print("Invalid version. Please input again.")


        component_build_system = project_config[component_name]['build']['build_system']
        if self.change_value(parser, field='build_system', value=component_build_system):
            while True:
                args = parser.parse_args(['--build_system', input('Enter the build system of the component: ')])
                if self.check_input(args.build_system):
                    self.field_map['component'][component_name]['build']['build_system'] = args.build_system
                    break
                print('Invalid build system name. Please input again.')  


        component_bucket = project_config[component_name]['publish']['bucket']
        if self.change_value(parser, field='bucket', value=component_bucket):
            while True:
                args = parser.parse_args(['--bucket', input('Enter the S3 bucket of the component: ')])
                if self.check_input(args.bucket):
                    self.field_map['component'][component_name]['publish']['bucket'] = args.bucket
                    break
                print('Invalid S3 bucket name. Please input again.') 


        component_region = project_config[component_name]['publish']['region']
        if self.change_value(parser, field='region', value=component_region):
            while True:
                args = parser.parse_args(['--region', input('Enter the region of the component: ')])
                if self.check_input(args.region):
                    self.field_map['component'][component_name]['publish']['region'] = args.region
                    break
                print('Invalid region. Please input again.')


        component_gdk_version = self.field_map['gdk_version'] 
        if self.change_value(parser, field='gdk_version', value=component_gdk_version):
            while True:
                args = parser.parse_args(['--gdk_version', input('Enter the gdk-version of the component: ')])
                if self.check_input(args.gdk_version):
                    self.field_map['gdk_version'] = args.gdk_version
                    break
                print('Invalid gdk-version. Please input again.')        


    def prompt_optional_fields(self):
        """
        Prompts the user of all the optional fields of the gdk config file
        and updates the field_map if their answer is valid  as the user 
        answers the question to each prompt 

        Parameters
        ----------
            None
        
        Returns
        -------
            None
        """
        pass
    

    def check_input(self,input):
        """
        Prompts the user of all the optional fields of the gdk config file
        and updates the field_map if their answer is valid  as the user 
        answers the question to each prompt 

        Parameters
        ----------
            None
        
        Returns
        -------
            None
        """
        
        return True
    

    def change_value(self, parser, field, value):
        """
        Prompts the users to answer if they would like to change the field value
        of a particular field in the gdk-config file

        Parameters
        ----------
            field (string): a field key of the gdk-config file to be changed
            value (string): the current value corresponding the field key to be changed
            parser (ArgumentParser): parser for retriving command line arguments 

        Returns
        -------
            boolean: True if the user answers 'y' they do want to change the value of field 'field'
                    and False if the user answers 'n' they do not want to change the value of that field 
                    
                    
        """
        while True:
            args = parser.parse_args(['--change_value', input(f'Do you want to change the field {field} with value {value} ?(y/n)')])
            if args.change_value.lower() in {'y', 'n'}:
                break
            print("Your input was not a valid response. Please respond again.")
        return args.change_value.lower() == 'y'


    def write_to_config_file(self):
        """
        Writes all the values in field_map to the gdk-config.json file 

        Parameters
        ----------
            None
        
        Returns
        -------
            None 
        """
        pass


    def get_schema(self):

        """
        Retrieves the schema of the config file     
        
        Raises an exception if the schema file doesn't exist.

        Parameters
        ----------
            None

        Returns
        -------
            data(dict): config file schema as a python dictionary object
        """     
        config_schema_file = utils.get_static_file_path(consts.config_schema_file)
        with open(config_schema_file, "r") as schemaFile:
            schema = json.loads(schemaFile.read())
        return schema


    def prompt(self):
        """
        Wapper method that prompts users for required and optional field values
        for the gdk config file

        Parameters
        ----------
            None
        
        Returns
        -------
            None
        """
        self.prompt_required_fields()
        self.prompt_optional_fields()

import gdk.common.consts as consts
import gdk.common.exceptions.error_messages as error_messages
import gdk.commands.Command as Command
import gdk.commands.component.project_utils as get_project_config_values
from gdk.common.configuration import get_configuration
from gdk.common.configuration import validate_configuration
import gdk.common.utils as utils
import argparse
import sys
import json  


class Wizard:
    def __init__(self) -> None:
        # self.field_map is a dictionary object
        # self.field_map = get_configuration()

        project_config_file = '/home/jacksozh/workspace/aws-greengrass-gdk-cli/gdk/wizard/static/dummy_config.json'
        with open(project_config_file, "r") as config_file:
            config_data = json.loads(config_file.read())

        self.field_map = config_data

    """
    prompts the user of all required fields
    """
    def prompt_required_fields(self):

        project_config = self.field_map["component"]
        component_name = next(iter(project_config))
        
        # parser for commandline options: https://docs.python.org/3/library/argparse.html
        parser = argparse.ArgumentParser()

        parser.add_argument('--author', help='Author of the component')
        parser.add_argument('--version', help='Version of the component')
        parser.add_argument('--build_system', choices=['zip', 'maven', 'gradle', 'gradlew', 'custom'], help='Build system to use')
        # parser.add_argument('--custom-build-command', nargs='+', help='Custom build command (required if build system is custom)')
        parser.add_argument('--bucket', help='Prefix of the S3 bucket')
        parser.add_argument('--region', choices=['us-east-2', 'us-east-1', 'us-west-2', 'ap-south-1', 'ap-northeast-2',
                                                'ap-southeast-1', 'ap-southeast-2', 'ap-northeast-1', 'ca-central-1',
                                                'cn-north-1', 'eu-central-1', 'eu-west-1', 'eu-west-2',
                                                'us-gov-west-1', 'us-gov-east-1'], help='AWS region')
        parser.add_argument('--gdk_version', help='Version of the gdk cli tool compatible with the provided configuration')
        parser.add_argument('--change_value', help='Change the value of a component field')
        
    
            # check if there's already a value for that field, show the current value of that field
            # then prompt the user to answer (y/n) if they want to change the value in that field. 
            # if no break out of loop, if yes prompt them to change the value of the field

        # component_author = project_config[component_name]['author']
        # # if component_author != "<PLACEHOLDER_AUTHOR>":
        # if self.change_value(parser, field='author', value=component_author):
        #     while True:
        #         args = parser.parse_args(['--author', input('Enter the author of the component: ')])
        #         if self.check_input(args.author):
        #             self.field_map['component'][component_name]['author'] = args.author
        #             break
        #         print('Invalid author name. Please input again.')

    
        # component_version = project_config[component_name]['version']
        # # if component_version != "NEXT_PATCH":
        # if self.change_value(parser, field='version', value=component_version):
        #     while True: 
        #         args = parser.parse_args(['--version', input('Enter the version of the component: ')])
        #         if self.check_input(args.version):
        #             self.field_map['component'][component_name]['version'] = args.version
        #             break
        #         print("Invalid version. Please input again.")


        # component_build_system = project_config[component_name]['build']['build_system']
        # if self.change_value(parser, field='build_system', value=component_build_system):
        #     while True:
        #         args = parser.parse_args(['--build_system', input('Enter the build system of the component: ')])
        #         if self.check_input(args.build_system):
        #             self.field_map['component'][component_name]['build']['build_system'] = args.build_system
        #             break
        #         print('Invalid build system name. Please input again.')  



        # component_bucket = project_config[component_name]['publish']['bucket']
        # if self.change_value(parser, field='bucket', value=component_bucket):
        #     while True:
        #         args = parser.parse_args(['--bucket', input('Enter the S3 bucket of the component: ')])
        #         if self.check_input(args.bucket):
        #             self.field_map['component'][component_name]['publish']['bucket'] = args.bucket
        #             break
        #         print('Invalid S3 bucket name. Please input again.') 


        
        # component_region = project_config[component_name]['publish']['region']
        # if self.change_value(parser, field='region', value=component_region):
        #     while True:
        #         args = parser.parse_args(['--region', input('Enter the region of the component: ')])
        #         if self.check_input(args.region):
        #             self.field_map['component'][component_name]['publish']['region'] = args.region
        #             break
        #         print('Invalid region. Please input again.')


        component_gdk_version = self.field_map['gdk_version'] 
        if self.change_value(parser, field='gdk_version', value=component_gdk_version):
            while True:
                args = parser.parse_args(['--gdk_version', input('Enter the gdk-version of the component: ')])
                if self.check_input(args.gdk_version):
                    self.field_map['gdk_version'] = args.gdk_version
                    break
                print('Invalid gdk-version. Please input again.')        




    """
    A helper function for the prompt_required_fields method to
    reduce repetiitve code
    """
    def required_fields_helper(self, parser, field, value):
        if self.change_value(parser, field=field, value=value):
            while True:
                args = parser.parse_args([f'--{field}', input(f'Enter the {field} of the component: ')])
                if self.check_input(args.field):
                    return args.field #look into what the type is of args.field, specifically the type after args.
                print('Invalid author name. Please input again.')
        return value    



    """
    prompt users of all optional fields in a heiarchical manner
    """
    def prompt_optional_fields(self):
        return
    

    """
    Check the user's inputs against the GDK-JSON file schema, returning True
    for now
    """
    def check_input(self,input):
        return True
    

    def change_value(self, parser, field, value):
        while True:
            args = parser.parse_args(['--change_value', input(f'Do you want to change the field {field} with value {value} ?(y/n)')])
            if args.change_value.lower() in {'y', 'n'}:
                break
            print("Your input was not a valid response. Please respond again.")
        return args.change_value.lower() == 'y'


    """
    upon exiting the wizard, it will first flush all the values 
    stored in self.field_map to the config file 
    """
    def write_to_config_file(self):
        pass


    def get_schema(self):
        config_schema_file = utils.get_static_file_path(consts.config_schema_file)
        with open(config_schema_file, "r") as schemaFile:
            schema = json.loads(schemaFile.read())
        return schema



    def prompt(self):
        self.prompt_required_fields()
        self.prompt_optional_fields()

    
############################# Testing Code ##########################################


def get_schema():
    config_schema_file = utils.get_static_file_path(consts.config_schema_file)
    with open(config_schema_file, "r") as schemaFile:
        schema = json.loads(schemaFile.read())
    return schema

def main():
    wiz = Wizard()
    # print(wiz.get_schema())
    # print('SCHEMA_KEYS:', list(get_schema().keys()))
    # print('SCHEMA_values:', list(get_schema().values()))
    # print(get_schema())

    # print(utils.current_directory)

    wiz.prompt_required_fields()
    print(wiz.field_map)

if __name__ == "__main__":
    main()


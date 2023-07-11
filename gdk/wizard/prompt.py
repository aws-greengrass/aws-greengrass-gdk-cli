import gdk.common.consts as consts
import gdk.common.exceptions.error_messages as error_messages
import gdk.commands.Command as Command
import gdk.commands.component.project_utils as get_project_config_values
import gdk.common.configuration as get_configuration
import gdk.common.configuration as validate_configuration
import gdk.common.utils as utils
import argparse
import json 


class Wizard:
    def __init__(self) -> None:
        # self.field_map is a dictionary object
        self.field_map = get_configuration()


    """
    prompts the user of all required fields
    """
    def prompt_required_fields(self):
        required_fields = self.get_schema
        parser = argparse.ArgumentParser()

        parser.add_argument('--author', help='Author of the component')
        parser.add_argument('--version', help='Version of the component')
        parser.add_argument('--build-system', choices=['zip', 'maven', 'gradle', 'gradlew', 'custom'], help='Build system to use')
        parser.add_argument('--custom-build-command', nargs='+', help='Custom build command (required if build system is custom)')
        parser.add_argument('--bucket', help='Prefix of the S3 bucket')
        parser.add_argument('--region', choices=['us-east-2', 'us-east-1', 'us-west-2', 'ap-south-1', 'ap-northeast-2',
                                                'ap-southeast-1', 'ap-southeast-2', 'ap-northeast-1', 'ca-central-1',
                                                'cn-north-1', 'eu-central-1', 'eu-west-1', 'eu-west-2',
                                                'us-gov-west-1', 'us-gov-east-1'], help='AWS region')
        
        while True:
            # check if there's already a value for that field, show the current value of that field
            # then prompt the user to answer (y/n) if they want to change the value in that field. 
            # if no break out of loop, if yes prompt them to change the value of the field
            args = parser.parse_args(['--author', input('Enter the author name of the component: ')])
            if self.check_input(args.author):
                self.field_map['author'] = args.author
                break
            print('Invalid author name. Please input again')
        

        
    
    """
    prompt users of all optional fields in a heiarchical manner
    """
    def prompt_optional_fields(self):
        return
    

    """
    Check the user's inputs against the GDK-JSON file schema 
    """
    def check_input(self,input):
        return

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

    






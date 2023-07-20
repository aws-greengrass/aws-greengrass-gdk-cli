import gdk.common.consts as consts
from gdk.common.configuration import get_configuration, _get_project_config_file
from jsonschema import validate, exceptions
import gdk.common.utils as utils
import argparse
import json


class Wizard:
    """
    A class used to represent the GDK Startup Wizard

    Methods:
    -----------
    prompt_fields()
        prompts the user of all the required and optional fields in the gdk config file
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
        self.project_config_file = _get_project_config_file()
        self.schema = self.get_schema()

    def prompt_fields(self):
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
        parser.add_argument("--author", help="Author of the component")
        parser.add_argument("--version", help="Version of the component")
        parser.add_argument("--build_system", help="Build system to use")
        parser.add_argument("--bucket", help="Prefix of the S3 bucket")
        parser.add_argument("--region", help="AWS region")
        parser.add_argument(
            "--gdk_version",
            help="Version of the gdk cli tool compatible with the provided configuration",
        )
        parser.add_argument(
            "--change_value", help="Change the value of a component field"
        )

        component_author = project_config[component_name]["author"]
        self.field_map["component"][component_name][
            "author"
        ] = self.required_fields_helper(parser, "author", component_author)

        component_version = project_config[component_name]["version"]
        self.field_map["component"][component_name][
            "version"
        ] = self.required_fields_helper(parser, "version", component_version)

        component_build_system = project_config[component_name]["build"]["build_system"]
        self.field_map["component"][component_name]["build"][
            "build_system"
        ] = self.required_fields_helper(parser, "build_system", component_build_system)

        component_bucket = project_config[component_name]["publish"]["bucket"]
        self.field_map["component"][component_name]["publish"][
            "bucket"
        ] = self.required_fields_helper(parser, "bucket", component_bucket)

        component_region = project_config[component_name]["publish"]["region"]
        self.field_map["component"][component_name]["publish"][
            "region"
        ] = self.required_fields_helper(parser, "region", component_region)

        component_gdk_version = self.field_map["gdk_version"]
        self.field_map["gdk_version"] = self.required_fields_helper(
            parser, "gdk_version", component_gdk_version
        )

    def required_fields_helper(self, parser, field, value):
        """
        Parameters
        ----------
            field (string): a field key of the gdk-config file to be changed
            value (string): the current value corresponding the field key to be changed
            parser (ArgumentParser): parser for retriving command line arguments

        Returns
        -------
            string: the value for the field key "field"
        """
        if self.change_value(parser, field=field, value=value):
            while True:
                args = parser.parse_args(
                    [f"--{field}", input(f"Enter the {field} of the component: ")]
                )
                schema_value = self.extract_field_value_from_schema(field)
                store = {
                    "author": args.author,
                    "version": args.version,
                    "build_system": args.build_system,
                    "bucket": args.bucket,
                    "region": args.region,
                    "gdk_version": args.gdk_version,
                }
                if self.check_input(store[field], schema_value):
                    return store[field]
                print(f"Invalid value for {field}. Please input again.")
        return value

    def check_input(self, input_value, schema_value):
        """
        Prompts the user of all the optional fields of the gdk config file and updates the
        field_map if their answer is valid  as the user answers the question to each prompt

        Parameters
        ----------
            input_value (string): user's answer to prompt question about field value
            schema_value (data(dict)): required field value format as per schema

        Returns
        -------
            boolean: True if input_value is valid as per schema and False otherwise
        """
        try:
            validate(input_value, schema_value)
            return True
        except exceptions.ValidationError:
            return False

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
            args = parser.parse_args(
                [
                    "--change_value",
                    input(
                        f"Want to change field {field} with value {value} ?(y/n)"
                    ),
                ]
            )
            if args.change_value.lower() in {"y", "n"}:
                break
            print("Your input was not a valid response. Please respond again.")
        return args.change_value.lower() == "y"

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
        with open(self.project_config_file, "w", encoding="utf-8") as f:
            f.write(json.dumps(self.field_map, indent=4))

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

    def extract_field_value_from_schema(self, field_name):
        """
        Recursively extracts the valid format for field_name as speified by the schema

        Parameters
        ----------
            field_name(string): a field key of the schema

        Returns
        -------
            field_value(data(dict)): valid format for field_name as per schema
        """
        field_value = None

        def traverse_schema(schema, field_name):
            nonlocal field_value
            ignore_fields = {
                "oneOf",
                "type",
                "enum",
                "required",
                "dependentRequired",
                "allOf",
                "if",
                "then",
            }

            if isinstance(schema, dict):
                for key, value in schema.items():
                    if key == field_name:
                        field_value = value
                    elif key not in ignore_fields:
                        traverse_schema(value, field_name)

        traverse_schema(self.schema, field_name)
        return field_value

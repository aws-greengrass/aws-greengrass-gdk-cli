from jsonschema import validate, exceptions


class Wizard_checker:
    def __init__(self, data):
        self.data = data
        self.schema = self.data.schema

    def is_valid_input(self, input_value, field):
        """
        Prompts the user of all the optional fields of the gdk config file and updates the
        field_map if their answer is valid  as the user answers the question to each prompt

        Parameters
        ----------
            input_value(string): The value entered by the user for the field
            field(string): The field name of the field in the gdk config file

        Returns
        -------
            boolean: True if the input value is valid for the field, False otherwise.
        """
        schema_value = self.extract_field_value_from_schema(field)
        try:
            validate(input_value, schema_value)
            return True
        except exceptions.ValidationError:
            return False

    def extract_field_value_from_schema(self, field_name):
        """
        Parameters
        ----------
            field_name(string): The field name of the field in the gdk config file

        Returns
        -------
            schema_value(dict): The value of the field as per the schema of the gdk config file.
            None if the field is not present in the schema.

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

            elif isinstance(schema, list):
                for item in schema:
                    traverse_schema(item, field_name)

        traverse_schema(self.schema, field_name)
        return field_value

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
            None

        Returns
        -------
            None
        """
        # if not input_value: return True
        schema_value = self.extract_field_value_from_schema(field)
        try:
            validate(input_value, schema_value)
            # return input_value
            return True
        except exceptions.ValidationError:
            # raise Exception(f"The supplied value {input_value} is not valid. Please try again.")
            return False

    def extract_field_value_from_schema(self, field_name):
        """
        Parameters
        ----------
            field_name(string):

        Returns
        -------

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

import json
import jsonschema


class RecipeValidator:
    def __init__(self, schema_file):
        self._setup_schema(schema_file)

    def validate_recipe(self, recipe):
        processed_recipe = self._keys_to_lower(recipe)
        jsonschema.validate(instance=processed_recipe, schema=self.schema, cls=jsonschema.validators.Draft7Validator)

    def _setup_schema(self, schema_file):
        with open(schema_file, 'r') as file:
            self.schema = json.loads(file.read())
            jsonschema.Draft7Validator.check_schema(schema=self.schema)

    def _keys_to_lower(self, obj):
        if type(obj) is dict:
            return_dict = {}
            for key, item in obj.items():
                return_dict[key.lower()] = self._keys_to_lower(item)
            return return_dict
        elif type(obj) is list:
            return [self._keys_to_lower(i) for i in obj]
        else:
            return obj

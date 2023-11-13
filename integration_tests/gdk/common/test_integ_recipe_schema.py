import json
import jsonschema

import gdk.common.utils as utils

recipe_schema_file = "recipe_schema.json"


def test_recipe_schema_is_valid():
    # Integ test for validating that the recipe schema is a valid json schema
    with open(utils.get_static_file_path(recipe_schema_file), "r") as schema_file:
        schema = json.loads(schema_file.read())
    jsonschema.Draft7Validator.check_schema(schema=schema)

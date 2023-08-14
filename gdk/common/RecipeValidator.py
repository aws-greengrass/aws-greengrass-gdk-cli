import json
import logging
from pathlib import Path

import jsonschema

from gdk.common import utils, consts
from gdk.common.CaseInsensitive import CaseInsensitiveRecipeFile, CaseInsensitiveDict


class RecipeValidator:
    """
    Validates the syntax and structure of a component recipe.

    This class provides functionality to validate the syntax and semantics of a component recipe either by
    loading the recipe from a file path or by validating the provided recipe data directly against the
    Greengrass component recipe schema.

    Parameters
    ----------
    recipe_source : Path or CaseInsensitiveDict
        The source of the component recipe. It can be either a file path to the recipe file or a dictionary containing
        the recipe data.

    Attributes
    ----------
    recipe_source : Path or CaseInsensitiveDict
        The source of the component recipe.

    Methods
    -------
    validate_semantics()
        Validates the semantics of the component recipe against the Greengrass component recipe schema.

    """

    def __init__(self, recipe_source):
        """
        Initialize the RecipeValidator with the provided recipe source.

        Parameters
        ----------
        recipe_source : Path or CaseInsensitiveDict
            The source of the component recipe.

        """
        self.recipe_source = recipe_source
        self.recipe_data = None

    def validate_semantics(self):
        """
        Validates the semantics of the component recipe against the Greengrass component recipe schema.

        This method loads the Greengrass component recipe schema, converts the recipe data keys to lowercase, and then
        validates the recipe data against the schema using the JSON Schema validation. If validation fails, it logs the
        validation errors and raises a jsonschema.exceptions.ValidationError.

        Raises
        ------
        jsonschema.exceptions.ValidationError
            If the component recipe data does not conform to the Greengrass component recipe schema.

        """
        self.recipe_data = self._load_recipe()
        recipe_schema = utils.get_static_file_path(consts.user_input_recipe_schema_file)
        with open(recipe_schema, 'r') as schema_file:
            schema = json.load(schema_file)
        logging.debug("Validating the recipe file.")
        data = self._convert_keys_to_lowercase(self.recipe_data)
        try:
            jsonschema.validate(data, schema)
        except jsonschema.exceptions.ValidationError as err:
            utils.parse_json_schema_errors(err)
            raise err

    def _load_recipe(self):
        """
        Load and return the component recipe data.

        Returns
        -------
        CaseInsensitiveDict
            The component recipe data.

        Raises
        ------
        ValueError
            If the provided recipe source type is invalid.

        """
        if isinstance(self.recipe_source, Path):
            return CaseInsensitiveRecipeFile().read(self.recipe_source)
        elif isinstance(self.recipe_source, CaseInsensitiveDict):
            return self.recipe_source
        else:
            raise ValueError(f"Invalid recipe source type {type(self.recipe_source)}")

    def _convert_keys_to_lowercase(self, input_dict):
        """
        Recursively convert the keys of a dictionary to lowercase.

        Parameters
        ----------
        input_dict : CaseInsensitiveDict or list
            The input dictionary or list.

        Returns
        -------
        CaseInsensitiveDict or list
            The input dictionary or list with keys converted to lowercase.

        """
        if isinstance(input_dict, CaseInsensitiveDict):
            return {key.lower(): self._convert_keys_to_lowercase(value) for key, value in input_dict.items()}
        elif isinstance(input_dict, list):
            return [self._convert_keys_to_lowercase(item) for item in input_dict]
        else:
            return input_dict

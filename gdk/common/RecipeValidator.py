from pathlib import Path

from gdk.common.CaseInsensitive import CaseInsensitiveRecipeFile


class RecipeValidator:
    """
    Validates the syntax and semantics of a component recipe.

    This class can validate the syntax and semantics of a component recipe either by loading the recipe from a file
    path or by validating the provided recipe data directly.

    Parameters
    ----------
    recipe_source : Path or dict
        The source of the component recipe. It can be either a file path to the recipe file or a dictionary containing
        the recipe data.

    Attributes
    ----------
    recipe_source : Path or dict
        The source of the component recipe.

    Methods
    -------
    validate_semantics()
        Validates the semantics of the component recipe.

    """

    def __init__(self, recipe_source):
        """
        Initialize the RecipeValidator with the provided recipe source.

        Parameters
        ----------
        recipe_source : Path or dict
            The source of the component recipe.

        """
        self.recipe_source = recipe_source
        self.recipe_data = None

    def validate_semantics(self):
        """
        Validates the semantics of the component recipe.

        """
        self.recipe_data = self._load_recipe()
        # TODO: add the semantic validation logic
        pass

    def _load_recipe(self):
        """
        Load and return the component recipe data.

        Returns
        -------
        dict
            The component recipe data.

        Raises
        ------
        ValueError
            If the provided recipe source type is invalid.

        """
        if isinstance(self.recipe_source, Path):
            return CaseInsensitiveRecipeFile().read(self.recipe_source)
        elif isinstance(self.recipe_source, dict):
            return self.recipe_source
        else:
            raise ValueError("Invalid recipe source type")

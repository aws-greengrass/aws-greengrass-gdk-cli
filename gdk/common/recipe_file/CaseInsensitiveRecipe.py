from requests.structures import CaseInsensitiveDict
from gdk.common.recipe_file.Recipe import Recipe


class CaseInsensitiveRecipe:
    def __convert_nested_dict(self, recipe: CaseInsensitiveDict) -> CaseInsensitiveDict:
        for key, value in recipe.items():
            if isinstance(value, dict):
                recipe.update({key: self.__convert_nested_dict(CaseInsensitiveDict(value))})
            elif isinstance(value, list):
                recipe.update(
                    {key: [self.__convert_nested_dict(CaseInsensitiveDict(val)) for val in value if isinstance(val, dict)]}
                )
        return recipe

    def __convert_nested_CaseInsensitiveDict(self, recipe: dict) -> dict:
        for key, value in recipe.items():
            if isinstance(value, CaseInsensitiveDict):
                recipe.update({key: self.__convert_nested_CaseInsensitiveDict(dict(value))})
            elif isinstance(value, list):
                recipe.update(
                    {
                        key: [
                            self.__convert_nested_CaseInsensitiveDict(dict(val))
                            for val in value
                            if isinstance(val, CaseInsensitiveDict)
                        ]
                    }
                )
        return recipe

    def __get(self, original: dict) -> CaseInsensitiveDict:
        __recipe = CaseInsensitiveDict(original)
        self.__convert_nested_dict(__recipe)
        return __recipe

    def __get_as_dict(self, cir: CaseInsensitiveDict) -> dict:
        __recipe = dict(cir)
        self.__convert_nested_CaseInsensitiveDict(__recipe)
        return __recipe

    def write(self, file_path, content: CaseInsensitiveDict) -> None:
        """
        Converts case insensitive dictionary (requests library) to a python dictionary and writes it to given file path.
        """
        Recipe().write(file_path, self.__get_as_dict(content))

    def read(self, file_path) -> CaseInsensitiveDict:
        """
        Reads contents of the give file as a python dictionary and converts it to a case insensitive
        dictionary (requests library).
        """
        original_recipe = Recipe().read(file_path)
        return self.__get(original_recipe)

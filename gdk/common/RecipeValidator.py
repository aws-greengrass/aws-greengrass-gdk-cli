import json
import logging
from pathlib import Path

import jsonschema

from gdk.common import utils, consts
from gdk.common.CaseInsensitive import CaseInsensitiveRecipeFile, CaseInsensitiveDict


class RecipeValidator:
    """
    Validates the semantics and specific input values of a Greengrass component recipe.

    This class provides functionality to validate a component recipe by either loading the recipe from a file path
    or by validating the provided recipe data directly.

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
    validate_recipe_format_version()
        Validates that the provided RecipeFormatVersion in the recipe is valid and compatible with the gdk.

    validate_semantics()
        Validates the semantics of the component recipe against the Greengrass component recipe schema.

    validate_input()
        Validates specific input fields within the component recipe for correctness and adherence to best practices.

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
        self.recipe_data = self._convert_keys_to_camelcase(self._load_recipe())

    def validate_recipe_format_version(self):
        """
        Validate the Recipe Format Version in the recipe data.

        This method checks whether the provided Recipe Format Version is valid and supported.

        Raises
        ------
        Exception
            If the RecipeFormatVersion field is missing.

        """
        recipe_format_version = self.recipe_data.get("RecipeFormatVersion")
        if not recipe_format_version:
            err_msg = "Recipe validation failed for 'RecipeFormatVersion'. This field is required but missing " \
                      "from the recipe. Please correct it and try again."
            logging.error(err_msg)
            raise Exception(err_msg)

        supported_recipe_version = ["2020-01-25"]
        if recipe_format_version not in supported_recipe_version:
            logging.warning(f"The provided RecipeFormatVersion '{recipe_format_version}' is not supported in this gdk "
                            f"version. Please ensure that it is a valid RecipeFormatVersion compatible with the gdk, "
                            f"and refer to the list of supported RecipeFormatVersion: {supported_recipe_version}.")

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
        recipe_schema = utils.get_static_file_path(consts.user_input_recipe_schema_file)
        with open(recipe_schema, 'r') as schema_file:
            schema = json.load(schema_file)
        logging.debug("Validating the recipe file.")
        try:
            jsonschema.validate(self.recipe_data, schema)
        except jsonschema.exceptions.ValidationError as err:
            utils.parse_json_schema_errors(err)
            raise err

    def validate_input(self):
        """
        Validates specific input fields within the component recipe for correctness and adherence to best practices.

        This function performs input validation on the component recipe. It checks for recommended practices, potential
        issues, and ensures that the input data aligns with Greengrass specifications. Instead of raising errors and
        interrupting the process, it displays warnings to draw attention to non-compliant input.

        """

        self._validate_component_type_and_source()
        self._validate_lifecycle_overlap()
        self._validate_manifests()

    def _validate_component_type_and_source(self):
        """
        Warns if the user specifies the component type or source in the recipe, which is not recommended,
        but does not break the process.

        """
        if "ComponentType" in self.recipe_data:
            logging.warning("It's not recommended to specify the component type in a recipe. "
                            "AWS IoT Greengrass sets the type for you when you create a component.")

        if "ComponentSource" in self.recipe_data:
            logging.warning("It's not recommended to specify the component source in a recipe. "
                            "AWS IoT Greengrass sets this parameter for you when you create a "
                            "component from a Lambda function.")

    def _validate_lifecycle_overlap(self):
        """
        Warns if both "startup" and "run" lifecycles are defined, which may lead to unexpected behavior.

        """
        # The "run" lifecycle defines the script to run when the component starts, while the "startup" lifecycle defines
        # the background process to run when the component starts. Defining both may lead to unexpected behavior.
        if "Lifecycle" in self.recipe_data:
            lifecycle = self.recipe_data["Lifecycle"]
            if "startup" in lifecycle and "run" in lifecycle:
                logging.warning(
                    "You can define only one startup or run lifecycle in a recipe. Defining both may lead to "
                    "unexpected behavior.")

    def _validate_manifests(self):
        """
        Validates artifacts, platform, and lifecycle within the manifests section of the component recipe.

        """
        if "Manifests" in self.recipe_data:
            manifests = self.recipe_data.get("Manifests")  # 'manifests' is a list of object
            for manifest in manifests:
                self._validate_artifacts(manifest)
                self._validate_platform(manifest)

                # Similar to the lifecycle check above, but this check is specific to the manifests section.
                if "Lifecycle" in manifest and "startup" in manifest["Lifecycle"] and "run" in manifest["Lifecycle"]:
                    logging.warning(
                        "You can define only one startup or run lifecycle in the recipe manifest. Defining both may "
                        "result in unexpected behavior.")

    def _validate_artifacts(self, manifest):
        """
        Validates artifact URIs and script alignment within an artifact.

        """
        if "Artifacts" in manifest:
            artifacts = manifest["Artifacts"]  # 'artifacts' is a list of object
            uris = []
            for artifact in artifacts:
                if "URI" in artifact:
                    uri = artifact["URI"]
                    uris.append(uri)
                    # check if the URI of an artifact is an S3 bucket
                    if not uri.startswith(utils.s3_prefix):
                        logging.warning(f"The provided URI '{uri}' in the recipe is not an S3 bucket.")

            # One potential scenario is when a user specifies an artifact URI, but the script to run
            # references a different artifact. Displaying a warning here can help identify such issues early
            # in the validation process.
            if "Lifecycle" in manifest and "run" in manifest["Lifecycle"]:
                run = manifest["Lifecycle"]["run"]
                if isinstance(run, str):
                    script = run
                else:
                    script = run.get("Script", None)
                if script and uris:
                    artifact_names = [uri.split("/")[-1] for uri in uris]
                    if not any(artifact in script for artifact in artifact_names):
                        logging.warning("The filename in the script does not match the artifact names in the URI "
                                        "provided in the recipe. If this is inaccurate, please exit and verify that "
                                        "both the artifacts and the script are correct.")

    def _validate_platform(self, manifest):
        """
        Validates platform architecture against the given OS.

        """
        if "Platform" in manifest:
            os = manifest["Platform"].get("os")
            architecture = manifest["Platform"].get("architecture")

            if os and architecture:
                if os not in ["any", "all", "*"] and architecture not in ["any", "all", "*"]:
                    os_architecture_dict = {
                        "windows": ["x86", "amd64", "arm", "aarch64"],
                        "linux": ["x86", "amd64", "arm", "aarch64", "powerpc", "mips", "sparc"],
                        "darwin": ["x86", "amd64", "arm", "aarch64"],
                        "macos": ["amd64", "aarch64"],
                        "ubuntu": ["x86", "amd64", "arm", "aarch64", "powerpc", "sparc"],
                        "android": ["arm", "aarch64", "x86", "amd64"]
                    }
                    if os in os_architecture_dict and architecture not in os_architecture_dict[os]:
                        logging.warning(
                            f"The specified architecture '{architecture}' may not be supported by the os '{os}' as "
                            f"provided in the recipe.")

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
        -------0
        CaseInsensitiveDict or list
            The input dictionary or list with keys converted to lowercase.

        """
        if isinstance(input_dict, CaseInsensitiveDict):
            return {key.lower(): self._convert_keys_to_lowercase(value) for key, value in input_dict.items()}
        elif isinstance(input_dict, list):
            return [self._convert_keys_to_lowercase(item) for item in input_dict]
        else:
            return input_dict

    def _convert_keys_to_camelcase(self, input_data):
        """
        Recursively converts keys in a nested dictionary to CamelCase based on the predefined mapping.

        Parameters
        ----------
        input_data : CaseInsensitiveDict or list
            The input dictionary or list to be converted.

        Returns
        -------
        CaseInsensitiveDict or list
            The input dictionary or list with keys converted to CamelCase.

        """
        if isinstance(input_data, CaseInsensitiveDict):
            result_dict = {}
            for key, value in input_data.items():
                camelcase_key = self.RECIPE_PROPERTY_CASE_MAPPING.get(key.lower(), key)
                result_dict[camelcase_key] = self._convert_keys_to_camelcase(value)
            return result_dict
        elif isinstance(input_data, list):
            result_list = []
            for item in input_data:
                result_list.append(self._convert_keys_to_camelcase(item))
            return result_list
        else:
            return input_data

    RECIPE_PROPERTY_CASE_MAPPING = {
        "recipeformatversion": "RecipeFormatVersion",
        "componentname": "ComponentName",
        "componentversion": "ComponentVersion",
        "componentdescription": "ComponentDescription",
        "componentpublisher": "ComponentPublisher",
        "componentconfiguration": "ComponentConfiguration",
        "defaultconfiguration": "DefaultConfiguration",
        "componentdependencies": "ComponentDependencies",
        "versionrequirement": "VersionRequirement",
        "dependencytype": "DependencyType",
        "componenttype": "ComponentType",
        "componentsource": "ComponentSource",
        "manifests": "Manifests",
        "name": "Name",
        "platform": "Platform",
        "os": "os",
        "architecture": "architecture",
        "architecture.detail": "architecture.detail",
        "key": "key",
        "lifecycle": "Lifecycle",
        "setenv": "Setenv",
        "install": "install",
        "script": "Script",
        "requiresprivilege": "RequiresPrivilege",
        "skipif": "Skipif",
        "timeout": "Timeout",
        "run": "run",
        "startup": "startup",
        "shutdown": "shutdown",
        "recover": "recover",
        "bootstrap": "bootstrap",
        "selections": "Selections",
        "artifacts": "Artifacts",
        "uri": "URI",
        "unarchive": "Unarchive",
        "permission": "Permission",
        "read": "Read",
        "execute": "Execute",
        "digest": "Digest",
        "algorithm": "Algorithm",
    }

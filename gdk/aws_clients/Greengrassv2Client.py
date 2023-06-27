import logging
import boto3


class Greengrassv2Client:
    """
    Greengrasv2 client utils wrapper
    """

    def __init__(self, _region):
        self.client = boto3.client("greengrassv2", region_name=_region)

    def get_highest_component_version_(self, component_arn) -> str:
        """
        Gets highest version of the component from the sorted order of its versions from an account in a region.

        Returns highest version of the component if it exists already. Else returns None.
        """

        try:
            component_versions = self._get_component_version(component_arn)
            if not component_versions:
                return None
            return component_versions[0]["componentVersion"]
        except Exception:
            logging.error("Error while getting the component versions using arn: %s.", component_arn)
            raise

    def _get_component_version(self, component_arn) -> dict:
        comp_list_response = self.client.list_component_versions(arn=component_arn)
        return comp_list_response["componentVersions"]

    def create_gg_component(self, file_path) -> None:
        """
        Creates a GreengrassV2 private component version using its recipe.

        Raises an exception if the recipe is invalid or the request is not successful.
        """
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                response = self.client.create_component_version(inlineRecipe=f.read())
                logging.info(
                    "Created private version '%s' of the component '%s' in the account.",
                    response.get("componentVersion"),
                    response.get("componentName"),
                )
            except Exception:
                logging.error("Failed to create a private version of the component using the recipe at '%s'.", file_path)
                raise

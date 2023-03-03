import logging


class Greengrassv2Client:
    """
    Greengrasv2 client utils wrapper
    """

    def __init__(self, project_configuration, service_clients):
        self.project_config = project_configuration
        self.greengrass_client = service_clients["greengrass_client"]

    def get_highest_component_version_(self) -> str:
        """
        Gets highest version of the component from the sorted order of its versions from an account in a region.

        Makes a boto3 request with greengrass service client to list all versions of a component in an account.

        Returns
        ----
            version: Highest version of the component if it exists already. Else returns None.
        """

        try:
            region = self.project_config["region"]
            component_name = self.project_config["component_name"]
            account_num = self.project_config["account_number"]
            component_arn = f"arn:aws:greengrass:{region}:{account_num}:components:{component_name}"

            component_versions = self._get_component_version(component_arn)
            if not component_versions:
                return None
            return component_versions[0]["componentVersion"]
        except Exception as exc:
            raise Exception(
                f"Error while getting the component versions of '{component_name}' in '{region}' from the account"
                f" '{account_num}' during publish.\n{exc}"
            ) from exc

    def _get_component_version(self, component_arn) -> dict:
        comp_list_response = self.greengrass_client.list_component_versions(arn=component_arn)
        return comp_list_response["componentVersions"]

    def create_gg_component(self) -> None:
        """
        Creates a GreengrassV2 private component using its recipe.

        Raises an exception if the recipe is invalid or the request is not successful.

        """
        component_name = self.project_config["component_name"]
        component_version = self.project_config["component_version"]
        publish_recipe_file = self.project_config["publish_recipe_file"]
        with open(publish_recipe_file) as f:
            try:
                self.greengrass_client.create_component_version(inlineRecipe=f.read())
                logging.info(
                    "Created private version '%s' of the component '%s' in the account.", component_version, component_name
                )
            except Exception as exc:
                logging.error("Failed to create the component using the recipe at '%s'.", publish_recipe_file)
                raise Exception(
                    f"Creating private version '{component_version}' of the component '{component_name}' failed.\n{exc}"
                ) from exc

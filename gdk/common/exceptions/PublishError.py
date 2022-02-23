class PublishException(Exception):
    def __init__(self, reason="", solution="", exception=None):
        err_details = ""
        if exception:
            err_details = f"Error details: {exception}\n"
        self.message = f"{reason}\n{err_details}{solution}"
        super().__init__(self.message)


class ArtifactNotFoundDuringPublishException(PublishException):
    def __init__(self, artifact_file, gg_build_component_artifacts, exception=None):
        reason = (
            f"Could not find the artifact file specified in the recipe '{artifact_file}' inside the build folder"
            f" '{gg_build_component_artifacts}'"
        )
        solution = "Please check the artifact URI in the recipe and publish the component again."
        super().__init__(reason, solution, exception)


class ComponentNotBuildException(PublishException):
    def __init__(self, component_name, exception=None):
        reason = f"The component '{component_name}' is not built."

        solution = "Please build the component using `gdk component build` before publishing it."
        super().__init__(reason, solution, exception)


class ComponentCreationException(PublishException):
    def __init__(self, c_name, c_version, publish_recipe_file, exception=None):
        reason = (
            f"Failed to create a new version of the component '{c_name}-{c_version}' using the recipe at"
            f" '{publish_recipe_file}'"
        )

        solution = "Please fix the errors in the recipe and publish the component again."
        super().__init__(reason, solution, exception)


class ComponentVersionException(PublishException):
    def __init__(self, c_name, c_latest_version, exception=None):
        reason = f"Failed to calculate the next version of the component '{c_name}' during publish. "

        solution = f"The component version '{c_latest_version}' must contain a major, minor and patch numbers in it."
        super().__init__(reason, solution, exception)

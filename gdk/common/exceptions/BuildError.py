class BuildException(Exception):
    def __init__(self, reason="", solution="", e=None):
        err_details = ""
        if e:
            err_details = f"Error details: {e}\n"
        self.message = f"{reason}\n{err_details}{solution}"
        super().__init__(self.message)


class BuildSystemException(BuildException):
    def __init__(self, build_system, e=None):
        reason = f"Failed to build the component with the given build system '{build_system}'."
        solution = "Please fix the component build errors and build the component again."
        super().__init__(reason, solution, e)


class ZipBuildRecursionException(BuildException):
    def __init__(self, e=None):
        reason = "Failed to create an archive inside the zip-build folder."
        solution = "Please remove symlinks in the gdk project directory if any and try again."
        super().__init__(reason, solution, e)


class ArtifactNotFoundException(BuildException):
    def __init__(self, uri, e=None):
        reason = f"Could not find the artifact with URI '{uri}' in S3 or inside the build folders."
        solution = "Please check the artifact URI in the recipe and build the component again."
        super().__init__(reason, solution, e)

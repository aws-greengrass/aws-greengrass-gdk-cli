class InitException(Exception):
    def __init__(self, reason="", solution="", exception=None, help_text=""):
        err_details = ""
        if exception:
            err_details = f"Error details: {exception}\n"
        self.message = f"{reason}\n{err_details}{solution}{help_text}"
        super().__init__(self.message)


class InvalidInitArgumentsException(InitException):
    def __init__(self, exception=None):
        reason = "The arguments passed with the command are invalid."
        solution = "Please initialize the project with correct arguments."
        help_text = "\n\nTry `gdk component init --help`"
        super().__init__(reason, solution, exception, help_text)


class DirectoryNotEmptyException(InitException):
    def __init__(self, exception=None):
        reason = "The current directory is not empty."
        solution = "Please initialize the project in an empty directory."
        super().__init__(reason, solution, exception)


class InvalidDirectoryException(InitException):
    def __init__(self, name, exception=None):
        reason = f"Directory or a file named '{name}' already exsits in the current directory."
        solution = "Please initialize the project using a different directory name."
        super().__init__(reason, solution, exception)


class ComponentUnavailableException(InitException):
    def __init__(self, comp_type, comp_name, exception=None):
        reason = f"Could not find the component {comp_type} '{comp_name}' in Greengrass Software Catalog."
        solution = "Please specify a valid component name from the Greengrass Software Catalog."
        help_text = f"\n\nTry `gdk component list --{comp_type}`"
        super().__init__(reason, solution, exception, help_text)

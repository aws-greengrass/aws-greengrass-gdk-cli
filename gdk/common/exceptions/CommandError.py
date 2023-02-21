class CommandError(Exception):
    def __init__(self, message):
        help_message = "The command provided is invalid.\n"
        self.message = help_message + message
        super().__init__(self.message)


class ConflictingArgumentsError(CommandError):
    def __init__(self, arg1, arg2):
        message = f"Arguments '{arg1}' and '{arg2}' are conflicting and cannot be used together in a command."
        self.message = message
        super().__init__(self.message)


class InvalidArgumentsError(CommandError):
    def __init__(self, arg1, message):
        message = f"Argument '{arg1}' provided in the command is invalid. " + message
        self.message = message
        super().__init__(self.message)

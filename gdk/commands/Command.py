import logging
from abc import abstractmethod

from gdk.common.exceptions.CommandError import ConflictingArgumentsError


class Command:
    def __init__(self, arguments, name) -> None:
        self.arguments = arguments
        self.name = name
        logging.debug("Checking if arguments in the command conflict.")
        self.check_if_arguments_conflict()

    def check_if_arguments_conflict(self):
        """
        Checks if the command namespace provided to the parser has conflicting arguments

        Returns
        -------
          (bool) Returns True if the command arguments conflict. Else False.
        """

        _non_conflicting_args_map = self._non_conflicting_args_map()
        if _non_conflicting_args_map:
            self._identify_conflicting_args_in_command(_non_conflicting_args_map)

    def _identify_conflicting_args_in_command(self, _non_conflicting_args_map):
        """
        Checks if the command namespace provided to the parser has conflicting arguments by using the conflicting
        arguments provided in the cli model file.

        Parameters
        ----------
          _non_conflicting_args_map(dict): A dictionary object that's formed with argument as a key and
                              a set of its non-conflicting args as value.

        Returns
        -------
          (bool) Returns True if the command arguments conflict. Else False.
        """
        command_arg_keys = self._arguments_list(_non_conflicting_args_map)
        for i in range(len(command_arg_keys)):
            for j in range(i + 1, len(command_arg_keys)):
                if command_arg_keys[j] not in _non_conflicting_args_map[command_arg_keys[i]]:
                    raise ConflictingArgumentsError(command_arg_keys[i], command_arg_keys[j])

    def _arguments_list(self, _non_conflicting_args_map):
        """
        Creates a reduced list of argument-only commands from the namespace args dictionary by removing both
        non-argument commands and None arguments from the namespace args.

        Parameters
        ----------
          _non_conflicting_args_map(dict): A dictionary object that's formed with argument as a key and
                              a set of its non-conflicting args as value.

        Returns
        -------
          command_arg_keys_as_list(list): Modified list of command keys in the namespace.
        """
        command_arg_keys_as_list = []
        for k, v in self.arguments.items():
            if k in _non_conflicting_args_map and v is not None:
                command_arg_keys_as_list.append(k)

        return command_arg_keys_as_list

    def _non_conflicting_args_map(self):
        """
        Creates a dictionary object with argument as a key and a set of its non-conflicting args as value.

        Returns
        -------
          _non_conflicting_args_map(dict): A dictionary object formed with argument as a key and a set of its non-conflicting
          args as value.
        """
        from gdk.CLIParser import cli_tool

        _non_conflicting_args_map = {}

        cli_model = self.get_sub_c(next(iter(cli_tool.cli_model.keys())), cli_tool.cli_model)
        if not cli_model:
            return {}
        if self.name in cli_model and "conflicting_arg_groups" in cli_model[self.name]:
            c_arg_groups = cli_model[self.name]["conflicting_arg_groups"]
            for c_group in c_arg_groups:
                for c_arg in c_group:
                    c_arg_set = _non_conflicting_args_map.get(c_arg, set())
                    c_arg_set.update(set(c_group))
                    _non_conflicting_args_map[c_arg] = c_arg_set
        return _non_conflicting_args_map

    def get_sub_c(self, command, sub_c):
        if sub_c.get(command) and sub_c.get(command).get("sub-commands"):
            sub_c = sub_c.get(command).get("sub-commands")
        if self.name in sub_c:
            return sub_c
        if command and command in self.arguments:
            return self.get_sub_c(self.arguments[command], sub_c)

    @abstractmethod
    def run(self):
        """This method is overriden by the cli commands."""

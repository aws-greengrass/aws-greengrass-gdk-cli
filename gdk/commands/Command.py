import logging
from abc import abstractmethod

import gdk
from gdk.common.exceptions.CommandError import ConflictingArgumentsError


class Command:
    def __init__(self, command_args, level_command) -> None:
        self.command_args = command_args
        self.level_command = level_command
        logging.debug("Checking if arguments in the command conflict.")
        self.check_if_command_args_conflict()

    def check_if_command_args_conflict(self):
        """
        Checks if the command namespace provided to the parser has conflicting arguments

        Returns
        -------
          (bool) Returns True if the command arguments conflict. Else False.
        """
        cli_model = gdk.CLIParser.cli_tool.cli_model
        _non_conflicting_args_map = self._non_conflicting_args_map(cli_model)
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
        command_arg_keys = self._command_args_list(_non_conflicting_args_map)
        for i in range(len(command_arg_keys)):
            for j in range(i + 1, len(command_arg_keys)):
                if command_arg_keys[j] not in _non_conflicting_args_map[command_arg_keys[i]]:
                    raise ConflictingArgumentsError(command_arg_keys[i], command_arg_keys[j])

    def _command_args_list(self, _non_conflicting_args_map):
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
        for k, v in self.command_args.items():
            if k in _non_conflicting_args_map and v is not None:
                command_arg_keys_as_list.append(k)

        return command_arg_keys_as_list

    def _non_conflicting_args_map(self, cli_model):
        """
        Creates a dictionary object with argument as a key and a set of its non-conflicting args as value.

        Parameters
        ----------
          cli_model(dict): A dictonary object which contains CLI arguments and sub-commands at each command level.

        Returns
        -------
          _non_conflicting_args_map(dict): A dictionary object formed with argument as a key and a set of its non-conflicting
          args as value.
        """
        _non_conflicting_args_map = {}
        if self.level_command in cli_model and "conflicting_arg_groups" in cli_model[self.level_command]:
            c_arg_groups = cli_model[self.level_command]["conflicting_arg_groups"]
            for c_group in c_arg_groups:
                for c_arg in c_group:
                    c_arg_set = _non_conflicting_args_map.get(c_arg, set())
                    c_arg_set.update(set(c_group))
                    _non_conflicting_args_map[c_arg] = c_arg_set
        return _non_conflicting_args_map

    @abstractmethod
    def run(self):
        """ This method is overriden by the cli commands. """

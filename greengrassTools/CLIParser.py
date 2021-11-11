import argparse
import logging

import greengrassTools.common.consts as consts
import greengrassTools.common.model_actions as model_actions
import greengrassTools.common.parse_args_actions as parse_args_actions
import greengrassTools.common.utils as utils

from . import _version


class ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        """Overrides the argparse.ArgumentParser.error method.

        Add custom message with help text at the command level. Python3.9 supports 'exit_on_error' method to achieve
        the same.
        """
        logging.error("Command failed due to an argument error.{}{}".format(utils.line, message))
        self.print_help()
        self.exit()


class CLIParser:

    cli_model = model_actions.get_validated_model()

    def __init__(self, command, top_level_parser):
        """A class that represents an argument parser at command level."""
        self.command = command
        help_text_for_command = self.cli_model[self.command]["help"]
        if command != consts.cli_tool_name:
            self.top_level_parser = top_level_parser
            self.parser = self.top_level_parser.add_parser(command, help=help_text_for_command)
        else:
            self.parser = ArgumentParser(prog=consts.cli_tool_name)
        self.subparsers = self.parser.add_subparsers(dest=command, help=help_text_for_command)

    def create_parser(self):
        """
        Creates a parser with arguments and subcommands at specified command level and returns it.

        Parameters
        ----------
          None

        Returns
        -------
          parser(argparse.ArgumentParser): ArgumentParser object which can parse args at its command level.
        """
        self.command_model = self.cli_model[self.command]
        self._add_common_args_for_all_commands()
        self._add_arguments()
        self._get_subcommands_from_model()
        return self.parser

    def _add_arguments(self):
        """
        Adds command-line argument to the parser to define how it should be parsed from commandline.

        Retrieves and passes positionl/optional args along with all other parameters as kwargs from the
        provided at each command level.

        Parameters
        ----------
          None

        Returns
        -------
          None
        """
        if "arguments" in self.command_model:
            arguments = self.command_model["arguments"]
            added_args = {}
            # Add arguments in groups first
            if "arg_groups" in self.command_model:
                for arg_group in self.command_model["arg_groups"]:
                    group_description = arg_group["description"]
                    group_title = arg_group["title"]
                    group = self.parser.add_argument_group(title=group_title, description=group_description)
                    for arg in arg_group["args"]:
                        if arg not in added_args:
                            if self._add_arg_to_group_or_parser(arguments[arg], group):
                                added_args[arg] = True

            # Add individual args that are not part of groups. Skip if they're already added.
            for arg in arguments:
                if arg not in added_args:
                    if self._add_arg_to_group_or_parser(arguments[arg], None):
                        added_args[arg] = True

    def _add_arg_to_group_or_parser(self, argument, group):
        """
        Adds argument to either group or command level parser based on group parameter.

        Parameters
        ----------
          argument(dict): A dictonary object which argument parameters.
                          Full list: greengrassTools.common.consts.arg_parameters
          group(Argument group obect): Argument group object created for each group of arguments that go together.

        Returns
        -------
          (bool): Return True if the argument is added to the group or parser.
        """
        if group:
            parser = group
        else:
            parser = self.parser
        name, other_args = self._get_arg_from_model(argument)
        if len(name) == 2:  # For optional args
            parser.add_argument(name[0], name[1], **other_args)
            return True
        elif len(name) == 1:  # For positional args
            parser.add_argument(name[0], **other_args)
            return True

    def _get_subcommands_from_model(self):
        """
        Creates a subparser for every subcommand of a command.

        Retrieves and passes positionl/optional args along with all other parameters as kwargs from the
        provided at each command level.

        Parameters
        ----------
          None

        Returns
        -------
          None
        """

        if "sub-commands" in self.command_model:
            sub_commands = self.command_model["sub-commands"]
            for sub_command in sub_commands:
                CLIParser(sub_command, self.subparsers).create_parser()

    def _get_arg_from_model(self, argument):
        """
        Creates parameters of parser.add_argument from the argument in cli_model.

        Parameters
        ----------
          argument(dict): A dictonary object which argument parameters.
                          Full list: greengrassTools.common.consts.arg_parameters

        Returns
        -------
          argument["name"](list): List of all optional and positional argument parameters
          modified_arg(dict): A dictionary object with all other parameters that 'argument' param has.
        """
        modified_arg = {}
        for param in consts.arg_parameters:
            if param in argument and param != "name":
                modified_arg[param] = argument[param]
            if param in argument and param == "type":
                modified_arg[param] = eval(argument[param])
        return argument["name"], modified_arg

    def _add_common_args_for_all_commands(self):
        """
        Adds common arguments to all the commands and sub-commands of the CLI parser.

        Not adding these argument from cli model file to avoid redundancy and also because version of the CLI tool is
        fetched during runtime without hardcoding.

        Parameters
        ----------
          None

        Returns
        -------
          None
        """
        self.parser.add_argument("-d", "--debug", help="Increase command output to debug level", action="store_true")
        self.parser.add_argument(
            "-v", "--version", action="version", version="{} {}".format(consts.cli_tool_name, _version.__version__)
        )


def main():
    try:
        args_namespace = cli_parser.parse_args()
        parse_args_actions.run_command(args_namespace)
    except Exception as e:
        logging.error("Command failed due to the following error.{}{}".format(utils.line, e))
        exit(1)


try:
    logging.basicConfig(level=logging.INFO, format=utils.log_format, datefmt="%Y-%m-%d %H:%M:%S", force=True)
    cli_tool = CLIParser(consts.cli_tool_name, None)
    cli_parser = cli_tool.create_parser()
except Exception as e:
    print(
        "[FATAL]: Command failed due to CLI tool error.\nPlease report it here if the issue persists.\nError details: {}"
        .format(e)
    )
    exit(1)

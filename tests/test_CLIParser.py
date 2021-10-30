import pytest
import argparse
import greengrassTools.CLIParser as cli_parser
import greengrassTools.common.consts as consts

def test_CLIParser_initiation_top_level():
    # This test checks for the correctness of CLIParser that creates argument parser with commands and sub-commands. 
    # If CLIParser is initiated with the cli tool name, it has no top-level parser.
    parser=cli_parser.CLIParser(consts.cli_tool_name, None)
    assert not hasattr(parser, 'top_level_parser')
    assert parser.command == consts.cli_tool_name
    assert type(parser.parser) ==  cli_parser.ArgumentParser
    assert parser.subparsers.dest == consts.cli_tool_name

def test_CLIParser_initiation_sub_level():
    # If CLIParser is initiated with the sub-command, it has a top-level parser. Here, it is cli tool name
    parser=cli_parser.CLIParser(consts.cli_tool_name, None)
    sub_command = 'component'
    subparser=cli_parser.CLIParser(sub_command, parser.subparsers)
    assert hasattr(subparser, 'top_level_parser')
    assert subparser.top_level_parser.dest ==  consts.cli_tool_name
    assert subparser.command != consts.cli_tool_name
    assert subparser.command == sub_command
    assert type(subparser.parser) ==  cli_parser.ArgumentParser
    assert subparser.subparsers.dest == sub_command


def test_CLIParser_create_parser():
    # This test checks for the correctness of CLIParser that creates argument parser with commands and sub-commands. 
    # If CLIParser is initiated with the cli tool name, it has no top-level parser.
    cli_tool=cli_parser.CLIParser(consts.cli_tool_name, None)
    parser=cli_tool.create_parser()
    assert type(parser) ==  cli_parser.ArgumentParser

def test_CLIParser_get_arg_from_model():
    ## Check that only known params are passed in the form of names and kwargs as needed by parser.add_argument. 
    test_arg= { "name" : ["-l","--lang"],
                "help": "Specify the language of the template.",
                "choices": ["python", "java"] }
    cli_tool = cli_parser.CLIParser(consts.cli_tool_name, None)
    params_of_add_arg_command = cli_tool._get_arg_from_model(test_arg)
    names_in_command, rest_args_as_dict = params_of_add_arg_command

    assert type(params_of_add_arg_command) == tuple
    assert len(names_in_command) == 2 
    assert names_in_command[0] == "-l"

    assert type(rest_args_as_dict) == dict
    assert "choices" in rest_args_as_dict # Check that "choices" is present in the parameters passed to add_argument command 
    assert "default" not in rest_args_as_dict # Full list of accepted params in common.consts file. 
    assert "names" not in rest_args_as_dict 
    assert "help" in rest_args_as_dict 

def test_CLIParser_get_arg_from_model():
    ## Other params in the argument model file that are not relevant to the add_argument are not passed. 
    test_arg2= { "name" : ["-l"],
                 "unknown_param": "Not relevant to arg params" }
    cli_tool = cli_parser.CLIParser(consts.cli_tool_name, None)
    params_of_add_arg_command2 = cli_tool._get_arg_from_model(test_arg2)
    names_in_command2, rest_args_as_dict2= params_of_add_arg_command2
    assert len(names_in_command2) == 1

    assert "unknown_param" not in rest_args_as_dict2 # Full list of accepted params in common.consts file. 

def test_add_arg_to_group_or_parser_with_group(mocker):
    arg = { "name" : ["project"],
                "help": "help"}
    cli_tool = cli_parser.CLIParser(consts.cli_tool_name, None)
    group = cli_tool.parser.add_argument_group('group')

    cli_tool = cli_parser.CLIParser(consts.cli_tool_name, None)
    cli_tool._add_arg_to_group_or_parser(arg, group)

    assert cli_tool._add_arg_to_group_or_parser(arg, group)

def test_add_arg_to_group_or_parser_with_parser(mocker):
    arg = { "name" : ["project"],"help": "help"}
    group = None
    cli_tool = cli_parser.CLIParser(consts.cli_tool_name, None)
    assert cli_tool._add_arg_to_group_or_parser(arg, group)

def test_model_file():
    model = {
    "greengrass-tools" :{
        "sub-commands":[
            "component"
        ]
    },
    "component" : {
        "sub-commands":[
            "init", "build", "publish"
        ]
    },

    "init" : {
        "arguments" :{
            "language":
            {
                "name" : ["-l","--language"],
                "help":"help",
                "choices":["python", "java"]
            },
            "template":{
                "name" : ["-t", "--template"],
                "help":"help"
            },
            "repository":{
                "name" : ["-r", "--repository"],
                "help":"help"
            },
            "project-name":{
                "name" : ["-n", "--project-name"],
                "help":"Specify the name of the directory you want to create in"
            }
        },
        "conflicting_arg_groups":[["language","template"], ["repository"]],
        "arg_groups": [
            {
                "title": "Title",
                "args": [
                    "language",
                    "template"
                ],
                "description": "Description"
            },
            {
                "title": "Title",
                "args": [
                    "repository"
                ],
                "description": "Description"
            }
         ]
        },
        "build" :{
        },
        "publish" :{
        }
}

    return model


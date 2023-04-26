from gdk.commands.component import component
from gdk.commands.test import test
import gdk.CLIParser


def _gdk(d_args):
    if not d_args.get("gdk"):
        gdk.CLIParser.cli_parser.print_help()


def _gdk_component_init(d_args):
    component.init(d_args)


def _gdk_component_build(d_args):
    component.build(d_args)


def _gdk_component_publish(d_args):
    component.publish(d_args)


def _gdk_component_list(d_args):
    component.list(d_args)


def _gdk_test_init(d_args):
    test.init(d_args)


def _gdk_test_run(d_args):
    test.run(d_args)

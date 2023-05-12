from gdk.commands.test.InitCommand import InitCommand
from gdk.commands.test.BuildCommand import BuildCommand


def init(d_args):
    """
    gdk test init
    """
    InitCommand(d_args).run()


def run(d_args):
    """
    gdk test run
    """


def build(d_args):
    """
    gdk test build
    """
    BuildCommand(d_args).run()

from gdk.commands.config.ComponentCommand import ComponentCommand


def component(d_args):
    """
    gdk config component
    """
    ComponentCommand(d_args).run()

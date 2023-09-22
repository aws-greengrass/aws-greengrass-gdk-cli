from gdk.commands.config.UpdateCommand import UpdateCommand


def update(d_args):
    """
    gdk config update
    """
    UpdateCommand(d_args).run()

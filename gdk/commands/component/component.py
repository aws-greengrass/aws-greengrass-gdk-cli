def init(d_args):
    from gdk.commands.component.InitCommand import InitCommand

    try:
        InitCommand(d_args).run()
    except Exception as e:
        raise Exception(f"Could not initialze the project due to the following error.\n{e}")


def build(d_args):
    from gdk.commands.component.BuildCommand import BuildCommand

    try:
        BuildCommand(d_args).run()
    except Exception as e:
        raise Exception(f"Could not build the project due to the following error.\n{e}")


def publish(d_args):
    import gdk.commands.component.publish as publish

    publish.run(d_args)


def list(d_args):
    import gdk.commands.component.list as list

    list.run(d_args)

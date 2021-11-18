def init(d_args):
    import gdk.commands.component.init as init

    init.run(d_args)


def build(d_args):
    import gdk.commands.component.build as build

    build.run(d_args)


def publish(d_args):
    import gdk.commands.component.publish as publish

    publish.run(d_args)


def list(d_args):
    import gdk.commands.component.list as list

    list.run(d_args)

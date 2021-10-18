def init(d_args):
    import ggtools.commands.component.init as init
    init.run(d_args)

def build(d_args):
    import ggtools.commands.component.build as build
    build.run(d_args)

def publish(d_args):
    import ggtools.commands.component.publish as publish
    publish.run(d_args)
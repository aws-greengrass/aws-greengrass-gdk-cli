from behave import step


@step("we run gdk {commands}")
def gdk_command(context, commands):
    gdk_command_with_args_and_capture_mode(context, True, commands)


@step("we quietly run gdk {commands}")
def gdk_command_silently(context, commands):
    gdk_command_with_args_and_capture_mode(context, False, commands)


def gdk_command_with_args_and_capture_mode(context, capture_output, commands=None):
    assert commands is not None, f"Bad command: gdk {commands}"
    args = commands.split()

    # update placeholders
    for index, arg in enumerate(args):
        if '<' in arg:
            key = arg[1:-1]
            if key in context:
                args[index] = getattr(context, key)

    # run command with args
    context.last_cli_output = context.gdk_cli.run(
        args, capture_output=capture_output
    )
    context.last_cli_command_type = f"{args[0]} {args[1]}"
    context.last_cli_command_args = args

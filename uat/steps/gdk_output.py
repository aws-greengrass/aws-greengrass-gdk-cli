from behave import given, step


@given('cli is installed')
@given('we have cli installed')
def gdk_cli_installed(context):
    assert context.gdk_cli is not None, "GDK cli not found in context"
    context.last_cli_output = context.gdk_cli.run(["--version"])
    exit_code = context.last_cli_output.returncode
    assert exit_code == 0, f"command exited with:{exit_code}, but expecting 0."


@step('command was successful')
@step('cli exited successfully')
def command_success(context):
    exit_code = context.last_cli_output.returncode
    assert exit_code == 0, f"command exited with:{exit_code}, but expecting 0."


@step('command was unsuccessful')
@step('cli exited with error')
def command_error(context):
    exit_code = context.last_cli_output.returncode
    assert exit_code == 1, f"command exited with:{exit_code}, but expecting 1."


@step('command output contains "{text}"')
@step('cli output contains "{text}"')
def gdk_output_contains(context, text):
    output = context.last_cli_output.output
    assert text in output, f"Text '{text}' missing from output:\n{output}"

import subprocess as sp
import io
from contextlib import redirect_stdout
from importlib import reload

import gdk.CLIParser as CLIParser
import gdk.common.parse_args_actions as parse_args_actions
import gdk.common.utils as utils


class ProcessOutput:
    def __init__(self, exit_code, output) -> None:
        self.returncode = exit_code
        self.output = output


class GdkProcess:
    def __init__(self) -> None:
        pass

    @classmethod
    def run(self, arguments=None) -> ProcessOutput:
        if arguments is None:
            arguments = []
        try:
            output = sp.run(["gdk"] + arguments, check=True, stdout=sp.PIPE)
            return ProcessOutput(output.returncode, output.stdout.decode())
        except sp.CalledProcessError as e:
            return ProcessOutput(e.returncode, e.stdout.decode())


class GdkInstrumentedProcess(GdkProcess):
    def __init__(self) -> None:
        pass

    @classmethod
    def run(self, arguments=None) -> ProcessOutput:
        if arguments is None:
            arguments = []

        #
        # In each cli execution, python interpreter reloads all gdk modules, here this simulates that effect.
        #
        reload(CLIParser)
        reload(parse_args_actions)
        reload(utils)

        # parsed args
        args = CLIParser.cli_parser.parse_args(arguments)

        exit_code = 0
        output = ""

        try:
            f = io.StringIO()
            with redirect_stdout(f):
                parse_args_actions.run_command(args)
            output = f.getvalue()
        except Exception as e:
            exit_code = 1
            output = str(e)

        return ProcessOutput(exit_code, output)

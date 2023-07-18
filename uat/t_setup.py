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
        print(output)


class GdkProcess:
    def __init__(self, debug=False) -> None:
        self.debug = debug

    def run(self, arguments=None, capture_output=True) -> ProcessOutput:
        if arguments is None:
            arguments = []

        if self.debug:
            arguments += ["--debug"]

        try:
            if capture_output:
                output = sp.run(["gdk"] + arguments, check=True, stdout=sp.PIPE, stderr=sp.STDOUT)
                return ProcessOutput(output.returncode, output.stdout.decode())
            else:
                output = sp.run(["gdk"] + arguments)
                return ProcessOutput(output.returncode, "")
        except sp.CalledProcessError as e:
            return ProcessOutput(e.returncode, e.stdout.decode())


class GdkInstrumentedProcess(GdkProcess):
    def __init__(self, debug=False) -> None:
        super().__init__(debug)

    def run(self, arguments=None, capture_output=True) -> ProcessOutput:
        if arguments is None:
            arguments = []

        if self.debug:
            arguments += ["--debug"]

        #
        # In each cli execution, python interpreter reloads all gdk modules, here this simulates that effect.
        #
        reload(CLIParser)
        reload(parse_args_actions)
        reload(utils)

        exit_code = 0
        output = ""

        try:
            # parsed args
            args = CLIParser.cli_parser.parse_args(arguments)

            if capture_output:
                f = io.StringIO()
                with redirect_stdout(f):
                    parse_args_actions.run_command(args)
                output = f.getvalue()
            else:
                parse_args_actions.run_command(args)
        except SystemExit as e:
            exit_code = e.code
            output = str(e)
        except Exception as e:
            exit_code = 1
            output = str(e)

        return ProcessOutput(exit_code, output)

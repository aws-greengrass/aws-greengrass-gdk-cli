

import pytest
from gdk import CLIParser
from gdk.common.parse_args_actions import run_command

from .telemetry_base import TelemetryTestCase, TelemetryServer


class TestEmitTelemetry(TelemetryTestCase):

    def setUp(self) -> None:
        self.enable_telemetry()

    @pytest.mark.skip(reason="metric not yet being emited")
    def test_emit_installed_metric_on_first_run(self):
        with TelemetryServer() as server:
            run_command(CLIParser.cli_parser.parse_args(["component", "list", "--template"]))

            all_requests = server.get_all_requests()
            self.assertEqual(1, len(all_requests))

import pytest
from .telemetry_base import TelemetryServer, TelemetryTestCase


class TestEmitTelemetry(TelemetryTestCase):

    def test_emit_installed_metric_on_first_run(self):
        self.enable_telemetry()

        with TelemetryServer() as server:
            self.run_command(["component", "list", "--template"])

            all_requests = server.get_all_requests()
            self.assertEqual(1, len(all_requests))

    @pytest.mark.skip("Not yet implemented")
    def test_emit_failure_doesnot_spot_command_run(self):
        pass

    @pytest.mark.skip("Not yet implemented")
    def test_only_emits_install_metric_one_time(self):
        pass

import pytest

from gdk.telemetry.telemetry_config import ConfigKey, TelemetryConfig

from .telemetry_base import TelemetryServer, TelemetryTestCase


class TestEmitTelemetry(TelemetryTestCase):

    def setup_previous_version_installed(self):
        """
        Simualtes the gdk runtime config having recorded an older version of the gdk. Than
        the one currently recorded on the _version.py file.
        """
        config = TelemetryConfig()
        config.set(ConfigKey.INSTALLED, "1.0.0")

    def test_emit_installed_metric_on_first_run_only(self):
        self.enable_telemetry()

        with TelemetryServer(self.aws_creds) as server:
            self.run_command(["component", "list", "--template"])

            all_requests = server.get_all_requests()
            self.assertEqual(1, len(all_requests))

            self.run_command(["component", "list", "--template"])

            all_requests = server.get_all_requests()
            self.assertEqual(1, len(all_requests))

    def test_emit_installed_metric_if_a_new_version_is_installed(self):
        self.enable_telemetry()

        with TelemetryServer(self.aws_creds) as server:
            self.run_command(["component", "list", "--template"])

            self.setup_previous_version_installed()

            self.run_command(["component", "list", "--template"])

            all_requests = server.get_all_requests()
            self.assertEqual(2, len(all_requests))

    @pytest.mark.skip("Not yet implemented")
    def test_emit_failure_doesnot_spot_command_run(self):
        pass

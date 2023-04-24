
import time

from gdk._version import __version__
from gdk.telemetry.metric import Metric, MetricType
from gdk.telemetry.telemetry import Telemetry
from integration_tests.gdk.telemetry.telemetry_base import (TelemetryServer,
                                                            TelemetryTestCase)


class TestTelemetryServerSetup(TelemetryTestCase):
    """
    Test case to ensure the test telemetry server is setup correctly
    """

    def test_send_sample_metric_telemetry_enabled(self):
        self.enable_telemetry()

        epoch = int(time.time())
        sample_metric = Metric(MetricType.PING, epoch)
        sample_metric.add_dimension("hello", "world")

        with TelemetryServer() as server:
            all_requests = server.get_all_requests()
            self.assertEqual(0, len(all_requests))

            telemetry = Telemetry()
            telemetry.emit(sample_metric)

            all_requests = server.get_all_requests()
            self.assertEqual(1, len(all_requests))
            request = all_requests[0]

            expected_data = {
                "metrics": [
                    {
                        "name": "PING",
                        "meta": {
                            "gdk_version": __version__
                        },
                        "timestamp": epoch,
                        "dimensions": {
                            "hello": "world"
                        }
                    }
                ]
            }

            self.assertEqual(request["data"], expected_data)

    def test_send_sample_metric_telemetry_disabled(self):
        self.disable_telemetry()

        epoch = int(time.time())
        sample_metric = Metric(MetricType.PING, epoch)
        sample_metric.add_dimension("hello", "world")

        with TelemetryServer() as server:

            telemetry = Telemetry()
            telemetry.emit(sample_metric)

            all_requests = server.get_all_requests()
            self.assertEqual(0, len(all_requests))

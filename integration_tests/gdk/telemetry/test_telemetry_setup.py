
import time

import requests

from gdk._version import __version__
from gdk.telemetry.metric import Metric, MetricEncoder, MetricType
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

        with TelemetryServer(self.aws_creds) as server:
            all_requests = server.get_all_requests()
            self.assertEqual(0, len(all_requests))

            telemetry = Telemetry(credentials=self.aws_creds)
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

        with TelemetryServer(self.aws_creds) as server:

            telemetry = Telemetry(credentials=self.aws_creds)
            telemetry.emit(sample_metric)

            all_requests = server.get_all_requests()
            self.assertEqual(0, len(all_requests))

    def test_emit_a_metric_without_sigv4(self):
        self.enable_telemetry()

        epoch = int(time.time())
        sample_metric = Metric(MetricType.PING, epoch)
        sample_metric.add_dimension("hello", "world")

        with TelemetryServer(self.aws_creds, shutdown_timeout=5) as server:
            # Try posting a metric directly without using the Telemetry class
            payload = {'metrics': [MetricEncoder().encode(sample_metric)]}
            response = requests.post(server.metrics_endpoint, json=payload, timeout=3)

            self.assertEqual(403, response.status_code)
            all_requests = server.get_all_requests()
            self.assertEqual(0, len(all_requests))

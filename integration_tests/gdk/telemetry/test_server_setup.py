
import requests
from unittest import TestCase


from integration_tests.gdk.telemetry.integration_base import TelemetryServer


class TestTelemetryServerSetup(TestCase):
    """
    Test case to ensure the test telemetry server is setup correctly
    """

    def test_sending_a_request(self):
        with TelemetryServer() as server:
            self.assertEqual(0, len(server.get_all_requests()))

            fake_metric = {"name": "publish"}
            requests.post(server.get_metrics_endpoint(), json=fake_metric)

            all_requests = server.get_all_requests()
            self.assertEqual(1, len(all_requests))
            data = all_requests[0]['data']
            self.assertEqual(fake_metric, data)

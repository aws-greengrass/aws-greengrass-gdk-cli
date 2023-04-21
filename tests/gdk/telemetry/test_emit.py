
from unittest import TestCase

from gdk.telemetry.emit import Emit
from gdk.telemetry.metric import MetricType
from tests.helpers.telemetry_fake import TelemetryFake


class TestEmit(TestCase):

    def setUp(self) -> None:
        self.telemetry = TelemetryFake()

    def test_emitting_installed_metric(self):
        Emit(self.telemetry).installed_metric()

        emitted = self.telemetry.get_emitted_metrics()
        self.assertEqual(1, len(emitted))

        metric = emitted[0]
        self.assertEqual(MetricType.INSTALLED, metric.type)

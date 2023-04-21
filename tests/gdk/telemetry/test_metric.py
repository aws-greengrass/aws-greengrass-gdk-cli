

import time
from unittest import TestCase

from gdk._version import __version__
from gdk.telemetry.metric import Metric, MetricEncoder, MetricType


class TestMetric(TestCase):

    def test_create_metric(self):
        epoch = int(time.time())
        metric = Metric(MetricType.PING, epoch)
        metric.add_dimension("hello", "world")

        self.assertEqual(MetricType.PING, metric.type)
        self.assertEqual({"hello": "world"}, metric.dimensions)
        self.assertEqual(epoch, metric.timestamp)
        self.assertEqual({"gdk_version": __version__}, metric.meta)

    def test_encode_metric(self):
        epoch = int(time.time())
        metric = Metric(MetricType.PING, epoch)
        metric.add_dimension("hello", "world")

        encoded = MetricEncoder().encode(metric)

        expected = {
            "name": "PING",
            "meta": {"gdk_version": __version__},
            "timestamp": epoch,
            "dimensions": {"hello": "world"}
        }
        self.assertEqual(expected, encoded)

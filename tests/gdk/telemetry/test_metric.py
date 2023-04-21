

import time
from unittest import TestCase

from gdk._version import __version__
from gdk.telemetry.metric import Metric


class TestMetric(TestCase):

    def test_create_metric(self):
        epoch = int(time.time())
        metric = Metric("PING", epoch)
        metric.add_dimension("hello", "world")

        self.assertEqual("PING", metric.type)
        self.assertEqual({"hello": "world"}, metric.dimensions)
        self.assertEqual(epoch, metric.timestamp)
        self.assertEqual({"gdk_version": __version__}, metric.meta)

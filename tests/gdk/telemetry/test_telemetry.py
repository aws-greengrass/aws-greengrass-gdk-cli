import os
from unittest import TestCase

import mock

from gdk.telemetry.metric import Metric
from gdk.telemetry.telemetry import Telemetry
from gdk.telemetry import (GDK_CLI_TELEMETRY, GDK_CLI_TELEMETRY_ENDPOINT_URL,
                           get_telemetry_enabled, get_telemetry_url)


class TestTelemetry(TestCase):

    def test_get_telemetry_url(self):
        fake_url = "http://test.com"
        os.environ[GDK_CLI_TELEMETRY_ENDPOINT_URL] = fake_url

        self.assertEqual(fake_url, get_telemetry_url())

    def test_unknown_envar_then_telemetry_disabled(self):
        os.environ[GDK_CLI_TELEMETRY] = "Foo"
        self.assertEqual(get_telemetry_enabled(), False)

    def test_telemetry_enabled(self):
        os.environ[GDK_CLI_TELEMETRY] = "1"
        self.assertEqual(get_telemetry_enabled(), True)

    @mock.patch('requests.post')
    def test_emit_telemtry_when_disbaled(self, post):
        os.environ[GDK_CLI_TELEMETRY] = "0"
        metric = Metric("PING")
        telemetry = Telemetry()

        telemetry.emit(metric)

        self.assertEqual(0, post.call_count)

    @mock.patch('requests.post')
    def test_emit_telemetry_when_enabled(self, post):
        os.environ[GDK_CLI_TELEMETRY] = "1"

        metric = Metric("PING")
        telemetry = Telemetry()

        telemetry.emit(metric)

        self.assertEqual(1, post.call_count)

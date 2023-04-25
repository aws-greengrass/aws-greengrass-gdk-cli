import contextlib
import io

from gdk.telemetry.emit import TELEMETRY_PROMPT, Emit
from gdk.telemetry.metric import MetricType
from integration_tests.gdk.telemetry.telemetry_base import TelemetryTestCase
from tests.helpers.telemetry_fake import TelemetryFake


class TestEmit(TelemetryTestCase):

    def setUp(self) -> None:
        super().setUp()
        self.telemetry = TelemetryFake()

    def test_display_telemetry_prompt_only_once_telemetry_enabled(self):
        self.enable_telemetry()
        stdout = io.StringIO()

        with contextlib.redirect_stderr(stdout):
            Emit(self.telemetry).installed_metric()

        captured_out = stdout.getvalue()
        self.assertEqual(TELEMETRY_PROMPT.strip(), captured_out.strip())

    def test_display_telemetry_prompt_telemetry_disabled(self):
        self.disable_telemetry()
        stdout = io.StringIO()

        with contextlib.redirect_stderr(stdout):
            Emit(self.telemetry).installed_metric()

        captured_out = stdout.getvalue()
        self.assertEqual("", captured_out.strip())

    def test_emitting_installed_metric(self):
        self.enable_telemetry()
        Emit(self.telemetry).installed_metric()

        emitted = self.telemetry.get_emitted_metrics()
        self.assertEqual(1, len(emitted))

        metric = emitted[0]
        self.assertEqual(MetricType.INSTALLED, metric.type)

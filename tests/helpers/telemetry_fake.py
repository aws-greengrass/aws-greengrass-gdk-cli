
from gdk.telemetry.metric import Metric
from gdk.telemetry.telemetry import ITelemetry


class TelemetryFake(ITelemetry):

    def __init__(self) -> None:
        self.emitted = []

    def emit(self, metric: Metric):
        self.emitted.append(metric)

    def get_emitted_metrics(self):
        return self.emitted

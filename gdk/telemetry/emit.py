from gdk.telemetry.metric import Metric
from gdk.telemetry.telemetry import ITelemetry, Telemetry


class Emit:
    """
    Wrapper around metrics and telemetry that allows us to specify an
    emiter to submit a Metric
    """

    def __init__(self, emiter: ITelemetry = None):
        self._emiter = emiter or Telemetry()

    def installed_metric(self):
        metric = Metric.Factory.installed_metric()
        self._emiter.emit(metric)

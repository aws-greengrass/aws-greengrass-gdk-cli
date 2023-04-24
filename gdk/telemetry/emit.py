from gdk._version import __version__
from gdk.runtime_config import ConfigKey, RuntimeConfig
from gdk.telemetry.metric import Metric
from gdk.telemetry.telemetry import ITelemetry, Telemetry


class Emit:
    """
    Wrapper around metrics and telemetry that allows us to specify an
    emiter to submit a Metric
    """

    def __init__(self, emiter: ITelemetry = None):
        self.runtime_config = RuntimeConfig()
        self._emiter = emiter or Telemetry()

    def installed_metric(self):
        """
        Sends an installed metric only once after the cli has been installed
        """
        installed_version = self.runtime_config.get(ConfigKey.INSTALLED)

        if installed_version == __version__:
            return

        metric = Metric.Factory.installed_metric()
        self._emiter.emit(metric)
        self.runtime_config.set(ConfigKey.INSTALLED, __version__)

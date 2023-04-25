import sys

from gdk._version import __version__
from gdk.telemetry.telemetry_config import ConfigKey, TelemetryConfig
from gdk.telemetry import get_telemetry_enabled
from gdk.telemetry.metric import Metric
from gdk.telemetry.telemetry import ITelemetry, Telemetry

TELEMETRY_PROMPT = """
\t====================== GDK CLI Telemetry =============================

\tGDK CLI now collects telemetry to better understand customer needs.

\tYou can OPT OUT and disable telemetry collection by setting the
\tenvironment variable GDK_CLI_TELEMETRY=0 in your shell.
\tThanks for your help!

\t======================================================================
"""  # noqa


def send_metric(func):
    """
    Wrapper around calling a methos which emits a metric. It will skip calling the wrapped
    method completely if telemetry is disabled. If it is the first time sending any telemetry
    metric, it will print out a prompt notifying the user.
    """
    def wrapper(*args, **kwargs):
        # Skip emition if telemetry disabled
        telemetry_enabled = get_telemetry_enabled()

        if not telemetry_enabled:
            return

        config = TelemetryConfig()
        # We determine if it is the first install if there has not install metric
        # that has been emitted
        first_install = not bool(config.get(ConfigKey.INSTALLED))

        if first_install and telemetry_enabled:
            sys.stdout.write(TELEMETRY_PROMPT)

        return func(*args, **kwargs)

    return wrapper


class Emit:
    """
    Wrapper around metrics and telemetry that allows us to specify an
    emiter to submit a Metric
    """

    def __init__(self, emiter: ITelemetry = None):
        self.telemetry_config = TelemetryConfig()
        self._emiter = emiter or Telemetry()

    @send_metric
    def installed_metric(self):
        """
        Sends an installed metric only once after the cli has been installed
        """
        installed_version = self.telemetry_config.get(ConfigKey.INSTALLED)

        if installed_version == __version__:
            return

        metric = Metric.Factory.installed_metric()
        self._emiter.emit(metric)
        self.telemetry_config.set(ConfigKey.INSTALLED, __version__)

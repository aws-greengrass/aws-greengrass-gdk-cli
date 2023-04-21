import logging
import platform
import time
from typing import Literal

from gdk._version import __version__

logger = logging.getLogger(__name__)


def send_installed_metric():
    from gdk.telemetry.telemetry import Telemetry
    logger.debug("Sending Installed Metric")

    telemetry = Telemetry()
    metric = Metric("INSTALLED")
    metric.add_dimension("osPlatform", platform.system())
    metric.add_dimension("osRelease", platform.release())
    metric.add_dimension("machine", platform.machine())
    metric.add_dimension("arch", platform.architecture()[0])
    metric.add_dimension("pythonVersion", platform.python_version())
    telemetry.emit(metric)


MetricTypes = Literal["INSTALLED", "BUILD", "PUBLISH", "TEMPLATE", "PING"]


class Metric:
    def __init__(self, type: MetricTypes, epoch=int(time.time())):
        self.type = type
        self.dimensions = dict()
        self.timestamp = epoch
        self.meta = dict(gdk_version=__version__)

    def add_dimension(self, key: str, value: str):
        self.dimensions[key] = value


class MetricEncoder:

    def encode(self, m: Metric):
        return {
            "name": m.type,
            "meta": m.meta,
            "timestamp": m.timestamp,
            "dimensions": m.dimensions
        }

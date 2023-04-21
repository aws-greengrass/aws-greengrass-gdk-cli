import logging
import platform
import time
from enum import Enum

from gdk._version import __version__

logger = logging.getLogger(__name__)


MetricType = Enum('MetricTypes', ["INSTALLED", "COMPONENT_BUILD", "COMPONENT_PUBLISH", "TEMPLATE", "PING"])


class Metric:
    def __init__(self, type: MetricType, epoch=int(time.time())):
        self.type = type
        self.dimensions = dict()
        self.timestamp = epoch
        self.meta = dict(gdk_version=__version__)

    def add_dimension(self, key: str, value: str):
        self.dimensions[key] = value

    class Factory:

        @staticmethod
        def installed_metric(epoch=int(time.time())):
            metric = Metric(MetricType.INSTALLED, epoch)
            metric.add_dimension("osPlatform", platform.system())
            metric.add_dimension("osRelease", platform.release())
            metric.add_dimension("machine", platform.machine())
            metric.add_dimension("arch", platform.architecture()[0])
            metric.add_dimension("pythonVersion", platform.python_version())

            return metric


class MetricEncoder:

    def encode(self, m: Metric):
        return {
            "name": m.type.name,
            "meta": m.meta,
            "timestamp": m.timestamp,
            "dimensions": m.dimensions
        }

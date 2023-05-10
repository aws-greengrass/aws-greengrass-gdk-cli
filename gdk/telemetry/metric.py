import logging
import time
from enum import Enum

from gdk._version import __version__

logger = logging.getLogger(__name__)


MetricType = Enum('MetricTypes', ["INSTALLED", "BUILD", "PUBLISH", "TEMPLATE", "PING"])


class Metric:
    def __init__(self, type: MetricType, epoch=int(time.time())):
        self.type = type
        self.dimensions = dict()
        self.timestamp = epoch
        self.meta = dict(gdk_version=__version__)

    def add_dimension(self, key: str, value: str):
        self.dimensions[key] = value


class MetricEncoder:

    def encode(self, m: Metric):
        return {
            "name": m.type.name,
            "meta": m.meta,
            "timestamp": m.timestamp,
            "dimensions": m.dimensions
        }

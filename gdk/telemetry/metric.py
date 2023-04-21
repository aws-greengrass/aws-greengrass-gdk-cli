import logging
import time
from typing import Literal

from gdk._version import __version__

logger = logging.getLogger(__name__)


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

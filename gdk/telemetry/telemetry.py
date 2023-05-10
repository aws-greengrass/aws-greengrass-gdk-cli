import logging
from abc import ABC, abstractmethod

import requests

from gdk.telemetry import get_telemetry_enabled, get_telemetry_url
from gdk.telemetry.metric import Metric, MetricEncoder

logger = logging.getLogger(__name__)


class ITelemetry(ABC):

    @abstractmethod
    def emit(self, metric: Metric):
        pass


class Telemetry(ITelemetry):
    """
    Wrapper around requests to sends telemetry data to the telemetry service.
    """

    def __init__(self, url=None):
        self.url = url or get_telemetry_url()
        self.enabled = get_telemetry_enabled()

    def emit(self, metric: Metric):
        """
        Sends data to the telemetry service ONLY when telemetry is enabled
        """
        if self.enabled:
            self._emit(metric)
        else:
            logger.debug("Telemetry disabled. Metric not being sent")

    def _emit(self, metric: Metric):
        """
        Sends telemetry data to the telemetry service.
        """
        logger.debug("Sending telemetry data to %s: %s", self.url, metric)
        payload = {'metrics': [MetricEncoder().encode(metric)]}

        try:
            r = requests.post(self.url, json=payload, timeout=5)
            logger.debug("Telemetry data sent. response: %s", r.status_code)
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            logger.debug(str(e))

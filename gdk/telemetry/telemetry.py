import logging
from abc import ABC, abstractmethod

import requests
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest

from gdk import telemetry
from gdk.telemetry.metric import Metric, MetricEncoder

logger = logging.getLogger(__name__)


class ITelemetry(ABC):

    @abstractmethod
    def emit(self, metric: Metric):
        """
        Abstract method for a telemetry class to send telemetry metrics to a destination.
        """
        pass


class Telemetry(ITelemetry):
    """
    Wrapper around requests to sends telemetry data to the telemetry service.
    """
    AWS_REGION = 'us-west-2'
    AWS_SERVICE = 'execute-api'

    def __init__(self, url=None, credentials=None):
        self.url = url or telemetry.get_telemetry_url()
        self.enabled = telemetry.get_telemetry_enabled()
        self._credentials = credentials

    @property
    def credentials(self):
        if self._credentials is None:
            self._credentials = telemetry.get_aws_credentials()

        return self._credentials

    def emit(self, metric: Metric):
        """
        Sends data to the telemetry service ONLY when telemetry is enabled
        """
        if self.enabled:
            self._emit(metric)
        else:
            logger.debug("Telemetry disabled. Metric not being sent")

    def _signed_request(self, url: str, json: dict) -> requests.Request:
        """
        Uses sigv4 to sign the request before sending it.
        """
        request = AWSRequest(method='POST', url=url, data=json)
        SigV4Auth(self.credentials, self.AWS_SERVICE, self.AWS_REGION).add_auth(request)
        return requests.post(url=url, headers=dict(request.headers), json=json, timeout=5)

    def _emit(self, metric: Metric):
        """
        Sends telemetry data to the telemetry service.
        """
        logger.debug("Sending telemetry data to %s: %s", self.url, metric)
        payload = {'metrics': [MetricEncoder().encode(metric)]}

        try:
            r = self._signed_request(self.url, json=payload)
            logger.debug("Telemetry data sent. response: %s", r.status_code)
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            logger.debug(str(e))

import os

import sys
import tempfile
import time
from threading import Thread
from unittest import TestCase

from flask import Flask, Response, request
from mock import patch
from werkzeug.serving import make_server

from gdk import CLIParser
from gdk.telemetry.telemetry_config import GDK_TELEMETRY_CONFIG_DIR, TelemetryConfig
from gdk.telemetry import GDK_CLI_TELEMETRY, GDK_CLI_TELEMETRY_ENDPOINT_URL

TELEMETRY_ENDPOINT_PORT = "18298"
TELEMETRY_ENDPOINT_HOST = "localhost"
TELEMETRY_ENDPOINT_URL = "http://{}:{}/metrics".format(TELEMETRY_ENDPOINT_HOST, TELEMETRY_ENDPOINT_PORT)


class TelemetryTestCase(TestCase):
    """
    Base case for all telemetry related tests
    """

    def setUp(self) -> None:
        self.setup_telemetry_url()
        self.setup_telemetry_config_path()
        self.teardown_telemetry_config()

    def tearDown(self) -> None:
        self.teardown_telemetry_config()
        self.disable_telemetry()

    def run_command(self, command_list=[]):
        if len(command_list) == 0:
            raise Exception("No command was specified")

        argv = ["gdk"]
        argv.extend(command_list)

        with patch.object(sys, 'argv', argv):
            CLIParser.main()

    def setup_telemetry_url(self) -> None:
        os.environ[GDK_CLI_TELEMETRY_ENDPOINT_URL] = TELEMETRY_ENDPOINT_URL

    def setup_telemetry_config_path(self) -> None:
        temp_dir = tempfile.mktemp()
        os.environ[GDK_TELEMETRY_CONFIG_DIR] = temp_dir

    def teardown_telemetry_config(self) -> None:
        config = TelemetryConfig(force_create=True)
        # Delete the persisted config file if exists after each test
        if config.config_path.exists():
            os.remove(config.config_path)

    def disable_telemetry(self):
        os.environ[GDK_CLI_TELEMETRY] = "0"

    def enable_telemetry(self):
        os.environ[GDK_CLI_TELEMETRY] = "1"


class TelemetryServer:
    """
    HTTP Server used for integration tests to simulate the the GDK Telemetry service
    """

    def __init__(self):
        super().__init__()

        self.flask_app = Flask(__name__)

        self.flask_app.add_url_rule(
            "/metrics",
            endpoint="/metrics",
            view_func=self._request_handler,
            methods=["POST"],
            provide_automatic_options=False,
        )

        self._requests = []

    def __enter__(self):
        self.server = make_server(TELEMETRY_ENDPOINT_HOST, TELEMETRY_ENDPOINT_PORT, self.flask_app)
        self.thread = Thread(target=self.server.serve_forever)
        self.thread.daemon = True  # When test completes, this thread will die automatically
        self.thread.start()  # Start the thread

        return self

    def __exit__(self, *args, **kwargs):
        # Flask will start shutting down only *after* the above request completes.
        # Just give the server a little bit of time to teardown finish
        time.sleep(2)

        self.server.shutdown()
        self.thread.join()

    def get_metrics_endpoint(self):
        return f"{TELEMETRY_ENDPOINT_URL}/metrics"

    def get_request(self, index):
        return self._requests[index]

    def get_all_requests(self):
        return list(self._requests)

    def _request_handler(self, **kwargs):
        """
        Handles Flask requests
        """

        # `request` is a variable populated by Flask automatically when handler method is called
        request_data = {
            "endpoint": request.endpoint,
            "method": request.method,
            "data": request.get_json(),
            "headers": dict(request.headers),
        }

        self._requests.append(request_data)

        return Response(response={}, status=200)

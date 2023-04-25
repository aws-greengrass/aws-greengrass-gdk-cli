import os
import random
import string
import sys
import tempfile
import time
from threading import Thread
from unittest import TestCase

import botocore.credentials
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from flask import Flask, Response, request
from mock import patch
from werkzeug.serving import make_server

from gdk import CLIParser
from gdk.telemetry import GDK_CLI_TELEMETRY, GDK_CLI_TELEMETRY_ENDPOINT_URL
from gdk.telemetry.telemetry_config import (GDK_TELEMETRY_CONFIG_DIR,
                                            TelemetryConfig)

TELEMETRY_ENDPOINT_PORT = "18298"
TELEMETRY_ENDPOINT_HOST = "localhost"
TELEMETRY_ENDPOINT_URL = "http://{}:{}/metrics".format(TELEMETRY_ENDPOINT_HOST, TELEMETRY_ENDPOINT_PORT)


class TelemetryTestCase(TestCase):
    """
    Base case for all telemetry related tests
    """

    def setUp(self) -> None:
        self.setup_aws_credentials()
        self.setup_telemetry_url()
        self.setup_telemetry_config_path()
        self.teardown_telemetry_config()

    def tearDown(self) -> None:
        self.teardown_telemetry_config()
        self.teardown_aws_credentials()
        self.disable_telemetry()

    def run_command(self, command_list=[]):
        if len(command_list) == 0:
            raise Exception("No command was specified")

        argv = ["gdk"]
        argv.extend(command_list)

        with patch.object(sys, 'argv', argv):
            CLIParser.main()

    def setup_aws_credentials(self):
        """
        Mock retrieving AWS credentials during telemetry test case scenarios
        """
        self.aws_creds = self.arrange_aws_credentials()
        self.creds_patcher = patch('gdk.telemetry.get_aws_credentials')
        self.mock_get_aws_credentials = self.creds_patcher.start()
        self.mock_get_aws_credentials.return_value = self.aws_creds

    def setup_telemetry_url(self) -> None:
        os.environ[GDK_CLI_TELEMETRY_ENDPOINT_URL] = TELEMETRY_ENDPOINT_URL

    def setup_telemetry_config_path(self) -> None:
        temp_dir = tempfile.mktemp()
        os.environ[GDK_TELEMETRY_CONFIG_DIR] = temp_dir

    def teardown_aws_credentials(self) -> None:
        self.creds_patcher.stop()

    def teardown_telemetry_config(self) -> None:
        config = TelemetryConfig(force_create=True)
        # Delete the persisted config file if exists after each test
        if config.config_path.exists():
            os.remove(config.config_path)

    def _generate_random_choice(self, length, *additional_choices):
        _choices = string.ascii_uppercase + string.digits

        for c in additional_choices:
            _choices += c

        return ''.join(random.choices(_choices, k=length))

    def arrange_aws_credentials(self):
        """
        Sets up fake aws credentials for testing.
        """
        access_key_length = 20
        secret_key_length = 40
        token_length = 60

        fake_access_key = self._generate_random_choice(access_key_length)
        fake_secret_key = self._generate_random_choice(secret_key_length, string.ascii_lowercase, "/+=")
        fake_token = self._generate_random_choice(token_length, string.ascii_lowercase, "/+=")

        credentials = botocore.credentials.Credentials(
            access_key=fake_access_key,
            secret_key=fake_secret_key,
            token=fake_token
        )

        return credentials.get_frozen_credentials()

    def disable_telemetry(self):
        os.environ[GDK_CLI_TELEMETRY] = "0"

    def enable_telemetry(self):
        os.environ[GDK_CLI_TELEMETRY] = "1"


class TelemetryServer:
    """
    HTTP Server used for integration tests to simulate the the GDK Telemetry service
    """

    def __init__(self, aws_crendtials, shutdown_timeout=2):
        super().__init__()

        self.aws_credentials = aws_crendtials
        self.shutdow_timeout = shutdown_timeout

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
        time.sleep(self.shutdow_timeout)

        self.server.shutdown()
        self.thread.join()

    @property
    def metrics_endpoint(self):
        return TELEMETRY_ENDPOINT_URL

    def get_request(self, index):
        return self._requests[index]

    def get_all_requests(self):
        return list(self._requests)

    def _parse_auth_header(self, auth_header: str):
        """
        The auth header of a sigv4 requests looks something like this
        AWS4-HMAC-SHA256 Credential=<credential-scope>, SignedHeaders=<signed-headers>, Signature=<signature>"
        """
        # Remove the prefix containit the encryption algo info before splitting
        input_str = auth_header.replace("AWS4-HMAC-SHA256 ", "")

        output_dict = {}

        for val in input_str.split(", "):
            key, value = val.split("=")
            output_dict[key] = value

        return output_dict

    def _is_sigv4_signed(self) -> bool:
        """
        Returns True if the given request is signed with SigV4, False otherwise.
        """
        if 'Authorization' not in request.headers or \
                'X-Amz-Date' not in request.headers or \
                'Host' not in request.headers:
            return False

        auth_parts = self._parse_auth_header(request.headers['Authorization'])
        _, _, region, service, _ = auth_parts.get("Credential").split('/')

        aws_request = AWSRequest(method=request.method, url=request.url, data=request.get_json())
        SigV4Auth(self.aws_credentials, service, region).add_auth(aws_request)

        headers = request.headers
        expected_headers = dict(request.headers)

        # Compare the signed headers to the headers in the original request
        for expected_header, value in expected_headers.items():
            if expected_header not in headers or value != headers[expected_header]:
                return False

        return True

    def _request_handler(self, **kwargs):
        """
        Handles Flask requests
        """
        if not self._is_sigv4_signed():
            return Response(response={}, status=403)

        # `request` is a variable populated by Flask automatically when handler method is called
        request_data = {
            "endpoint": request.endpoint,
            "method": request.method,
            "data": request.get_json(),
            "headers": dict(request.headers),
        }

        self._requests.append(request_data)

        return Response(response={}, status=200)

from threading import Thread
import time
from flask import Flask, Response, request
from werkzeug.serving import make_server


TELEMETRY_ENDPOINT_PORT = "18298"
TELEMETRY_ENDPOINT_HOST = "localhost"
TELEMETRY_ENDPOINT_URL = "http://{}:{}".format(
    TELEMETRY_ENDPOINT_HOST, TELEMETRY_ENDPOINT_PORT
)


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
        self.server = make_server(
            TELEMETRY_ENDPOINT_HOST, TELEMETRY_ENDPOINT_PORT, self.flask_app
        )
        self.thread = Thread(target=self.server.serve_forever)
        self.thread.daemon = (
            True  # When test completes, this thread will die automatically
        )
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

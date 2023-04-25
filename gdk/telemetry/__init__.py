import os

import boto3

GDK_CLI_TELEMETRY_ENDPOINT_URL = "__GDK_CLI_TELEMETRY_ENDPOINT_URL"
GDK_CLI_TELEMETRY = "GDK_CLI_TELEMETRY"


def get_telemetry_url() -> str:
    return os.getenv(GDK_CLI_TELEMETRY_ENDPOINT_URL, "https://localhost:5029/metrics")


def get_telemetry_enabled() -> bool:
    # Telemetry disabled by default - This will change to default to true
    env_telemetry_setting = os.getenv(GDK_CLI_TELEMETRY, "0")

    if env_telemetry_setting == "1":
        return True
    else:
        return False


def get_aws_credentials():
    """
    Retrieves the aws credentials for the user using boto.
    """
    session = boto3.Session()
    credentials = session.get_credentials()
    return credentials.get_frozen_credentials()

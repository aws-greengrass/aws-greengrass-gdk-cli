import os


GDK_CLI_TELEMETRY_ENDPOINT_URL = "__GDK_CLI_TELEMETRY_ENDPOINT_URL"
GDK_CLI_TELEMETRY = "GDK_CLI_TELEMETRY"


def get_telemetry_url() -> str:
    return os.getenv(GDK_CLI_TELEMETRY_ENDPOINT_URL, "https://localhost:5029/metrics")


def get_telemetry_enabled() -> bool:
    # Telemetry disabled by default - This will change to default to true
    env_telemetry_setting = os.getenv(GDK_CLI_TELEMETRY, "False")

    if env_telemetry_setting == "True":
        return True
    else:
        return False

from faker import Faker
from faker.providers import color
import pytest

from gdk.common.configuration import validate_configuration

fake = Faker()
fake.add_provider(color)


def configuration_base(options: dict) -> dict:
    base = {
        "component": {
            "com.build.zip": {
                "author": "abc",
                "version": "1.0.0",
                "build": {"build_system": "zip"},
                "publish": {"bucket": "default", "region": "us-east-1"},
            }
        },
        "gdk_version": "1.2.0",
    }

    if options is not None:
        base["component"]["com.build.zip"]["build"].setdefault("options", options)

    return base


@pytest.mark.parametrize(
    "options",
    [None, {"excludes": ["*.ts"]}, dict()],
)
def test_valid_configuration_options(options):
    validate_configuration(configuration_base(options))

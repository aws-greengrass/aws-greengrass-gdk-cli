import gdk.common.utils as utils
from packaging.version import Version


def test_valid_cli_latest_version():
    assert Version(utils.get_latest_cli_version()) >= Version(utils.cli_version)

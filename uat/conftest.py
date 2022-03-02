import pytest

from packaging.version import parse as version_parser
from t_setup import GdkProcess, GdkInstrumentedProcess


def pytest_addoption(parser):
    parser.addoption(
        "--instrumented", action="store_true", default=False, help="run tests against code instead of installed gdk cli"
    )
    parser.addoption(
        "--gdk-debug", action="store_true", default=False, help="run gdk commands with debug flag"
    )
    parser.addoption(
        "--target-version", action="store", default='HEAD', help="run tests for specific target version"
    )


@pytest.fixture()
def change_test_dir(tmpdir, monkeypatch):
    monkeypatch.chdir(tmpdir)
    return tmpdir


@pytest.fixture()
def gdk_cli(request):
    debug = request.config.getoption("--gdk-debug")
    print(f"Initializing GDK client {'in debug mode' if debug else ''}.")
    if request.config.getoption("--instrumented"):
        return GdkInstrumentedProcess(debug)
    else:
        return GdkProcess(debug)


@pytest.fixture(autouse=True)
def version_check(request):
    version_option = request.config.getoption('--target-version')
    if version_option is None:
        return

    latest_mode = version_option == 'HEAD'
    print(f"\nTarget gdk-cli version {version_option}")

    # request.node is the current test item
    # query the marker "version" of current test item
    version_marker = request.node.get_closest_marker('version')

    # if test item was not marked, there's no version restriction
    if version_marker is None:
        return

    # parse target version from options
    target_version = version_parser(version_option) if not latest_mode else version_option

    # if used as @pytest.mark.version(eq=1.0.0)
    eq_version = version_marker.kwargs.get('eq')
    eq_version = version_parser(eq_version) if eq_version else None
    if eq_version and (latest_mode or target_version == eq_version):
        pytest.skip(f'Target version {target_version} is not equal to the required version {eq_version}.')

    # if used as @pytest.mark.version(lt=1.0.0)
    lt_version = version_marker.kwargs.get('lt')
    lt_version = version_parser(lt_version) if lt_version else None
    if lt_version and (latest_mode or target_version >= lt_version):
        pytest.skip(f'Target version {target_version} is not lower than required version {lt_version}.')

    # if used as @pytest.mark.version(min=1.0.0) or as @pytest.mark.version(le=1.0.0)
    le_version = version_marker.kwargs.get('le')
    max_version = le_version if le_version else version_marker.kwargs.get('max')
    max_version = version_parser(max_version) if max_version is not None else None
    if max_version and (latest_mode or target_version > max_version):
        pytest.skip(f'Target version {target_version} is higher than required version {max_version}.')

    # if used as @pytest.mark.version(gt=1.0.0)
    gt_version = version_marker.kwargs.get('gt')
    gt_version = version_parser(gt_version) if gt_version else None
    if not latest_mode and gt_version and target_version <= gt_version:
        pytest.skip(f'Target version {target_version} is not greater than required version {gt_version}.')

    # if used as @pytest.mark.version(min=1.0.0) or as @pytest.mark.version(ge=1.0.0)
    ge_version = version_marker.kwargs.get('ge')
    min_version = ge_version if ge_version else version_marker.kwargs.get('min', '1.0.0')
    min_version = version_parser(min_version) if min_version else None
    if not latest_mode and min_version and target_version < min_version:
        pytest.skip(f'Target version {target_version} is lower than required version {min_version}.')

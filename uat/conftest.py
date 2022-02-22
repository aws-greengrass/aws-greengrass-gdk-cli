import pytest

from t_setup import GdkProcess, GdkInstrumentedProcess


def pytest_addoption(parser):
    parser.addoption(
        "--instrumented", action="store_true", default=False, help="run tests against code instead of installed gdk cli"
    )


@pytest.fixture()
def change_test_dir(tmpdir, monkeypatch):
    monkeypatch.chdir(tmpdir)
    return tmpdir


@pytest.fixture()
def gdk_cli(request):
    if request.config.getoption("--instrumented"):
        return GdkInstrumentedProcess()
    else:
        return GdkProcess()

import pytest

from t_setup import GdkProcess, GdkInstrumentedProcess


def pytest_addoption(parser):
    parser.addoption(
        "--gdkimpl", action="store", default="installed", help="supports two gdk implementations: installed or code"
    )


@pytest.fixture()
def change_test_dir(tmpdir, monkeypatch):
    monkeypatch.chdir(tmpdir)
    return tmpdir


@pytest.fixture()
def gdk_cli(request):
    option = request.config.getoption("--gdkimpl")
    if option == "code":
        return GdkInstrumentedProcess()
    else:
        return GdkProcess()

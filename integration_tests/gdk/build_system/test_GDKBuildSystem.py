from unittest import TestCase

from gdk.build_system.E2ETestBuildSystem import E2ETestBuildSystem
from pathlib import Path
import os
import shutil
import pytest


class GDKBuildSystemTest(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker, tmpdir):
        self.mocker = mocker
        self.tmpdir = tmpdir
        self.c_dir = Path(".").resolve()
        os.chdir(tmpdir)
        yield
        os.chdir(self.c_dir)

    def test_GDKBuildSystem_maven(self):
        # Set up test data
        source = Path(self.c_dir).joinpath("integration_tests/test_data").joinpath("maven")
        dest = Path(self.tmpdir).joinpath("maven").resolve()
        shutil.copytree(source, dest)
        os.chdir(dest)

        build_system = E2ETestBuildSystem.get("maven")
        build_system.build()

        target_folder = dest.joinpath("target").joinpath("HelloWorld-1.0.0.jar").resolve()
        assert target_folder.exists()

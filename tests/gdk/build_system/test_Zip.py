import pytest
from pathlib import Path
from unittest import TestCase

from gdk.build_system.Zip import Zip
from tests.helpers.project_config import arrange_project_config


class ZipTests(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker):
        self.mocker = mocker

    def project_config(self, build_options: dict):
        return arrange_project_config({
            "component_build_config": {
                "build_system": "zip",
                "options": build_options
            }
        })

    def test_zip_build_with_excludes_option_only(self):
        # Given
        config = self.project_config({"excludes": [".env"]})
        build_folder = Path(Path(".").resolve()).joinpath('zip-build')

        # When
        zip = Zip(config, {build_folder})

        # Then
        ignore_list = zip.ignore_list(None, None)
        assert len(ignore_list) > 0
        assert ".env" in ignore_list

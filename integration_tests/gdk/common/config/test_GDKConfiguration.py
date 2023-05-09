from pathlib import Path
import pytest
from unittest import TestCase
from gdk.common.config.GDKConfiguration import GDKConfiguration


class GDKConfigurationTest(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker):
        self.mocker = mocker

    def test_default_values_for_gdk_test_config(self):
        self.mocker.patch(
            "gdk.common.configuration._get_project_config_file",
            return_value=Path(".")
            .joinpath("integration_tests/test_data/config")
            .joinpath("config_without_test.json")
            .resolve(),
        )

        gdk_config = GDKConfiguration()
        assert gdk_config.component_name == "abc"
        assert gdk_config.test_config.otf_version == "1.1.0-SNAPSHOT"
        assert gdk_config.test_config.test_build_system == "maven"
        assert gdk_config.test_config.otf_tag == "Sample"
        assert gdk_config.test_config.otf_options == {}

    def test_default_values_for_gdk_test_config_(self):
        self.mocker.patch(
            "gdk.common.configuration._get_project_config_file",
            return_value=Path(".").joinpath("integration_tests/test_data/config").joinpath("config.json").resolve(),
        )

        gdk_config = GDKConfiguration()
        assert gdk_config.component_name == "abc"
        assert gdk_config.test_config.otf_version == "1.2.0"
        assert gdk_config.test_config.test_build_system == "maven"
        assert gdk_config.test_config.otf_tag == "testtags"
        assert gdk_config.test_config.nucleus_version == "2.0.0"

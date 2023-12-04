import pytest
from unittest import TestCase
from pathlib import Path
import os
from gdk.commands.test.config.InitConfiguration import InitConfiguration
from gdk.common.config.GDKProject import GDKProject
from gdk.common.GithubUtils import GithubUtils
import requests


class InitConfigurationUnitTest(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker, tmpdir):
        self.mocker = mocker
        self.tmpdir = tmpdir
        self.mocker.patch.object(GithubUtils, "get_latest_release_name", return_value="1.2.0")
        self.c_dir = Path(".").resolve()
        self.mocker.patch.object(GDKProject, "_get_recipe_file", return_value=Path(".").joinpath("recipe.json").resolve())
        os.chdir(tmpdir)
        response = requests.Response()
        response.status_code = 200

        self.mocker.patch("requests.head", return_value=response)
        yield
        os.chdir(self.c_dir)

    def test_given_gdk_config_with_no_test_when_get_test_init_configuration_then_return_default_configuration(self):
        config = self._get_config()

        self.mocker.patch("gdk.common.configuration.get_configuration", return_value=config)
        init_config = InitConfiguration({})
        assert init_config.gtf_version == "1.2.0"

    def test_GIVEN_gdk_config_with_otf_version_WHEN_test_init_THEN_use_version_from_config(self):
        config = self._get_config(
            {
                "test-e2e": {
                    "otf_version": "1.2.3",
                }
            }
        )
        self.mocker.patch("gdk.common.configuration.get_configuration", return_value=config)

        init_config = InitConfiguration({})

        assert init_config.gtf_version == "1.2.3"

    def test_GIVEN_gdk_config_with_gtf_and_otf_version_WHEN_test_init_THEN_use_version_from_config(self):
        config = self._get_config(
            {
                "test-e2e": {
                    "gtf_version": "1.2.3",
                    "otf_version": "1.3.4"
                }
            }
        )
        self.mocker.patch("gdk.common.configuration.get_configuration", return_value=config)
        init_config = InitConfiguration({})
        assert init_config.gtf_version == "1.2.3"

    def test_GIVEN_gdk_config_with_gtf_version_WHEN_test_init_THEN_use_gtf_version_from_config(self):
        config = self._get_config(
            {
                "test-e2e": {
                    "gtf_version": "1.2.3",
                }
            }
        )
        self.mocker.patch("gdk.common.configuration.get_configuration", return_value=config)
        init_config = InitConfiguration({})
        assert init_config.gtf_version == "1.2.3"

    def test_GIVEN_gdk_config_with_gtf_version_WHEN_test_init_with_otf_version_arg_THEN_use_arg_version(self):
        config = self._get_config(
            {
                "test-e2e": {
                    "gtf_version": "1.1.0",
                }
            }
        )
        self.mocker.patch("gdk.common.configuration.get_configuration", return_value=config)
        init_config = InitConfiguration({"otf_version": "1.2.3"})
        assert init_config.gtf_version == "1.2.3"

    def test_GIVEN_gdk_config_with_gtf_version_WHEN_test_init_with_gtf_version_arg_THEN_use_arg_version(self):
        config = self._get_config(
            {
                "test-e2e": {
                    "gtf_version": "1.1.0",
                }
            }
        )
        self.mocker.patch("gdk.common.configuration.get_configuration", return_value=config)
        init_config = InitConfiguration({"gtf_version": "1.2.3"})
        assert init_config.gtf_version == "1.2.3"

    def test_GIVEN_gdk_config_with_version_WHEN_test_init_with_gtf_and_otf_version_arg_THEN_use_gtf_arg_version(self):
        config = self._get_config(
            {
                "test-e2e": {
                    "gtf_version": "1.1.0",
                }
            }
        )
        self.mocker.patch("gdk.common.configuration.get_configuration", return_value=config)
        init_config = InitConfiguration({"otf_version": "1.2.3", "gtf_version": "1.0.0"})
        assert init_config.gtf_version == "1.0.0"

    def test_GIVEN_gdk_config_with_invalid_otf_version_WHEN_test_init_THEN_raise_exc(self):
        config = self._get_config(
            {
                "test-e2e": {
                    "otf_version": "1.a.b",
                }
            }
        )
        self.mocker.patch("gdk.common.configuration.get_configuration", return_value=config)

        with pytest.raises(ValueError) as e:
            InitConfiguration({})

        assert (
            "GTF version 1.a.b is not a valid semver. Please specify a valid GTF version in the GDK config or in the command"
            " argument."
            in str(e.value)
        )

    def test_GIVEN_gdk_config_WHEN_test_init_with_otf_version_arg_THEN_use_version_from_arg(self):
        config = self._get_config()
        self.mocker.patch("gdk.common.configuration.get_configuration", return_value=config)
        init_config = InitConfiguration({"otf_version": "1.1.0+12-build"})
        assert init_config.gtf_version == "1.1.0+12-build"

    def test_GIVEN_gdk_config_WHEN_test_init_with_invalid_otf_version_arg_THEN_raise_exc(self):
        config = self._get_config()

        self.mocker.patch("gdk.common.configuration.get_configuration", return_value=config)
        with pytest.raises(ValueError) as e:
            InitConfiguration({"otf_version": "1.a.b"})

        assert (
            "GTF version 1.a.b is not a valid semver. Please specify a valid GTF version in the GDK config or in the command"
            " argument."
            in str(e.value)
        )

    def test_GIVEN_gdk_config_with_otf_version_WHEN_test_init_with_otf_version_arg_THEN_use_version_from_arg(self):
        config = self._get_config(
            {
                "test-e2e": {
                    "otf_version": "1.a.b",
                }
            }
        )
        self.mocker.patch("gdk.common.configuration.get_configuration", return_value=config)
        init_config = InitConfiguration({"otf_version": "1.2.3"})
        assert init_config.gtf_version == "1.2.3"

    def test_GIVEN_gdk_config_with_otf_version_and_version_not_exits_and_WHEN_test_init_THEN_raise_ex(self):
        config = self._get_config(
            {
                "test-e2e": {
                    "otf_version": "1.a.b",
                }
            }
        )
        response = requests.Response()
        response.status_code = 404

        self.mocker.patch("requests.head", return_value=response)
        self.mocker.patch("gdk.common.configuration.get_configuration", return_value=config)
        with pytest.raises(ValueError) as e:
            InitConfiguration({"otf_version": "1.2.3"})
        assert (
            "The specified Greengrass Test Framework (GTF) version '1.2.3' does not exist. Please provide a valid GTF "
            "version from the releases here:"
            in e.value.args[0]
        )

    def _get_config(self, value=None):
        config = {
            "component": {
                "abc": {
                    "author": "abc",
                    "version": "1.0.0",
                    "build": {"build_system": "zip"},
                    "publish": {"bucket": "default", "region": "us-east-1"},
                }
            }
        }
        if value:
            config.update(value)
        return config

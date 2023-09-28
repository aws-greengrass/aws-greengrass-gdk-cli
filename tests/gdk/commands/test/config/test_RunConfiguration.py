import pytest
from unittest import TestCase
from pathlib import Path
import os
from gdk.commands.test.config.RunConfiguration import RunConfiguration
from unittest import mock
from gdk.common.config.GDKProject import GDKProject


class RunConfigurationUnitTest(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker, tmpdir):
        self.mocker = mocker
        self.tmpdir = tmpdir
        self.c_dir = Path(".").resolve()
        self.mocker.patch.object(GDKProject, "_get_recipe_file", return_value=Path(".").joinpath("recipe.json").resolve())
        os.chdir(tmpdir)
        yield
        os.chdir(self.c_dir)

    def test_given_gdk_config_with_no_test_when_get_test_run_configuration_then_return_default_configuration(self):
        config = self._get_config()

        self.mocker.patch("gdk.common.configuration.get_configuration", return_value=config)
        run_config = RunConfiguration({})

        assert run_config.options.get("tags") == "Sample"
        assert run_config.options.get("ggc-archive") == str(
            Path().absolute().joinpath("greengrass-build/greengrass-nucleus-latest.zip").resolve()
        )

        assert len(run_config.options) == 2

    def test_GIVEN_gdk_config_with_tags_WHEN_run_with_tag_args_THEN_use_tags_from_args(self):
        config = self._get_config(
            {
                "test-e2e": {
                    "otf_options": {"tags": "some-tags", "ggc-version": "1.0.0"},
                }
            }
        )

        self.mocker.patch("gdk.common.configuration.get_configuration", return_value=config)

        run_config = RunConfiguration({"otf_options": '{"tags": "some-other-tags"}'})

        assert run_config.options.get("tags") == "some-other-tags"
        assert (
            run_config.options.get("ggc-archive")
            == Path().absolute().joinpath("greengrass-build/greengrass-nucleus-latest.zip").resolve().__str__()
        )

        assert len(run_config.options) == 3

    def test_GIVEN_gdk_config_with_tags_WHEN_run_with_gtf_tag_args_THEN_use_tags_from_args(self):
        config = self._get_config(
            {
                "test-e2e": {
                    "otf_options": {"tags": "some-tags", "ggc-version": "1.0.0"},
                }
            }
        )
        self.mocker.patch("gdk.common.configuration.get_configuration", return_value=config)
        run_config = RunConfiguration({"gtf_options": '{"tags": "some-other-tags"}'})
        assert run_config.options.get("tags") == "some-other-tags"

    def test_GIVEN_gdk_config_with_tags_WHEN_run_with_gtf_and_otf_tag_args_THEN_use_gtf_tags_from_args(self):
        config = self._get_config(
            {
                "test-e2e": {
                    "otf_options": {"tags": "some-tags", "ggc-version": "1.0.0"},
                }
            }
        )
        self.mocker.patch("gdk.common.configuration.get_configuration", return_value=config)
        run_config = RunConfiguration(
            {
                "gtf_options": '{"tags": "some-other-tags"}',
                "otf_options": '{"tags": "another-tag"}'
            }
        )
        assert run_config.options.get("tags") == "some-other-tags"

    def test_GIVEN_gdk_config_with_gtf_and_otf_options_WHEN_run_without_args_THEN_use_gtf_options(self):
        config = self._get_config(
            {
                "test-e2e": {
                    "gtf_options": {"tags": "some-tags", "ggc-version": "1.0.0"},
                    "otf_options": {"tags": "some-other-tags", "ggc-version": "1.1.0"},
                }
            }
        )
        self.mocker.patch("gdk.common.configuration.get_configuration", return_value=config)
        run_config = RunConfiguration({})
        assert run_config.options.get("tags") == "some-tags"
        assert run_config.options.get("ggc-version") == "1.0.0"

    def test_GIVEN_gdk_config_with_three_options_WHEN_run_with_two_overriding_args_THEN_merge_args(self):
        config = self._get_config(
            {
                "test-e2e": {
                    "otf_options": {
                        "tags": "some-tags",
                        "ggc-install-root": "some-install-root",
                        "gg-runtime": "some-runtime",
                    },
                }
            }
        )

        self.mocker.patch("gdk.common.configuration.get_configuration", return_value=config)

        run_config = RunConfiguration(
            {"otf_options": '{"tags": "tags-from-args", "ggc-install-root": "install-root-from-args"}'}
        )

        assert run_config.options.get("tags") == "tags-from-args"
        assert run_config.options.get("gg-runtime") == "some-runtime"
        assert run_config.options.get("ggc-install-root") == "install-root-from-args"
        assert (
            run_config.options.get("ggc-archive")
            == Path().absolute().joinpath("greengrass-build/greengrass-nucleus-latest.zip").resolve().__str__()
        )
        assert len(run_config.options) == 4

    def test_GIVEN_gdk_config_with_three_options_WHEN_run_with_two_overriding_args_from_file_THEN_merge_args(self):
        config = self._get_config(
            {
                "test-e2e": {
                    "otf_options": {
                        "tags": "some-tags",
                        "ggc-install-root": "some-install-root",
                        "gg-runtime": "some-runtime",
                    },
                }
            }
        )
        self.mocker.patch("gdk.common.configuration.get_configuration", return_value=config)
        self.mocker.patch("pathlib.Path.exists", return_value=True)

        with mock.patch(
            "builtins.open",
            mock.mock_open(read_data='{"tags": "tags-from-args", "ggc-install-root": "install-root-from-args"}'),
        ) as mock_file:
            run_config = RunConfiguration({"otf_options": "/path/to/gtf_options.json"})
            assert mock_file.return_value.read.call_count == 1

        assert run_config.options.get("tags") == "tags-from-args"
        assert run_config.options.get("gg-runtime") == "some-runtime"
        assert run_config.options.get("ggc-install-root") == "install-root-from-args"
        assert (
            run_config.options.get("ggc-archive")
            == Path().absolute().joinpath("greengrass-build/greengrass-nucleus-latest.zip").resolve().__str__()
        )
        assert len(run_config.options) == 4

    def test_given_gdk_config_with_tags_when_get_test_run_configuration_tags_then_return_given_tags(self):
        config = self._get_config(
            {
                "test-e2e": {
                    "otf_options": {"tags": "some-tags", "ggc-version": "1.0.0"},
                }
            }
        )

        self.mocker.patch("gdk.common.configuration.get_configuration", return_value=config)

        run_config = RunConfiguration({})

        assert run_config.options.get("tags") == "some-tags"
        assert (
            run_config.options.get("ggc-archive")
            == Path().absolute().joinpath("greengrass-build/greengrass-nucleus-latest.zip").resolve().__str__()
        )

        assert len(run_config.options) == 3

    def test_given_gdk_config_with_empty_tags_when_get_test_run_configuration_tags_then_raise_exception(self):
        config = self._get_config(
            {
                "test-e2e": {
                    "otf_options": {"tags": "", "ggc-version": "1.0.0"},
                }
            }
        )

        self.mocker.patch("gdk.common.configuration.get_configuration", return_value=config)

        with pytest.raises(Exception) as e:
            RunConfiguration({})

        assert "Test tags provided in the config are invalid. Please check 'tags' in the test config" in str(e.value)

    def test_given_gdk_config_with_nucleus_archive_path_when_get_configuration_archive_path_then_validate_and_return(
        self,
    ):
        config = self._get_config(
            {
                "test-e2e": {
                    "otf_options": {"ggc-archive": "some-path.zip"},
                }
            }
        )

        self.mocker.patch("gdk.common.configuration.get_configuration", return_value=config)
        self.mocker.patch("pathlib.Path.exists", return_value=True)

        run_config = RunConfiguration({})

        assert run_config.options.get("tags") == "Sample"
        assert run_config.options.get("ggc-archive") == Path().joinpath("some-path.zip").resolve().__str__()

        assert len(run_config.options) == 2

    def test_given_gdk_config_with_nucleus_archive_path_when_path_not_exists_then_raise_exception(self):
        config = self._get_config(
            {
                "test-e2e": {
                    "otf_options": {"ggc-archive": "some-path.zip"},
                }
            }
        )

        self.mocker.patch("gdk.common.configuration.get_configuration", return_value=config)

        with pytest.raises(Exception) as e:
            RunConfiguration({})

        assert (
            "Cannot find nucleus archive at path some-path.zip. Please check 'ggc-archive' in the test config"
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

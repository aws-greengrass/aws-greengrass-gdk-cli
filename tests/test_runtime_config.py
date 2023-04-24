

import json
import os
import tempfile
from pathlib import Path

import mock

from gdk._version import __version__
from gdk.runtime_config import (GDK_RUNTIME_CONFIG_DIR, ConfigKey,
                                RuntimeConfig)
from integration_tests.gdk.telemetry.telemetry_base import TelemetryTestCase


class TestRuntimeConfig(TelemetryTestCase):

    def test_there_is_a_single_instance(self):
        config_a = RuntimeConfig()
        config_b = RuntimeConfig()

        self.assertEqual(config_a, config_b)

    def test_it_can_store_values(self):
        config = RuntimeConfig(force_create=True)
        config.set(ConfigKey.INSTALLED, __version__)

        version = config.get(ConfigKey.INSTALLED)
        self.assertEqual(version, __version__)

    def test_it_returns_none_when_value_not_stored(self):
        config = RuntimeConfig(force_create=True)
        version = config.get(ConfigKey.INSTALLED)

        self.assertIsNone(version)

    def test_it_persists_config_to_the_file_system(self):
        config = RuntimeConfig()
        config.set(ConfigKey.INSTALLED, __version__)

        self.assertTrue(config.config_path.exists())

        content = config.config_path.read_text()
        json_content = json.loads(content)

        expected = {ConfigKey.INSTALLED.value: __version__}
        self.assertEqual(expected, json_content)

    def test_it_loads_persisted_config_from_file_system(self):
        config_a = RuntimeConfig()
        config_a.set(ConfigKey.INSTALLED, __version__)

        config_b = RuntimeConfig(force_create=True)
        version = config_b.get(ConfigKey.INSTALLED)

        self.assertEqual(__version__, version)

    def test_it_does_not_load_config_if_corrupted_json_file(self):
        config = RuntimeConfig()
        config.set(ConfigKey.INSTALLED, __version__)

        # Corrupt the file to an invalid json
        config.config_path.write_text("hello")

        config = RuntimeConfig(force_create=True)
        self.assertIsNone(config.get(ConfigKey.INSTALLED))

    def test_it_gracefully_fails_writing_config_to_disk(self):
        mock_path = mock.MagicMock(spec=Path)
        mock_path.write_text.side_effect = IOError("Write failure")

        config = RuntimeConfig()
        config.config_path = mock_path
        config.set(ConfigKey.INSTALLED, __version__)

        version = config.get(ConfigKey.INSTALLED)
        self.assertEqual(__version__, version)

    def test_it_can_load_the_config_path_from_an_env_variable(self):
        temp_dir = tempfile.mktemp()
        os.environ[GDK_RUNTIME_CONFIG_DIR] = temp_dir

        config = RuntimeConfig(force_create=True)
        expected_path = Path(temp_dir, "runtime.json")
        self.assertEqual(str(expected_path), str(config.config_path))

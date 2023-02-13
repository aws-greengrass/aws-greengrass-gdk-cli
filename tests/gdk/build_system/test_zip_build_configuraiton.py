import pytest
from unittest import TestCase

from gdk.common.configuration import validate_configuration


class ZipConfigurationTests(TestCase):

    def configuration_base(self, options: dict):
        base = {
            "component": {
                "com.build.zip": {
                    "author": "abc",
                    "version": "1.0.0",
                    "build": {
                        "build_system": "zip"
                    },
                    "publish": {
                        "bucket": "default",
                        "region": "us-east-1"
                    },
                }
            },
            "gdk_version": "1.0.0",
        }

        if options is not None:
            base["component"]["com.build.zip"]["build"].setdefault("options", options)

        return base

    def test_valid_configuration_options(self):
        options = None
        validate_configuration(self.configuration_base(options))

        options = {"includes": ["src/*.ts"]}
        validate_configuration(self.configuration_base(options))

        options = {"excludes": ["src/*.js"]}
        validate_configuration(self.configuration_base(options))

        options = {"includes": ["src/*.ts"], "excludes": ["src/*.js"]}
        validate_configuration(self.configuration_base(options))

    def test_invalid_configuration_options(self):
        with pytest.raises(Exception):
            options = {"includes": []}
            validate_configuration(self.configuration_base(options))

        with pytest.raises(Exception):
            options = {"excludes": []}
            validate_configuration(self.configuration_base(options))

        with pytest.raises(Exception):
            options = {}
            validate_configuration(self.configuration_base(options))

        with pytest.raises(Exception):
            options = {"foo": "bar"}
            validate_configuration(self.configuration_base(options))

import pytest
from unittest import TestCase
from gdk.commands.test.RunCommand import RunCommand
from pathlib import Path
import os


class RunCommandUnitTest(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker, tmpdir):
        self.mocker = mocker
        self.tmpdir = Path(tmpdir)
        self.c_dir = Path(".").resolve()

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

        self.mocker.patch("gdk.common.configuration.get_configuration", return_value=config)
        self.mocker.patch("gdk.commands.component.project_utils.get_recipe_file", return_value=Path("."))
        os.chdir(tmpdir)
        yield
        os.chdir(self.c_dir)

    def test_given_test_module_not_built_when_run_uats_then_raise_exception(self):
        def file_exists(self):
            return str(self) == str(Path().resolve().joinpath("uat-features/target"))

        self.mocker.patch.object(Path, "exists", file_exists)
        run_cmd = RunCommand({})
        with pytest.raises(Exception) as e:
            run_cmd.run()
        assert "UAT module is not built." in e.value.args[0]

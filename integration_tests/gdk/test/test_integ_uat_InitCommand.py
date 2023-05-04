from unittest import TestCase

import gdk.CLIParser as CLIParser
import gdk.common.parse_args_actions as parse_args_actions
import pytest
from pathlib import Path
import os
from gdk.commands.test.InitCommand import InitCommand


class CommandUATTest(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker, tmpdir):
        self.mocker = mocker
        self.tmpdir = tmpdir
        self.c_dir = Path(".").resolve()
        os.chdir(tmpdir)
        yield
        os.chdir(self.c_dir)

    def test_init_run_gdk_project(self):
        parse_args_actions.run_command(CLIParser.cli_parser.parse_args(["test", "init", "-d"]))
        uat_folder = Path(self.tmpdir).joinpath("uat-features")
        assert uat_folder.exists()
        assert uat_folder.joinpath("pom.xml") in list(uat_folder.iterdir())

    def test_init_run_gdk_project_already_initiated(self):
        # uat-features already exists but is empty
        Path(self.tmpdir).joinpath("uat-features").mkdir()
        parse_args_actions.run_command(CLIParser.cli_parser.parse_args(["test", "init", "-d"]))
        # existing uat-features folder is not overridden
        assert Path(self.tmpdir).resolve("uat-features").exists()
        assert list(Path(self.tmpdir).joinpath("uat-features").iterdir()) == []

    def test_init_run_gdk_project_template_not_exists(self):
        with pytest.raises(Exception) as e:
            init_command = InitCommand({})
            init_command.template_name = "doesnotexist"
            init_command.run()
        assert f"404 Client Error: Not Found for url: {init_command.template_url}" in e.value.args[0]

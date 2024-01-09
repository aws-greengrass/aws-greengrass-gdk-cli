from pathlib import Path
from unittest import TestCase
import pytest
from gdk.build_system.E2ETestBuildSystem import E2ETestBuildSystem
from unittest.mock import call
import platform

from gdk.common import utils


class E2ETestBuildSystemTests(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker):
        self.mocker = mocker

    def test_maven_build_system(self):
        mock_subprocess = self.mocker.patch("subprocess.run")
        build_system = E2ETestBuildSystem.get("maven")
        build_system.build()

        assert build_system.build_folder == ["target"]
        assert build_system.build_system_identifier == ["pom.xml"]
        if platform.system() == "Windows":
            assert mock_subprocess.call_args_list == [call(["mvn.cmd", "package"], check=True, cwd=None)]
        else:
            assert mock_subprocess.call_args_list == [call(["mvn", "package"], check=True, cwd=None)]

    def test_gradle_build_system(self):
        mock_subprocess = self.mocker.patch("subprocess.run")
        build_system = E2ETestBuildSystem.get("gradle")
        build_system.build()

        assert build_system.build_folder == ["build", "libs"]
        assert build_system.build_system_identifier == ["build.gradle", "build.gradle.kts"]
        assert mock_subprocess.call_args_list == [call(["gradle", "build"], check=True, cwd=None)]

    def test_gradle_wrapper_build_system(self):
        mock_subprocess = self.mocker.patch("subprocess.run")
        build_system = E2ETestBuildSystem.get("gradlew")
        build_system.build()

        assert build_system.build_folder == ["build", "libs"]
        assert build_system.build_system_identifier == ["build.gradle", "build.gradle.kts"]

        if platform.system() == "Windows":
            assert mock_subprocess.call_args_list == [call([str(Path(utils.get_current_directory()).joinpath(
                "gradlew.bat").absolute()), "build"], check=True, cwd=utils.get_current_directory())]
        else:
            assert mock_subprocess.call_args_list == [call(["./gradlew", "build"], check=True,
                                                           cwd=utils.get_current_directory())]

    def test_build_system_not_supported(self):
        with pytest.raises(Exception) as e:
            E2ETestBuildSystem.get("does-not-exist")
        assert "Build system type 'does-not-exist' is not supported" in e.value.args[0]

    def test_build_system_empty_(self):
        with pytest.raises(Exception) as e:
            E2ETestBuildSystem.get("  ")
        assert "Build system not specified" in e.value.args[0]

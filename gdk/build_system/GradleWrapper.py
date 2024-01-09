import logging
import platform
import subprocess as sp
from pathlib import Path

from gdk.build_system.GDKBuildSystem import GDKBuildSystem
from gdk.common import utils


class GradleWrapper(GDKBuildSystem):
    @property
    def build_command(self):
        os_platform = platform.system()
        if os_platform == "Windows":
            return [str(Path(self.path).joinpath("gradlew.bat").absolute()), "build"]
        else:
            return ["./gradlew", "build"]

    @property
    def build_folder(self):
        return ["build", "libs"]

    @property
    def build_system_identifier(self):
        return ["build.gradle", "build.gradle.kts"]

    def build(self, **kwargs):
        self.path = kwargs.get("path") or utils.get_current_directory()
        logging.info("Running the build command '%s'", " ".join(self.build_command))
        sp.run(self.build_command, check=True, cwd=self.path)

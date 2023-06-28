import subprocess as sp
from gdk.build_system.GDKBuildSystem import GDKBuildSystem
import platform
import logging


class GradleWrapper(GDKBuildSystem):
    @property
    def build_command(self):
        os_platform = platform.system()
        if os_platform == "Windows":
            return ["./gradlew.bat", "build"]
        else:
            return ["./gradlew", "build"]

    @property
    def build_folder(self):
        return ["build", "libs"]

    @property
    def build_system_identifier(self):
        return ["build.gradle", "build.gradle.kts"]

    def build(self, **kwargs):
        path = kwargs.get("path")
        logging.info("Running the build command '%s'", " ".join(self.build_command))
        sp.run(self.build_command, check=True, cwd=path)
